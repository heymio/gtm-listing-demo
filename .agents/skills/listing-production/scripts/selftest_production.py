#!/usr/bin/env python3
"""Global listing-production regressions including v0.3.3 fail-closed Freeze behavior."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
LEGACY = SCRIPT_DIR / "selftest_production_legacy.py"
SPEC = importlib.util.spec_from_file_location("global_production_legacy_tests", LEGACY)
assert SPEC and SPEC.loader
legacy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(legacy)

_original_approved_ledger = legacy.approved_ledger


def _approved_ledger_v033() -> dict:
    ledger = _original_approved_ledger()
    for asset_id, row in ledger.get("assets", {}).items():
        if isinstance(row, dict):
            row["selected_candidate_id"] = f"{asset_id}-approved"
    return ledger


legacy.approved_ledger = _approved_ledger_v033


def test_required_set_unions_asset_set_page_plan_and_blockers() -> None:
    from production_state import build_production_freeze
    handoff = {
        "asset_set": [{"asset_id": "G1"}],
        "page_plan": {"gallery": ["G1", "G2"], "enhanced_content": [], "other_required_regions": []},
        "blocked_assets": [{"asset_id": "G3", "reason": "missing identity source"}],
        "page_visual_system": {"asset_directions": [{"asset_id": "G1"}, {"asset_id": "G2"}, {"asset_id": "G3"}]},
    }
    ledger = {
        "assets": {
            "G1": {"status": "USER_APPROVED", "selected_candidate_id": "G1-v1", "current_output_ref": "file:g1"},
            "G2": {"status": "USER_APPROVED", "selected_candidate_id": "G2-v1", "current_output_ref": "file:g2"},
        },
        "set_qa": {
            "status": "CLEAR",
            "reviewed_asset_ids": ["G1", "G2", "G3"],
            "reviewed_output_refs": {"G1": "file:g1", "G2": "file:g2", "G3": "file:g3"},
            "visual_review_ref": "set-review:1",
        },
    }
    freeze = build_production_freeze(handoff, ledger)
    assert freeze["required_asset_ids"] == ["G1", "G2", "G3"], freeze
    assert freeze["blocked_assets"] == ["G3"], freeze
    assert freeze["ready_for_hardening"] is False, freeze


def test_freeze_binds_each_asset_to_exact_candidate_and_output() -> None:
    from production_state import build_production_freeze
    handoff = {
        "asset_set": [{"asset_id": "G1"}],
        "page_plan": {"gallery": ["G1"], "enhanced_content": [], "other_required_regions": []},
        "page_visual_system": {"asset_directions": [{"asset_id": "G1"}]},
    }
    ledger = {
        "assets": {"G1": {"status": "USER_APPROVED", "selected_candidate_id": "G1-v2", "current_output_ref": "file:g1-v2"}},
        "set_qa": {"status": "CLEAR", "reviewed_asset_ids": ["G1"], "reviewed_output_refs": {"G1": "file:g1-v2"}, "visual_review_ref": "set-review:final"},
    }
    freeze = build_production_freeze(handoff, ledger)
    assert freeze["approved_outputs"] == {"G1": {"candidate_id": "G1-v2", "output_ref": "file:g1-v2"}}, freeze
    assert freeze["ready_for_hardening"] is True, freeze


def main() -> int:
    legacy_tests = [value for name, value in vars(legacy).items() if name.startswith("test_") and callable(value)]
    current_tests = [value for name, value in globals().items() if name.startswith("test_") and callable(value)]
    for test in legacy_tests + current_tests:
        test()
    print(f"PASS: {len(legacy_tests) + len(current_tests)} global-production tests (v0.3.3)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
