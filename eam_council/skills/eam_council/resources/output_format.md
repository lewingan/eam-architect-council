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

## Agentic Architecture Perspective
[Key points from the Agentic Architecture expert. If no agentic expert was invoked, state: "Not applicable for this question."]

## Agent Suitability Decision
- **Decision:** [Suitable | Not Suitable]
- **Why (technical + business):** [Justify whether this use case should be implemented as an agent]
- **If Not Suitable, Better Alternative:** [Describe the preferred non-agent architecture]

## Impact & Worthwhile Assessment
- **SAP EAM Expert View:** [High/Medium/Low impact and why]
- **General EAM Expert View:** [High/Medium/Low impact and why]
- **Agentic Architecture Expert View:** [High/Medium/Low impact and why]
- **Overall Council Verdict:** [Is this worth building now? Why?]

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
[Describe what the next logical agent or module to build would be to advance this architecture. MUST include: inputs, outputs, tool/API contracts, memory/state strategy, MVP scope, and acceptance criteria]
```

Notes:
- For agentic requests (e.g., design/build an EAM agent), `Agentic Architecture Perspective`, `Agent Suitability Decision`, and `Impact & Worthwhile Assessment` are mandatory.
- For non-agentic requests, keep these sections present and mark them as not applicable.
