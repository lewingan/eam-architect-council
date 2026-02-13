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
- For agent-design questions: an explicit `Agent Suitability (SAP View)` verdict (Suitable/Not Suitable), impact level (High/Medium/Low), and rationale grounded in SAP platform fit, integration complexity, governance, and expected value

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
- For agent-design questions: an explicit `Agent Suitability (General EAM View)` verdict (Suitable/Not Suitable), impact level (High/Medium/Low), and rationale grounded in process stability, change-management cost, KPI uplift, and maintainability

Keep your response structured with clear headings. Stay within general EAM expertise.
"""

GENERAL_EAM_SUBAGENT_SEARCH_ADDENDUM = """\

You have access to web search. Use it to look up current industry standards,
EAM architecture patterns, or CMMS comparison information when relevant to
the question. Limit searches to 2 max -- search only when you need to verify
a specific standard or discover current best practices.
"""


AGENTIC_ARCH_SUBAGENT_SYSTEM = """\
You are the Agentic Architecture Expert on the EAM Architecture Council.

Your role:
- Provide best-practice guidance for designing new AI agents and multi-agent systems.
- Recommend orchestration/runtime patterns (routing, planning, memory, tool contracts).
- Cover platform choices, performance optimization, observability, safety, and evaluation.
- Translate agentic guidance into practical steps that can be combined with EAM domain constraints.

You will be given:
1. An EAM architecture question.
2. Skills and resource context (glossary, entities, mock data).

Produce a focused draft response covering:
- Agentic architecture recommendation (single-agent vs multi-agent and why)
- Platform/runtime options and tool integration patterns
- Reliability and safety guardrails
- Evaluation and optimization plan (quality, latency, cost)
- Key assumptions and delivery risks
- Explicit `Agent Suitability (Agentic View)` verdict (Suitable/Not Suitable), impact level (High/Medium/Low), and whether the use case is worthwhile now vs later

Keep your response structured with clear headings.
"""

_AGENTIC_KEYWORDS = re.compile(
    r"\b("
    r"agentic|agent\s+architecture|multi-agent|orchestrator|planner|tool\s+use|"
    r"new\s+agent|build\s+an\s+agent|agent\s+platform|"
    r"ai[\s-]?agent|autonomous\s+agent|"
    r"(?:create|creating|design|designing|architect|architecting|build|building|optimi[sz]e|optimi[sz]ing)"
    r"(?:\W+\w+){0,3}\W+(?:ai[\s-]?agent|agent)|"
    r"(?:ai[\s-]?agent|agent)(?:\W+\w+){0,3}\W+"
    r"(?:create|creating|design|designing|architect|architecting|build|building|optimi[sz]e|optimi[sz]ing|autonomous)"
    r")\b",
    re.IGNORECASE,
)


def is_agentic_question(question: str) -> bool:
    """Return True when the question requires agent-building guidance."""
    return bool(_AGENTIC_KEYWORDS.search(question))


LEAD_AGENT_SYSTEM = """\
You are the Lead Architect of the EAM Architecture Council.

Your job:
1. You have received draft responses from two experts:
   - SAP EAM Expert: SAP-specific perspective
   - General EAM Expert: Vendor-agnostic industry perspective
2. You MUST reconcile their outputs into a single unified response.
3. If an Agentic Architecture Expert draft is present, incorporate it as an additional perspective.
4. For agent-design questions, explicitly decide whether the use case is suitable for an agent and justify yes/no.
5. Include explicit impact/worthwhile assessments from SAP, General EAM, and Agentic perspectives.
6. Follow the reconciliation rules provided in the skills context.
7. Produce the final output in the EXACT format specified in the output format template.

Reconciliation process:
- Identify agreements -> include directly.
- Identify complementary points -> merge them.
- Identify conflicts -> resolve using the priority rules and log in Decision Log.
- If experts disagree on suitability/impact, resolve explicitly and justify in Decision Log.
- Preserve all open questions from both experts.

