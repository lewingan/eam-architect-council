# EAM Council Output Format

Every council response MUST follow this structure exactly:

```
# EAM Architecture Council -- Response

## Question
[Restate the original question]

## Executive Summary
[2-3 sentence summary of the recommendation]

## SAP EAM Perspective
[Key points from the SAP EAM expert]

## General EAM Perspective
[Key points from the general EAM expert]

## Agentic Architecture Perspective (if applicable)
[Key points from the agentic architecture expert -- agent pattern, tools, platform, guardrails]

## Unified Recommendation
[Merged, reconciled recommendation with clear action items]

### Architecture Components
- [Component 1]: [Description]
- [Component 2]: [Description]

### Data Model Considerations
- [Entity/field considerations]

### Integration Points
- [System-to-system interfaces]

#### SAP API References
| API Service | Entity Set | Purpose | Hub Link |
|---|---|---|---|
| [OData service name] | [Entity set name] | [What it is used for] | [api.sap.com link] |

## Assumptions & Open Questions
- [ ] [Assumption or open question 1]
- [ ] [Assumption or open question 2]

## Decision Log
| # | Decision | Rationale | Alternative Considered |
|---|----------|-----------|----------------------|
| 1 | ...      | ...       | ...                  |

## Next Agent To Build
[Describe what the next logical agent or module to build would be to advance this architecture, including its inputs, outputs, and purpose]
```
