"""General EAM subagent - calls Claude with industry-standard EAM system prompt."""

from __future__ import annotations

import anthropic

from eam_council.council.models import SubagentDraft
from eam_council.council.prompts import (
    GENERAL_EAM_SUBAGENT_SYSTEM,
    build_subagent_prompt,
)

DRY_RUN_RESPONSE = """\
## General EAM Expert Draft

### Recommendation
Work order scheduling should follow a priority-driven, constraint-based approach \
aligned with ISO 55000 asset management principles. The architecture should separate \
the scheduling engine from the CMMS to allow pluggable optimization strategies.

### Best Practices
- **Priority matrix:** Combine asset criticality (A/B/C) with work order urgency to \
derive a composite scheduling score.
- **Constraint-based scheduling:** Model resource availability, production windows, \
and safety lockout periods as hard constraints.
- **Rolling horizon:** Use a 2-week firm schedule with a 6-week planning horizon.
- **Backlog management:** Maintain a groomed backlog with aging metrics.

### Data Model
- Decouple the scheduling model from the CMMS data model via an integration layer.
- Canonical entities: Work Order, Resource (generalizes Work Center), Asset, Time Slot.
- Use event sourcing for schedule change history.

### Integration Patterns
- **Pull:** Periodically sync work orders and resource data from the CMMS.
- **Push:** Emit scheduling events (assigned, rescheduled, completed) back to the CMMS.
- **API-first:** Expose the scheduling engine via REST for UI and other consumers.

### Risks & Assumptions
- Assumes a single-site deployment for PoC.
- Real-time optimization may require a dedicated solver (e.g., OR-Tools, OptaPlanner).
- Change management: planners may resist automated scheduling.
"""


async def run_general_subagent(
    question: str,
    skills_context: str,
    mock_context: str,
    model: str,
    dry_run: bool = False,
) -> SubagentDraft:
    """Run the General EAM subagent and return its draft."""
    if dry_run:
        return SubagentDraft(
            agent_name="General EAM Expert",
            perspective="Industry-standard",
            content=DRY_RUN_RESPONSE,
        )

    client = anthropic.Anthropic()
    user_prompt = build_subagent_prompt(question, skills_context, mock_context)

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=GENERAL_EAM_SUBAGENT_SYSTEM,
        messages=[{"role": "user", "content": user_prompt}],
    )

    content = response.content[0].text
    return SubagentDraft(
        agent_name="General EAM Expert",
        perspective="Industry-standard",
        content=content,
    )
