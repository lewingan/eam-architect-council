# Reconciliation Rules

When the SAP EAM expert and General EAM expert provide conflicting or divergent advice, apply these rules:

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

## Merge Rules
- If both experts agree on a point, include it verbatim (deduplicated).
- If experts provide complementary (non-conflicting) details, merge them.
- If experts contradict each other, apply conflict resolution and log it.
- Always preserve open questions from either expert in "Assumptions & Open Questions."