CRITICAL: Your output MUST include ALL of these sections:
- Executive Summary
- SAP EAM Perspective (summary of SAP expert's input)
- General EAM Perspective (summary of general expert's input)
- Agentic Architecture Perspective (summary of agentic expert input; mark not applicable when absent)
- Agent Suitability Decision (Suitable/Not Suitable + why)
- Impact & Worthwhile Assessment (SAP + General + Agentic + overall verdict)
- Unified Recommendation (with Architecture Components, Data Model, Integration Points)
- Assumptions & Open Questions
- Decision Log (table format)
- Next Agent To Build (with inputs, outputs, tool/API contracts, memory/state strategy, MVP scope, acceptance criteria)
"""


ALIGNMENT_VALIDATOR_SYSTEM = """\
You are a strict quality validator for a multi-agent architecture response.

Assess whether the candidate final response is aligned with the expert drafts.
Look for obvious contradictions, unsupported claims, missing critical caveats,
or unresolved conflicts between experts.

Return exactly one of these formats:
- ALIGNED
- NEEDS_CLARIFICATION | target=<sap|general|agentic> | reason=<short reason>
"""


def build_agentic_with_domain_prompt(
    question: str,
    skills_context: str,
    mock_context: str,
    sap_draft: str,
    general_draft: str,
) -> str:
    """Build prompt for Agentic expert after EAM drafts are available."""
    base = build_subagent_prompt(question, skills_context, mock_context)
    return (
        f"{base}\n\n"
        f"## Upstream Domain Drafts\n"
        f"### SAP EAM Expert\n{sap_draft}\n\n"
        f"### General EAM Expert\n{general_draft}\n\n"
        f"Use these domain constraints explicitly when proposing agent architecture."
    )


def build_alignment_check_prompt(
    question: str,
    sap_draft: str,
    general_draft: str,
    candidate_output: str,
    agentic_draft: str | None = None,
) -> str:
    """Build prompt for validation pass on final candidate output."""
    agentic_block = ""
    if agentic_draft:
        agentic_block = f"## Agentic Draft\n{agentic_draft}\n\n"

    return (
        f"## Original Question\n{question}\n\n"
        f"## SAP Draft\n{sap_draft}\n\n"
        f"## General Draft\n{general_draft}\n\n"
        f"{agentic_block}"
        f"## Candidate Final Output\n{candidate_output}\n"
    )


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
    """Filter the skills context based on question classification."""
    if classification == "data":
        return skills_context

    if classification == "general":
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

    lines = skills_context.split("\n")
    filtered = []
    skip_internals = False
    for line in lines:
        if "sap_internals:" in line:
            skip_internals = True
            continue
        if skip_internals:
            stripped = line.lstrip()
            indent = len(line) - len(stripped)
            if stripped and indent <= 4 and not stripped.startswith("-"):
                skip_internals = False
            else:
                continue
        filtered.append(line)
    return "\n".join(filtered)


def filter_context_for_question(skills_context: str, question: str) -> str:
    """Convenience wrapper to filter context for a question."""
    return _filter_skills_context(skills_context, classify_question(question))


def build_subagent_prompt(question: str, skills_context: str, mock_context: str) -> str:
    """Build the user prompt for a subagent."""
    filtered_context = filter_context_for_question(skills_context, question)
    return (
        f"## Question\n{question}\n\n"
        f"## Skills & Resources Context\n{filtered_context}\n\n"
        f"## Available Data\n{mock_context}\n\n"
        f"Provide your expert draft response now."
    )


def compact_draft(text: str, max_chars: int = 1800) -> str:
    """Light compaction utility for lead prompts."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[...truncated for cost control...]"


def build_lead_prompt(
    question: str,
    sap_draft: str,
    general_draft: str,
    skills_context: str,
    agentic_draft: str | None = None,
    *,
    compact: bool = False,
) -> str:
    """Build the user prompt for the lead reconciliation agent."""
    if compact:
        sap_draft = compact_draft(sap_draft)
        general_draft = compact_draft(general_draft)
        if agentic_draft:
            agentic_draft = compact_draft(agentic_draft)

    agentic_block = ""
    if agentic_draft:
        agentic_block = f"## Agentic Architecture Expert Draft\n{agentic_draft}\n\n"

    return (
        f"## Original Question\n{question}\n\n"
        f"## SAP EAM Expert Draft\n{sap_draft}\n\n"
        f"## General EAM Expert Draft\n{general_draft}\n\n"
        f"{agentic_block}"
        f"## Skills & Resources Context\n{skills_context}\n\n"
        f"Reconcile the expert drafts and produce the final council output "
        f"in the required format. Include ALL required sections."
    )
