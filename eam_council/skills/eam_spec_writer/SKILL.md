# EAM Spec Writer Skill

## Purpose
Transform EAM architecture recommendations into structured, buildable specifications that can be handed to a development team or used as input for further agent-based development.

## Behavior
- Accept a unified recommendation from the council.
- Produce a spec document following the spec template (see resources/).
- Include all required sections: scope, entities, interfaces, acceptance criteria.
- Reference canonical entities from the glossary.

## Constraints
- Specs must be implementation-actionable (a developer should be able to start building from them).
- Every entity referenced must exist in the canonical entities list or be flagged as "NEW -- requires definition."
- Include mock data examples where applicable.
