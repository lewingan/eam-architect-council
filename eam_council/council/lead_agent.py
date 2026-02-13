"""Lead orchestrator agent - dispatches to subagents and reconciles."""

from __future__ import annotations

import asyncio
from pathlib import Path

import anthropic
from rich.console import Console

from eam_council.council.agentic_architecture_subagent import run_agentic_arch_subagent
from eam_council.council.general_eam_subagent import run_general_subagent
from eam_council.council.mock_data import get_mock_context
from eam_council.council.prompts import (
    ALIGNMENT_VALIDATOR_SYSTEM,
    LEAD_AGENT_SYSTEM,
    build_alignment_check_prompt,
    build_lead_prompt,
    classify_question,
    filter_context_for_question,
    is_agentic_question,
)
from eam_council.council.sap_eam_subagent import run_sap_subagent
from eam_council.council.llm import create_with_retry
from eam_council.council.runtime_config import load_runtime_config
from eam_council.council.skills_loader import load_all_skills, load_selected_skills
from eam_council.council.telemetry import RunTelemetry

console = Console()

DRY_RUN_FINAL = """\
# EAM Architecture Council -- Response

## Question
How should we architect a work order scheduling module for SAP EAM?

## Executive Summary
The council recommends a hybrid architecture that leverages SAP PM's native scheduling capabilities via published OData APIs (API_MAINTORDER_SRV, API_MAINTENANCEPLAN_SRV) while introducing an external constraint-based scheduling engine for advanced optimization. This approach combines SAP's data authority with industry-standard scheduling best practices.

## SAP EAM Perspective
The SAP expert recommends building on SAP PM's scheduling framework using the published OData v4 APIs on the SAP Business Accelerator Hub. Key services include API_MAINTORDER_SRV (work orders and operations), API_EQUIPMENT_SRV (asset master), and API_WORKCENTER_SRV (resource/capacity data). Integration via SAP BTP Integration Suite for event-driven patterns.

## General EAM Perspective
The general EAM expert recommends a priority-driven, constraint-based scheduling engine decoupled from the CMMS via an integration layer. Follows ISO 55000 principles with a rolling 2-week firm / 6-week planning horizon.

## Agentic Architecture Perspective
Not applicable for this question.

## Agent Suitability Decision
- **Decision:** Not Suitable
- **Why (technical + business):** This request is not asking for a new AI agent, so an agent implementation would add unnecessary complexity.
- **If Not Suitable, Better Alternative:** Deliver as a deterministic service/module with standard integration patterns.

## Impact & Worthwhile Assessment
- **SAP EAM Expert View:** Low impact for an agent approach in this specific request.
- **General EAM Expert View:** Low impact for an agent approach in this specific request.
- **Agentic Architecture Expert View:** Not applicable for this question.
- **Overall Council Verdict:** Not worthwhile to build an agent for this request.

## Unified Recommendation

### Architecture Components
- **SAP PM Core:** Source of truth for work orders, equipment, and work centers.
- **Scheduling Engine:** External service implementing constraint-based optimization.
- **Integration Layer:** OData v4 adapter for SAP PM data synchronization.
- **Scheduling UI:** Custom frontend with Gantt view and drag-and-drop rescheduling.

### Data Model Considerations
- Use SAP canonical entities (Work Order, Equipment, Work Center, Operation) as the base.
- Extend with scheduling-specific entities: Time Slot, Resource Calendar, Scheduling Score.
- Event sourcing for schedule change audit trail.

### Integration Points
- SAP PM <-> Scheduling Engine: OData v4 (pull), BTP events (push)
- Scheduling Engine <-> UI: REST API (JSON)
- Scheduling Engine <-> MRP: Async check for parts availability

#### SAP API References
| API Service | Entity Set | Purpose | Hub Link |
|---|---|---|---|
| API_MAINTORDER_SRV | MaintenanceOrder, MaintenanceOrderOperation | Work order and operation CRUD | https://api.sap.com/api/API_MAINTORDER/overview |
| API_EQUIPMENT_SRV | Equipment | Asset master data | https://api.sap.com/api/API_EQUIPMENT/overview |
| API_WORKCENTER_SRV | WorkCenter | Resource/capacity data | https://api.sap.com/api/API_WORKCENTER/overview |
| API_MAINTENANCEPLAN_SRV | MaintenancePlan | Schedule definitions | https://api.sap.com/api/API_MAINTENANCEPLAN/overview |
| API_FUNCLOCATION_SRV | FunctionalLocation | Plant hierarchy | https://api.sap.com/api/API_FUNCLOCATION/overview |

## Assumptions & Open Questions
- [ ] S/4HANA 2023+ is the target platform
- [ ] Single-plant scope for initial PoC
- [ ] OData APIs are enabled and accessible
- [ ] Confirm OData vs BAPI for write-back operations
- [ ] Define priority escalation rules for overdue PMs
- [ ] Clarify whether scheduling considers spare parts availability
- [ ] Evaluate solver options (OR-Tools vs OptaPlanner vs custom)

## Decision Log
| # | Decision | Rationale | Alternative Considered |
|---|----------|-----------|----------------------|
| 1 | Use OData v4 for SAP integration | Industry-standard, real-time capable, supported in S/4HANA | RFC/BAPI (less modern, harder to maintain) |
| 2 | External scheduling engine | SAP native scheduling lacks constraint-based optimization | Pure SAP CM01-based scheduling (limited flexibility) |
| 3 | Event sourcing for schedule changes | Audit trail and change history are critical for maintenance compliance | Simple CRUD (loses history) |
| 4 | Rolling horizon (2wk firm / 6wk plan) | Industry best practice balances commitment with flexibility | Fixed monthly schedule (too rigid) |

## Next Agent To Build
**Scheduling Constraint Solver Module** -- A deterministic optimization module that takes a set of work orders,
resource calendars, and constraints (safety windows, production schedules, parts availability) and produces an
optimized schedule.
- **Inputs:** work order list, resource availability, constraint rules.
- **Outputs:** scheduled timeline, conflict report, optimization score.
- **Tool/API contracts:** SAP OData read/write endpoints for orders/operations and calendar ingestion interface.
- **Memory/state strategy:** Persist schedule snapshots and decision traces per planning run.
- **MVP scope:** Single plant, preventive maintenance orders only, daily batch optimization.
- **Acceptance criteria:** >=90% schedule feasibility, <10 min run time per batch, auditable decision log.
"""


