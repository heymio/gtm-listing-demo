#!/usr/bin/env python3
"""Validate one-job Asset Packets and project production-only context."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

EVIDENCE_MODES = {"SOURCE_FAITHFUL", "CREATIVE_MOCK", "PROOF_VISUAL"}
REQUIRED_TOP_LEVEL = {
    "asset_id", "role", "objective", "strategy_context", "evidence", "evidence_mode",
    "product_sources", "benchmark", "composition", "set_context", "output", "must_preserve", "must_not_generate",
}
PROJECTION_KEYS = [
    "asset_id", "role", "objective", "strategy_context", "evidence", "evidence_mode",
    "product_sources", "benchmark", "composition", "set_context", "output", "must_preserve", "must_not_generate",
]
NEIGHBOR_KEYS = ("asset_id", "scene_family", "composition_family", "tone", "product_scale", "proof_form")


def validate_asset_packet(packet: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(packet.get("asset_id"), str) or not packet.get("asset_id"):
        errors.append("Asset Packet requires exactly one asset_id string")
    if packet.get("output", {}).get("quantity") != 1:
        errors.append("Asset Packet output quantity must be 1; batch control belongs outside the packet")
    if packet.get("composition", {}).get("one_image_focus") is not True:
        errors.append("one_image_focus must be true")
    missing = sorted(REQUIRED_TOP_LEVEL - set(packet))
    errors.extend(f"missing field: {name}" for name in missing)
    if packet.get("evidence_mode") not in EVIDENCE_MODES:
        errors.append("evidence_mode must be SOURCE_FAITHFUL, CREATIVE_MOCK, or PROOF_VISUAL")
    set_context = packet.get("set_context")
    if not isinstance(set_context, dict):
        errors.append("set_context must be a mapping")
    else:
        if not isinstance(set_context.get("page_visual_direction"), dict):
            errors.append("set_context.page_visual_direction must be a mapping")
        if not isinstance(set_context.get("nearest_neighbors"), list):
            errors.append("set_context.nearest_neighbors must be a list")
    return errors


def project_generation_context(packet: dict) -> dict:
    errors = validate_asset_packet(packet)
    if errors:
        raise ValueError("; ".join(errors))
    return {key: packet[key] for key in PROJECTION_KEYS}


def _direction_index(handoff: dict[str, Any]) -> dict[str, dict[str, Any]]:
    visual_system = handoff.get("page_visual_system")
    if not isinstance(visual_system, dict):
        raise ValueError("Production Handoff missing page_visual_system")
    rows = visual_system.get("asset_directions")
    if not isinstance(rows, list):
        raise ValueError("page_visual_system.asset_directions must be a list")
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("page_visual_system asset direction must be a mapping")
        asset_id = row.get("asset_id")
        if not isinstance(asset_id, str) or not asset_id:
            raise ValueError("page_visual_system asset direction requires asset_id")
        if asset_id in result:
            raise ValueError(f"duplicate visual direction asset_id: {asset_id}")
        result[asset_id] = row
    return result


def _region_order(handoff: dict[str, Any], asset_id: str) -> list[str]:
    page_plan = handoff.get("page_plan")
    if not isinstance(page_plan, dict):
        raise ValueError("Production Handoff missing page_plan")
    for region in ("gallery", "enhanced_content", "other_required_regions"):
        values = page_plan.get(region, [])
        if not isinstance(values, list):
            raise ValueError(f"page_plan.{region} must be a list")
        if asset_id in values:
            return [value for value in values if isinstance(value, str) and value]
    raise ValueError(f"asset {asset_id} is not present in page_plan")


def build_set_context(handoff: dict[str, Any], asset_id: str) -> dict[str, Any]:
    if not isinstance(asset_id, str) or not asset_id:
        raise ValueError("asset_id must be a non-empty string")
    directions = _direction_index(handoff)
    current = directions.get(asset_id)
    if current is None:
        raise ValueError(f"missing page visual direction for asset {asset_id}")
    order = _region_order(handoff, asset_id)
    index = order.index(asset_id)
    neighbor_ids: list[str] = []
    if index > 0:
        neighbor_ids.append(order[index - 1])
    if index + 1 < len(order):
        neighbor_ids.append(order[index + 1])
    nearest_neighbors: list[dict[str, Any]] = []
    for neighbor_id in neighbor_ids:
        row = directions.get(neighbor_id)
        if row is not None:
            nearest_neighbors.append({key: row.get(key) for key in NEIGHBOR_KEYS})
    allowed = {"asset_id", "visual_role", "scene_family", "composition_family", "tone", "product_scale", "proof_form", "neighbor_contrast_note"}
    return {
        "page_visual_direction": {key: value for key, value in current.items() if key in allowed},
        "nearest_neighbors": nearest_neighbors,
    }


def evidence_mode_for_asset(handoff: dict[str, Any], asset_id: str) -> str:
    assets = handoff.get("asset_set")
    if not isinstance(assets, list):
        raise ValueError("Production Handoff asset_set must be a list")
    for row in assets:
        if isinstance(row, dict) and row.get("asset_id") == asset_id:
            mode = row.get("evidence_mode")
            if mode not in EVIDENCE_MODES:
                raise ValueError(f"invalid evidence_mode for asset {asset_id}")
            return mode
    raise ValueError(f"asset {asset_id} is not present in asset_set")


def _source_ids(sources: dict[str, Any], key: str) -> list[str] | None:
    values = sources.get(key, [])
    if not isinstance(values, list) or any(not isinstance(value, str) or not value for value in values):
        return None
    return values


def evaluate_source_readiness(packet: dict[str, Any], available_source_ids: set[str]) -> dict[str, Any]:
    mode = packet.get("evidence_mode")
    empty = {"missing_source_ids": [], "missing_identity_source_ids": [], "missing_proof_source_ids": []}
    if mode not in EVIDENCE_MODES:
        return {"status": "BLOCKED", **empty, "reason": "invalid evidence_mode"}
    sources = packet.get("product_sources")
    if not isinstance(sources, dict):
        return {"status": "BLOCKED", **empty, "reason": "invalid product_sources mapping"}
    identity_key = "identity_required" if "identity_required" in sources else "required"
    identity_required = _source_ids(sources, identity_key)
    proof_required = _source_ids(sources, "proof_required")
    if identity_required is None or proof_required is None:
        return {"status": "BLOCKED", **empty, "reason": "invalid source requirement list"}
    missing_identity = [sid for sid in identity_required if sid not in available_source_ids]
    missing_proof = [sid for sid in proof_required if sid not in available_source_ids]
    missing_all = missing_identity + [sid for sid in missing_proof if sid not in missing_identity]
    if missing_identity:
        return {
            "status": "BLOCKED", "missing_source_ids": missing_all,
            "missing_identity_source_ids": missing_identity, "missing_proof_source_ids": missing_proof,
            "reason": "authoritative product identity source required for every evidence mode",
        }
    if missing_proof:
        if mode == "CREATIVE_MOCK":
            return {
                "status": "READY_WITH_LIMITATION", "missing_source_ids": missing_proof,
                "missing_identity_source_ids": [], "missing_proof_source_ids": missing_proof,
                "reason": "creative mock may proceed; missing proof details are not Product Truth or proof",
            }
        return {
            "status": "BLOCKED", "missing_source_ids": missing_proof,
            "missing_identity_source_ids": [], "missing_proof_source_ids": missing_proof,
            "reason": "authoritative proof source required for this evidence mode",
        }
    return {"status": "READY", **empty, "reason": "required identity/proof sources available"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Project an Asset Packet into production-only JSON context")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    packet = json.loads(args.input.read_text(encoding="utf-8"))
    projected = project_generation_context(packet)
    encoded = json.dumps(projected, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    else:
        print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
