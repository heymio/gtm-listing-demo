#!/usr/bin/env python3
"""Global listing-hardening regressions including v0.3.3 fail-closed gates."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
LEGACY = SCRIPT_DIR / "selftest_hardening_legacy.py"
SPEC = importlib.util.spec_from_file_location("global_hardening_legacy_tests", LEGACY)
assert SPEC and SPEC.loader
legacy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(legacy)

import validate_delivery_state as validator  # noqa: E402

_original_minimal_state = legacy.minimal_state


def _valid_frontend(state: dict) -> dict:
    value = {
        "mode": "CONTENT_REVIEW",
        "evidence_refs": ["frontend-ref:generic"],
        "shell_supported": None,
        "section_order_supported": None,
        "regions_distinguished": None,
        "desktop_structure_known": None,
        "mobile_behavior": None,
        "interactions_supported": None,
        "content_regions_verified": None,
        "unsupported_ui_fabricated": None,
        "content_review_labeled": True,
        "channel_native_claimed": False,
    }
    payload = validator._frontend_payload(value)
    approval_id = "AP-FRONTEND"
    state["approval_events"].append({
        "approval_id": approval_id,
        "actor": "user",
        "source_ref": "checkpoint:frontend",
        "scope": "frontend_fidelity",
        "stage": "8.5",
        "approved_hash": validator.canonical_hash(payload),
    })
    value["approval_id"] = approval_id
    return value


def _minimal_state_v033() -> dict:
    state = _original_minimal_state()
    state["audit_checkpoints"] = {"pre_9_required": True}
    state["production_freeze"] = {
        "expected_assets": 1,
        "required_asset_ids": ["A01"],
        "user_approved_assets": ["A01"],
        "blocked_assets": [],
        "revision_pending": [],
        "approved_outputs": {"A01": {"candidate_id": "A01-v1", "output_ref": "file:a01"}},
        "set_qa_status": "CLEAR",
        "ready_for_hardening": True,
    }
    state["frontend_fidelity"] = _valid_frontend(state)
    state["demo"] = {"sha256": "d" * 64}
    state["demo_runtime_evidence"] = {
        "validator": "browser-runtime",
        "demo_sha256": "d" * 64,
        "network_requests": 0,
        "viewports": {
            "1440": {"horizontal_overflow": False, "broken_images": 0, "clipped_primary_elements": 0},
            "390": {"horizontal_overflow": False, "broken_images": 0, "clipped_primary_elements": 0},
        },
        "carousel": {"present": False, "next_verified": None, "prev_verified": None},
    }
    return state


# Public fixture used by cross-skill adversarial regressions.
minimal_state = _minimal_state_v033
legacy.minimal_state = _minimal_state_v033


def test_valid_v033_delivery_state_passes_all_mandatory_final_gates() -> None:
    result = validator.validate_state(_minimal_state_v033())
    assert result["overall_status"] == "PASS", result
    for gate in [
        "PRODUCTION_FREEZE_GATE", "PRE_DEMO_ASSET_GATE",
        "FRONTEND_FIDELITY_GATE", "DEMO_RUNTIME_GATE", "DELIVERY_PARITY_GATE",
    ]:
        assert result["gates"][gate]["status"] == "PASS", (gate, result["gates"][gate])


def test_missing_frontend_or_runtime_evidence_cannot_pass() -> None:
    for key, gate in [("frontend_fidelity", "FRONTEND_FIDELITY_GATE"), ("demo_runtime_evidence", "DEMO_RUNTIME_GATE")]:
        state = _minimal_state_v033()
        state.pop(key)
        result = validator.validate_state(state)
        assert result["gates"][gate]["status"] != "PASS", result
        assert result["overall_status"] != "PASS", result


def test_channel_native_frontend_requires_evidence_backed_capabilities() -> None:
    state = _minimal_state_v033()
    state["frontend_fidelity"] = {
        "mode": "CHANNEL_NATIVE",
        "evidence_refs": ["frontend-ref:native"],
        "shell_supported": False,
        "section_order_supported": True,
        "regions_distinguished": True,
        "desktop_structure_known": True,
        "mobile_behavior": "KNOWN",
        "interactions_supported": True,
        "content_regions_verified": True,
        "unsupported_ui_fabricated": False,
        "approval_id": "AP-FRONTEND",
    }
    result = validator.validate_state(state)
    assert result["gates"]["FRONTEND_FIDELITY_GATE"]["status"] == "FAIL", result


def test_runtime_carousel_requires_actual_both_directions() -> None:
    state = _minimal_state_v033()
    state["demo_runtime_evidence"]["carousel"] = {"present": True, "next_verified": True, "prev_verified": False}
    result = validator.validate_state(state)
    assert result["gates"]["DEMO_RUNTIME_GATE"]["status"] == "FAIL", result


def main() -> int:
    skip = {"test_frontend_fidelity_blocks_native_claim_without_reference"}
    legacy_tests = [
        value for name, value in vars(legacy).items()
        if name.startswith("test_") and callable(value) and name not in skip
    ]
    current_tests = [value for name, value in globals().items() if name.startswith("test_") and callable(value)]
    for test in legacy_tests + current_tests:
        test()
    print(f"PASS: {len(legacy_tests) + len(current_tests)} global-hardening tests (v0.3.3)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
