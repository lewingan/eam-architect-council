# Plan: API-First Agent Improvements + Web Search Capability

## Problem Summary

The agents produce generic, table-centric responses (AUFK, AFVC, CRHD, etc.) because:

1. **Canonical entities YAML** defines every entity with `sap_table` as a top-level field, priming the model to regurgitate table names.
2. **Glossary** embeds SAP table names directly in term definitions (e.g., "Work Order... In SAP: AUFK table").
3. **SAP subagent system prompt** explicitly mandates listing "Relevant SAP objects/tables/transactions" in every response, regardless of the question.
4. **No context filtering** — the full knowledge base (glossary, entities, mock data) is injected into every call via `build_subagent_prompt`, so every question gets the same table-heavy context dump.
5. **No live data** — agents cannot look up current SAP API Hub documentation, so they fall back on static, memorized table knowledge.

---

## Step 1: Restructure canonical entities from table-first to API-first

**File:** `eam_council/skills/eam_glossary_entities/resources/canonical_entities.yaml`

**Changes:**
- Rename `sap_table` field to `sap_legacy_table` and move it to a secondary/reference position under a new `sap_internals` block.
- Add a new top-level `sap_api` block per entity with fields:
  - `odata_service` — the primary OData v4 service name (e.g., `API_MAINTORDER_SRV` for work orders)
  - `odata_entity_set` — the entity set name within the service
  - `api_hub_url` — SAP Business Accelerator Hub link for the service
- This ensures the model sees the API as the primary interface, with the table as legacy context only.

**Example (work_order entity after change):**
```yaml
work_order:
  description: A formal maintenance task instruction
  sap_api:
    odata_service: API_MAINTORDER_SRV
    odata_entity_set: MaintenanceOrder
    api_hub_url: https://api.sap.com/api/API_MAINTORDER/overview
  sap_internals:
    legacy_table: AUFK
    transactions: [IW31, IW32, IW33]
  fields:
    ...
```

---

## Step 2: Update glossary to lead with API abstractions

**File:** `eam_council/skills/eam_glossary_entities/resources/glossary.md`

**Changes:**
- Rewrite each glossary entry to lead with the OData service / API name instead of the SAP table.
- Move the table reference to a parenthetical at the end, labelled as "legacy."

**Example:**
```
| **Work Order (WO)** | A formal instruction to perform a maintenance task. SAP API: API_MAINTORDER_SRV. (Legacy table: AUFK) |
```

---

## Step 3: Rewrite SAP subagent system prompt to be API-first and question-aware

**File:** `eam_council/council/prompts.py` — `SAP_EAM_SUBAGENT_SYSTEM`

**Changes:**
- Replace the mandate to list "Relevant SAP objects/tables/transactions" with a mandate to list "Relevant SAP APIs (OData services, entity sets)" as the primary output.
- Add explicit instruction: "Only reference SAP tables or transactions when the question specifically concerns data migration, ABAP custom development, or debugging — never for integration or architecture questions."
- Add instruction: "When recommending integration approaches, always lead with the published OData API from SAP Business Accelerator Hub. Reference BAPIs/RFCs only as fallbacks when no OData API exists."
- Update the required output structure headings from:
  - `Relevant SAP objects/tables/transactions` → `Relevant SAP APIs & Services`
- Add a new output heading: `Fallback / Legacy Notes` (optional, only when table-level info is genuinely needed).

**Updated prompt draft:**
```
Produce a focused draft response covering:
- SAP-specific architecture recommendation
- Relevant SAP APIs & services (OData service names, entity sets, SAP API Hub references)
- Integration approach (OData v4 preferred; RFC/BAPI only as fallback with justification)
- SAP-specific risks or constraints
- Key assumptions

IMPORTANT: Do NOT list SAP database tables (e.g., AUFK, EQUI, IFLO) unless the question
specifically involves data migration, ABAP custom code, or database-level debugging.
Modern SAP S/4HANA development uses published OData APIs, not direct table access.
```

---

## Step 4: Add question-aware context selection to `build_subagent_prompt`

**File:** `eam_council/council/prompts.py` — `build_subagent_prompt()`

**Changes:**
- Add a lightweight question classifier that decides which portions of the knowledge base to include. This is not an LLM call — it is keyword-based classification:
  - **Integration/architecture questions** → include API mappings from canonical entities, exclude `sap_internals` block.
  - **Data migration/ABAP questions** → include full canonical entities including `sap_internals`.
  - **General/business process questions** → include glossary only, exclude canonical entities entirely.
- Implement via a new function `classify_question(question: str) -> str` in `prompts.py` that returns one of: `"api"`, `"data"`, `"general"`.
- Modify `build_subagent_prompt` to accept the classification and filter `skills_context` accordingly.

**New function sketch:**
```python
def classify_question(question: str) -> str:
    """Classify question to determine which context to inject."""
    q = question.lower()
    data_keywords = ["migration", "abap", "table", "custom code", "debug", "data dictionary"]
    general_keywords = ["process", "strategy", "business case", "roadmap", "organizational"]
    if any(kw in q for kw in data_keywords):
        return "data"
    if any(kw in q for kw in general_keywords):
        return "general"
    return "api"  # default: API-first context
```

---

## Step 5: Add web search capability via Anthropic tool use

