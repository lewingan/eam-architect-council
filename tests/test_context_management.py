from __future__ import annotations

from eam_council.council.prompts import build_lead_prompt, filter_context_for_question
from eam_council.council.skills_loader import load_selected_skills


def test_filter_context_general_removes_canonical_entities():
    ctx = (
        "=== SKILL: eam_glossary_entities ===\nfoo\n"
        "--- Resource: eam_glossary_entities/canonical_entities.yaml ---\nbar\n"
        "--- Resource: eam_glossary_entities/glossary.md ---\nbaz\n"
    )
    out = filter_context_for_question(ctx, "Create an organizational roadmap")
    assert "canonical_entities" not in out
    assert "glossary.md" in out


def test_build_lead_prompt_compacts_long_drafts():
    long_text = "x" * 2500
    prompt = build_lead_prompt("q", long_text, long_text, "skills", compact=True)
    assert "[...truncated for cost control...]" in prompt


def test_load_selected_skills_subset():
    ctx = load_selected_skills(include_skills={"eam_council"})
    assert "=== SKILL: eam_council ===" in ctx
    assert "=== SKILL: eam_spec_writer ===" not in ctx
