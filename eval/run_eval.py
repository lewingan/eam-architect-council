"""Evaluation harness - runs golden questions through the council and collects outputs."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

GOLDEN_QUESTIONS_FILE = Path(__file__).parent / "golden_questions.md"
OUTPUTS_DIR = Path(__file__).parent / "outputs"

REQUIRED_SECTIONS = [
    "Executive Summary",
    "SAP EAM Perspective",
    "General EAM Perspective",
    "Unified Recommendation",
    "Assumptions & Open Questions",
    "Decision Log",
    "Next Agent To Build",
]


def parse_golden_questions() -> list[tuple[str, str]]:
    """Parse golden_questions.md and return list of (label, question)."""
    text = GOLDEN_QUESTIONS_FILE.read_text(encoding="utf-8")
    questions: list[tuple[str, str]] = []
    blocks = re.split(r"^## ", text, flags=re.MULTILINE)
    for block in blocks:
        block = block.strip()
        if not block or block.startswith("#"):
            continue
        lines = block.split("\n", 1)
        label = lines[0].strip().rstrip(":")
        question = lines[1].strip() if len(lines) > 1 else label
        questions.append((label, question))
    return questions


def check_format_compliance(output: str) -> tuple[int, list[str]]:
    """Check if all required sections are present. Returns (score, missing)."""
    missing = [s for s in REQUIRED_SECTIONS if s.lower() not in output.lower()]
    if not missing:
        return 5, []
    elif len(missing) == 1:
        return 3, missing
    elif len(missing) <= 3:
        return 2, missing
    return 1, missing




def estimate_cost_signals(output: str) -> dict[str, int]:
    """Heuristic cost/quality signals from output text."""
    lower = output.lower()
    return {
        "has_decision_log_rows": lower.count("| 1 |"),
        "has_api_refs": int("sap api references" in lower),
        "assumption_checkboxes": output.count("- [ ]"),
    }
def run_question(label: str, question: str, dry_run: bool) -> Path:
    """Run the CLI for a single question and save output."""
    OUTPUTS_DIR.mkdir(exist_ok=True)
    safe_label = re.sub(r"[^a-zA-Z0-9]+", "_", label).strip("_").lower()
    out_file = OUTPUTS_DIR / f"{safe_label}.md"

    cmd = [sys.executable, "-m", "eam_council", question]
    if dry_run:
        cmd.append("--dry-run")

    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    result = subprocess.run(
        cmd, capture_output=True, encoding="utf-8", errors="replace",
        cwd=str(Path(__file__).parent.parent), env=env,
    )
    stdout = result.stdout or ""
    stderr = result.stderr or ""
    out_file.write_text(stdout + "\n\n---\nSTDERR:\n" + stderr, encoding="utf-8")
    return out_file


def main() -> None:
    dry_run = "--dry-run" in sys.argv or "--dry_run" in sys.argv
    questions = parse_golden_questions()

    print(f"Running {len(questions)} golden questions ({'DRY-RUN' if dry_run else 'LIVE'} mode)\n")
    print(f"{'Question':<40} {'Format':>8} {'Missing Sections'}")
    print("-" * 80)

    results: list[dict] = []
    for label, question in questions:
        out_file = run_question(label, question, dry_run)
        output = out_file.read_text(encoding="utf-8")
        fmt_score, missing = check_format_compliance(output)
        signals = estimate_cost_signals(output)

        missing_str = ", ".join(missing) if missing else "-"
        print(f"{label:<40} {fmt_score:>5}/5   {missing_str}")

        results.append({
            "label": label,
            "format_score": fmt_score,
            "missing": missing,
            "signals": signals,
            "output_file": str(out_file),
        })

    print("\n" + "=" * 80)
    avg = sum(r["format_score"] for r in results) / len(results) if results else 0
    avg_assumptions = (sum(r["signals"]["assumption_checkboxes"] for r in results) / len(results)) if results else 0
    print(f"Average format compliance: {avg:.1f}/5")
    print(f"Average assumptions checklist items: {avg_assumptions:.1f}")
    print(f"\nOutputs saved to: {OUTPUTS_DIR.resolve()}")
    print(
        "\nNote: Completeness, Correctness, Assumptions Quality, and Actionability "
        "scores require manual review. See eval/rubric.md for criteria."
    )
    print(
        "To manually score, open each output file and rate 1-5 per rubric dimension."
    )


if __name__ == "__main__":
    main()
