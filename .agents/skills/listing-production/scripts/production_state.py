#!/usr/bin/env python3
"""Creative-production state helpers for Asset Ledger and Production Freeze."""

from __future__ import annotations

import json

ALLOWED_STATUSES = {"PLANNED", "READY", "REVIEW", "REVISE", "USER_APPROVED", "BLOCKED"}
SET_QA_READY_STATUSES = {"CLEAR", "USER_ACCEPTED"}


def _copy(value: dict) -> dict:
    return json.loads(json.dumps(value))


def _require_non_empty_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value


def _required_ids(handoff: dict) -> list[str]:
    result: list[str] = []
    for item in handoff.get("asset_set", []):
        asset_id = item.get("asset_id") if isinstance(item, dict) else None
        if isinstance(asset_id, str) and asset_id:
            result.append(asset_id)
    return result


def _validate_asset_objects(items: object, label: str) -> list[dict]:
    if not isinstance(items, list):
        raise ValueError(f"{label} must be a list")
    result: list[dict] = []
    seen: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"{label}[{index}] must be a complete asset mapping")
        asset_id = _require_non_empty_string(item.get("asset_id"), f"{label}[{index}].asset_id")
        if asset_id in seen:
            raise ValueError(f"duplicate {label} asset_id: {asset_id}")
        seen.add(asset_id)
        result.append(item)
    return result


def _remove_ids_from_page_plan(result: dict, remove_set: set[str]) -> None:
    page_plan = result.get("page_plan")
    if page_plan is None:
        return
    if not isinstance(page_plan, dict):
        raise ValueError("handoff.page_plan must be a mapping when present")
    for region in ("gallery", "enhanced_content", "other_required_regions"):
        values = page_plan.get(region)
        if values is None:
            continue
        if not isinstance(values, list):
            raise ValueError(f"handoff.page_plan.{region} must be a list")
        page_plan[region] = [value for value in values if value not in remove_set]


def _remove_ids_from_visual_system(result: dict, remove_set: set[str]) -> None:
    system = result.get("page_visual_system")
    if system is None:
        return
    if not isinstance(system, dict):
        raise ValueError("handoff.page_visual_system must be a mapping when present")
    directions = system.get("asset_directions")
    if directions is None:
        return
    if not isinstance(directions, list):
        raise ValueError("handoff.page_visual_system.asset_directions must be a list")
    system["asset_directions"] = [row for row in directions if not (isinstance(row, dict) and row.get("asset_id") in remove_set)]


def apply_scope_delta(handoff: dict, delta: dict) -> dict:
    if not isinstance(handoff, dict) or not isinstance(delta, dict):
        raise ValueError("handoff and delta must be mappings")
    assets = handoff.get("asset_set")
    if not isinstance(assets, list):
        raise ValueError("handoff.asset_set must be a list")
    current_by_id: dict[str, dict] = {}
    current_order: list[str] = []
    for index, item in enumerate(assets):
        if not isinstance(item, dict):
            raise ValueError(f"handoff.asset_set[{index}] must be a mapping")
        asset_id = _require_non_empty_string(item.get("asset_id"), f"handoff.asset_set[{index}].asset_id")
        if asset_id in current_by_id:
            raise ValueError(f"duplicate current asset_id: {asset_id}")
        current_by_id[asset_id] = item
        current_order.append(asset_id)
    removed = delta.get("removed", [])
    if not isinstance(removed, list) or any(not isinstance(value, str) or not value for value in removed):
        raise ValueError("delta.removed must be a list of Asset IDs")
    if len(set(removed)) != len(removed):
        raise ValueError("delta.removed contains duplicate Asset IDs")
    unknown = [asset_id for asset_id in removed if asset_id not in current_by_id]
    if unknown:
        raise ValueError("unknown removed Asset IDs: " + ", ".join(unknown))
    added = _validate_asset_objects(delta.get("added", []), "delta.added")
    changed = _validate_asset_objects(delta.get("changed", []), "delta.changed")
    if added or changed:
        raise ValueError("Production cannot add/change authoritative assets directly; return to Planning for a revised handoff")
    reason = delta.get("reason")
    if not isinstance(reason, list) or not reason or any(not isinstance(value, str) or not value.strip() for value in reason):
        raise ValueError("delta.reason must be a non-empty list of strings")
    result = _copy(handoff)
    remove_set = set(removed)
    result["asset_set"] = [_copy(current_by_id[asset_id]) for asset_id in current_order if asset_id not in remove_set]
    _remove_ids_from_page_plan(result, remove_set)
    _remove_ids_from_visual_system(result, remove_set)
    previous_revision = result.get("scope_revision", 1)
    if not isinstance(previous_revision, int) or isinstance(previous_revision, bool) or previous_revision < 1:
        previous_revision = 1
    result["scope_revision"] = previous_revision + 1
    result["scope_delta"] = {"added": [], "removed": list(removed), "changed": [], "reason": list(reason)}
    return result


