#!/usr/bin/env python3
"""Build deterministic one-install gtm-listing-demo with embedded stage/audit Skills."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile

MAIN_SKILL = Path(__file__).resolve().parents[1]
REPO_ROOT = MAIN_SKILL.parents[2]
SKILLS_ROOT = REPO_ROOT / ".agents" / "skills"
DIST_DIR = REPO_ROOT / "dist"
OUTPUT = DIST_DIR / "gtm-listing-demo.skill.zip"
PREFIX = Path("gtm-listing-demo")

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from package_common import collect_files, reject_symlinks, write_deterministic_zip  # noqa: E402

INTERNAL_SKILL_NAMES = [
    "listing-planning",
    "listing-production",
    "listing-hardening",
    "listing-evidence-auditor",
]
MAIN_FILES = [
    "SKILL.md",
    "SINGLE_CONTEXT_LIMITATION.txt",
    "agents/openai.yaml",
    "scripts/validate_project_state.py",
    "scripts/validate_install.py",
]
MAIN_DIRS = ["profiles", "references"]

REQUIRED_MEMBERS = {
    "gtm-listing-demo/SKILL.md",
    "gtm-listing-demo/SINGLE_CONTEXT_LIMITATION.txt",
    "gtm-listing-demo/references/routing.md",
    "gtm-listing-demo/scripts/validate_project_state.py",
    "gtm-listing-demo/scripts/validate_install.py",
    "gtm-listing-demo/internal-skills/listing-planning/SKILL.md",
    "gtm-listing-demo/internal-skills/listing-planning/scripts/validate_planning_contracts.py",
    "gtm-listing-demo/internal-skills/listing-production/SKILL.md",
    "gtm-listing-demo/internal-skills/listing-production/scripts/production_state.py",
    "gtm-listing-demo/internal-skills/listing-production/scripts/production_state_legacy.py",
    "gtm-listing-demo/internal-skills/listing-hardening/SKILL.md",
    "gtm-listing-demo/internal-skills/listing-hardening/scripts/validate_delivery_state.py",
    "gtm-listing-demo/internal-skills/listing-hardening/scripts/_delivery_state_core.py",
    "gtm-listing-demo/internal-skills/listing-hardening/scripts/validate_demo_html.py",
    "gtm-listing-demo/internal-skills/listing-hardening/scripts/validate_demo_html_legacy.py",
    "gtm-listing-demo/internal-skills/listing-hardening/scripts/validate_demo_runtime.py",
    "gtm-listing-demo/internal-skills/listing-evidence-auditor/SKILL.md",
    "gtm-listing-demo/internal-skills/listing-evidence-auditor/scripts/fingerprint_assets.py",
    "gtm-listing-demo/internal-skills/listing-evidence-auditor/scripts/fingerprint_assets_legacy.py",
    "gtm-listing-demo/internal-skills/listing-evidence-auditor/scripts/reconcile_evidence.py",
    "gtm-listing-demo/internal-skills/listing-evidence-auditor/scripts/reconcile_evidence_legacy.py",
}


def exclude_dev(relative: Path) -> bool:
    return relative.name.startswith("selftest_") or "__pycache__" in relative.parts or relative.suffix == ".pyc"


def add_tree(entries: list[tuple[str, bytes]], source_root: Path, target_root: Path) -> None:
    for path in collect_files(source_root, exclude=exclude_dev):
        entries.append(((target_root / path.relative_to(source_root)).as_posix(), path.read_bytes()))


def smoke_test_archive(output: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp_name:
        root = Path(tmp_name)
        with ZipFile(output) as archive:
            archive.extractall(root)
        installed = root / "gtm-listing-demo"
        result = subprocess.run(
            [sys.executable, str(installed / "scripts" / "validate_install.py")],
            cwd=installed,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr, file=sys.stderr)
            raise SystemExit("FAIL: extracted one-install package validation failed")
        print(result.stdout.strip())


def main() -> None:
    reject_symlinks(MAIN_SKILL)
    for name in INTERNAL_SKILL_NAMES:
        reject_symlinks(SKILLS_ROOT / name)

    entries: list[tuple[str, bytes]] = []
    for relative in MAIN_FILES:
        path = MAIN_SKILL / relative
        if not path.is_file() or path.is_symlink():
            raise SystemExit(f"FAIL: missing/unsafe main runtime file: {relative}")
        entries.append(((PREFIX / relative).as_posix(), path.read_bytes()))
    for directory in MAIN_DIRS:
        source = MAIN_SKILL / directory
        if source.is_dir():
            add_tree(entries, source, PREFIX / directory)
    for name in INTERNAL_SKILL_NAMES:
        source = SKILLS_ROOT / name
        if not (source / "SKILL.md").is_file():
            raise SystemExit(f"FAIL: missing internal Skill source: {name}")
        add_tree(entries, source, PREFIX / "internal-skills" / name)

    try:
        write_deterministic_zip(OUTPUT, entries)
    except ValueError as exc:
        raise SystemExit(f"FAIL: {exc}") from exc

    with ZipFile(OUTPUT) as archive:
        members = set(archive.namelist())
        missing = sorted(REQUIRED_MEMBERS - members)
        if missing:
            raise SystemExit(f"FAIL: compatibility package is missing: {', '.join(missing)}")
        if any("/selftest_" in name for name in members):
            raise SystemExit("FAIL: repository-only selftests leaked into one-install package")
        note = archive.read("gtm-listing-demo/SINGLE_CONTEXT_LIMITATION.txt").decode("utf-8")
        if "HUMAN_REVIEW_REQUIRED" not in note or "listing-evidence-auditor" not in note:
            raise SystemExit("FAIL: semantic-audit limitation is missing")

    smoke_test_archive(OUTPUT)
    print(f"PASS: deterministic one-install package contains {len(members)} runtime files")
    print(OUTPUT)


if __name__ == "__main__":
    main()
