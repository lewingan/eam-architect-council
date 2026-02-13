# Claude Agent SDK -- Quick Reference for EAM Agents

## Overview
The Claude Agent SDK (Python) provides a streamlined way to build agents that use
Claude's tool_use capability. It is the default recommended platform for EAM agents
in this council due to its strong reasoning, native tool support, and low overhead.

## Key Concepts

### Tool Definition
Tools are defined as typed dictionaries and passed to `messages.create()`:

```python
tools = [
    {
        "name": "get_work_orders",
        "description": "Query SAP maintenance orders via API_MAINTORDER_SRV. "
                       "Supports filtering by status, priority, equipment, and date range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["CRTD", "REL", "TECO", "CLSD"]},
                "priority": {"type": "integer", "minimum": 1, "maximum": 4},
                "equipment_id": {"type": "string"},
                "from_date": {"type": "string", "format": "date"},
                "to_date": {"type": "string", "format": "date"},
            },
            "required": [],
        },
    }
]
```

### Agent Loop Pattern
The standard agent loop processes tool_use responses iteratively:

```python
import anthropic

client = anthropic.Anthropic()
messages = [{"role": "user", "content": user_question}]

while True:
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        system=system_prompt,
        tools=tools,
        messages=messages,
    )

    # Collect all content blocks
    assistant_content = response.content
    messages.append({"role": "assistant", "content": assistant_content})

    # Check if the model wants to use tools
    if response.stop_reason == "tool_use":
        tool_results = []
        for block in assistant_content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                })
        messages.append({"role": "user", "content": tool_results})
    else:
        # Model produced final text response
        break
```

### Server-Side Web Search
Claude supports server-side web search as a built-in tool type. No client-side
implementation needed -- the search happens within the API call:

```python
tools = [
    {
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": 3,
    },
    # ... other custom tools
]
```

### Multi-Agent Orchestration
For multi-agent patterns (like the EAM Architecture Council), orchestrate
by running separate `messages.create()` calls and combining results:

```python
import asyncio

async def run_council(question):
    sap_task = run_sap_agent(question)
    general_task = run_general_agent(question)

    sap_result, general_result = await asyncio.gather(sap_task, general_task)

    # Lead agent reconciles
    return await run_lead_agent(question, sap_result, general_result)
```

## EAM-Specific Tool Design Guidelines

### SAP OData API Tools
Map each major SAP API to a tool. Keep tools focused on single entity sets:

| Tool Name | SAP API | Entity Set | Operations |
|-----------|---------|------------|------------|
| get_work_orders | API_MAINTORDER_SRV | MaintenanceOrder | Read, filter |
| create_work_order | API_MAINTORDER_SRV | MaintenanceOrder | Create (requires approval) |
| get_equipment | API_EQUIPMENT_SRV | Equipment | Read, filter |
| get_notifications | API_MAINTNOTIFICATION_SRV | MaintenanceNotification | Read, filter |
| create_notification | API_MAINTNOTIFICATION_SRV | MaintenanceNotification | Create |
| get_maintenance_plans | API_MAINTENANCEPLAN_SRV | MaintenancePlan | Read |
| get_func_locations | API_FUNCLOCATION_SRV | FunctionalLocation | Read, navigate hierarchy |
| get_work_centers | API_WORKCENTER_SRV | WorkCenter | Read, capacity check |

### Human-in-the-Loop Pattern
For safety-critical EAM operations, implement an approval gate:

```python
if action_type in ("create_work_order", "change_status", "schedule_shutdown"):
    # Return proposed action for human review instead of executing
    return {
        "status": "pending_approval",
        "proposed_action": action_type,
        "parameters": params,
        "rationale": agent_reasoning,
    }
```

### Guardrail Implementation
```python
MAX_TOOL_CALLS = 10
WRITE_OPERATIONS = {"create_work_order", "update_status", "create_notification"}

tool_call_count = 0

for block in response.content:
    if block.type == "tool_use":
        tool_call_count += 1
        if tool_call_count > MAX_TOOL_CALLS:
            # Force stop -- agent is looping
            break
        if block.name in WRITE_OPERATIONS:
            # Require human approval
            ...
```

## Model Selection
- **claude-sonnet-4-5-20250929**: Best balance of speed and capability for most EAM agent tasks.
- **claude-opus-4-6**: Use for complex multi-step reasoning or when highest accuracy is needed.
- **claude-haiku-4-5-20251001**: Use for high-volume, simple tool-use tasks (e.g., batch work order classification).

## Limitations to Note
- No built-in persistent memory -- implement with external storage (database, vector store).
- No built-in workflow checkpointing -- for resumable workflows, consider LangGraph.
- Context window limits apply -- for large SAP data sets, paginate and summarize.
- Concurrent tool execution is not native -- orchestrate parallel tool calls client-side.
