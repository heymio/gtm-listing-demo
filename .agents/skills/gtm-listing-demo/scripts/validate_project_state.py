#!/usr/bin/env python3
"""Compatibility shim delegating legacy Project State calls to validate_delivery_state."""

from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve()
MAIN_SKILL = HERE.parents[1]
REPO_ROOT = MAIN_SKILL.parents[2]

CANDIDATES = [
    REPO_ROOT / ".agents" / "skills" / "listing-hardening" / "scripts" / "validate_delivery_state.py",
    MAIN_SKILL / "internal-skills" / "listing-hardening" / "scripts" / "validate_delivery_state.py",
]
TARGET = next((path for path in CANDIDATES if path.is_file()), None)
if TARGET is None:
    raise RuntimeError("cannot locate listing-hardening validate_delivery_state.py")

SPEC = importlib.util.spec_from_file_location("global_listing_hardening_validate_delivery_state", TARGET)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load hardening validator: {TARGET}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

canonical_hash = MODULE.canonical_hash
validate_state = MODULE.validate_state
main = MODULE.main

if __name__ == "__main__":
    raise SystemExit(main())
