# Codebase Overview

This repository is a Python CLI that orchestrates a three-agent workflow for Enterprise Asset Management (EAM) architecture questions:

1. **SAP EAM subagent** (SAP-specific recommendations)
2. **General EAM subagent** (vendor-agnostic best practices)
3. **Lead agent** (reconciles both drafts into one structured answer)

## Runtime flow

- `python -m eam_council ...` starts the CLI entrypoint in `eam_council/__main__.py`, which calls `cli.main()`.
- `cli.main()` parses arguments, resolves mode (`--dry-run` or live based on `ANTHROPIC_API_KEY`), and calls `run_council(...)`.
- `run_council(...)` in `lead_agent.py`:
  - loads skill markdown/resources via `skills_loader.load_all_skills()`
  - loads mock context via `mock_data.get_mock_context()`
  - runs SAP + General subagents concurrently with `asyncio.gather(...)`
  - either returns deterministic dry-run markdown or asks a lead Anthropic model to reconcile both drafts

## Prompting and context strategy

- System prompts are centralized in `council/prompts.py`.
- `build_subagent_prompt(...)` injects:
  - user question
  - loaded skills/resources
  - mock data
- Question classification (`data`, `general`, `api`) controls how much context is injected.
  - General questions remove heavy canonical YAML context.
  - API questions strip `sap_internals` blocks.
  - Data/migration questions keep full context.

## Subagent behavior

- Both subagents support:
  - **dry-run mode** with deterministic, prebuilt markdown
  - **live mode** via `anthropic.Anthropic().messages.create(...)`
- Optional server-side web search tool integration is enabled unless `--no-search` is passed.
- Mixed tool/text responses are normalized by `extract_text_from_response(...)`, which concatenates only text blocks.

## Skills model

- Skills are plain folders under `eam_council/skills/<skill_name>/`.
- Each skill can provide:
  - `SKILL.md`
  - `resources/*`
- Loader behavior is simple and deterministic: read skill docs and resource files in sorted directory order and concatenate into one prompt context string.

## Testing and evaluation

- `tests/test_cli_smoke.py` validates dry-run execution, output file creation, and skill loading.
- `eval/run_eval.py` runs golden questions and checks format compliance against required sections.

## Design strengths

- Clear orchestration boundary in `lead_agent.py`
- Deterministic dry-run for local development without credentials
- Prompt templates and tool definitions are separated from business flow
- Context filtering prevents unnecessary prompt bloat for non-data questions

## Key limitations to be aware of

- No retry/backoff or explicit exception handling around Anthropic calls
- Skill loading is eager and string-based (no schema validation)
- Evaluation harness scores only structural compliance automatically; semantic quality remains manual