**Files:** New file `eam_council/council/web_search.py`, modifications to `sap_eam_subagent.py` and `lead_agent.py`

This is the most impactful improvement — it allows the SAP subagent to look up current SAP API documentation from the SAP Business Accelerator Hub at query time rather than relying on stale memorized knowledge.

### 5a: Create `web_search.py` module

**New file:** `eam_council/council/web_search.py`

Implement a function that uses the Anthropic client's tool-use capability to give the SAP subagent access to web search. This uses Anthropic's built-in `web_search` tool type supported by the Messages API.

**Implementation approach:**
- Define a web search tool configuration using Anthropic's server-side `web_search_20250305` tool type.
- When the SAP subagent is called in live mode, include this tool in the API request so the model can autonomously search SAP API Hub documentation.
- Add a prompt instruction telling the agent *when* to search: "Before recommending a specific OData API, search the SAP Business Accelerator Hub to verify the API exists and get current details (entity sets, parameters, deprecation status)."

**Tool definition:**
```python
WEB_SEARCH_TOOL = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 3,
}
```

### 5b: Modify SAP subagent to use web search tool

**File:** `eam_council/council/sap_eam_subagent.py`

**Changes:**
- Import the web search tool configuration.
- Add the tool to the `client.messages.create()` call via the `tools` parameter.
- Update the system prompt injection to include a search instruction:
  ```
  You have access to web search. Use it to look up SAP Business Accelerator Hub
  (api.sap.com) for current OData API details relevant to the question. Verify API
  names, entity sets, and availability before recommending them. Limit searches to
  3 max — search only when you need to confirm or discover a specific API.
  ```
- Handle the tool-use response loop: after the initial response, if the model returns `tool_use` blocks, process them and continue the conversation until the model produces a final `text` response.

### 5c: Optionally enable web search for the General EAM subagent

**File:** `eam_council/council/general_eam_subagent.py`

- Add web search with a different focus: searching for industry standards (ISO 55000 updates, CMMS comparison articles, EAM architecture patterns) rather than SAP-specific APIs.
- Use `max_uses: 2` to keep it lighter since this agent's value is more in domain reasoning than API specifics.

### 5d: Add `--no-search` CLI flag

**File:** `eam_council/cli.py`

- Add a `--no-search` argument that disables web search (useful for offline/cost-sensitive runs).
- Pass through to `run_council()` as a parameter.

---

## Step 6: Update dry-run responses and example spec to reflect API-first approach

**Files:**
- `eam_council/council/sap_eam_subagent.py` — `DRY_RUN_RESPONSE`
- `eam_council/council/lead_agent.py` — `DRY_RUN_FINAL`
- `eam_council/skills/eam_spec_writer/resources/example_spec_work_order_scheduling.md`

**Changes:**
- Rewrite the dry-run SAP subagent response to lead with OData API names instead of tables.
- Update the Key Entities table in the example spec from `SAP PM (AUFK/AFIH)` to `SAP PM — API_MAINTORDER_SRV (OData v4)`.
- Update `DRY_RUN_FINAL` to reflect the new API-first output style.

---

## Step 7: Update reconciliation rules to prefer API-based integration

**File:** `eam_council/skills/eam_council/resources/reconciliation_rules.md`

**Changes:**
- Add a new priority rule between #2 and #3:
  > **Published SAP API** — If a published OData API exists on the SAP Business Accelerator Hub for a capability, prefer it over custom ABAP/RFC/BAPI development.
- This ensures the lead agent's reconciliation logic favors API-based recommendations when merging the two expert drafts.

---

## Step 8: Update output format to include API references section

**File:** `eam_council/skills/eam_council/resources/output_format.md`

**Changes:**
- Under `### Integration Points`, add a sub-section `#### SAP API References` with a table:
  ```
  | API Service | Entity Set | Purpose | Hub Link |
  ```
- This gives the lead agent a structured place to surface verified API details, replacing the ad-hoc table name dumps.

---

## Summary of files changed

| # | File | Action |
|---|------|--------|
| 1 | `resources/canonical_entities.yaml` | Restructure to API-first with legacy table as secondary |
| 2 | `resources/glossary.md` | Rewrite entries to lead with API service names |
| 3 | `council/prompts.py` | Rewrite SAP system prompt; add question classifier; update prompt builder |
| 4 | **`council/web_search.py`** | **New file** — web search tool config and helper |
| 5 | `council/sap_eam_subagent.py` | Add web search tool to API call; update dry-run |
| 6 | `council/general_eam_subagent.py` | Optionally add web search; update dry-run |
| 7 | `council/lead_agent.py` | Thread `search_enabled` param; update dry-run |
| 8 | `cli.py` | Add `--no-search` flag |
| 9 | `resources/reconciliation_rules.md` | Add API-preference rule |
| 10 | `resources/output_format.md` | Add SAP API References sub-section |
| 11 | `resources/example_spec_work_order_scheduling.md` | Update to API-first references |
| 12 | `pyproject.toml` | No new dependencies needed (web search is server-side via Anthropic API) |

## Execution order

Steps 1-4 can be done in sequence (knowledge base → prompts → context filtering).
Step 5 (web search) is independent and can be developed in parallel.
Steps 6-8 are cleanup/alignment done last.
