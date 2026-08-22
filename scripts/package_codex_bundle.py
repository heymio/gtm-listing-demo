#!/usr/bin/env python3
"""Package the five-Skill gtm-listing-demo architecture for repository/Codex use."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / ".agents" / "skills"
DIST_DIR = REPO_ROOT / "dist"
OUTPUT = DIST_DIR / "gtm-listing-demo-codex-bundle.zip"

SKILL_NAMES = [
    "gtm-listing-demo",
    "listing-planning",
    "listing-production",
    "listing-hardening",
    "listing-evidence-auditor",
]

REQUIRED_MEMBERS = {
    ".agents/skills/gtm-listing-demo/SKILL.md",
    ".agents/skills/gtm-listing-demo/references/routing.md",
    ".agents/skills/gtm-listing-demo/scripts/validate_project_state.py",
    ".agents/skills/listing-planning/SKILL.md",
    ".agents/skills/listing-planning/scripts/validate_planning_contracts.py",
    ".agents/skills/listing-planning/scripts/account_capability.py",
    ".agents/skills/listing-production/SKILL.md",
    ".agents/skills/listing-production/scripts/project_asset_packet.py",
    ".agents/skills/listing-production/scripts/production_state.py",
    ".agents/skills/listing-production/scripts/set_level_qa.py",
    ".agents/skills/listing-production/scripts/cleanup_policy.py",
    ".agents/skills/listing-hardening/SKILL.md",
    ".agents/skills/listing-hardening/scripts/validate_delivery_state.py",
    ".agents/skills/listing-hardening/scripts/validate_demo_html.py",
    ".agents/skills/listing-evidence-auditor/SKILL.md",
    ".agents/skills/listing-evidence-auditor/scripts/fingerprint_assets.py",
    ".agents/skills/listing-evidence-auditor/scripts/reconcile_evidence.py",
}


def add_tree(archive: ZipFile, root: Path) -> None:
    for path in sorted(root.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            archive.write(path, path.relative_to(REPO_ROOT))


def main() -> None:
    skill_dirs = [SKILLS_ROOT / name for name in SKILL_NAMES]
    for name, directory in zip(SKILL_NAMES, skill_dirs):
        if not (directory / "SKILL.md").is_file():
            raise SystemExit(f"FAIL: missing Skill directory/source: {name}")

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as archive:
        for directory in skill_dirs:
            add_tree(archive, directory)

    with ZipFile(OUTPUT) as archive:
        members = set(archive.namelist())
        missing = sorted(REQUIRED_MEMBERS - members)
        if missing:
            raise SystemExit(f"FAIL: Codex bundle is missing: {', '.join(missing)}")
        roots = {name for name in SKILL_NAMES if f".agents/skills/{name}/SKILL.md" in members}
        if roots != set(SKILL_NAMES):
            raise SystemExit(f"FAIL: expected five Skill roots, found: {sorted(roots)}")

    print(f"PASS: Codex bundle contains {len(members)} files across five sibling Skills")
    print(OUTPUT)


if __name__ == "__main__":
    main()
