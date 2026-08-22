#!/usr/bin/env python3
"""Build deterministic self-validating five-Skill Global Codex bundle."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / ".agents" / "skills"
DIST_DIR = REPO_ROOT / "dist"
OUTPUT = DIST_DIR / "gtm-listing-demo-codex-bundle.zip"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from package_common import collect_files, reject_symlinks, write_deterministic_zip  # noqa: E402

SKILL_NAMES = [
    "gtm-listing-demo",
    "listing-planning",
    "listing-production",
    "listing-hardening",
    "listing-evidence-auditor",
]
REPO_METADATA = [
    "README.md",
    "CHANGELOG.md",
    "VERSION",
    ".github/workflows/validate-skill.yml",
    "scripts/package_codex_bundle.py",
    "scripts/package_common.py",
]
REQUIRED_MEMBERS = {
    ".agents/skills/gtm-listing-demo/SKILL.md",
    ".agents/skills/gtm-listing-demo/references/routing.md",
    ".agents/skills/gtm-listing-demo/scripts/validate_overlay.py",
    ".agents/skills/gtm-listing-demo/scripts/validate_project_state.py",
    ".agents/skills/listing-planning/SKILL.md",
    ".agents/skills/listing-planning/scripts/validate_planning_contracts.py",
    ".agents/skills/listing-production/SKILL.md",
    ".agents/skills/listing-production/scripts/production_state.py",
    ".agents/skills/listing-hardening/SKILL.md",
    ".agents/skills/listing-hardening/scripts/validate_delivery_state.py",
    ".agents/skills/listing-hardening/scripts/validate_demo_html.py",
    ".agents/skills/listing-hardening/scripts/validate_demo_runtime.py",
    ".agents/skills/listing-evidence-auditor/SKILL.md",
    ".agents/skills/listing-evidence-auditor/scripts/fingerprint_assets.py",
    ".agents/skills/listing-evidence-auditor/scripts/reconcile_evidence.py",
    *REPO_METADATA,
}


def smoke_test_archive(output: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp_name:
        root = Path(tmp_name)
        with ZipFile(output) as archive:
            archive.extractall(root)
        command = [
            sys.executable,
            str(root / ".agents" / "skills" / "gtm-listing-demo" / "scripts" / "validate_overlay.py"),
        ]
        result = subprocess.run(command, cwd=root, capture_output=True, text=True)
        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr, file=sys.stderr)
            raise SystemExit("FAIL: extracted Codex bundle validate_overlay.py failed")
        print(result.stdout.strip())


def main() -> None:
    entries: list[tuple[str, bytes]] = []
    for name in SKILL_NAMES:
        directory = SKILLS_ROOT / name
        if not (directory / "SKILL.md").is_file():
            raise SystemExit(f"FAIL: missing Skill directory/source: {name}")
        reject_symlinks(directory)
        for path in collect_files(directory):
            entries.append((path.relative_to(REPO_ROOT).as_posix(), path.read_bytes()))

    for relative in REPO_METADATA:
        path = REPO_ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise SystemExit(f"FAIL: missing/unsafe Codex bundle metadata: {relative}")
        entries.append((relative, path.read_bytes()))

    try:
        write_deterministic_zip(OUTPUT, entries)
    except ValueError as exc:
        raise SystemExit(f"FAIL: {exc}") from exc

    with ZipFile(OUTPUT) as archive:
        members = set(archive.namelist())
        missing = sorted(REQUIRED_MEMBERS - members)
        if missing:
            raise SystemExit(f"FAIL: Codex bundle is missing: {', '.join(missing)}")
        roots = {name for name in SKILL_NAMES if f".agents/skills/{name}/SKILL.md" in members}
        if roots != set(SKILL_NAMES):
            raise SystemExit(f"FAIL: expected five Skill roots, found: {sorted(roots)}")

    smoke_test_archive(OUTPUT)
    print(f"PASS: deterministic Codex bundle contains {len(members)} files and validates after extraction")
    print(OUTPUT)


if __name__ == "__main__":
    main()
