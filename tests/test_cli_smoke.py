"""Smoke tests for the EAM Council CLI."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

# Ensure subprocesses use UTF-8
_ENV = {**os.environ, "ANTHROPIC_API_KEY": "", "PYTHONIOENCODING": "utf-8"}


def _run_cli(*extra_args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "eam_council", *extra_args],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(PROJECT_ROOT),
        env=_ENV,
    )


def test_dry_run_produces_output():
    """CLI in --dry-run mode should produce structured output without an API key."""
    result = _run_cli("How should we schedule work orders?", "--dry-run")
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    assert "Executive Summary" in result.stdout
    assert "Decision Log" in result.stdout
    assert "Next Agent To Build" in result.stdout


def test_dry_run_writes_file():
    """CLI in --dry-run mode should write output to out/latest.md."""
    out_file = PROJECT_ROOT / "out" / "latest.md"
    result = _run_cli("Test question for file output", "--dry-run")
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    assert out_file.exists(), "out/latest.md was not created"
    content = out_file.read_text(encoding="utf-8")
    assert "EAM Architecture Council" in content


def test_skills_loader():
    """Skills loader should find all 3 skills."""
    from eam_council.council.skills_loader import load_all_skills

    skills_root = PROJECT_ROOT / "eam_council" / "skills"
    context = load_all_skills(skills_root)
    assert "eam_council" in context
    assert "eam_spec_writer" in context
    assert "eam_glossary_entities" in context
    assert "glossary" in context.lower()
