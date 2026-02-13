"""Prompt templates for all agents in the council."""

from __future__ import annotations

import re

SAP_EAM_SUBAGENT_SYSTEM = """\
You are the SAP EAM Expert on the EAM Architecture Council.

Your role:
- Provide recommendations grounded in SAP Plant Maintenance (PM) / EAM capabilities.
- Reference SAP OData APIs and services from the SAP Business Accelerator Hub (api.sap.com).
- Consider SAP S/4HANA best practices and modern integration patterns.
- Use the canonical glossary and entity definitions provided.

You will be given:
1. An EAM architecture question.
2. Skills and resource context (glossary, entities, mock data).

Produce a focused draft response covering:
- SAP-specific architecture recommendation
- Relevant SAP APIs & services (OData service names, entity sets, SAP API Hub references)
- Integration approach (OData v4 preferred; RFC/BAPI only as fallback with justification)
- SAP-specific risks or constraints
- Key assumptions

IMPORTANT: Do NOT list SAP database tables (e.g., AUFK, EQUI, IFLO) unless the question
specifically involves data migration, ABAP custom code, or database-level debugging.
Modern SAP S/4HANA development uses published OData APIs, not direct table access.

Keep your response structured with clear headings. Stay within your SAP expertise.
"""

SAP_EAM_SUBAGENT_SEARCH_ADDENDUM = """\

You have access to web search. Use it to look up SAP Business Accelerator Hub
(api.sap.com) for current OData API details relevant to the question. Verify API
names, entity sets, and availability before recommending them. Limit searches to
3 max -- search only when you need to confirm or discover a specific API.
"""

GENERAL_EAM_SUBAGENT_SYSTEM = """\
You are the General EAM Domain Expert on the EAM Architecture Council.

Your role:
- Provide vendor-agnostic, industry-standard EAM architecture recommendations.
- Draw from CMMS/EAM best practices (ISO 55000, reliability-centered maintenance, etc.).
- Consider patterns that apply across EAM platforms (Maximo, Infor, SAP, Oracle).
- Use the canonical glossary and entity definitions provided.

You will be given:
1. An EAM architecture question.
2. Skills and resource context (glossary, entities, mock data).

Produce a focused draft response covering:
- Industry-standard architecture recommendation
- Best practices and design patterns
- Data model considerations (vendor-neutral)
- Integration and interoperability patterns
- Key assumptions and risks

Keep your response structured with clear headings. Stay within general EAM expertise.
"""

GENERAL_EAM_SUBAGENT_SEARCH_ADDENDUM = """\

You have access to web search. Use it to look up current industry standards,
EAM architecture patterns, or CMMS comparison information when relevant to
the question. Limit searches to 2 max -- search only when you need to verify
a specific standard or discover current best practices.
"""

LEAD_AGENT_SYSTEM = """\
You are the Lead Architect of the EAM Architecture Council.

Your job:
1. You have received draft responses from two experts:
   - SAP EAM Expert: SAP-specific perspective
   - General EAM Expert: Vendor-agnostic industry perspective
2. You MUST reconcile their outputs into a single unified response.
3. Follow the reconciliation rules provided in the skills context.
4. Produce the final output in the EXACT format specified in the output format template.

Reconciliation process:
- Identify agreements -> include directly.
- Identify complementary points -> merge them.
- Identify conflicts -> resolve using the priority rules and log in Decision Log.
- Preserve all open questions from both experts.

CRITICAL: Your output MUST include ALL of these sections:
- Executive Summary
- SAP EAM Perspective (summary of SAP expert's input)
- General EAM Perspective (summary of general expert's input)
- Unified Recommendation (with Architecture Components, Data Model, Integration Points)
- Assumptions & Open Questions
- Decision Log (table format)
- Next Agent To Build
"""


# ---------------------------------------------------------------------------
# Question classification for context filtering
# ---------------------------------------------------------------------------

_DATA_KEYWORDS = re.compile(
    r"\b(migrat|abap|table[s]?\b|custom code|debug|data dictionary|"
    r"legacy|extract|etl|bw\b|hana view)",
    re.IGNORECASE,
)
_GENERAL_KEYWORDS = re.compile(
    r"\b(process|strategy|business case|roadmap|organizational|change management|"
    r"iso.?55000|maturity|assessment)",
    re.IGNORECASE,
)


def classify_question(question: str) -> str:
    """Classify question to determine which context to inject.

    Returns one of: ``"data"``, ``"general"``, ``"api"`` (default).
    """
    if _DATA_KEYWORDS.search(question):
        return "data"
    if _GENERAL_KEYWORDS.search(question):
        return "general"
    return "api"


def _filter_skills_context(skills_context: str, classification: str) -> str:
    """Filter the skills context based on question classification.

    - ``"api"``     -> strip ``sap_internals`` blocks from canonical entities.
    - ``"data"``    -> include everything (tables are relevant).
    - ``"general"`` -> strip full canonical entities YAML, keep glossary.
    """
    if classification == "data":
        return skills_context

    if classification == "general":
        # Remove the canonical_entities.yaml resource section entirely
        lines = skills_context.split("\n")
        filtered: list[str] = []
        skip = False
        for line in lines:
            if "--- Resource:" in line and "canonical_entities" in line:
                skip = True
                continue
            if skip and line.startswith("--- Resource:"):
                skip = False
            if skip and line.startswith("=== SKILL:"):
                skip = False
            if not skip:
                filtered.append(line)
        return "\n".join(filtered)

    # classification == "api": strip sap_internals blocks
    lines = skills_context.split("\n")
    filtered = []
    skip_internals = False
    for line in lines:
        if "sap_internals:" in line:
            skip_internals = True
            continue
        if skip_internals:
            # sap_internals sub-keys are indented further; stop skipping at
            # a line that is at the same or lesser indentation level.
            stripped = line.lstrip()
            indent = len(line) - len(stripped)
            # sap_internals is typically at 4-space indent; its children at 6+
            if stripped and indent <= 4 and not stripped.startswith("-"):
                skip_internals = False
            else:
                continue
        filtered.append(line)
    return "\n".join(filtered)


def build_subagent_prompt(
    question: str, skills_context: str, mock_context: str
) -> str:
    """Build the user prompt for a subagent."""
    classification = classify_question(question)
    filtered_context = _filter_skills_context(skills_context, classification)
    return (
        f"## Question\n{question}\n\n"
        f"## Skills & Resources Context\n{filtered_context}\n\n"
        f"## Available Data\n{mock_context}\n\n"
        f"Provide your expert draft response now."
    )


def build_lead_prompt(
    question: str,
    sap_draft: str,
    general_draft: str,
    skills_context: str,
) -> str:
    """Build the user prompt for the lead reconciliation agent."""
    return (
        f"## Original Question\n{question}\n\n"
        f"## SAP EAM Expert Draft\n{sap_draft}\n\n"
        f"## General EAM Expert Draft\n{general_draft}\n\n"
        f"## Skills & Resources Context\n{skills_context}\n\n"
        f"Reconcile the two expert drafts and produce the final council output "
        f"in the required format. Include ALL required sections."
    )
