#!/usr/bin/env python3
"""Plan the smallest sufficient creative cleanup for known production problems."""

from __future__ import annotations
from typing import Any

PROBLEM_CLASSES = {"SINGLE_ASSET_DEFECT", "SET_REPETITION", "WRONG_MESSAGE_ROLE", "EVIDENCE_LIMITATION", "CLAIM_ERROR", "PRODUCT_DISTORTION"}


def _unique_ids(values: object, label: str) -> list[str]:
    if not isinstance(values, list):
        raise ValueError(f"{label} must be a list")
    result: list[str] = []
    seen: set[str] = set()
    for index, value in enumerate(values):
        if not isinstance(value, str) or not value:
            raise ValueError(f"{label}[{index}] must be a non-empty Asset ID")
        if value in seen:
            raise ValueError(f"duplicate {label} Asset ID: {value}")
        seen.add(value)
        result.append(value)
    return result


def plan_cleanup(problem_class: str, *, affected_assets: list[str], approved_assets: list[str], evidence_modes: dict[str, str] | None = None, reopen_approved: bool = False) -> dict[str, Any]:
    if problem_class not in PROBLEM_CLASSES:
        raise ValueError(f"unsupported problem_class: {problem_class}")
    affected = _unique_ids(affected_assets, "affected_assets")
    approved = _unique_ids(approved_assets, "approved_assets")
    approved_set = set(approved)
    modes = evidence_modes or {}
    if not isinstance(modes, dict):
        raise ValueError("evidence_modes must be a mapping when present")
    if problem_class == "EVIDENCE_LIMITATION":
        creative_mocks = [asset_id for asset_id in affected if modes.get(asset_id) == "CREATIVE_MOCK"]
        non_mock = [asset_id for asset_id in affected if asset_id not in creative_mocks]
        if not non_mock:
            return {"reopen": [], "preserve": [a for a in affected if a in approved_set], "reason": "Creative Mock keeps the approved creative; evidence entitlement remains limited for Hardening."}
        return {"reopen": non_mock, "preserve": [a for a in affected if a in approved_set and a not in non_mock], "reason": "Only assets whose evidence mode requires the missing proof source are reopened."}
    if problem_class == "SET_REPETITION":
        preserved_approved = [a for a in affected if a in approved_set]
        nonapproved = [a for a in affected if a not in approved_set]
        if nonapproved:
            return {"reopen": [nonapproved[0]], "preserve": preserved_approved, "reason": "Reopen the smallest non-approved subset first to restore set-level rhythm."}
        if not reopen_approved:
            return {"reopen": [], "preserve": list(affected), "reason": "All affected assets are already approved; explicit user choice is required before reopening one."}
        return {"reopen": [affected[-1]] if affected else [], "preserve": affected[:-1] if affected else [], "reason": "Explicit approval allows one approved asset to reopen; preserve the rest."}
    return {"reopen": list(affected), "preserve": [], "reason": "Reopen only the explicitly affected intrinsic-defect assets."}
