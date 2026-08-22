#!/usr/bin/env python3
"""Reconcile candidate asset claims against real-file, approval and semantic evidence."""

from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any
from fingerprint_assets import fingerprint_packet, validate_audit_packet

FINAL_USABLE = {"VERIFIED", "HUMAN_APPROVED"}
SUPPORTED_IMAGE_FAMILIES = {"png", "jpeg", "webp"}


def _index(items: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    result = {}
    for item in items:
        value = item.get(key)
        if isinstance(value, str) and value: result[value] = item
    return result


def _expected_role(packet: dict[str, Any], asset: dict[str, Any]) -> str | None:
    asset_id = asset.get("asset_id")
    for entry in packet.get("expected_visual_roles", []):
        if entry.get("asset_id") == asset_id:
            role = entry.get("role")
            if isinstance(role, str) and role: return role
    role = asset.get("claimed_role"); return role if isinstance(role, str) and role else None


def _semantic_result(asset_id: str, expected_role: str | None, semantic_review: dict[str, Any] | None, independent_semantic: bool) -> dict[str, Any]:
    entry = ((semantic_review or {}).get("assets") or {}).get(asset_id)
    if not isinstance(entry, dict): return {"semantic_role_status":"NOT_VISUALLY_AUDITED","actual_role":None,"review_source":None}
    source = entry.get("review_source"); actual_role = entry.get("actual_role"); supplied_status = entry.get("role_status")
    trusted_source = source == "human" or (source == "independent_context" and independent_semantic)
    if not trusted_source: return {"semantic_role_status":"ROLE_AMBIGUOUS","actual_role":actual_role,"review_source":source}
    if supplied_status in {"ROLE_AMBIGUOUS","NOT_VISUALLY_AUDITED"}: status = supplied_status
    elif expected_role and actual_role == expected_role: status = "ROLE_MATCH"
    elif expected_role and actual_role != expected_role: status = "ROLE_MISMATCH"
    else: status = "ROLE_AMBIGUOUS"
    return {"semantic_role_status":status,"actual_role":actual_role,"review_source":source}


def _approval_matches(event, asset, fingerprint, expected_role, semantic) -> bool:
    if not event or event.get("type") != "explicit_user_approval": return False
    if event.get("asset_id") != asset.get("asset_id") or event.get("sha256") != fingerprint.get("sha256"): return False
    approved_role = event.get("approved_role")
    if approved_role != expected_role or semantic.get("semantic_role_status") != "ROLE_MATCH" or semantic.get("actual_role") != approved_role: return False
    return sorted(event.get("approved_slots", [])) == sorted(asset.get("allowed_slots", []))


def _exact_recovery(prior, asset, fingerprint, expected_role) -> bool:
    return bool(prior) and prior.get("sha256") == fingerprint.get("sha256") and prior.get("approved_role") == expected_role and sorted(prior.get("approved_slots", [])) == sorted(asset.get("allowed_slots", []))


def _physical_ok(fingerprint: dict[str, Any]) -> bool:
    family=fingerprint.get("signature_family"); extension=fingerprint.get("extension_family"); width=fingerprint.get("width"); height=fingerprint.get("height"); byte_size=fingerprint.get("byte_size")
    return fingerprint.get("exists") is True and fingerprint.get("path_allowed") is True and isinstance(fingerprint.get("sha256"),str) and len(fingerprint.get("sha256", ""))==64 and isinstance(byte_size,int) and not isinstance(byte_size,bool) and byte_size>0 and family in SUPPORTED_IMAGE_FAMILIES and extension==family and isinstance(width,int) and not isinstance(width,bool) and width>0 and isinstance(height,int) and not isinstance(height,bool) and height>0 and not fingerprint.get("errors")


def _provenance(asset, fingerprint, prior, fingerprints, approvals, expected_role) -> str:
    if not _physical_ok(fingerprint): return "PROVENANCE_CONFLICT"
    if _exact_recovery(prior, asset, fingerprint, expected_role): return "EXACT_RECOVERY_VERIFIED"
    parent_id=asset.get("claimed_parent_asset_id"); transform=asset.get("claimed_transform")
    if parent_id or transform:
        if not isinstance(parent_id,str) or parent_id not in fingerprints: return "PROVENANCE_CONFLICT"
        parent_fp=fingerprints.get(parent_id) or {}
        if not _physical_ok(parent_fp): return "PROVENANCE_CONFLICT"
        if not isinstance(transform,dict): return "PROVENANCE_UNKNOWN"
        approval_id=transform.get("approval_event_id"); event=approvals.get(approval_id) if isinstance(approval_id,str) else None
        if not event or event.get("type") != "explicit_user_approval": return "PROVENANCE_UNKNOWN"
        if event.get("asset_id") != asset.get("asset_id") or event.get("sha256") != fingerprint.get("sha256"): return "PROVENANCE_CONFLICT"
        return "DERIVATIVE_VERIFIED"
    return "ORIGINAL_VERIFIED"


def _effective_status(physical_ok: bool, provenance: str, approval_match: bool, semantic: dict[str, Any]) -> str:
    semantic_status=semantic.get("semantic_role_status")
    if not physical_ok or provenance=="PROVENANCE_CONFLICT" or semantic_status=="ROLE_MISMATCH": return "INVALIDATED"
    if semantic_status in {"ROLE_AMBIGUOUS","NOT_VISUALLY_AUDITED"}: return "HUMAN_REVIEW_REQUIRED"
    if provenance=="PROVENANCE_UNKNOWN": return "UNVERIFIED"
    if not approval_match: return "PHYSICALLY_VERIFIED_ONLY"
    return "HUMAN_APPROVED" if semantic.get("review_source")=="human" else "VERIFIED"


def reconcile_evidence(packet: dict[str, Any], fingerprints_payload: dict[str, Any], semantic_review: dict[str, Any] | None, independent_semantic: bool) -> dict[str, Any]:
    validate_audit_packet(packet)
    fingerprints=fingerprints_payload.get("assets",{}); approvals=_index(packet.get("approval_events",[]),"approval_event_id"); prior_locked=_index(packet.get("prior_locked_assets",[]),"asset_id"); assets_out={}
    for asset in packet.get("assets",[]):
        asset_id=asset["asset_id"]
        fingerprint=fingerprints.get(asset_id) or {"exists":False,"path_allowed":False,"sha256":None,"byte_size":None,"signature_family":None,"extension_family":None,"width":None,"height":None,"errors":["fingerprint missing"]}
        expected_role=_expected_role(packet,asset); semantic=_semantic_result(asset_id,expected_role,semantic_review,independent_semantic)
        provenance=_provenance(asset,fingerprint,prior_locked.get(asset_id),fingerprints,approvals,expected_role)
        approval_id=asset.get("claimed_approval_event_id"); approval_match=_approval_matches(approvals.get(approval_id) if isinstance(approval_id,str) else None,asset,fingerprint,expected_role,semantic)
        if not approval_match and provenance=="EXACT_RECOVERY_VERIFIED" and semantic.get("semantic_role_status")=="ROLE_MATCH": approval_match=semantic.get("actual_role")==expected_role
        physical_ok=_physical_ok(fingerprint); effective_status=_effective_status(physical_ok,provenance,approval_match,semantic)
        assets_out[asset_id]={"asset_id":asset_id,"physical_sha256":fingerprint.get("sha256"),"physical_identity_ok":physical_ok,"provenance":provenance,"approval_match":approval_match,**semantic,"effective_status":effective_status,"allowed_slots":list(asset.get("allowed_slots",[]))}
    set_errors=[]
    for slot in packet.get("slots",[]):
        slot_id=slot["slot_id"]
        for asset_id in slot.get("required_asset_ids",[]):
            result=assets_out.get(asset_id)
            if not result: set_errors.append(f"{slot_id}: required asset {asset_id} missing from audit"); continue
            if result.get("effective_status") not in FINAL_USABLE: set_errors.append(f"{slot_id}: required asset {asset_id} status {result.get('effective_status')} is not final-consumable")
            if slot_id not in result.get("allowed_slots",[]): set_errors.append(f"{slot_id}: required asset {asset_id} is not approved for this slot scope")
    asset_set_gate={"status":"FAIL" if set_errors else ("PASS" if packet.get("slots") else "N/A"),"messages":set_errors}
    return {"audit_version":packet.get("audit_version"),"project_id":packet.get("project_id"),"checkpoint":packet.get("checkpoint"),"independent_semantic":independent_semantic,"assets":assets_out,"asset_set_gate":asset_set_gate}


def reconcile_from_files(packet: dict[str, Any], project_root: Path, semantic_review: dict[str, Any] | None = None, independent_semantic: bool = False) -> dict[str, Any]:
    return reconcile_evidence(packet, fingerprint_packet(packet, project_root), semantic_review, independent_semantic)


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try: value=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,UnicodeError,json.JSONDecodeError) as exc: raise ValueError(f"invalid {label}: {exc}") from exc
    if not isinstance(value,dict): raise ValueError(f"invalid {label}: root must be an object")
    return value


def main() -> int:
    parser=argparse.ArgumentParser(description="Reconcile candidate listing assets against real files and review evidence")
    parser.add_argument("audit_input",type=Path); parser.add_argument("project_root",type=Path); parser.add_argument("--semantic-review",type=Path); parser.add_argument("--output",type=Path); args=parser.parse_args()
    try:
        packet=_load_json(args.audit_input,"audit input"); semantic_review=_load_json(args.semantic_review,"semantic review") if args.semantic_review else None; result=reconcile_from_files(packet,args.project_root,semantic_review,independent_semantic=False)
    except ValueError as exc: print(f"FAIL: {exc}"); return 1
    text=json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)
    if args.output: args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(text+"\n",encoding="utf-8")
    else: print(text)
    return 0 if result["asset_set_gate"]["status"] in {"PASS","N/A"} else 1

if __name__ == "__main__": raise SystemExit(main())
