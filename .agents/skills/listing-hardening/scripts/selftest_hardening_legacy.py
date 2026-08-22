#!/usr/bin/env python3
"""Regression tests for generic listing hardening."""

from __future__ import annotations

import importlib.util
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_DIR / "scripts" / "validate_delivery_state.py"


def load_validator():
    assert VALIDATOR.is_file(), "validate_delivery_state.py must exist"
    spec = importlib.util.spec_from_file_location("global_hardening_validator", VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def minimal_state() -> dict:
    validator = load_validator()
    asset_payload = {
        "asset_id": "A01",
        "canonical_source": "assets/a01.png",
        "sha256": "a" * 64,
        "role": "enhanced-content",
        "page_offer_scope": ["single"],
        "allowed_slots": ["M01"],
    }
    asset_hash = validator.canonical_hash(asset_payload)
    module = {
        "module_id": "M01",
        "native_type": "full-image",
        "interaction": "static",
        "asset_ids": ["A01"],
        "approved_stage": "7",
    }
    plan_hash = validator.canonical_hash({"modules": [module]})
    return {
        "schema_version": "0.2",
        "channel": {
            "id": "marketplace-example",
            "capabilities": {"declared_max_modules": 5},
        },
        "approval_events": [
            {"approval_id": "AP-ASSET", "actor": "user", "source_ref": "checkpoint:asset", "scope": "asset_lock:A01", "stage": "8", "approved_hash": asset_hash},
            {"approval_id": "AP-PLAN", "actor": "user", "source_ref": "checkpoint:plan", "scope": "module_plan", "stage": "7", "approved_hash": plan_hash},
        ],
        "assets": [{**asset_payload, "status": "LOCKED", "approval_id": "AP-ASSET"}],
        "locked_module_plan": {"status": "LOCKED", "approval_id": "AP-PLAN", "plan_hash": plan_hash, "modules": [module]},
        "asset_slot_contract": [{"slot_id": "M01", "module_id": "M01", "required_asset_ids": ["A01"], "interaction": "static"}],
        "implementation": {"plan_hash": plan_hash, "slots": [{"slot_id": "M01", "module_id": "M01", "native_type": "full-image", "interaction": "static", "asset_ids": ["A01"]}]},
        "audit_checkpoints": {"pre_9_required": True},
        "production_freeze": {"expected_assets": 1, "user_approved_assets": ["A01"], "approved_output_refs": ["file:a01"]},
        "auditor_evidence": {
            "checkpoint": "pre-demo",
            "independent_semantic": True,
            "asset_set_gate": {"status": "PASS", "messages": []},
            "assets": {"A01": {"physical_sha256": "a" * 64, "effective_status": "VERIFIED"}},
        },
        "frontend_fidelity": {"required": False, "status": "N/A", "reference_ref": None},
    }


def test_hardening_files_and_contract_exist() -> None:
    required = [
        SKILL_DIR / "SKILL.md",
        VALIDATOR,
        SKILL_DIR / "references" / "asset-integrity.md",
        SKILL_DIR / "references" / "executable-gates.md",
        SKILL_DIR / "references" / "frontend-fidelity.md",
        SKILL_DIR / "references" / "final-qa.md",
        SKILL_DIR / "references" / "demo-output.md",
    ]
    missing = [str(path.relative_to(SKILL_DIR)) for path in required if not path.is_file()]
    assert missing == [], missing


def test_valid_generic_delivery_state_passes_core_gates() -> None:
    validator = load_validator()
    result = validator.validate_state(minimal_state())
    assert result["gates"]["SCHEMA_GATE"]["status"] == "PASS"
    for gate in [
        "CHANNEL_MODULE_BUDGET_GATE",
        "APPROVAL_PROVENANCE_GATE",
        "MODULE_ORIGIN_GATE",
        "ASSET_SLOT_GATE",
        "PRODUCTION_FREEZE_GATE",
        "PRE_DEMO_ASSET_GATE",
        "DELIVERY_PARITY_GATE",
    ]:
        assert result["gates"][gate]["status"] == "PASS", (gate, result["gates"][gate])


def test_channel_budget_uses_declared_current_capability_not_site_hardcode() -> None:
    validator = load_validator()
    state = minimal_state()
    state["channel"]["id"] = "retailer-custom"
    state["channel"]["capabilities"]["declared_max_modules"] = 0
    result = validator.validate_state(state)
    assert result["gates"]["CHANNEL_MODULE_BUDGET_GATE"]["status"] == "FAIL"


def test_production_freeze_requires_exact_required_asset_ids() -> None:
    validator = load_validator()
    state = minimal_state()
    state["production_freeze"]["user_approved_assets"] = ["WRONG"]
    result = validator.validate_state(state)
    assert result["gates"]["PRODUCTION_FREEZE_GATE"]["status"] == "FAIL"


def test_pre_demo_gate_requires_current_exact_hash_evidence() -> None:
    validator = load_validator()
    state = minimal_state()
    state["auditor_evidence"]["assets"]["A01"]["physical_sha256"] = "b" * 64
    result = validator.validate_state(state)
    assert result["gates"]["PRE_DEMO_ASSET_GATE"]["status"] == "FAIL"


def test_module_origin_and_delivery_parity_reject_implementation_drift() -> None:
    validator = load_validator()
    state = minimal_state()
    state["implementation"]["slots"][0]["native_type"] = "carousel"
    result = validator.validate_state(state)
    assert result["gates"]["MODULE_ORIGIN_GATE"]["status"] == "FAIL" or result["gates"]["DELIVERY_PARITY_GATE"]["status"] == "FAIL"


def test_frontend_fidelity_blocks_native_claim_without_reference() -> None:
    validator = load_validator()
    state = minimal_state()
    state["frontend_fidelity"] = {"required": True, "status": "UNVERIFIED", "reference_ref": None}
    result = validator.validate_state(state)
    assert result["gates"]["FRONTEND_FIDELITY_GATE"]["status"] == "UNVERIFIED"


def test_malformed_or_duplicate_state_fails_schema_without_throwing() -> None:
    validator = load_validator()
    malformed = {"schema_version": "0.2", "channel": [], "assets": "bad", "approval_events": {}}
    result = validator.validate_state(malformed)
    assert result["gates"]["SCHEMA_GATE"]["status"] == "FAIL"
    state = minimal_state()
    state["assets"].append(dict(state["assets"][0]))
    result = validator.validate_state(state)
    assert result["gates"]["SCHEMA_GATE"]["status"] == "FAIL"
    assert any("duplicate" in m.casefold() for m in result["gates"]["SCHEMA_GATE"]["messages"])


def test_hardening_core_has_no_marketplace_specific_defaults() -> None:
    paths = [SKILL_DIR / "SKILL.md"] + sorted((SKILL_DIR / "references").glob("*.md"))
    joined = "\n".join(path.read_text(encoding="utf-8") for path in paths if path.is_file()).casefold()
    for forbidden in ["amazon.co.jp", "switchbot", "light bars", "s30 mini"]:
        assert forbidden not in joined


def main() -> int:
    tests = [value for name, value in globals().items() if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"PASS: {len(tests)} global-hardening tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
