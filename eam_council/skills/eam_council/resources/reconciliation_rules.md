# Reconciliation Rules

When the council experts (SAP EAM, General EAM, and optionally Agentic Architecture) provide conflicting or divergent advice, apply these rules:

## Priority Order
1. **Safety & Compliance** -- Any recommendation touching regulatory compliance or safety wins by default.
2. **SAP-native capability** -- If SAP PM/EAM has a built-in feature that directly addresses the requirement, prefer the SAP-native approach over custom development.
3. **Published SAP API** -- If a published OData API exists on the SAP Business Accelerator Hub for a capability, prefer it over custom ABAP/RFC/BAPI development. Reference table-level details only for data migration or ABAP debugging scenarios.
4. **Industry best practice** -- Where SAP has no native capability, defer to the general EAM expert's industry-standard recommendation.
5. **Simplicity** -- Between two otherwise-equal approaches, prefer the simpler one with fewer integration points.

## Conflict Resolution Steps
1. Identify the specific point of disagreement.
2. Classify the disagreement type: (a) technical feasibility, (b) best practice, (c) scope/boundary, (d) data model.
3. Apply the priority order above.
4. Document the chosen path AND the rejected alternative in the Decision Log with rationale.

## Agentic Architecture Integration
When the Agentic Architecture Expert has participated:
- The agentic expert's recommendations on agent patterns, tools, memory, and guardrails take precedence for the "Next Agent To Build" section.
- SAP and General EAM experts define WHAT the agent should do; the agentic expert defines HOW it should be built.
- Platform recommendations from the agentic expert should be respected unless they conflict with organizational constraints noted by the other experts.

## Merge Rules
- If all participating experts agree on a point, include it verbatim (deduplicated).
- If experts provide complementary (non-conflicting) details, merge them.
- If experts contradict each other, apply conflict resolution and log it.
- Always preserve open questions from all experts in "Assumptions & Open Questions."
