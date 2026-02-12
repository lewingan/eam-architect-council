"""SAP EAM subagent - calls Claude with SAP-specific system prompt."""

from __future__ import annotations

import anthropic

from eam_council.council.models import SubagentDraft
from eam_council.council.prompts import SAP_EAM_SUBAGENT_SYSTEM, build_subagent_prompt

DRY_RUN_RESPONSE = """\
## SAP EAM Expert Draft

### Recommendation
For work order scheduling in SAP EAM, leverage the SAP PM scheduling framework \
built around maintenance plans (IP10/IP30), work center capacity planning (CM01), \
and the MRP integration for spare parts.

### Relevant SAP Objects
- **Tables:** AUFK (Order Header), AFIH (Maintenance Header), AFVC (Operations), CRHD (Work Centers)
- **Transactions:** IW31/IW32 (Work Order Create/Change), IP10 (Schedule Maintenance Plan), CM01 (Capacity Planning)
- **BAPIs:** BAPI_ALM_ORDER_MAINTAIN, BAPI_SCHEDULE_MAINTAIN
- **OData:** API_MAINTORDER_SRV, API_EQUIPMENT_SRV

### Integration Approach
Use OData v4 APIs from S/4HANA for real-time scheduling data. Fall back to RFCs for \
batch operations. Consider SAP BTP Integration Suite for event-driven patterns.

### Risks & Constraints
- SAP standard scheduling does not natively support drag-and-drop rescheduling; custom UI required.
- Capacity leveling in SAP is limited to work-center-level granularity.
- Cross-plant scheduling requires additional configuration.

### Assumptions
- S/4HANA 2023 or later is the target platform.
- OData APIs are enabled and accessible.
- Single-plant scope for PoC.
"""


async def run_sap_subagent(
    question: str,
    skills_context: str,
    mock_context: str,
    model: str,
    dry_run: bool = False,
) -> SubagentDraft:
    """Run the SAP EAM subagent and return its draft."""
    if dry_run:
        return SubagentDraft(
            agent_name="SAP EAM Expert",
            perspective="SAP-specific",
            content=DRY_RUN_RESPONSE,
        )

    client = anthropic.Anthropic()
    user_prompt = build_subagent_prompt(question, skills_context, mock_context)

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=SAP_EAM_SUBAGENT_SYSTEM,
        messages=[{"role": "user", "content": user_prompt}],
    )

    content = response.content[0].text
    return SubagentDraft(
        agent_name="SAP EAM Expert",
        perspective="SAP-specific",
        content=content,
    )
