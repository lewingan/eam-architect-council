# Agent Design Patterns for EAM

## Core Agent Architectures

### 1. ReAct (Reasoning + Acting) Agent
- **Pattern:** The agent alternates between reasoning (thinking about what to do) and acting (calling tools). Each observation from a tool informs the next reasoning step.
- **Best for:** Diagnostic agents, root-cause analysis, exploratory queries against SAP data.
- **EAM example:** An agent that investigates equipment failure history by querying maintenance records, then reasons about failure patterns before recommending preventive actions.
- **Tools needed:** SAP API query tools, knowledge retrieval, calculation tools.

### 2. Tool-Use Agent (Single-Turn)
- **Pattern:** The agent receives a request, selects and calls one or more tools, and returns a structured result. No iterative reasoning loop.
- **Best for:** Well-defined tasks with predictable tool sequences (CRUD operations, report generation).
- **EAM example:** An agent that creates a work order in SAP by calling API_MAINTORDER_SRV with validated parameters.
- **Tools needed:** SAP OData API tools with schema validation.

### 3. Multi-Agent Coordinator (Orchestrator)
- **Pattern:** A lead agent dispatches subtasks to specialist agents, collects results, and synthesizes a unified response. The current EAM Architecture Council uses this pattern.
- **Best for:** Complex decisions requiring multiple perspectives or domains.
- **EAM example:** A maintenance planning system where separate agents handle scheduling optimization, parts availability checking, and safety compliance validation.
- **Coordination:** Parallel dispatch for independent tasks; sequential for dependent chains.

### 4. Pipeline Agent (Sequential Chain)
- **Pattern:** Agents are chained in sequence where each agent's output becomes the next agent's input. No central orchestrator.
- **Best for:** Multi-stage workflows with clear handoff points.
- **EAM example:** Notification triage -> Work order creation -> Scheduling -> Resource assignment.
- **Trade-off:** Simple to build but brittle; failure at any stage blocks the pipeline.

### 5. Event-Driven Agent (Reactive)
- **Pattern:** The agent listens for events (sensor readings, status changes, threshold breaches) and triggers actions when conditions are met.
- **Best for:** Real-time monitoring, predictive maintenance, IoT-driven workflows.
- **EAM example:** An agent that monitors vibration sensor data via SAP IoT and auto-creates maintenance notifications when anomaly thresholds are exceeded.
- **Platform consideration:** Requires persistent runtime (not request-response).

### 6. Human-in-the-Loop Agent
- **Pattern:** The agent performs automated reasoning and preparation but pauses for human approval before executing consequential actions (e.g., creating work orders, changing equipment status).
- **Best for:** Safety-critical EAM operations, high-value asset decisions.
- **EAM example:** An agent that drafts a shutdown maintenance plan but requires planner approval before scheduling against the production calendar.
- **Implementation:** Checkpoint/approval gates in the agent workflow.

## Tool Design Best Practices

### Granularity
- **Fine-grained tools** (one API call per tool) give the agent maximum flexibility but require more reasoning steps. Better for exploratory tasks.
- **Coarse-grained tools** (multi-step workflows bundled) reduce token usage and error surface. Better for well-understood, repeatable operations.
- **Recommendation:** Start coarse, decompose to fine-grained only when the agent needs more control.

### Tool Schema Design
- Every tool must have a clear name, description, and typed input schema.
- Include constraints in the description (e.g., "priority must be 1-4", "equipment_id must match pattern EQ-XXXX").
- Return structured data (JSON), not prose, so downstream agents can parse it.

### Idempotency
- SAP write operations (create work order, change status) should be designed as idempotent where possible.
- Include deduplication checks (e.g., check for existing work order before creating a new one).

### Error Handling
- Tools should return structured errors, not raw HTTP status codes.
- The agent should have a retry strategy for transient failures (network timeouts to SAP).
- For non-retryable errors, the agent should escalate to human-in-the-loop.

## Memory and State Management

### Short-Term (Conversation) Memory
- The agent's context window holds the current conversation.
- For multi-turn EAM interactions, maintain a running summary of decisions made.

### Long-Term (Persistent) Memory
- Store past recommendations, agent outputs, and decision logs for future reference.
- Use retrieval (vector search or keyword) to surface relevant past decisions when similar questions arise.
- EAM-specific: maintain an audit trail of all agent-initiated changes for compliance.

### Temporal Context
- EAM agents often need to reason about time (maintenance schedules, equipment age, failure intervals).
- Provide time-aware context: current date, last maintenance date, next scheduled maintenance.

## Failure Modes and Guardrails

### Common Failure Modes
1. **Hallucinated API names** -- Agent invents SAP APIs that don't exist. Mitigate with web search verification and a canonical API list.
2. **Unsafe operations** -- Agent attempts to close work orders or change equipment status without authorization. Mitigate with approval gates.
3. **Context overflow** -- Agent receives too much data from SAP queries and loses track of the original question. Mitigate with pagination and summarization.
4. **Infinite loops** -- Agent repeatedly queries the same data without making progress. Mitigate with max-iteration limits.

### Guardrails for EAM
- **Safety-critical actions** (equipment lockout, shutdown scheduling) must always require human approval.
- **Compliance logging** -- Every agent action that modifies SAP data must be logged with timestamp, user context, and rationale.
- **Scope boundaries** -- Agents should refuse to operate outside their defined scope (e.g., a scheduling agent should not modify equipment master data).