DRY_RUN_FINAL_AGENTIC = """\
# EAM Architecture Council -- Response

## Question
How should we architect an agent to design and optimize SAP EAM work order scheduling workflows?

## Executive Summary
Yes -- add a dedicated **Agentic Architecture Expert** when questions involve building a new agent or
multi-agent workflow. SAP and General EAM experts should remain responsible for domain correctness, while
this new expert guides runtime architecture, orchestration, safety, and optimization.

## SAP EAM Perspective
Retain SAP PM/S4 API-first patterns and constrain agent outputs to supported integration surfaces.

## General EAM Perspective
Retain vendor-agnostic reliability and maintenance planning best practices as non-negotiable domain guardrails.

## Agentic Architecture Perspective
The agentic expert recommends a dedicated agentic design layer for agent-building requests,
with explicit orchestration, tool contracts, observability, and evaluation loops.

## Agent Suitability Decision
- **Decision:** Suitable
- **Why (technical + business):** The use case explicitly asks to design an EAM-related agent; agentic capabilities provide measurable value via orchestration, tool use, and adaptive planning while retaining domain guardrails.
- **If Not Suitable, Better Alternative:** Not applicable.

## Impact & Worthwhile Assessment
- **SAP EAM Expert View:** High impact when constrained to approved SAP APIs and governance boundaries.
- **General EAM Expert View:** High impact when paired with stable maintenance processes and clear KPI ownership.
- **Agentic Architecture Expert View:** High impact due to improved adaptability, observability, and optimization loops.
- **Overall Council Verdict:** Worth building now as a scoped MVP with clear guardrails and measurable outcomes.

## Unified Recommendation

### Architecture Components
- **Intent Router** to detect EAM-only vs agentic requests.
- **SAP EAM Expert** for SAP constraints and integration details.
- **General EAM Expert** for industry process guidance.
- **Agentic Architecture Expert** for agent platform, orchestration, and optimization patterns.
- **Lead Reconciler** to merge into one buildable response.

### Data Model Considerations
- Keep canonical EAM entities unchanged as shared facts.
- Add agent-runtime entities: Tool Contract, Plan Step, Trace Event, and Eval Result.

### Integration Points
- Agent runtime <-> EAM experts: structured prompt contracts.
- Agent runtime <-> SAP systems: only approved API/OData endpoints.
- Agent runtime <-> observability: trace and evaluation sinks.

## Assumptions & Open Questions
- [ ] Preferred agent runtime platform (hosted vs self-managed) is still open.
- [ ] Cost/latency SLOs need definition before selecting planner depth.
- [ ] Safety policy for tool use/write actions needs approval.

## Decision Log
| # | Decision | Rationale | Alternative Considered |
|---|----------|-----------|----------------------|
| 1 | Add Agentic Architecture Expert | Existing experts are domain-strong but not runtime-architecture focused | Keep only 2 experts |
| 2 | Use routing for optional third expert | Avoids extra cost on non-agentic questions | Always invoke third expert |

## Next Agent To Build
**EAM Work Order Orchestrator Agent** -- Coordinates planning, SAP data retrieval, and schedule recommendation generation.
- **Inputs:** user intent, maintenance backlog, equipment criticality, work-center capacity, policy constraints.
- **Outputs:** ranked execution plan, rationale trace, exception list, and write-back payload candidates.
- **Tool/API contracts:** SAP OData APIs (orders/equipment/work centers), policy-check tool, and notification tool.
- **Memory/state strategy:** Short-term task memory for current planning cycle + persistent audit trace store.
- **MVP scope:** Read-only recommendations for one plant and one order type.
- **Acceptance criteria:** recommendation precision target met, policy violations blocked, and full traceability for each recommendation.
"""


