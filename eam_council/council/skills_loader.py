"""Load SKILL.md files and their resources into a structured context string."""

from __future__ import annotations

from pathlib import Path


def load_all_skills(skills_root: Path | None = None) -> str:
    """Read all skills and their resources, returning a formatted context string."""
    if skills_root is None:
        skills_root = Path(__file__).resolve().parent.parent / "skills"

    sections: list[str] = []

    for skill_dir in sorted(skills_root.iterdir()):
        if not skill_dir.is_dir():
            continue

        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        skill_text = skill_md.read_text(encoding="utf-8")
        sections.append(f"=== SKILL: {skill_dir.name} ===\n{skill_text}")

        resources_dir = skill_dir / "resources"
        if resources_dir.is_dir():
            for res_file in sorted(resources_dir.iterdir()):
                if res_file.is_file():
                    content = res_file.read_text(encoding="utf-8")
                    sections.append(
                        f"--- Resource: {skill_dir.name}/{res_file.name} ---\n{content}"
                    )

    return "\n\n".join(sections)