def _is_selected_lock(row: dict) -> bool:
    selected = row.get("selected_candidate_id")
    return row.get("status") == "USER_APPROVED" and isinstance(selected, str) and bool(selected) and row.get("reopened") is not True


def add_candidate(ledger: dict, asset_id: str, candidate_id: str, output_ref: str) -> dict:
    _require_non_empty_string(asset_id, "asset_id")
    _require_non_empty_string(candidate_id, "candidate_id")
    _require_non_empty_string(output_ref, "output_ref")
    result = _copy(ledger)
    row = result.setdefault("assets", {}).setdefault(asset_id, {})
    if _is_selected_lock(row):
        raise ValueError("asset is locked to a user-selected candidate; reopen before adding another candidate")
    candidates = row.setdefault("candidates", [])
    if not isinstance(candidates, list):
        raise ValueError("asset candidates must be a list")
    if any(isinstance(candidate, dict) and candidate.get("candidate_id") == candidate_id for candidate in candidates):
        raise ValueError(f"duplicate candidate_id: {candidate_id}")
    candidates.append({"candidate_id": candidate_id, "output_ref": output_ref, "status": "REVIEW"})
    row["status"] = "REVIEW"
    row["latest_candidate_id"] = candidate_id
    return result


def select_candidate(ledger: dict, asset_id: str, candidate_id: str, approval_ref: str | None = None) -> dict:
    _require_non_empty_string(asset_id, "asset_id")
    _require_non_empty_string(candidate_id, "candidate_id")
    if approval_ref is not None:
        _require_non_empty_string(approval_ref, "approval_ref")
    result = _copy(ledger)
    row = result.setdefault("assets", {}).setdefault(asset_id, {})
    candidates = row.get("candidates", [])
    if not isinstance(candidates, list):
        raise ValueError("asset candidates must be a list")
    selected = next((candidate for candidate in candidates if isinstance(candidate, dict) and candidate.get("candidate_id") == candidate_id), None)
    if selected is None:
        raise ValueError(f"candidate_id not found for {asset_id}: {candidate_id}")
    previous_id = row.get("selected_candidate_id")
    reopened = row.get("reopened") is True
    if isinstance(previous_id, str) and previous_id and previous_id != candidate_id and not reopened:
        raise ValueError("asset must be explicitly reopened before selecting a different candidate")
    if reopened and isinstance(previous_id, str) and previous_id != candidate_id:
        for candidate in candidates:
            if isinstance(candidate, dict) and candidate.get("candidate_id") == previous_id:
                candidate["status"] = "SUPERSEDED"
    selected["status"] = "USER_SELECTED"
    row["selected_candidate_id"] = candidate_id
    row["current_output_ref"] = selected.get("output_ref")
    row["status"] = "USER_APPROVED"
    row["reopened"] = False
    if approval_ref is not None:
        row["approval_ref"] = approval_ref
    return result


def reopen_asset(ledger: dict, asset_id: str, reason: str) -> dict:
    _require_non_empty_string(asset_id, "asset_id")
    _require_non_empty_string(reason, "reason")
    result = _copy(ledger)
    row = result.setdefault("assets", {}).setdefault(asset_id, {})
    if row.get("status") != "USER_APPROVED":
        raise ValueError("only a USER_APPROVED asset can be reopened")
    if not isinstance(row.get("selected_candidate_id"), str) or not row.get("selected_candidate_id"):
        raise ValueError("approved asset has no selected candidate to preserve")
    row["status"] = "REVIEW"
    row["reopened"] = True
    row["reopen_reason"] = reason
    return result


