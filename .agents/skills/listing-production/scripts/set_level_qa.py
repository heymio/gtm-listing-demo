#!/usr/bin/env python3
"""Deterministic set-level Creative QA over structured visual-direction metadata."""

from __future__ import annotations
from typing import Any

SIGNATURE_FIELDS = ("scene_family", "composition_family", "tone", "product_scale", "proof_form")


def _asset_id(row: dict[str, Any], index: int) -> str:
    value = row.get("asset_id")
    return value if isinstance(value, str) and value else f"index-{index}"


def _signature(row: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(row.get(field) for field in SIGNATURE_FIELDS)


def _run_issues(rows: list[dict[str, Any]], field: str, issue_type: str, message: str) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    start = 0
    while start < len(rows):
        value = rows[start].get(field)
        end = start + 1
        while end < len(rows) and rows[end].get(field) == value:
            end += 1
        if value not in {None, ""} and end - start >= 3:
            issues.append({"type": issue_type, "asset_ids": [_asset_id(rows[i], i) for i in range(start, end)], "message": message})
        start = end
    return issues


def evaluate_set(asset_rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(asset_rows, list):
        raise ValueError("asset_rows must be a list")
    for index, row in enumerate(asset_rows):
        if not isinstance(row, dict):
            raise ValueError(f"asset_rows[{index}] must be a mapping")
    issues: list[dict[str, Any]] = []
    has_revise = False
    for index in range(1, len(asset_rows)):
        previous, current = asset_rows[index - 1], asset_rows[index]
        ids = [_asset_id(previous, index - 1), _asset_id(current, index)]
        if _signature(previous) == _signature(current):
            has_revise = True
            issues.append({"type": "scene_repetition", "asset_ids": ids, "message": "Adjacent assets repeat the full visual signature."})
            issues.append({"type": "composition_repetition", "asset_ids": ids, "message": "Adjacent assets repeat the same composition with the same full signature."})
            continue
        if previous.get("composition_family") not in {None, ""} and previous.get("composition_family") == current.get("composition_family"):
            issues.append({"type": "composition_repetition", "asset_ids": ids, "message": "Adjacent assets repeat the same composition family."})
        if previous.get("message_role") not in {None, ""} and previous.get("message_role") == current.get("message_role"):
            issues.append({"type": "message_role_redundancy", "asset_ids": ids, "message": "Adjacent assets repeat the same message role."})
    issues.extend(_run_issues(asset_rows, "scene_family", "scene_repetition", "Three or more consecutive assets repeat the same scene family."))
    issues.extend(_run_issues(asset_rows, "tone", "tone_brightness_rhythm", "Three or more consecutive assets repeat the same tone/brightness family."))
    issues.extend(_run_issues(asset_rows, "product_scale", "product_scale_repetition", "Three or more consecutive assets repeat the same product scale."))
    issues.extend(_run_issues(asset_rows, "proof_form", "proof_form_diversity", "Three or more consecutive assets repeat the same proof form."))
    return {"status": "REVISE" if has_revise else "REVIEW" if issues else "CLEAR", "issues": issues}
