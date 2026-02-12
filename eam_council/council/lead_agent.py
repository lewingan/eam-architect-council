"""Lead orchestrator agent - dispatches to subagents and reconciles."""

from __future__ import annotations

import asyncio

import anthropic
from rich.console import Console

from eam_council.council.general_eam_subagent import run_general_subagent
from eam_council.council.mock_data import get_mock_context
from eam_council.council.prompts import LEAD_AGENT_SYSTEM, build_lead_prompt
from eam_council.council.sap_eam_subagent import run_sap_subagent
from eam_council.council.skills_loader import load_all_skills

console = Console()

DRY_RUN_FINAL = """\
# EAM Architecture Council -- Response

## Question
How should we architect a work order scheduling module for SAP EAM?

## Executive Summary
The council recommends a hybrid architecture that leverages SAP PM's native scheduling \
capabilities (maintenance plans, capacity planning) while introducing an external \
constraint-based scheduling engine for advanced optimization. This approach combines \
SAP's data authority with industry-standard scheduling best practices.

## SAP EAM Perspective
The SAP expert recommends building on SAP PM's scheduling framework (IP10/IP30, CM01) \
with OData v4 APIs for real-time data access. Key SAP objects include AUFK, AFVC, and \
CRHD tables. Integration via SAP BTP Integration Suite for event-driven patterns.

## General EAM Perspective
The general EAM expert recommends a priority-driven, constraint-based scheduling engine \
decoupled from the CMMS via an integration layer. Follows ISO 55000 principles with a \
rolling 2-week firm / 6-week planning horizon.

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
**Scheduling Constraint Solver Agent** -- An agent that takes a set of work orders, \
resource calendars, and constraints (safety windows, production schedules, parts \
availability) and produces an optimized schedule. Inputs: work order list, resource \
availability, constraint rules. Outputs: scheduled timeline with conflict report. \
Purpose: Core optimization logic that the scheduling engine wraps as a service.
"""


async def run_council(
    question: str, model: str, dry_run: bool = False
) -> str:
    """Run the full council workflow and return the final output."""
    # 1. Load skills and mock data
    console.print("[dim]Loading skills and resources...[/dim]")
    skills_context = load_all_skills()
    mock_context = get_mock_context()

    # 2. Run subagents (parallel)
    console.print("[dim]Consulting SAP EAM expert...[/dim]")
    console.print("[dim]Consulting General EAM expert...[/dim]")

    sap_draft, general_draft = await asyncio.gather(
        run_sap_subagent(question, skills_context, mock_context, model, dry_run),
        run_general_subagent(question, skills_context, mock_context, model, dry_run),
    )

    console.print(f"[green]OK[/green] SAP expert responded ({len(sap_draft.content)} chars)")
    console.print(f"[green]OK[/green] General expert responded ({len(general_draft.content)} chars)")

    # 3. Lead agent reconciliation
    console.print("[dim]Lead architect reconciling...[/dim]")

    if dry_run:
        final_output = DRY_RUN_FINAL
    else:
        client = anthropic.Anthropic()
        lead_prompt = build_lead_prompt(
            question, sap_draft.content, general_draft.content, skills_context
        )
        response = client.messages.create(
            model=model,
            max_tokens=8192,
            system=LEAD_AGENT_SYSTEM,
            messages=[{"role": "user", "content": lead_prompt}],
        )
        final_output = response.content[0].text

    console.print("[green]OK[/green] Reconciliation complete")
    return final_output
