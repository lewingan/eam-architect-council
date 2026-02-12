# EAM Architecture Council

A multi-agent CLI tool that orchestrates two expert subagents (SAP EAM + General EAM) to answer Enterprise Asset Management architecture questions and produce structured buildable specs.

Built with the Anthropic Claude API (Python SDK).

## Architecture

```
User Question
     |
     v
+-------------+
| Lead Agent  |  <-- Orchestrator / Reconciler
+------+------+
       | dispatches in parallel
  +----+----+
  v         v
+-----+  +---------+
| SAP |  | General |
| EAM |  |  EAM    |
|Expert|  | Expert  |
+--+--+  +---+-----+
   |         |
   +----+----+
        v
  Reconciliation
   (Lead Agent)
        |
        v
  Structured Output
  (Buildable Spec)
```

## Setup

### Prerequisites
- Python 3.11+
- An Anthropic API key

### Install

```bash
cd eam-architect-council
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -e ".[dev]"
```

### Configure

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Usage

### Ask a question (live mode)

```bash
python -m eam_council "How should we architect work order scheduling for SAP EAM?"
```

### Dry-run mode (no API key needed)

```bash
python -m eam_council "Any question here" --dry-run
```

### Override model

```bash
python -m eam_council "Your question" --model claude-sonnet-4-20250514
```

### Output
- Printed to stdout with rich formatting
- Written to `out/latest.md`

## Evaluation

Run all 5 golden questions:

```bash
python eval/run_eval.py --dry-run    # without API key
python eval/run_eval.py              # with API key (live)
```

Outputs are saved to `eval/outputs/`. See `eval/rubric.md` for scoring criteria.

## Tests

```bash
pytest tests/ -v
```

## Project Structure

```
eam-architect-council/
  eam_council/
    __main__.py          # Entry point
    cli.py               # CLI argument parsing
    council/
      lead_agent.py      # Orchestrator + reconciliation
      sap_eam_subagent.py
      general_eam_subagent.py
      models.py          # Pydantic models
      prompts.py         # All prompt templates
      skills_loader.py   # Reads SKILL.md + resources
      mock_data.py       # Mock SAP data
    skills/
      eam_council/       # Orchestration skill
      eam_spec_writer/   # Spec writing skill
      eam_glossary_entities/  # Glossary + entities
  eval/                  # Evaluation harness
  tests/                 # Smoke tests
```

## Skills & Resources Pattern

Each skill folder contains:
- `SKILL.md` -- Purpose, behavior, and constraints
- `resources/` -- Domain content (templates, glossary, rules)

The skills loader reads all skills at startup and injects them into agent prompts as context.

## Extending

### Adding MCP Servers
The architecture is designed for future MCP integration. Replace `mock_data.py` with real MCP tool calls when ready.

### Adding Real SAP Integration
Replace mock data with OData/BAPI calls. The canonical entities in `skills/eam_glossary_entities/resources/canonical_entities.yaml` define the expected data shapes.

### Adding New Subagents
1. Create a new file in `council/` following the subagent pattern.
2. Add a system prompt in `prompts.py`.
3. Update `lead_agent.py` to dispatch to the new subagent.

## License

MIT
