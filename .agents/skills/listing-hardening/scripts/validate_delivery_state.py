#!/usr/bin/env python3
"""Validate generic listing Delivery State and compute hardening gates."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

FINAL_EVIDENCE_STATUSES = {"VERIFIED", "HUMAN_APPROVED"}
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
    "DELIVERY_PARITY_GATE",
]


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _gate(status: str, messages: list[str] | None = None) -> dict[str, Any]:
    return {"status": status, "messages": messages or []}


def _asset_payload(asset: dict[str, Any]) -> dict[str, Any]:
    return {key: asset.get(key) for key in ["asset_id", "canonical_source", "sha256", "role", "page_offer_scope", "allowed_slots"]}


def _unique_dict(items: Any, key: str, label: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    if not isinstance(items, list):
        errors.append(f"{label} must be a list")
        return result
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{label}[{index}] must be an object")
            continue
        value = item.get(key)
        if not isinstance(value, str) or not value:
            errors.append(f"{label}[{index}].{key} must be a non-empty string")
            continue
        if value in result:
            errors.append(f"duplicate {label}.{key}: {value}")
            continue
        result[value] = item
    return result


def _schema(state: Any) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    indexes: dict[str, Any] = {}
    if not isinstance(state, dict):
        return ["Delivery State root must be an object"], indexes
    if state.get("schema_version") != "0.2":
        errors.append("schema_version must be 0.2")
    channel = state.get("channel")
    if not isinstance(channel, dict):
        errors.append("channel must be an object")
    elif not isinstance(channel.get("id"), str) or not channel.get("id"):
        errors.append("channel.id must be a non-empty string")
    indexes["assets"] = _unique_dict(state.get("assets"), "asset_id", "assets", errors)
    indexes["approvals"] = _unique_dict(state.get("approval_events"), "approval_id", "approval_events", errors)
    indexes["contracts"] = _unique_dict(state.get("asset_slot_contract"), "slot_id", "asset_slot_contract", errors)

    locked = state.get("locked_module_plan")
    if not isinstance(locked, dict):
        errors.append("locked_module_plan must be an object")
        modules: Any = []
    else:
        modules = locked.get("modules")
    indexes["modules"] = _unique_dict(modules, "module_id", "locked_module_plan.modules", errors)

    implementation = state.get("implementation")
    if not isinstance(implementation, dict):
        errors.append("implementation must be an object")
        impl_slots: Any = []
    else:
        impl_slots = implementation.get("slots")
    indexes["impl_slots"] = _unique_dict(impl_slots, "slot_id", "implementation.slots", errors)
    if isinstance(impl_slots, list):
        seen_module_ids: set[str] = set()
        for index, item in enumerate(impl_slots):
            if not isinstance(item, dict):
                continue
            module_id = item.get("module_id")
            if not isinstance(module_id, str) or not module_id:
                errors.append(f"implementation.slots[{index}].module_id must be a non-empty string")
            elif module_id in seen_module_ids:
                errors.append(f"duplicate implementation.slots.module_id: {module_id}")
            else:
                seen_module_ids.add(module_id)

    freeze = state.get("production_freeze")
    if not isinstance(freeze, dict):
        errors.append("production_freeze must be an object")
    audit = state.get("audit_checkpoints", {})
    if audit is not None and not isinstance(audit, dict):
        errors.append("audit_checkpoints must be an object")
    return errors, indexes


def _channel_budget(state: dict[str, Any], modules: dict[str, Any]) -> dict[str, Any]:
    channel = state.get("channel", {})
    capabilities = channel.get("capabilities") if isinstance(channel, dict) else None
    max_modules = capabilities.get("declared_max_modules") if isinstance(capabilities, dict) else None
    if not isinstance(max_modules, int) or isinstance(max_modules, bool) or max_modules < 0:
        return _gate("UNVERIFIED", ["current channel/account declared_max_modules is not verified"])
    if len(modules) > max_modules:
        return _gate("FAIL", [f"locked plan has {len(modules)} modules, exceeding declared maximum {max_modules}"])
    return _gate("PASS")


def _approval_gate(state: dict[str, Any], indexes: dict[str, Any]) -> dict[str, Any]:
    messages: list[str] = []
    approvals = indexes["approvals"]
    for asset_id, asset in indexes["assets"].items():
        if asset.get("status") != "LOCKED":
            continue
        approval_id = asset.get("approval_id")
        event = approvals.get(approval_id) if isinstance(approval_id, str) else None
        expected_hash = canonical_hash(_asset_payload(asset))
        if not event or event.get("actor") != "user" or event.get("scope") != f"asset_lock:{asset_id}" or event.get("approved_hash") != expected_hash:
            messages.append(f"asset {asset_id} lacks exact user approval provenance")
    locked = state.get("locked_module_plan", {})
    approval_id = locked.get("approval_id") if isinstance(locked, dict) else None
    event = approvals.get(approval_id) if isinstance(approval_id, str) else None
    modules = locked.get("modules", []) if isinstance(locked, dict) else []
    expected_plan_hash = canonical_hash({"modules": modules})
    if not event or event.get("actor") != "user" or event.get("scope") != "module_plan" or event.get("approved_hash") != expected_plan_hash:
        messages.append("locked module plan lacks exact user approval provenance")
    return _gate("FAIL" if messages else "PASS", messages)


def _module_origin(state: dict[str, Any], indexes: dict[str, Any]) -> dict[str, Any]:
    messages: list[str] = []
    locked = state.get("locked_module_plan", {})
    modules = locked.get("modules", []) if isinstance(locked, dict) else []
    expected_hash = canonical_hash({"modules": modules})
    if locked.get("plan_hash") != expected_hash:
        messages.append("locked module plan hash does not match canonical modules")
    implementation = state.get("implementation", {})
    if implementation.get("plan_hash") != expected_hash:
        messages.append("implementation plan_hash differs from locked plan")
    for slot in indexes["impl_slots"].values():
        module_id = slot.get("module_id")
        module = indexes["modules"].get(module_id)
        if not module:
            messages.append(f"implementation slot references unknown module {module_id}")
            continue
        for key in ["native_type", "interaction"]:
            if slot.get(key) != module.get(key):
                messages.append(f"module {module_id} {key} drifted from locked plan")
    return _gate("FAIL" if messages else "PASS", messages)


def _transform_gate(state: dict[str, Any], indexes: dict[str, Any]) -> dict[str, Any]:
    messages: list[str] = []
    approvals = indexes["approvals"]
    for asset_id, asset in indexes["assets"].items():
        transform = asset.get("transform")
        if transform is None:
            continue
        if not isinstance(transform, dict):
            messages.append(f"asset {asset_id} transform must be an object")
            continue
        approval_id = transform.get("approval_id")
        event = approvals.get(approval_id) if isinstance(approval_id, str) else None
        if not event or event.get("actor") != "user" or event.get("scope") != f"transform:{asset_id}":
            messages.append(f"asset {asset_id} transform lacks explicit authorization")
    return _gate("FAIL" if messages else "PASS", messages)


def _asset_slot_gate(indexes: dict[str, Any]) -> dict[str, Any]:
    messages: list[str] = []
    assets, impl = indexes["assets"], indexes["impl_slots"]
    for slot_id, contract in indexes["contracts"].items():
        impl_slot = impl.get(slot_id)
        if not impl_slot:
            messages.append(f"required slot {slot_id} missing from implementation")
            continue
        if contract.get("module_id") != impl_slot.get("module_id"):
            messages.append(f"slot {slot_id} module_id mismatch")
        required = contract.get("required_asset_ids", [])
        if not isinstance(required, list):
            messages.append(f"slot {slot_id} required_asset_ids must be a list")
            continue
        impl_assets = impl_slot.get("asset_ids", [])
        for asset_id in required:
            asset = assets.get(asset_id)
            if not asset:
                messages.append(f"slot {slot_id} missing required asset {asset_id}")
                continue
            if slot_id not in asset.get("allowed_slots", []):
                messages.append(f"asset {asset_id} is not allowed in slot {slot_id}")
            if asset_id not in impl_assets:
                messages.append(f"implementation slot {slot_id} does not use required asset {asset_id}")
    return _gate("FAIL" if messages else "PASS", messages)


def _required_asset_ids(indexes: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for contract in indexes["contracts"].values():
        values = contract.get("required_asset_ids", [])
        if isinstance(values, list):
            result.update(value for value in values if isinstance(value, str) and value)
    return result


def _production_freeze(state: dict[str, Any], indexes: dict[str, Any]) -> dict[str, Any]:
    freeze = state.get("production_freeze", {})
    required = _required_asset_ids(indexes)
    messages: list[str] = []
    expected = freeze.get("expected_assets")
    approved = freeze.get("user_approved_assets")
    refs = freeze.get("approved_output_refs")
    if not isinstance(expected, int) or isinstance(expected, bool) or expected != len(required):
        messages.append(f"production freeze expected_assets must equal required asset count {len(required)}")
    if not isinstance(approved, list) or len(approved) != len(set(approved)) or set(approved) != required:
        messages.append("production freeze user_approved_assets must equal the exact required asset ID set")
    if not isinstance(refs, list) or len(refs) != len(required) or any(not isinstance(ref, str) or not ref for ref in refs):
        messages.append("production freeze approved_output_refs must contain one non-empty ref per required asset")
    return _gate("FAIL" if messages else "PASS", messages)


def _early_evidence_gate(state: dict[str, Any]) -> dict[str, Any]:
    checkpoints = state.get("audit_checkpoints", {})
    if not isinstance(checkpoints, dict) or checkpoints.get("post_6_5_required") is not True:
        return _gate("N/A")
    evidence = state.get("post_6_5_auditor_evidence")
    if not isinstance(evidence, dict) or evidence.get("asset_set_gate", {}).get("status") != "PASS":
        return _gate("UNVERIFIED", ["targeted inherited/reused asset evidence is not verified"])
    return _gate("PASS")


def _pre_demo_gate(state: dict[str, Any], indexes: dict[str, Any]) -> dict[str, Any]:
    checkpoints = state.get("audit_checkpoints", {})
    if not isinstance(checkpoints, dict) or checkpoints.get("pre_9_required") is not True:
        return _gate("N/A")
    evidence = state.get("auditor_evidence")
    if not isinstance(evidence, dict):
        return _gate("UNVERIFIED", ["pre-Demo auditor evidence missing"])
    messages: list[str] = []
    if evidence.get("asset_set_gate", {}).get("status") != "PASS":
        messages.append("auditor asset_set_gate is not PASS")
    evidence_assets = evidence.get("assets", {})
    if not isinstance(evidence_assets, dict):
        messages.append("auditor assets mapping missing")
        evidence_assets = {}
    for asset_id in _required_asset_ids(indexes):
        asset = indexes["assets"].get(asset_id, {})
        item = evidence_assets.get(asset_id)
        if not isinstance(item, dict):
            messages.append(f"required asset {asset_id} missing from auditor evidence")
            continue
        if item.get("physical_sha256") != asset.get("sha256"):
            messages.append(f"required asset {asset_id} auditor hash differs from locked asset hash")
        if item.get("effective_status") not in FINAL_EVIDENCE_STATUSES:
            messages.append(f"required asset {asset_id} evidence status is not final usable")
    return _gate("FAIL" if messages else "PASS", messages)


def _frontend_gate(state: dict[str, Any]) -> dict[str, Any]:
    fidelity = state.get("frontend_fidelity")
    if not isinstance(fidelity, dict) or fidelity.get("required") is not True:
        return _gate("N/A")
    if fidelity.get("status") == "PASS" and isinstance(fidelity.get("reference_ref"), str) and fidelity.get("reference_ref"):
        return _gate("PASS")
    if fidelity.get("status") == "FAIL":
        return _gate("FAIL", ["current frontend reference does not support native fidelity"])
    return _gate("UNVERIFIED", ["current frontend visual reference is missing or unverified; use Content Review Demo"])


def _delivery_parity(indexes: dict[str, Any]) -> dict[str, Any]:
    messages: list[str] = []
    modules = indexes["modules"]
    impl_by_module = {slot.get("module_id"): slot for slot in indexes["impl_slots"].values() if isinstance(slot.get("module_id"), str)}
    if set(impl_by_module) != set(modules):
        messages.append("implementation module set differs from locked module plan")
    for module_id, module in modules.items():
        slot = impl_by_module.get(module_id)
        if not slot:
            continue
        for key in ["native_type", "interaction"]:
            if slot.get(key) != module.get(key):
                messages.append(f"module {module_id} {key} differs at delivery")
        if sorted(slot.get("asset_ids", [])) != sorted(module.get("asset_ids", [])):
            messages.append(f"module {module_id} asset set differs at delivery")
    return _gate("FAIL" if messages else "PASS", messages)


def validate_state(state: Any) -> dict[str, Any]:
    errors, indexes = _schema(state)
    gates = {name: _gate("N/A") for name in GATE_NAMES}
    if errors:
        gates["SCHEMA_GATE"] = _gate("FAIL", errors)
        return {"overall_status": "FAIL", "gates": gates}
    assert isinstance(state, dict)
    gates["SCHEMA_GATE"] = _gate("PASS")
    gates["CHANNEL_MODULE_BUDGET_GATE"] = _channel_budget(state, indexes["modules"])
    gates["APPROVAL_PROVENANCE_GATE"] = _approval_gate(state, indexes)
    gates["MODULE_ORIGIN_GATE"] = _module_origin(state, indexes)
    gates["TRANSFORM_AUTH_GATE"] = _transform_gate(state, indexes)
    gates["ASSET_SLOT_GATE"] = _asset_slot_gate(indexes)
    gates["PRODUCTION_FREEZE_GATE"] = _production_freeze(state, indexes)
    gates["EVIDENCE_RECONCILIATION_GATE"] = _early_evidence_gate(state)
    gates["PRE_DEMO_ASSET_GATE"] = _pre_demo_gate(state, indexes)
    gates["FRONTEND_FIDELITY_GATE"] = _frontend_gate(state)
    gates["DELIVERY_PARITY_GATE"] = _delivery_parity(indexes)
    statuses = {gate["status"] for gate in gates.values()}
    overall = "FAIL" if "FAIL" in statuses else "UNVERIFIED" if "UNVERIFIED" in statuses else "PASS"
    return {"overall_status": overall, "gates": gates}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate global listing Delivery State")
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
