#!/usr/bin/env python3
"""Global v0.3.3 production state with fail-closed required-set and Freeze bindings."""

from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEGACY_PATH = HERE / "production_state_legacy.py"
SPEC = importlib.util.spec_from_file_location("global_listing_production_state_legacy", LEGACY_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load legacy production state helpers: {LEGACY_PATH}")
_legacy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(_legacy)

ALLOWED_STATUSES = _legacy.ALLOWED_STATUSES
SET_QA_READY_STATUSES = _legacy.SET_QA_READY_STATUSES

add_candidate = _legacy.add_candidate
select_candidate = _legacy.select_candidate
reopen_asset = _legacy.reopen_asset
set_creative_status = _legacy.set_creative_status
apply_scope_delta = _legacy.apply_scope_delta


def _ordered_unique(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _blocked_ids(handoff: dict) -> set[str]:
    result: set[str] = set()
    for item in handoff.get("blocked_assets", []):
        if isinstance(item, str) and item:
            result.add(item)
        elif isinstance(item, dict):
            asset_id = item.get("asset_id")
            if isinstance(asset_id, str) and asset_id:
                result.add(asset_id)
    return result


def _required_ids(handoff: dict) -> list[str]:
    """Union every Production-side source that can still require a final asset."""
    values: list[str] = []
    for item in handoff.get("asset_set", []):
        asset_id = item.get("asset_id") if isinstance(item, dict) else None
        if isinstance(asset_id, str) and asset_id:
            values.append(asset_id)
    page_plan = handoff.get("page_plan") or {}
    if isinstance(page_plan, dict):
        for region in ("gallery", "enhanced_content", "other_required_regions"):
            region_values = page_plan.get(region, [])
            if isinstance(region_values, list):
                values.extend(asset_id for asset_id in region_values if isinstance(asset_id, str) and asset_id)
    values.extend(sorted(_blocked_ids(handoff)))
    return _ordered_unique(values)


def production_progress(handoff: dict, ledger: dict) -> dict:
    required = _required_ids(handoff)
    rows = ledger.get("assets", {}) if isinstance(ledger, dict) else {}
    approved = sum(
        1 for asset_id in required
        if isinstance(rows.get(asset_id), dict) and rows.get(asset_id, {}).get("status") == "USER_APPROVED"
    )
    expected = len(required)
    return {
        "expected": expected,
        "approved": approved,
        "remaining": expected - approved,
        "complete": expected > 0 and expected == approved,
    }


def _set_qa_state(handoff: dict, ledger: dict, required: list[str]) -> tuple[str, bool]:
    if "page_visual_system" not in handoff:
        return "MISSING", False
    return _legacy._set_qa_state(handoff, ledger, required)


def build_production_freeze(handoff: dict, ledger: dict) -> dict:
    required = _required_ids(handoff)
    rows = ledger.get("assets", {}) if isinstance(ledger, dict) else {}
    blocked_from_handoff = _blocked_ids(handoff)
    approved_assets: list[str] = []
    blocked_assets: list[str] = []
    revision_pending: list[str] = []
    approved_outputs: dict[str, dict[str, str]] = {}

    for asset_id in required:
        row = rows.get(asset_id, {}) if isinstance(rows.get(asset_id), dict) else {}
        if asset_id in blocked_from_handoff:
            blocked_assets.append(asset_id)
            continue
        status = row.get("status", "PLANNED")
        if status == "USER_APPROVED":
            candidate_id = row.get("selected_candidate_id")
            output_ref = row.get("current_output_ref")
            if isinstance(candidate_id, str) and candidate_id and isinstance(output_ref, str) and output_ref:
                approved_assets.append(asset_id)
                approved_outputs[asset_id] = {
                    "candidate_id": candidate_id,
                    "output_ref": output_ref,
                }
            else:
                revision_pending.append(asset_id)
        elif status == "BLOCKED":
            blocked_assets.append(asset_id)
        else:
            revision_pending.append(asset_id)

    set_qa_status, set_qa_ready = _set_qa_state(handoff, ledger, required)
    expected = len(required)
    ready = (
        expected > 0
        and len(approved_assets) == expected
        and set(approved_outputs) == set(required)
        and not blocked_assets
        and not revision_pending
        and set_qa_ready
    )
    return {
        "expected_assets": expected,
        "required_asset_ids": list(required),
        "user_approved_assets": approved_assets,
        "blocked_assets": blocked_assets,
        "revision_pending": revision_pending,
        "approved_outputs": approved_outputs,
        "set_qa_status": set_qa_status,
        "ready_for_hardening": ready,
    }
