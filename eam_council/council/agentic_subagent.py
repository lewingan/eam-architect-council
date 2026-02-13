"""Agentic Architecture subagent - provides agent design guidance for EAM use cases."""

from __future__ import annotations

import anthropic

from eam_council.council.models import SubagentDraft
from eam_council.council.prompts import (
    AGENTIC_SUBAGENT_SEARCH_ADDENDUM,
    AGENTIC_SUBAGENT_SYSTEM,
    build_subagent_prompt,
    detect_platform_preference,
)
from eam_council.council.web_search import GENERAL_WEB_SEARCH_TOOL, extract_text_from_response

DRY_RUN_RESPONSE = """\
## Agentic Architecture Expert Draft

### Recommendation
For this EAM use case, a **ReAct (Reasoning + Acting) agent** with tool-use capabilities \
is recommended. The agent should query SAP OData APIs as tools, reason about the results, \
and produce actionable recommendations or trigger downstream actions with human approval.

### Agent Architecture
- **Pattern:** ReAct agent with human-in-the-loop for safety-critical actions.
- **Reasoning loop:** Analyze request -> query SAP data via tools -> reason about results -> \
propose action -> await approval (for write operations) -> execute.
- **Tool design:** Fine-grained tools mapping to individual OData API entity sets. Each tool \
returns structured JSON for downstream reasoning.

### Tools Specification
| Tool Name | SAP API / Source | Purpose |
|-----------|-----------------|---------|
| get_work_orders | API_MAINTORDER_SRV | Query and filter maintenance orders |
| get_equipment | API_EQUIPMENT_SRV | Retrieve equipment master data and status |
| get_func_locations | API_FUNCLOCATION_SRV | Navigate plant hierarchy |
| create_notification | API_MAINTNOTIFICATION_SRV | Create maintenance notifications |

### Memory & State
- **Short-term:** Maintain conversation context with running summary of queries made and \
decisions reached during the current session.
- **Long-term:** Persist decision logs and past recommendations for retrieval when similar \
questions arise. Use vector search over past council outputs.

### Platform Recommendation
**Claude Agent SDK** is recommended for this use case:
- Native tool_use maps directly to SAP OData API calls.
- Server-side web search enables real-time API Hub verification.
- Strong reasoning capabilities for EAM domain analysis.
- Low learning curve for rapid prototyping.
- For production, consider LangGraph if persistent checkpointing or complex stateful \
workflows are required.

### Guardrails
- All SAP write operations (create/update work orders, change equipment status) require \
human approval before execution.
- Agent must log every tool call with timestamp, parameters, and result for compliance audit.
- Max 10 tool calls per invocation to prevent runaway loops.
- Agent refuses to operate outside its defined scope (e.g., a scheduling agent cannot \
modify equipment master data).

### Risks
- Hallucinated API names: mitigated by web search verification against SAP API Hub.
- Context overflow on large SAP query results: mitigate with pagination and summarization.
- Latency of multi-tool reasoning loops: target < 30s for interactive use cases.
"""


async def run_agentic_subagent(
    question: str,
    skills_context: str,
    mock_context: str,
    model: str,
    dry_run: bool = False,
    search_enabled: bool = True,
) -> SubagentDraft:
    """Run the Agentic Architecture subagent and return its draft."""
    if dry_run:
        return SubagentDraft(
            agent_name="Agentic Architecture Expert",
            perspective="Agent design & orchestration",
            content=DRY_RUN_RESPONSE,
        )

    client = anthropic.Anthropic()
    platform = detect_platform_preference(question)
    user_prompt = build_subagent_prompt(
        question, skills_context, mock_context, platform_preference=platform
    )

    system_prompt = AGENTIC_SUBAGENT_SYSTEM
    if search_enabled:
        system_prompt += AGENTIC_SUBAGENT_SEARCH_ADDENDUM

    kwargs: dict = dict(
        model=model,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    if search_enabled:
        kwargs["tools"] = [GENERAL_WEB_SEARCH_TOOL]

    response = client.messages.create(**kwargs)

    content = extract_text_from_response(response)
    return SubagentDraft(
        agent_name="Agentic Architecture Expert",
        perspective="Agent design & orchestration",
        content=content,
    )
