# Agent Specification Template

When recommending a "Next Agent To Build," use this structure:

## Agent: [Agent Name]

### Purpose
[1-2 sentences: What problem does this agent solve? Why is an agent needed vs. a static script?]

### Agent Pattern
[Which pattern from agent_design_patterns.md: ReAct, Tool-Use, Multi-Agent Coordinator, Pipeline, Event-Driven, Human-in-the-Loop]

### Inputs
- [Input 1]: [Source, format, frequency]
- [Input 2]: [Source, format, frequency]

### Outputs
- [Output 1]: [Target, format, schema]
- [Output 2]: [Target, format, schema]

### Tools
| Tool Name | Description | SAP API / Data Source | Input Schema | Output Schema |
|-----------|-------------|---------------------|--------------|---------------|
| [tool_1]  | [What it does] | [API_xxx_SRV or external] | [Key params] | [Return shape] |

### Reasoning Strategy
[How does the agent decide what to do? What is the reasoning loop?]
- Step 1: [Analyze input / classify request]
- Step 2: [Query relevant data via tools]
- Step 3: [Reason about results]
- Step 4: [Take action or escalate]

### Memory Requirements
- **Short-term:** [What context must the agent hold during a single invocation?]
- **Long-term:** [What should persist across invocations? Decision history, past recommendations?]

### Failure Modes & Guardrails
- [Failure 1]: [How it manifests] -> [Mitigation]
- [Failure 2]: [How it manifests] -> [Mitigation]
- **Human escalation trigger:** [When does the agent stop and ask a human?]

### Platform Recommendation
[Recommended platform from platform_comparison.md, with justification]

### Acceptance Criteria
- [ ] AC-1: [Testable criterion]
- [ ] AC-2: [Testable criterion]