def _validator_needs_clarification(result_text: str) -> tuple[bool, str | None, str | None]:
    """Parse validator output for clarification routing."""
    text = result_text.strip()
    if text == "ALIGNED":
        return False, None, None
    if not text.startswith("NEEDS_CLARIFICATION"):
        return False, None, None

    target = None
    reason = None
    for part in [p.strip() for p in text.split("|")]:
        if part.startswith("target="):
            target = part.split("=", 1)[1].strip().lower()
        if part.startswith("reason="):
            reason = part.split("=", 1)[1].strip()

    return True, target, reason


async def _request_clarification(
    *,
    target: str,
    reason: str | None,
    question: str,
    skills_context: str,
    mock_context: str,
    model: str,
    dry_run: bool,
    search_enabled: bool,
    sap_draft: str,
    general_draft: str,
    agentic_draft: str | None,
):
    """Request a targeted clarification from one expert."""
    clarification_question = (
        f"{question}\n\n"
        f"Clarification request from Lead Architect: {reason or 'Resolve any contradictions and align with other experts.'}\n"
        f"Please return only updated guidance for your domain and explicitly resolve the issue."
    )

    if target == "sap":
        return await run_sap_subagent(
            clarification_question,
            skills_context,
            mock_context,
            model,
            dry_run,
            search_enabled,
        )

    if target == "general":
        return await run_general_subagent(
            clarification_question,
            skills_context,
            mock_context,
            model,
            dry_run,
            search_enabled,
        )

    if target == "agentic":
        return await run_agentic_arch_subagent(
            clarification_question,
            skills_context,
            mock_context,
            model,
            dry_run,
            sap_draft=sap_draft,
            general_draft=general_draft,
        )

    return None


