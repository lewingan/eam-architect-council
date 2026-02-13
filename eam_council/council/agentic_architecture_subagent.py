"""Agentic architecture subagent for agent-building best practices."""

from __future__ import annotations

import anthropic

from eam_council.council.llm import create_with_retry
from eam_council.council.models import SubagentDraft
from eam_council.council.prompts import (
    AGENTIC_ARCH_SUBAGENT_SYSTEM,
    build_agentic_with_domain_prompt,
    build_subagent_prompt,
)

DRY_RUN_RESPONSE = """\
## Agentic Architecture Expert Draft

### Recommendation
For requests that involve designing a new AI agent (or multi-agent workflow), add a dedicated
Agentic Architecture Expert to the council. This role focuses on agent platform choices,
orchestration patterns, tool safety, observability, and evaluation loops.

### Why This Is Needed
- Existing experts optimize for EAM domain correctness (SAP + industry practices), not agent runtime design.
- Agentic solutions require additional concerns: planner/executor decomposition, memory strategy,
  tool contracts, fallback policies, and cost/latency controls.

### Reference Architecture
- **Intent Router:** Detects whether question is EAM-only, agentic-only, or hybrid.
- **Domain Experts:** SAP EAM + General EAM provide domain constraints and business logic.
- **Agentic Expert:** Produces runtime architecture and optimization guidance.
- **Lead Reconciler:** Merges all perspectives into one implementation-ready plan.

### Guardrails and Metrics
- Add acceptance tests for tool-calling correctness and failure recovery.
- Track cost per response, median latency, and answer-grounding coverage.
- Require explicit assumptions and risk controls in every agentic design response.
"""


async def run_agentic_arch_subagent(
    question: str,
    skills_context: str,
    mock_context: str,
    model: str,
    dry_run: bool = False,
    sap_draft: str | None = None,
    general_draft: str | None = None,
) -> SubagentDraft:
    """Run the agentic architecture subagent and return its draft."""
    if dry_run:
        return SubagentDraft(
            agent_name="Agentic Architecture Expert",
            perspective="Agent design",
            content=DRY_RUN_RESPONSE,
        )

    client = anthropic.Anthropic()
    if sap_draft and general_draft:
        user_prompt = build_agentic_with_domain_prompt(
            question,
            skills_context,
            mock_context,
            sap_draft,
            general_draft,
        )
    else:
        user_prompt = build_subagent_prompt(question, skills_context, mock_context)

    response = create_with_retry(
        client,
        model=model,
        max_tokens=4096,
        system=AGENTIC_ARCH_SUBAGENT_SYSTEM,
        messages=[{"role": "user", "content": user_prompt}],
    )

    text = response.content[0].text
    return SubagentDraft(
        agent_name="Agentic Architecture Expert",
        perspective="Agent design",
        content=text,
    )
