#!/usr/bin/env python3
"""Global v0.3.3 evidence reconciliation with PROOF_VISUAL claim/source binding."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

from fingerprint_assets import fingerprint_packet, validate_audit_packet

HERE = Path(__file__).resolve().parent
LEGACY_PATH = HERE / "reconcile_evidence_legacy.py"
SPEC = importlib.util.spec_from_file_location("global_listing_reconcile_legacy", LEGACY_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load legacy reconciler: {LEGACY_PATH}")
_legacy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(_legacy)

FINAL_USABLE = {"VERIFIED", "HUMAN_APPROVED"}


def _trusted_review(entry: dict[str, Any], independent_semantic: bool) -> bool:
    source = entry.get("review_source")
    return source == "human" or (source == "independent_context" and independent_semantic)


def _claim_ids(asset: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for binding in asset.get("claim_bindings", []):
        if isinstance(binding, dict) and isinstance(binding.get("claim_id"), str) and binding.get("claim_id"):
            result.add(binding["claim_id"])
    return result


def _apply_proof_visual_claim_review(
    packet: dict[str, Any],
    semantic_review: dict[str, Any] | None,
    independent_semantic: bool,
    result: dict[str, Any],
) -> None:
    semantic_assets = ((semantic_review or {}).get("assets") or {}) if isinstance(semantic_review, dict) else {}
    packet_assets = {row.get("asset_id"): row for row in packet.get("assets", []) if isinstance(row, dict)}
    for asset_id, asset in packet_assets.items():
        if asset.get("evidence_mode", "SOURCE_FAITHFUL") != "PROOF_VISUAL":
            continue
        output = result.get("assets", {}).get(asset_id)
        if not isinstance(output, dict):
            continue
        entry = semantic_assets.get(asset_id)
        if not isinstance(entry, dict) or not _trusted_review(entry, independent_semantic):
            output["claim_binding_status"] = "NOT_TRUSTED_REVIEW"
            if output.get("effective_status") in FINAL_USABLE:
                output["effective_status"] = "HUMAN_REVIEW_REQUIRED"
            continue
        expected = _claim_ids(asset)
        reviewed = entry.get("reviewed_claim_ids")
        reviewed_set = set(reviewed) if isinstance(reviewed, list) and all(isinstance(x, str) for x in reviewed) else set()
        claim_status = entry.get("claim_status")
        if claim_status == "CLAIM_MISMATCH":
            output["claim_binding_status"] = "CLAIM_MISMATCH"
            output["effective_status"] = "INVALIDATED"
        elif claim_status == "CLAIM_MATCH" and expected and reviewed_set == expected:
            output["claim_binding_status"] = "CLAIM_MATCH"
        else:
            output["claim_binding_status"] = "CLAIM_UNVERIFIED"
            if output.get("effective_status") in FINAL_USABLE:
                output["effective_status"] = "HUMAN_REVIEW_REQUIRED"


def _recompute_asset_set_gate(packet: dict[str, Any], result: dict[str, Any]) -> None:
    errors: list[str] = []
    assets = result.get("assets", {})
    for slot in packet.get("slots", []):
        if not isinstance(slot, dict):
            continue
        slot_id = slot.get("slot_id", "<slot>")
        for asset_id in slot.get("required_asset_ids", []):
            row = assets.get(asset_id) if isinstance(assets, dict) else None
            if not isinstance(row, dict):
                errors.append(f"{slot_id}: required asset {asset_id} missing from audit")
            elif row.get("effective_status") not in FINAL_USABLE:
                errors.append(f"{slot_id}: required asset {asset_id} status {row.get('effective_status')} is not final-consumable")
            elif slot_id not in row.get("allowed_slots", []):
                errors.append(f"{slot_id}: required asset {asset_id} is not approved for this slot scope")
    result["asset_set_gate"] = {
        "status": "FAIL" if errors else ("PASS" if packet.get("slots") else "N/A"),
        "messages": errors,
    }


def reconcile_evidence(
    packet: dict[str, Any],
    fingerprints_payload: dict[str, Any],
    semantic_review: dict[str, Any] | None,
    independent_semantic: bool,
) -> dict[str, Any]:
    validate_audit_packet(packet)
    result = _legacy.reconcile_evidence(packet, fingerprints_payload, semantic_review, independent_semantic)
    _apply_proof_visual_claim_review(packet, semantic_review, independent_semantic, result)
    _recompute_asset_set_gate(packet, result)
    return result


def reconcile_from_files(
    packet: dict[str, Any],
    project_root: Path,
    semantic_review: dict[str, Any] | None = None,
    independent_semantic: bool = False,
) -> dict[str, Any]:
    fingerprints = fingerprint_packet(packet, project_root)
    return reconcile_evidence(packet, fingerprints, semantic_review, independent_semantic)


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"invalid {label}: root must be an object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile listing assets against real files, roles, approvals and proof claims")
    parser.add_argument("audit_input", type=Path)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--semantic-review", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        packet = _load_json(args.audit_input, "audit input")
        semantic_review = _load_json(args.semantic_review, "semantic review") if args.semantic_review else None
        result = reconcile_from_files(packet, args.project_root, semantic_review, independent_semantic=False)
    except ValueError as exc:
        print(f"FAIL: {exc}")
        return 1
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if result["asset_set_gate"]["status"] in {"PASS", "N/A"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
