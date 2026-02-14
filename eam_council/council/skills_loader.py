"""Load SKILL.md files and their resources into a structured context string."""

from __future__ import annotations

from pathlib import Path


def _iter_skill_dirs(skills_root: Path):
    for skill_dir in sorted(skills_root.iterdir()):
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
            yield skill_dir


def _get_support_dir(skill_dir: Path) -> Path | None:
    """Return the primary support directory for a skill.

    Prefer ``references/`` for Claude-skill style packaging, but keep backward
    compatibility with existing ``resources/`` directories.
    """
    references_dir = skill_dir / "references"
    if references_dir.is_dir():
        return references_dir

    resources_dir = skill_dir / "resources"
    if resources_dir.is_dir():
        return resources_dir

    return None


def list_skill_inventory(skills_root: Path | None = None) -> dict[str, list[str]]:
    """Return skill -> resource-file mapping for routing decisions."""
    if skills_root is None:
        skills_root = Path(__file__).resolve().parent.parent / "skills"

    inventory: dict[str, list[str]] = {}
    for skill_dir in _iter_skill_dirs(skills_root):
        resources: list[str] = []
        support_dir = _get_support_dir(skill_dir)
        if support_dir is not None:
            resources = [p.name for p in sorted(support_dir.iterdir()) if p.is_file()]
        inventory[skill_dir.name] = resources
    return inventory


def load_all_skills(skills_root: Path | None = None) -> str:
    """Read all skills and their resources, returning a formatted context string."""
    if skills_root is None:
        skills_root = Path(__file__).resolve().parent.parent / "skills"

    sections: list[str] = []

    for skill_dir in _iter_skill_dirs(skills_root):
        skill_md = skill_dir / "SKILL.md"

        skill_text = skill_md.read_text(encoding="utf-8")
        sections.append(f"=== SKILL: {skill_dir.name} ===\n{skill_text}")

        support_dir = _get_support_dir(skill_dir)
        if support_dir is not None:
            for res_file in sorted(support_dir.iterdir()):
                if res_file.is_file():
                    content = res_file.read_text(encoding="utf-8")
                    sections.append(
                        f"--- Resource: {skill_dir.name}/{res_file.name} ---\n{content}"
                    )

    return "\n\n".join(sections)


def load_selected_skills(
    *,
    include_skills: set[str] | None = None,
    include_resources: dict[str, set[str]] | None = None,
    skills_root: Path | None = None,
) -> str:
    """Read selected skills/resources and return a formatted context string.

    If ``include_skills`` is None, include all skills. If ``include_resources`` has
    an entry for a skill, include only those resource file names for that skill.
    """
    if skills_root is None:
        skills_root = Path(__file__).resolve().parent.parent / "skills"

    sections: list[str] = []

    for skill_dir in _iter_skill_dirs(skills_root):
        skill_name = skill_dir.name
        if include_skills is not None and skill_name not in include_skills:
            continue

        skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        sections.append(f"=== SKILL: {skill_name} ===\n{skill_text}")

        support_dir = _get_support_dir(skill_dir)
        if support_dir is None:
            continue

        include_for_skill = None if include_resources is None else include_resources.get(skill_name)
        for res_file in sorted(support_dir.iterdir()):
            if not res_file.is_file():
                continue
            if include_for_skill is not None and res_file.name not in include_for_skill:
                continue
            content = res_file.read_text(encoding="utf-8")
            sections.append(f"--- Resource: {skill_name}/{res_file.name} ---\n{content}")

    return "\n\n".join(sections)