def set_creative_status(ledger: dict, asset_id: str, status: str, output_ref: str | None = None, approval_ref: str | None = None) -> dict:
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"invalid creative status: {status}")
    if not isinstance(asset_id, str) or not asset_id:
        raise ValueError("asset_id must be a non-empty string")
    result = _copy(ledger)
    row = result.setdefault("assets", {}).setdefault(asset_id, {})
    if _is_selected_lock(row):
        if status != "USER_APPROVED":
            raise ValueError("asset is locked to a user-selected candidate; reopen before changing status")
        current = row.get("current_output_ref")
        if output_ref is not None and current is not None and output_ref != current:
            raise ValueError("asset is locked to a user-selected candidate; reopen before replacing output")
    row["status"] = status
    if output_ref is not None:
        row["current_output_ref"] = output_ref
    if approval_ref is not None:
        row["approval_ref"] = approval_ref
    return result


def production_progress(handoff: dict, ledger: dict) -> dict:
    required = _required_ids(handoff)
    rows = ledger.get("assets", {})
    approved = sum(1 for asset_id in required if rows.get(asset_id, {}).get("status") == "USER_APPROVED")
    expected = len(required)
    return {"expected": expected, "approved": approved, "remaining": expected - approved, "complete": expected == approved}


def _set_qa_state(handoff: dict, ledger: dict, required: list[str]) -> tuple[str, bool]:
    if "page_visual_system" not in handoff:
        return "N/A", True
    qa = ledger.get("set_qa")
    if not isinstance(qa, dict):
        return "MISSING", False
    status = qa.get("status")
    if status not in SET_QA_READY_STATUSES:
        return str(status) if isinstance(status, str) and status else "MISSING", False
    reviewed = qa.get("reviewed_asset_ids")
    if not isinstance(reviewed, list) or any(not isinstance(value, str) or not value for value in reviewed) or len(reviewed) != len(set(reviewed)) or set(reviewed) != set(required):
        return "STALE", False
    reviewed_refs = qa.get("reviewed_output_refs")
    if not isinstance(reviewed_refs, dict) or set(reviewed_refs) != set(required):
        return "STALE", False
    rows = ledger.get("assets")
    if not isinstance(rows, dict):
        return "STALE", False
    for asset_id in required:
        reviewed_ref = reviewed_refs.get(asset_id)
        current_ref = rows.get(asset_id, {}).get("current_output_ref") if isinstance(rows.get(asset_id), dict) else None
        if not isinstance(reviewed_ref, str) or not reviewed_ref.strip() or not isinstance(current_ref, str) or not current_ref.strip() or reviewed_ref != current_ref:
            return "STALE", False
    visual_review_ref = qa.get("visual_review_ref")
    if not isinstance(visual_review_ref, str) or not visual_review_ref.strip():
        return "MISSING_REF", False
    return status, True


def build_production_freeze(handoff: dict, ledger: dict) -> dict:
    required = _required_ids(handoff)
    rows = ledger.get("assets", {})
    approved_assets: list[str] = []
    blocked_assets: list[str] = []
    revision_pending: list[str] = []
    approved_output_refs: list[str] = []
    for asset_id in required:
        row = rows.get(asset_id, {})
        status = row.get("status", "PLANNED")
        if status == "USER_APPROVED":
            approved_assets.append(asset_id)
            if row.get("current_output_ref"):
                approved_output_refs.append(row["current_output_ref"])
        elif status == "BLOCKED":
            blocked_assets.append(asset_id)
        else:
            revision_pending.append(asset_id)
    set_qa_status, set_qa_ready = _set_qa_state(handoff, ledger, required)
    expected = len(required)
    ready = len(approved_assets) == expected and not blocked_assets and not revision_pending and set_qa_ready
    return {
        "expected_assets": expected,
        "user_approved_assets": approved_assets,
        "blocked_assets": blocked_assets,
        "revision_pending": revision_pending,
        "approved_output_refs": approved_output_refs,
        "set_qa_status": set_qa_status,
        "ready_for_hardening": ready,
    }
