"""SAP EAM subagent - calls Claude with SAP-specific system prompt."""

from __future__ import annotations

import anthropic

from eam_council.council.llm import create_with_retry
from eam_council.council.models import SubagentDraft
from eam_council.council.prompts import (
    SAP_EAM_SUBAGENT_SEARCH_ADDENDUM,
    SAP_EAM_SUBAGENT_SYSTEM,
    build_subagent_prompt,
)
from eam_council.council.web_search import SAP_WEB_SEARCH_TOOL, extract_text_from_response

DRY_RUN_RESPONSE = """\
## SAP EAM Expert Draft

### Recommendation
For work order scheduling in SAP EAM, leverage the SAP PM scheduling framework \
using the published OData APIs on the SAP Business Accelerator Hub. The primary \
services are API_MAINTORDER_SRV for work order management and API_MAINTENANCEPLAN_SRV \
for scheduling plans. Use SAP BTP Integration Suite for event-driven patterns.

### Relevant SAP APIs & Services
- **API_MAINTORDER_SRV** (OData v4) -- MaintenanceOrder, MaintenanceOrderOperation entity sets. \
Covers work order CRUD, operation management, and status updates.
- **API_EQUIPMENT_SRV** (OData v4) -- Equipment entity set. Asset master data retrieval.
- **API_FUNCLOCATION_SRV** (OData v4) -- FunctionalLocation entity set. Plant hierarchy data.
- **API_MAINTENANCEPLAN_SRV** (OData v4) -- MaintenancePlan entity set. Schedule definitions.
- **API_WORKCENTER_SRV** (OData v4) -- WorkCenter entity set. Resource/capacity data.
- SAP API Hub: https://api.sap.com (search "Plant Maintenance" for full catalog)

### Integration Approach
Use OData v4 APIs from S/4HANA for real-time scheduling data. OData is the preferred \
protocol for all new integrations. Fall back to RFCs only for batch operations where \
no OData equivalent exists. Consider SAP BTP Integration Suite for event-driven patterns.

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
    search_enabled: bool = True,
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

    system_prompt = SAP_EAM_SUBAGENT_SYSTEM
    if search_enabled:
        system_prompt += SAP_EAM_SUBAGENT_SEARCH_ADDENDUM

    kwargs: dict = dict(
        model=model,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    if search_enabled:
        kwargs["tools"] = [SAP_WEB_SEARCH_TOOL]

    response = create_with_retry(client, **kwargs)

    content = extract_text_from_response(response)
    return SubagentDraft(
        agent_name="SAP EAM Expert",
        perspective="SAP-specific",
        content=content,
    )
