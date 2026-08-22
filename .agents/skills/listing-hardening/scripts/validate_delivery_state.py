#!/usr/bin/env python3
"""Validate Global listing Delivery State with v0.3.3 fail-closed hard gates."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
CORE_PATH = SCRIPT_DIR / "_delivery_state_core.py"
SPEC = importlib.util.spec_from_file_location("global_delivery_state_core", CORE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load delivery validator core: {CORE_PATH}")
_core = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(_core)

canonical_hash = _core.canonical_hash
FINAL_EVIDENCE_STATUSES = _core.FINAL_EVIDENCE_STATUSES
HEX64 = re.compile(r"^[0-9a-f]{64}$")

GATE_NAMES = [
    "SCHEMA_GATE",
    "CHANNEL_MODULE_BUDGET_GATE",
    "APPROVAL_PROVENANCE_GATE",
    "MODULE_ORIGIN_GATE",
    "TRANSFORM_AUTH_GATE",
    "ASSET_SLOT_GATE",
    "PRODUCTION_FREEZE_GATE",
    "EVIDENCE_RECONCILIATION_GATE",
    "PRE_DEMO_ASSET_GATE",
    "FRONTEND_FIDELITY_GATE",
    "DEMO_RUNTIME_GATE",
    "DELIVERY_PARITY_GATE",
]


def _gate(status: str, messages: list[str] | None = None) -> dict[str, Any]:
    return {"status": status, "messages": messages or []}


def _schema(state: Any) -> tuple[list[str], dict[str, Any]]:
    errors, indexes = _core._schema(state)
    if not isinstance(state, dict):
        return errors, indexes
    for key in ["frontend_fidelity", "demo", "demo_runtime_evidence"]:
        value = state.get(key)
        if value is not None and not isinstance(value, dict):
            errors.append(f"{key} must be an object when present")
    required = state.get("required_asset_ids")
    if required is not None:
        if not isinstance(required, list) or any(not isinstance(x, str) or not x for x in required):
            errors.append("required_asset_ids must be a list of Asset IDs when present")
        elif len(required) != len(set(required)):
            errors.append("required_asset_ids must not contain duplicates")
    return errors, indexes


def _demo_required(state: dict[str, Any]) -> bool:
    return state.get("schema_version") == "0.2"


def _required_asset_ids(state: dict[str, Any], indexes: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for module in indexes.get("modules", {}).values():
        for asset_id in module.get("asset_ids", []):
            if isinstance(asset_id, str) and asset_id:
                result.add(asset_id)
    for slot in indexes.get("impl_slots", {}).values():
        for asset_id in slot.get("asset_ids", []):
            if isinstance(asset_id, str) and asset_id:
                result.add(asset_id)
    for contract in indexes.get("contracts", {}).values():
        for asset_id in contract.get("required_asset_ids", []):
            if isinstance(asset_id, str) and asset_id:
                result.add(asset_id)
    for asset_id in state.get("required_asset_ids", []):
        if isinstance(asset_id, str) and asset_id:
            result.add(asset_id)
    freeze = state.get("production_freeze") or {}
    if isinstance(freeze, dict):
        for key in ["blocked_assets", "revision_pending"]:
            values = freeze.get(key, [])
            if isinstance(values, list):
                for asset_id in values:
                    if isinstance(asset_id, str) and asset_id:
                        result.add(asset_id)
    return result


def _production_freeze_gate(state: dict[str, Any], indexes: dict[str, Any]) -> dict[str, Any]:
    if not _demo_required(state):
        return _gate("N/A", ["Production Freeze hard gate applies to Demo Delivery State 0.2"])
    errors: list[str] = []
    checkpoints = state.get("audit_checkpoints") or {}
    if not isinstance(checkpoints, dict) or checkpoints.get("pre_9_required") is not True:
        errors.append("pre_9_required cannot disable mandatory Demo hardening")

    required = _required_asset_ids(state, indexes)
    if not required:
        errors.append("Demo delivery requires a non-empty required asset set")

    freeze = state.get("production_freeze")
    if not isinstance(freeze, dict):
        return _gate("FAIL", errors + ["production_freeze missing before pre-Demo hardening"])

    expected = freeze.get("expected_assets")
    approved = freeze.get("user_approved_assets")
    blocked = freeze.get("blocked_assets")
    revision_pending = freeze.get("revision_pending")
    set_qa_status = freeze.get("set_qa_status")
    ready = freeze.get("ready_for_hardening")
    approved_outputs = freeze.get("approved_outputs")

    if not isinstance(expected, int) or isinstance(expected, bool) or expected < 1:
        errors.append("production_freeze expected_assets must be a positive integer")
    elif expected != len(required):
        errors.append(f"production_freeze expected_assets {expected} does not match required asset count {len(required)}")

    if not isinstance(approved, list) or any(not isinstance(asset_id, str) or not asset_id for asset_id in approved):
        errors.append("production_freeze user_approved_assets must be a list of Asset IDs")
        approved = []
    elif len(approved) != len(set(approved)):
        errors.append("production_freeze user_approved_assets must not contain duplicates")
    if set(approved) != required:
        missing = sorted(required - set(approved))
        unexpected = sorted(set(approved) - required)
        detail: list[str] = []
        if missing:
            detail.append("missing: " + ", ".join(missing))
        if unexpected:
            detail.append("unexpected: " + ", ".join(unexpected))
        errors.append("production_freeze approved Asset IDs must equal required set" + (f" ({'; '.join(detail)})" if detail else ""))

    if not isinstance(blocked, list):
        errors.append("production_freeze blocked_assets must be a list")
    elif blocked:
        errors.append("production_freeze contains blocked assets: " + ", ".join(str(x) for x in blocked))
    if not isinstance(revision_pending, list):
        errors.append("production_freeze revision_pending must be a list")
    elif revision_pending:
        errors.append("production_freeze contains revision-pending assets: " + ", ".join(str(x) for x in revision_pending))
    if set_qa_status not in {"CLEAR", "USER_ACCEPTED"}:
        errors.append(f"production_freeze set_qa_status must be CLEAR or USER_ACCEPTED, got {set_qa_status!r}")
    if ready is not True:
        errors.append("production_freeze ready_for_hardening must be true")

    if not isinstance(approved_outputs, dict):
        errors.append("production_freeze approved_outputs must map Asset ID to candidate_id/output_ref")
        approved_outputs = {}
    if set(approved_outputs) != required:
        errors.append("production_freeze approved_outputs keys must equal required asset set")
    seen_refs: set[str] = set()
    for asset_id in sorted(required):
        row = approved_outputs.get(asset_id)
        if not isinstance(row, dict):
            errors.append(f"approved_outputs[{asset_id}] must be an object")
            continue
        candidate_id = row.get("candidate_id")
        output_ref = row.get("output_ref")
        if not isinstance(candidate_id, str) or not candidate_id.strip():
            errors.append(f"approved_outputs[{asset_id}].candidate_id missing")
        if not isinstance(output_ref, str) or not output_ref.strip():
            errors.append(f"approved_outputs[{asset_id}].output_ref missing")
        elif output_ref in seen_refs:
            errors.append(f"duplicate output_ref without explicit reuse authorization: {output_ref}")
        else:
            seen_refs.add(output_ref)

    freeze_required = freeze.get("required_asset_ids")
    if freeze_required is not None and (not isinstance(freeze_required, list) or set(freeze_required) != required):
        errors.append("production_freeze required_asset_ids must equal recomputed required set")
    return _gate("FAIL" if errors else "PASS", errors)


def _asset_slot_gate(state: dict[str, Any], indexes: dict[str, Any]) -> dict[str, Any]:
    base = _core._asset_slot_gate(indexes)
    errors = list(base.get("messages", [])) if base.get("status") == "FAIL" else []
    required = _required_asset_ids(state, indexes)
    assets = set(indexes.get("assets", {}))
    missing = sorted(required - assets)
    if missing:
        errors.append("required assets missing from Delivery State assets: " + ", ".join(missing))

    contracts = set(indexes.get("contracts", {}))
    for slot_id, slot in indexes.get("impl_slots", {}).items():
        asset_ids = slot.get("asset_ids", [])
        if isinstance(asset_ids, list) and asset_ids and slot_id not in contracts:
            errors.append(f"{slot_id}: implemented asset-bearing slot has no asset-slot contract")
    if errors:
        return _gate("FAIL", errors)
    if required and not contracts:
        return _gate("FAIL", ["required assets exist but asset-slot contract is empty"])
    return base


def _pre_demo_gate(state: dict[str, Any], indexes: dict[str, Any]) -> dict[str, Any]:
    if not _demo_required(state):
        return _gate("N/A")
    errors: list[str] = []
    checkpoints = state.get("audit_checkpoints") or {}
    if not isinstance(checkpoints, dict) or checkpoints.get("pre_9_required") is not True:
        errors.append("pre_9_required cannot disable mandatory Demo evidence audit")
    required = _required_asset_ids(state, indexes)
    if not required:
        errors.append("Demo delivery requires a non-empty required asset set")

    evidence = state.get("auditor_evidence")
    if not isinstance(evidence, dict):
        return _gate("UNVERIFIED", errors + ["pre-Demo auditor evidence missing"])
    checkpoint = evidence.get("checkpoint")
    if checkpoint not in {"pre-demo", "pre-9"}:
        errors.append("auditor evidence checkpoint must be pre-demo/pre-9")
    if evidence.get("asset_set_gate", {}).get("status") != "PASS":
        errors.append("auditor asset_set_gate is not PASS")
    evidence_assets = evidence.get("assets")
    if not isinstance(evidence_assets, dict):
        errors.append("auditor assets mapping missing")
        evidence_assets = {}
    for asset_id in sorted(required):
        asset = indexes.get("assets", {}).get(asset_id, {})
        item = evidence_assets.get(asset_id)
        if not isinstance(item, dict):
            errors.append(f"required asset {asset_id} missing from auditor evidence")
            continue
        if item.get("physical_sha256") != asset.get("sha256"):
            errors.append(f"required asset {asset_id} auditor hash differs from locked asset hash")
        if item.get("effective_status") not in FINAL_EVIDENCE_STATUSES:
            errors.append(f"required asset {asset_id} evidence status is not final usable")
    return _gate("FAIL" if errors else "PASS", errors)


def _frontend_payload(value: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "mode", "evidence_refs", "shell_supported", "section_order_supported",
        "regions_distinguished", "desktop_structure_known", "mobile_behavior",
        "interactions_supported", "content_regions_verified", "unsupported_ui_fabricated",
        "content_review_labeled", "channel_native_claimed",
    ]
    return {key: value.get(key) for key in keys}


def _frontend_fidelity_gate(state: dict[str, Any], indexes: dict[str, Any]) -> dict[str, Any]:
    if not _demo_required(state):
        return _gate("N/A")
    value = state.get("frontend_fidelity")
    if not isinstance(value, dict):
        return _gate("UNVERIFIED", ["frontend_fidelity evidence missing"])
    mode = value.get("mode")
    refs = value.get("evidence_refs")
    errors: list[str] = []
    if not isinstance(refs, list) or not refs or any(not isinstance(ref, str) or not ref.strip() for ref in refs):
        errors.append("frontend_fidelity requires non-empty evidence_refs")
    if mode == "CHANNEL_NATIVE":
        for key in ["shell_supported", "section_order_supported", "regions_distinguished", "desktop_structure_known", "interactions_supported", "content_regions_verified"]:
            if value.get(key) is not True:
                errors.append(f"frontend_fidelity {key} must be true for CHANNEL_NATIVE")
        if value.get("mobile_behavior") not in {"KNOWN", "SCOPED_OUT"}:
            errors.append("frontend_fidelity mobile_behavior must be KNOWN or SCOPED_OUT")
        if value.get("unsupported_ui_fabricated") is not False:
            errors.append("frontend_fidelity unsupported_ui_fabricated must be false")
    elif mode == "CONTENT_REVIEW":
        if value.get("content_review_labeled") is not True:
            errors.append("CONTENT_REVIEW mode must be explicitly labeled")
        if value.get("channel_native_claimed") is True:
            errors.append("CONTENT_REVIEW mode cannot claim channel-native fidelity")
    else:
        errors.append("frontend_fidelity mode must be CHANNEL_NATIVE or CONTENT_REVIEW")

    approval_id = value.get("approval_id")
    approval = indexes.get("approvals", {}).get(approval_id) if isinstance(approval_id, str) else None
    expected_hash = canonical_hash(_frontend_payload(value))
    if not approval or approval.get("actor") != "user" or approval.get("scope") != "frontend_fidelity" or approval.get("approved_hash") != expected_hash:
        errors.append("frontend_fidelity lacks exact user approval provenance")
    return _gate("FAIL" if errors else "PASS", errors)


def _demo_runtime_gate(state: dict[str, Any]) -> dict[str, Any]:
    if not _demo_required(state):
        return _gate("N/A")
    demo = state.get("demo")
    evidence = state.get("demo_runtime_evidence")
    if not isinstance(demo, dict) or not isinstance(demo.get("sha256"), str) or not HEX64.fullmatch(demo.get("sha256", "")):
        return _gate("UNVERIFIED", ["Demo exact SHA-256 missing from Delivery State"])
    if not isinstance(evidence, dict):
        return _gate("UNVERIFIED", ["browser runtime evidence missing"])
    errors: list[str] = []
    if evidence.get("demo_sha256") != demo.get("sha256"):
        errors.append("runtime evidence demo_sha256 does not match exact Demo SHA-256")
    if evidence.get("validator") != "browser-runtime":
        errors.append("runtime evidence validator must be browser-runtime")
    if evidence.get("network_requests") != 0:
        errors.append("runtime Demo must make zero network requests")
    viewports = evidence.get("viewports")
    if not isinstance(viewports, dict):
        errors.append("runtime evidence viewports missing")
    else:
        for key in ["1440", "390"]:
            row = viewports.get(key)
            if not isinstance(row, dict):
                errors.append(f"runtime viewport {key}px missing")
                continue
            if row.get("horizontal_overflow") is not False:
                errors.append(f"runtime viewport {key}px has horizontal overflow or unknown state")
            if row.get("broken_images") != 0:
                errors.append(f"runtime viewport {key}px has broken images or unknown state")
            if row.get("clipped_primary_elements") != 0:
                errors.append(f"runtime viewport {key}px has clipped primary elements or unknown state")
    carousel = evidence.get("carousel")
    if isinstance(carousel, dict) and carousel.get("present") is True:
        if carousel.get("next_verified") is not True or carousel.get("prev_verified") is not True:
            errors.append("runtime carousel must verify both next and previous transitions")
    return _gate("FAIL" if errors else "PASS", errors)


def validate_state(state: Any) -> dict[str, Any]:
    errors, indexes = _schema(state)
    gates = {name: _gate("N/A") for name in GATE_NAMES}
    if errors:
        gates["SCHEMA_GATE"] = _gate("FAIL", errors)
        return {"overall_status": "FAIL", "gates": gates}
    assert isinstance(state, dict)
    gates["SCHEMA_GATE"] = _gate("PASS")
    gates["CHANNEL_MODULE_BUDGET_GATE"] = _core._channel_budget(state, indexes["modules"])
    gates["APPROVAL_PROVENANCE_GATE"] = _core._approval_gate(state, indexes)
    gates["MODULE_ORIGIN_GATE"] = _core._module_origin(state, indexes)
    gates["TRANSFORM_AUTH_GATE"] = _core._transform_gate(state, indexes)
    gates["ASSET_SLOT_GATE"] = _asset_slot_gate(state, indexes)
    gates["PRODUCTION_FREEZE_GATE"] = _production_freeze_gate(state, indexes)
    gates["EVIDENCE_RECONCILIATION_GATE"] = _core._early_evidence_gate(state)
    gates["PRE_DEMO_ASSET_GATE"] = _pre_demo_gate(state, indexes)
    gates["FRONTEND_FIDELITY_GATE"] = _frontend_fidelity_gate(state, indexes)
    gates["DEMO_RUNTIME_GATE"] = _demo_runtime_gate(state)
    gates["DELIVERY_PARITY_GATE"] = _core._delivery_parity(indexes)
    statuses = {gate["status"] for gate in gates.values()}
    overall = "FAIL" if "FAIL" in statuses else "UNVERIFIED" if "UNVERIFIED" in statuses else "PASS"
    return {"overall_status": overall, "gates": gates, "note": "Global v0.3.3 fail-closed hard verification"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Global listing Delivery State v0.3.3")
    parser.add_argument("state", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        state = json.loads(args.state.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"FAIL: invalid Delivery State: {exc}")
        return 1
    result = validate_state(state)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(result["overall_status"])
        for name, gate in result["gates"].items():
            print(f"{name}: {gate['status']}")
            for message in gate["messages"]:
                print(f"- {message}")
    return 0 if result["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
