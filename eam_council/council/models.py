"""Data models for the council system."""

from __future__ import annotations

from pydantic import BaseModel


class SubagentDraft(BaseModel):
    """Draft response from a subagent."""

    agent_name: str
    perspective: str
    content: str


class CouncilResult(BaseModel):
    """Final reconciled output from the council."""

    question: str
    sap_draft: SubagentDraft
    general_draft: SubagentDraft
    agentic_draft: SubagentDraft | None = None
    final_output: str
