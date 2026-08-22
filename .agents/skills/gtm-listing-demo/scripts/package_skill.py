#!/usr/bin/env python3
"""Package one-install gtm-listing-demo with four embedded stage/audit Skills."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

MAIN_SKILL = Path(__file__).resolve().parents[1]
REPO_ROOT = MAIN_SKILL.parents[2]
SKILLS_ROOT = REPO_ROOT / ".agents" / "skills"
DIST_DIR = REPO_ROOT / "dist"
OUTPUT = DIST_DIR / "gtm-listing-demo.skill.zip"
PREFIX = Path("gtm-listing-demo")

INTERNAL_SKILL_NAMES = [
    "listing-planning",
    "listing-production",
    "listing-hardening",
    "listing-evidence-auditor",
]

SINGLE_CONTEXT_LIMITATION = MAIN_SKILL / "SINGLE_CONTEXT_LIMITATION.txt"

REQUIRED_MEMBERS = {
    "gtm-listing-demo/SKILL.md",
    "gtm-listing-demo/SINGLE_CONTEXT_LIMITATION.txt",
    "gtm-listing-demo/references/routing.md",
    "gtm-listing-demo/scripts/validate_project_state.py",
    "gtm-listing-demo/internal-skills/listing-planning/SKILL.md",
    "gtm-listing-demo/internal-skills/listing-planning/scripts/validate_planning_contracts.py",
    "gtm-listing-demo/internal-skills/listing-planning/scripts/account_capability.py",
    "gtm-listing-demo/internal-skills/listing-production/SKILL.md",
    "gtm-listing-demo/internal-skills/listing-production/scripts/project_asset_packet.py",
    "gtm-listing-demo/internal-skills/listing-production/scripts/production_state.py",
    "gtm-listing-demo/internal-skills/listing-production/scripts/set_level_qa.py",
    "gtm-listing-demo/internal-skills/listing-production/scripts/cleanup_policy.py",
    "gtm-listing-demo/internal-skills/listing-hardening/SKILL.md",
    "gtm-listing-demo/internal-skills/listing-hardening/references/demo-output.md",
    "gtm-listing-demo/internal-skills/listing-hardening/scripts/validate_delivery_state.py",
    "gtm-listing-demo/internal-skills/listing-hardening/scripts/validate_demo_html.py",
    "gtm-listing-demo/internal-skills/listing-evidence-auditor/SKILL.md",
    "gtm-listing-demo/internal-skills/listing-evidence-auditor/scripts/fingerprint_assets.py",
    "gtm-listing-demo/internal-skills/listing-evidence-auditor/scripts/reconcile_evidence.py",
}


def add_tree(archive: ZipFile, source_root: Path, target_root: Path) -> None:
    for path in sorted(source_root.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            archive.write(path, target_root / path.relative_to(source_root))


def smoke_test_archive(output: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)
        with ZipFile(output) as archive:
            archive.extractall(tmp)
        root = tmp / "gtm-listing-demo"
        commands = [
            [sys.executable, str(root / "scripts" / "selftest_router.py")],
            [sys.executable, str(root / "internal-skills" / "listing-planning" / "scripts" / "selftest_planning.py")],
            [sys.executable, str(root / "internal-skills" / "listing-production" / "scripts" / "selftest_production.py")],
            [sys.executable, str(root / "internal-skills" / "listing-evidence-auditor" / "scripts" / "selftest_auditor.py")],
            [sys.executable, str(root / "internal-skills" / "listing-hardening" / "scripts" / "selftest_hardening.py")],
            [sys.executable, str(root / "internal-skills" / "listing-hardening" / "scripts" / "selftest_demo_output.py")],
        ]
        for command in commands:
            result = subprocess.run(command, cwd=root, capture_output=True, text=True)
            if result.returncode != 0:
                print(result.stdout)
                print(result.stderr, file=sys.stderr)
                raise SystemExit(f"FAIL: compatibility archive smoke test failed: {' '.join(command)}")

        # The user-facing compatibility shim must resolve the embedded canonical validator.
        check = subprocess.run(
            [
                sys.executable,
                "-c",
                "import importlib.util, pathlib; p=pathlib.Path('scripts/validate_project_state.py'); "
                "s=importlib.util.spec_from_file_location('shim', p); m=importlib.util.module_from_spec(s); "
                "s.loader.exec_module(m); assert callable(m.validate_state); assert callable(m.canonical_hash)",
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        if check.returncode != 0:
            print(check.stdout)
            print(check.stderr, file=sys.stderr)
            raise SystemExit("FAIL: embedded compatibility validator shim did not resolve")


def main() -> None:
    if not (MAIN_SKILL / "SKILL.md").is_file():
        raise SystemExit("FAIL: missing user-facing SKILL.md")
    if not SINGLE_CONTEXT_LIMITATION.is_file():
        raise SystemExit("FAIL: missing SINGLE_CONTEXT_LIMITATION.txt")
    for name in INTERNAL_SKILL_NAMES:
        source = SKILLS_ROOT / name
        if not (source / "SKILL.md").is_file():
            raise SystemExit(f"FAIL: missing internal Skill source: {name}")

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as archive:
        add_tree(archive, MAIN_SKILL, PREFIX)
        for name in INTERNAL_SKILL_NAMES:
            add_tree(archive, SKILLS_ROOT / name, PREFIX / "internal-skills" / name)

    with ZipFile(OUTPUT) as archive:
        members = set(archive.namelist())
        missing = sorted(REQUIRED_MEMBERS - members)
        if missing:
            raise SystemExit(f"FAIL: compatibility package is missing: {', '.join(missing)}")
        note = archive.read("gtm-listing-demo/SINGLE_CONTEXT_LIMITATION.txt").decode("utf-8")
        if "HUMAN_REVIEW_REQUIRED" not in note or "listing-evidence-auditor" not in note:
            raise SystemExit("FAIL: compatibility package lacks semantic-audit limitation text")

    smoke_test_archive(OUTPUT)
    print(f"PASS: one-install package contains {len(members)} files with four embedded internal Skills")
    print(OUTPUT)


if __name__ == "__main__":
    main()
