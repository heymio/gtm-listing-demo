#!/usr/bin/env python3
"""Verify the user-facing compatibility validator delegates to Hardening."""

from __future__ import annotations

import importlib.util
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[2]
LEGACY = SKILL_DIR / "scripts" / "validate_project_state.py"
CANONICAL = REPO_ROOT / ".agents" / "skills" / "listing-hardening" / "scripts" / "validate_delivery_state.py"


def load(path: Path, name: str):
    assert path.is_file(), str(path)
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_compatibility_validator_matches_canonical_api() -> None:
    old = load(LEGACY, "global_compat_validator")
    canonical = load(CANONICAL, "global_canonical_validator")
    assert callable(old.canonical_hash)
    assert callable(old.validate_state)
    sample = {"b": 2, "a": 1}
    assert old.canonical_hash(sample) == canonical.canonical_hash(sample)


def test_compatibility_validator_does_not_duplicate_gate_logic() -> None:
    text = LEGACY.read_text(encoding="utf-8")
    assert "validate_delivery_state" in text
    for duplicated in ["CHANNEL_MODULE_BUDGET_GATE =", "def _channel_budget", "def _pre_demo_gate"]:
        assert duplicated not in text


def main() -> int:
    tests = [value for name, value in globals().items() if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"PASS: {len(tests)} global-project-state compatibility tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
