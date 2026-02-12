# EAM Council Orchestration Skill

## Purpose
Orchestrate a multi-expert council for Enterprise Asset Management (EAM) architecture decisions. The council consists of an SAP EAM specialist and a general EAM domain expert. Their outputs are reconciled into a single, actionable buildable spec.

## Workflow
1. Receive an EAM architecture question from the user.
2. Dispatch the question to both subagents (SAP EAM expert, General EAM expert).
3. Collect draft responses from each expert.
4. Reconcile differences using the reconciliation rules (see resources/).
5. Produce a final unified answer in the required output format (see resources/).

## Constraints
- Both experts MUST contribute before reconciliation.
- Disagreements MUST be explicitly logged in the Decision Log.
- The final output MUST conform to the output format template.
- All terminology MUST align with the canonical glossary.
