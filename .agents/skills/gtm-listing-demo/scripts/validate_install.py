#!/usr/bin/env python3
"""Validate an extracted Global one-install package without repository-only paths."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTERNAL = ROOT / "internal-skills"

REQUIRED = [
    ROOT / "SKILL.md",
    ROOT / "SINGLE_CONTEXT_LIMITATION.txt",
    ROOT / "references" / "routing.md",
    ROOT / "scripts" / "validate_project_state.py",
    ROOT / "scripts" / "validate_install.py",
    INTERNAL / "listing-planning" / "SKILL.md",
    INTERNAL / "listing-planning" / "scripts" / "validate_planning_contracts.py",
    INTERNAL / "listing-production" / "SKILL.md",
    INTERNAL / "listing-production" / "scripts" / "production_state.py",
    INTERNAL / "listing-production" / "scripts" / "production_state_legacy.py",
    INTERNAL / "listing-hardening" / "SKILL.md",
    INTERNAL / "listing-hardening" / "scripts" / "validate_delivery_state.py",
    INTERNAL / "listing-hardening" / "scripts" / "_delivery_state_core.py",
    INTERNAL / "listing-hardening" / "scripts" / "validate_demo_html.py",
    INTERNAL / "listing-hardening" / "scripts" / "validate_demo_html_legacy.py",
    INTERNAL / "listing-hardening" / "scripts" / "validate_demo_runtime.py",
    INTERNAL / "listing-evidence-auditor" / "SKILL.md",
    INTERNAL / "listing-evidence-auditor" / "scripts" / "fingerprint_assets.py",
    INTERNAL / "listing-evidence-auditor" / "scripts" / "fingerprint_assets_legacy.py",
    INTERNAL / "listing-evidence-auditor" / "scripts" / "reconcile_evidence.py",
    INTERNAL / "listing-evidence-auditor" / "scripts" / "reconcile_evidence_legacy.py",
]


def main() -> int:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED if not path.is_file()]
    if missing:
        print("FAIL: extracted package is missing runtime files: " + ", ".join(missing))
        return 1
    leaked_tests = [path for path in ROOT.rglob("selftest_*.py")]
    if leaked_tests:
        print("FAIL: repository-only selftests leaked into one-install package")
        return 1
    note = (ROOT / "SINGLE_CONTEXT_LIMITATION.txt").read_text(encoding="utf-8")
    if "HUMAN_REVIEW_REQUIRED" not in note or "listing-evidence-auditor" not in note:
        print("FAIL: semantic-audit limitation is missing")
        return 1

    shim = ROOT / "scripts" / "validate_project_state.py"
    spec = importlib.util.spec_from_file_location("installed_global_project_state", shim)
    if spec is None or spec.loader is None:
        print("FAIL: cannot load installed compatibility validator")
        return 1
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        print(f"FAIL: installed compatibility validator cannot resolve runtime: {exc}")
        return 1
    if not callable(getattr(module, "validate_state", None)) or not callable(getattr(module, "canonical_hash", None)):
        print("FAIL: installed compatibility validator exports are incomplete")
        return 1
    print("PASS: extracted Global one-install package validates its v0.3.3 runtime")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
