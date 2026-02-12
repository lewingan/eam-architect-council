# EAM Glossary & Canonical Entities Skill

## Purpose
Provide a canonical vocabulary and entity reference for all EAM architecture discussions. Ensures all agents use consistent terminology and reference the same data structures.

## Behavior
- Supply the glossary of EAM terms to any agent that needs domain context.
- Supply the canonical entity definitions (YAML) for data model discussions.
- Flag any term used by an agent that is NOT in the glossary as "undefined -- requires addition."

## Constraints
- All agent outputs must use glossary-standard terms.
- Entity references must match the canonical_entities.yaml schema.
- New entities proposed by agents must be clearly marked as provisional.
