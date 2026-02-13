"""Orchestration tests for council agent sequencing behavior."""

from __future__ import annotations

import asyncio

from eam_council.council.models import SubagentDraft


def test_agentic_flow_runs_agentic_after_eam(monkeypatch):
    """For agentic questions, SAP+General should run before Agentic expert."""
    from eam_council.council import lead_agent

    call_order: list[str] = []

    async def fake_sap(*_args, **_kwargs):
        call_order.append("sap")
        return SubagentDraft(agent_name="SAP", perspective="sap", content="sap draft")

    async def fake_general(*_args, **_kwargs):
        call_order.append("general")
        return SubagentDraft(agent_name="General", perspective="gen", content="general draft")

    async def fake_agentic(*_args, **kwargs):
        # Ensure upstream EAM context is passed into the agentic subagent call.
        assert kwargs.get("sap_draft") == "sap draft"
        assert kwargs.get("general_draft") == "general draft"
        call_order.append("agentic")
        return SubagentDraft(agent_name="Agentic", perspective="agentic", content="agentic draft")

    monkeypatch.setattr(lead_agent, "run_sap_subagent", fake_sap)
    monkeypatch.setattr(lead_agent, "run_general_subagent", fake_general)
    monkeypatch.setattr(lead_agent, "run_agentic_arch_subagent", fake_agentic)
    monkeypatch.setattr(lead_agent, "load_all_skills", lambda: "skills")
    monkeypatch.setattr(lead_agent, "get_mock_context", lambda: "mock")

    asyncio.run(
        lead_agent.run_council(
            question="Design an agentic EAM planner",
            model="dummy",
            dry_run=True,
            search_enabled=False,
        )
    )

    assert set(call_order[:2]) == {"sap", "general"}
    assert call_order[2] == "agentic"


def test_validator_parser_handles_clarification_and_aligned():
    """Validator parser should route target when clarification is requested."""
    from eam_council.council.lead_agent import _validator_needs_clarification

    assert _validator_needs_clarification("ALIGNED") == (False, None, None)
    assert _validator_needs_clarification(
        "NEEDS_CLARIFICATION | target=agentic | reason=conflict with SAP constraints"
    ) == (True, "agentic", "conflict with SAP constraints")