async def run_council(
    question: str,
    model: str,
    dry_run: bool = False,
    search_enabled: bool = True,
) -> str:
    """Run the full council workflow and return the final output."""
    cfg = load_runtime_config()
    telemetry = RunTelemetry()

    console.print("[dim]Loading skills and resources...[/dim]")
    if cfg.context_routing_v2:
        classification = classify_question(question)
        selected_skills = {"eam_council", "eam_glossary_entities"}
        if classification != "general":
            selected_skills.add("eam_spec_writer")
        include_resources = {
            "eam_glossary_entities": {"glossary.md"} if cfg.minimal_mode else {"glossary.md", "canonical_entities.yaml"},
            "eam_council": {"output_format.md", "reconciliation_rules.md"},
            "eam_spec_writer": {"spec_template.md"} if cfg.minimal_mode else {"spec_template.md", "example_spec_work_order_scheduling.md"},
        }
        skills_context = load_selected_skills(include_skills=selected_skills, include_resources=include_resources)
    else:
        skills_context = load_all_skills()

    mock_context = "" if cfg.minimal_mode else get_mock_context()

    effective_search = search_enabled
    if cfg.conditional_search:
        effective_search = search_enabled and classify_question(question) == "api"

    search_label = " (with web search)" if effective_search else ""
    console.print(f"[dim]Consulting SAP EAM expert{search_label}...[/dim]")
    console.print(f"[dim]Consulting General EAM expert{search_label}...[/dim]")

    agentic_mode = is_agentic_question(question)
    search_budget = cfg.search_budget
    sap_search = effective_search and search_budget > 0
    if sap_search:
        search_budget -= 1
    general_search = effective_search and search_budget > 0
    if general_search:
        search_budget -= 1

    sap_draft, general_draft = await asyncio.gather(
        run_sap_subagent(question, skills_context, mock_context, model, dry_run, sap_search),
        run_general_subagent(question, skills_context, mock_context, model, dry_run, general_search),
    )
    telemetry.record(stage="sap", prompt_chars=len(question) + len(skills_context) + len(mock_context), completion_chars=len(sap_draft.content), elapsed_ms=0, tool_uses=1 if sap_search else 0)
    telemetry.record(stage="general", prompt_chars=len(question) + len(skills_context) + len(mock_context), completion_chars=len(general_draft.content), elapsed_ms=0, tool_uses=1 if general_search else 0)

    if agentic_mode:
        console.print("[dim]Consulting Agentic Architecture expert (after EAM drafts)...[/dim]")
        agentic_draft = await run_agentic_arch_subagent(
            question,
            skills_context,
            mock_context,
            model,
            dry_run,
            sap_draft=sap_draft.content,
            general_draft=general_draft.content,
        )
        telemetry.record(stage="agentic", prompt_chars=len(question) + len(skills_context) + len(mock_context) + len(sap_draft.content) + len(general_draft.content), completion_chars=len(agentic_draft.content), elapsed_ms=0)
    else:
        agentic_draft = None

    console.print(f"[green]OK[/green] SAP expert responded ({len(sap_draft.content)} chars)")
    console.print(f"[green]OK[/green] General expert responded ({len(general_draft.content)} chars)")
    if agentic_draft:
        console.print(f"[green]OK[/green] Agentic expert responded ({len(agentic_draft.content)} chars)")

    console.print("[dim]Lead architect reconciling...[/dim]")

    lead_skills_context = filter_context_for_question(skills_context, question) if cfg.context_routing_v2 else skills_context

    if dry_run:
        final_output = DRY_RUN_FINAL_AGENTIC if agentic_mode else DRY_RUN_FINAL
    else:
        client = anthropic.Anthropic()

        lead_prompt = build_lead_prompt(
            question,
            sap_draft.content,
            general_draft.content,
            lead_skills_context,
            agentic_draft.content if agentic_draft else None,
            compact=cfg.lead_compaction,
        )
        response = create_with_retry(
            client,
            retries=cfg.retries if cfg.enable_retry else 0,
            model=model,
            max_tokens=cfg.lead_max_tokens,
            system=LEAD_AGENT_SYSTEM,
            messages=[{"role": "user", "content": lead_prompt}],
        )
        final_output = response.content[0].text
        telemetry.record(stage="lead", prompt_chars=len(lead_prompt), completion_chars=len(final_output), elapsed_ms=0)

        required_sections = [
            "Executive Summary",
            "SAP EAM Perspective",
            "General EAM Perspective",
            "Agentic Architecture Perspective",
            "Agent Suitability Decision",
            "Impact & Worthwhile Assessment",
            "Unified Recommendation",
            "Assumptions & Open Questions",
            "Decision Log",
            "Next Agent To Build",
        ]

        def _has_all_sections(text: str) -> bool:
            low = text.lower()
            return all(s.lower() in low for s in required_sections)

        if not _has_all_sections(final_output):
            response = create_with_retry(
                client,
                retries=cfg.retries if cfg.enable_retry else 0,
                model=model,
                max_tokens=cfg.lead_max_tokens_escalated,
                system=LEAD_AGENT_SYSTEM,
                messages=[{"role": "user", "content": lead_prompt}],
            )
            final_output = response.content[0].text

        for _ in range(2):
            check_prompt = build_alignment_check_prompt(
                question,
                sap_draft.content,
                general_draft.content,
                final_output,
                agentic_draft.content if agentic_draft else None,
            )
            check = create_with_retry(
                client,
                retries=cfg.retries if cfg.enable_retry else 0,
                model=model,
                max_tokens=400,
                system=ALIGNMENT_VALIDATOR_SYSTEM,
                messages=[{"role": "user", "content": check_prompt}],
            )
            verdict = check.content[0].text
            needs_fix, target, reason = _validator_needs_clarification(verdict)
            if not needs_fix or not target:
                break

            console.print(
                f"[yellow]Validation flagged misalignment[/yellow] -> requesting clarification from {target} expert"
            )
            updated = await _request_clarification(
                target=target,
                reason=reason,
                question=question,
                skills_context=skills_context,
                mock_context=mock_context,
                model=model,
                dry_run=dry_run,
                search_enabled=False,
                sap_draft=sap_draft.content,
                general_draft=general_draft.content,
                agentic_draft=agentic_draft.content if agentic_draft else None,
            )

            if updated is None:
                break

            if target == "sap":
                sap_draft = updated
            elif target == "general":
                general_draft = updated
            elif target == "agentic":
                agentic_draft = updated

            lead_prompt = build_lead_prompt(
                question,
                sap_draft.content,
                general_draft.content,
                lead_skills_context,
                agentic_draft.content if agentic_draft else None,
                compact=True,
            )
            response = create_with_retry(
                client,
                retries=cfg.retries if cfg.enable_retry else 0,
                model=model,
                max_tokens=cfg.lead_max_tokens,
                system=LEAD_AGENT_SYSTEM,
                messages=[{"role": "user", "content": lead_prompt}],
            )
            final_output = response.content[0].text

    telemetry.write_json(Path("out") / "telemetry_latest.json")

    console.print("[green]OK[/green] Reconciliation complete")
    return final_output
