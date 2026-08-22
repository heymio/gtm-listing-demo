#!/usr/bin/env python3
"""Strict structural validation for global planning handoff artifacts.

The public package has no YAML dependency. Contracts therefore use a small
2-space-indented YAML subset and fail closed when input falls outside it.
"""

from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path
from typing import Any

FORBIDDEN_HANDOFF = {
    "project_state_manifest",
    "auditor_evidence",
    "declared_gate_results",
    "change_impact_map",
    "delivery_parity_gate",
    "pre_demo_asset_gate",
}
EVIDENCE_MODES = {"SOURCE_FAITHFUL", "CREATIVE_MOCK", "PROOF_VISUAL"}
VISUAL_FIELDS = (
    "visual_role",
    "scene_family",
    "composition_family",
    "tone",
    "product_scale",
    "proof_form",
)
SIGNATURE_FIELDS = (
    "scene_family",
    "composition_family",
    "tone",
    "product_scale",
    "proof_form",
)
_KEY_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


class ContractParseError(ValueError):
    pass


def _tokenize(text: str) -> list[tuple[int, str, int]]:
    tokens: list[tuple[int, str, int]] = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        if "\t" in raw:
            raise ContractParseError(f"line {lineno}: tabs are not allowed")
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if indent % 2:
            raise ContractParseError(f"line {lineno}: indentation must use multiples of 2 spaces")
        tokens.append((indent, raw[indent:].rstrip(), lineno))
    return tokens


def _split_mapping(content: str, lineno: int) -> tuple[str, str]:
    if ":" not in content:
        raise ContractParseError(f"line {lineno}: expected mapping entry")
    key, rest = content.split(":", 1)
    key = key.strip()
    if not key or not _KEY_RE.match(key):
        raise ContractParseError(f"line {lineno}: invalid mapping key {key!r}")
    return key, rest.strip()


def _parse_scalar(value: str, lineno: int) -> Any:
    if value == "[]":
        return []
    if value == "{}":
        return {}
    lowered = value.casefold()
    if lowered in {"null", "~"}:
        return None
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if value.startswith(("'", '"')):
        try:
            parsed = ast.literal_eval(value)
        except (SyntaxError, ValueError) as exc:
            raise ContractParseError(f"line {lineno}: invalid quoted scalar") from exc
        if not isinstance(parsed, str):
            raise ContractParseError(f"line {lineno}: quoted scalar must be a string")
        return parsed
    if re.fullmatch(r"[-+]?\d+", value):
        return int(value)
    if re.fullmatch(r"[-+]?(?:\d+\.\d*|\d*\.\d+)", value):
        return float(value)
    if value.startswith("[") or value.startswith("{"):
        raise ContractParseError(f"line {lineno}: only empty inline containers are supported")
    return value


def _parse_mapping(tokens: list[tuple[int, str, int]], index: int, indent: int) -> tuple[dict[str, Any], int]:
    result: dict[str, Any] = {}
    while index < len(tokens):
        current_indent, content, lineno = tokens[index]
        if current_indent < indent:
            break
        if current_indent > indent:
            raise ContractParseError(f"line {lineno}: unexpected indentation")
        if content == "-" or content.startswith("- "):
            break
        key, rest = _split_mapping(content, lineno)
        if key in result:
            raise ContractParseError(f"line {lineno}: duplicate key {key!r}")
        index += 1
        if rest:
            result[key] = _parse_scalar(rest, lineno)
            if index < len(tokens) and tokens[index][0] > indent:
                raise ContractParseError(f"line {tokens[index][2]}: scalar {key!r} cannot own nested content")
            continue
        if index < len(tokens) and tokens[index][0] > indent:
            if tokens[index][0] != indent + 2:
                raise ContractParseError(f"line {tokens[index][2]}: nested block must indent exactly 2 spaces")
            result[key], index = _parse_block(tokens, index, indent + 2)
        else:
            result[key] = None
    return result, index


def _parse_list(tokens: list[tuple[int, str, int]], index: int, indent: int) -> tuple[list[Any], int]:
    result: list[Any] = []
    while index < len(tokens):
        current_indent, content, lineno = tokens[index]
        if current_indent < indent:
            break
        if current_indent > indent:
            raise ContractParseError(f"line {lineno}: unexpected indentation")
        if not (content == "-" or content.startswith("- ")):
            break
        item_text = content[1:].strip()
        index += 1
        if not item_text:
            if index < len(tokens) and tokens[index][0] == indent + 2:
                item, index = _parse_block(tokens, index, indent + 2)
            else:
                item = None
            result.append(item)
            continue
        if ":" in item_text:
            key, rest = _split_mapping(item_text, lineno)
            if not rest:
                raise ContractParseError(f"line {lineno}: list mapping must start with a scalar value")
            item: dict[str, Any] = {key: _parse_scalar(rest, lineno)}
            if index < len(tokens) and tokens[index][0] > indent:
                if tokens[index][0] != indent + 2:
                    raise ContractParseError(f"line {tokens[index][2]}: list mapping continuation must indent 2 spaces")
                continuation, index = _parse_mapping(tokens, index, indent + 2)
                duplicate = set(item) & set(continuation)
                if duplicate:
                    raise ContractParseError(f"duplicate key in list mapping: {sorted(duplicate)[0]!r}")
                item.update(continuation)
            result.append(item)
            continue
        result.append(_parse_scalar(item_text, lineno))
        if index < len(tokens) and tokens[index][0] > indent:
            raise ContractParseError(f"line {tokens[index][2]}: scalar list item cannot own nested content")
    return result, index


def _parse_block(tokens: list[tuple[int, str, int]], index: int, indent: int) -> tuple[Any, int]:
    if index >= len(tokens):
        raise ContractParseError("unexpected end of document")
    current_indent, content, lineno = tokens[index]
    if current_indent != indent:
        raise ContractParseError(f"line {lineno}: unexpected indentation")
    if content == "-" or content.startswith("- "):
        return _parse_list(tokens, index, indent)
    return _parse_mapping(tokens, index, indent)


def parse_contract_yaml(text: str) -> Any:
    tokens = _tokenize(text)
    if not tokens:
        return {}
    if tokens[0][0] != 0:
        raise ContractParseError(f"line {tokens[0][2]}: document must start at indentation 0")
    parsed, index = _parse_block(tokens, 0, 0)
    if index != len(tokens):
        raise ContractParseError(f"line {tokens[index][2]}: could not parse trailing content")
    return parsed


def _parse_root(text: str) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        parsed = parse_contract_yaml(text)
    except ContractParseError as exc:
        return None, [f"invalid contract YAML: {exc}"]
    if not isinstance(parsed, dict):
        return None, ["document root must be a mapping"]
    return parsed, []


def _require_type(container: dict[str, Any], key: str, expected: type, errors: list[str], path: str = "") -> Any:
    label = f"{path}.{key}" if path else key
    if key not in container:
        errors.append(f"missing required key: {label}")
        return None
    value = container[key]
    if not isinstance(value, expected) or (expected is int and isinstance(value, bool)):
        typename = {dict: "mapping", list: "list", str: "string", int: "integer"}.get(expected, expected.__name__)
        errors.append(f"{label} must be a {typename}")
        return None
    return value


def _non_empty_string(container: dict[str, Any], key: str, errors: list[str], path: str) -> str | None:
    value = _require_type(container, key, str, errors, path)
    if isinstance(value, str) and not value.strip():
        errors.append(f"{path}.{key} must be a non-empty string")
        return None
    return value if isinstance(value, str) else None


def _unique_ids(items: list[Any], key: str, errors: list[str], path: str) -> set[str]:
    seen: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{path}[{index}] must be a mapping")
            continue
        value = item.get(key)
        if not isinstance(value, str) or not value:
            errors.append(f"{path}[{index}].{key} must be a non-empty string")
            continue
        if value in seen:
            errors.append(f"duplicate {path} {key}: {value}")
        seen.add(value)
    return seen


def _find_forbidden(value: Any, path: str = "") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            if str(key).casefold() in FORBIDDEN_HANDOFF:
                errors.append(f"forbidden control-plane key in Production Handoff: {child_path}")
            errors.extend(_find_forbidden(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_find_forbidden(child, f"{path}[{index}]"))
    return errors


def _visual_signature(direction: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(direction.get(key) for key in SIGNATURE_FIELDS)


def validate_project_brief(text: str) -> list[str]:
    root, errors = _parse_root(text)
    if root is None:
        return errors
    _require_type(root, "project", dict, errors)
    _require_type(root, "offers", list, errors)
    _require_type(root, "product_truth", dict, errors)
    _require_type(root, "claim_boundaries", dict, errors)
    _require_type(root, "consumer_evidence_sources", list, errors)
    _require_type(root, "channel_reference", dict, errors)
    _require_type(root, "open_business_decisions", list, errors)
    return errors


def validate_creative_strategy(text: str) -> list[str]:
    root, errors = _parse_root(text)
    if root is None:
        return errors
    strategy = _require_type(root, "creative_strategy", dict, errors)
    if not isinstance(strategy, dict):
        return errors
    for key in [
        "target_user", "primary_purchase_reasons", "shopper_barriers", "reasons_to_believe",
        "market_implications", "proof_principles", "visual_direction", "visual_anti_patterns",
    ]:
        _require_type(strategy, key, list, errors, "creative_strategy")
    for key in ["core_tension", "core_promise"]:
        _require_type(strategy, key, str, errors, "creative_strategy")
    priority = _require_type(strategy, "message_priority", dict, errors, "creative_strategy")
    if isinstance(priority, dict):
        for key in ["p0", "p1", "p2"]:
            _require_type(priority, key, list, errors, "creative_strategy.message_priority")
    return errors


def _validate_page_visual_system(handoff: dict[str, Any], asset_ids: set[str], ordered: list[str], errors: list[str]) -> None:
    system = _require_type(handoff, "page_visual_system", dict, errors, "production_handoff")
    if not isinstance(system, dict):
        return
    directions = _require_type(system, "asset_directions", list, errors, "production_handoff.page_visual_system")
    if not isinstance(directions, list):
        return
    direction_ids = _unique_ids(directions, "asset_id", errors, "production_handoff.page_visual_system.asset_directions")
    unknown = sorted(direction_ids - asset_ids)
    missing = sorted(asset_ids - direction_ids)
    if unknown:
        errors.append("page_visual_system references Asset IDs absent from current asset_set: " + ", ".join(unknown))
    if missing:
        errors.append("page_visual_system missing directions for current Asset IDs: " + ", ".join(missing))
    by_id: dict[str, dict[str, Any]] = {}
    for index, direction in enumerate(directions):
        if not isinstance(direction, dict):
            continue
        asset_id = direction.get("asset_id")
        if isinstance(asset_id, str) and asset_id:
            by_id[asset_id] = direction
        path = f"production_handoff.page_visual_system.asset_directions[{index}]"
        for key in VISUAL_FIELDS:
            _non_empty_string(direction, key, errors, path)
        note = direction.get("neighbor_contrast_note")
        if note is not None and (not isinstance(note, str) or not note.strip()):
            errors.append(f"{path}.neighbor_contrast_note must be a non-empty string when present")
    for previous_id, current_id in zip(ordered, ordered[1:]):
        previous = by_id.get(previous_id)
        current = by_id.get(current_id)
        if previous and current and _visual_signature(previous) == _visual_signature(current):
            note = current.get("neighbor_contrast_note")
            if not isinstance(note, str) or not note.strip():
                errors.append(f"adjacent visual direction repeats without intentional contrast note: {previous_id} -> {current_id}")


def _validate_scope_delta(handoff: dict[str, Any], asset_ids: set[str], errors: list[str]) -> None:
    has_revision = "scope_revision" in handoff
    has_delta = "scope_delta" in handoff
    if not has_revision and not has_delta:
        return
    if not has_revision or not has_delta:
        errors.append("scope_revision and scope_delta must be provided together")
        return
    revision = _require_type(handoff, "scope_revision", int, errors, "production_handoff")
    if isinstance(revision, int) and not isinstance(revision, bool) and revision < 1:
        errors.append("production_handoff.scope_revision must be a positive integer")
    delta = _require_type(handoff, "scope_delta", dict, errors, "production_handoff")
    if not isinstance(delta, dict):
        return
    values: dict[str, list[Any]] = {}
    for key in ["added", "removed", "changed", "reason"]:
        value = _require_type(delta, key, list, errors, "production_handoff.scope_delta")
        if isinstance(value, list):
            values[key] = value
            for index, item in enumerate(value):
                if not isinstance(item, str) or not item.strip():
                    errors.append(f"production_handoff.scope_delta.{key}[{index}] must be a non-empty string")
    if "reason" in values and not values["reason"]:
        errors.append("production_handoff.scope_delta.reason must not be empty")
    removed = {item for item in values.get("removed", []) if isinstance(item, str)}
    added = {item for item in values.get("added", []) if isinstance(item, str)}
    if removed & asset_ids:
        errors.append("scope_delta removed Asset IDs must not remain in current asset_set: " + ", ".join(sorted(removed & asset_ids)))
    if added - asset_ids:
        errors.append("scope_delta added Asset IDs must exist in current asset_set: " + ", ".join(sorted(added - asset_ids)))


def validate_production_handoff(text: str) -> list[str]:
    root, errors = _parse_root(text)
    if root is None:
        return errors
    handoff = _require_type(root, "production_handoff", dict, errors)
    if not isinstance(handoff, dict):
        return errors
    project = _require_type(handoff, "project", dict, errors, "production_handoff")
    page_plan = _require_type(handoff, "page_plan", dict, errors, "production_handoff")
    asset_set = _require_type(handoff, "asset_set", list, errors, "production_handoff")
    source_assets = _require_type(handoff, "source_assets", list, errors, "production_handoff")
    for key in ["product_invariants", "global_visual_direction", "visual_benchmark_refs", "prohibited", "blocked_assets"]:
        _require_type(handoff, key, list, errors, "production_handoff")
    _non_empty_string(handoff, "creative_strategy_ref", errors, "production_handoff")
    errors.extend(_find_forbidden(handoff))

    asset_ids: set[str] = set()
    if isinstance(asset_set, list):
        asset_ids = _unique_ids(asset_set, "asset_id", errors, "production_handoff.asset_set")
        for index, asset in enumerate(asset_set):
            if not isinstance(asset, dict):
                continue
            path = f"production_handoff.asset_set[{index}]"
            for key in ["role", "slot", "primary_message", "status"]:
                _non_empty_string(asset, key, errors, path)
            mode = _non_empty_string(asset, "evidence_mode", errors, path)
            if mode is not None and mode not in EVIDENCE_MODES:
                errors.append(f"{path}.evidence_mode must be one of: {', '.join(sorted(EVIDENCE_MODES))}")

    if isinstance(source_assets, list):
        _unique_ids(source_assets, "source_id", errors, "production_handoff.source_assets")

    planned_ids: set[str] = set()
    ordered: list[str] = []
    if isinstance(page_plan, dict):
        for region in ["gallery", "enhanced_content", "other_required_regions"]:
            values = _require_type(page_plan, region, list, errors, "production_handoff.page_plan")
            if isinstance(values, list):
                for value in values:
                    if not isinstance(value, str) or not value:
                        errors.append(f"production_handoff.page_plan.{region} entries must be non-empty Asset IDs")
                    else:
                        planned_ids.add(value)
                        ordered.append(value)
    blocked_ids: set[str] = set()
    blocked = handoff.get("blocked_assets")
    if isinstance(blocked, list):
        for item in blocked:
            if isinstance(item, str) and item:
                blocked_ids.add(item)
            elif isinstance(item, dict) and isinstance(item.get("asset_id"), str):
                blocked_ids.add(item["asset_id"])
    missing_assets = sorted(planned_ids - asset_ids - blocked_ids)
    if missing_assets:
        errors.append("page_plan references Asset IDs absent from asset_set/blocked_assets: " + ", ".join(missing_assets))

    _validate_page_visual_system(handoff, asset_ids, [asset_id for asset_id in ordered if asset_id in asset_ids], errors)
    _validate_scope_delta(handoff, asset_ids, errors)

    if isinstance(project, dict):
        for key in ["market", "locale", "channel", "site", "category", "product", "offer", "page_target"]:
            _non_empty_string(project, key, errors, "production_handoff.project")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a global planning artifact")
    parser.add_argument("kind", choices=["project-brief", "creative-strategy", "production-handoff"])
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    try:
        text = args.path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"FAIL: could not read contract: {exc}")
        return 1
    validators = {
        "project-brief": validate_project_brief,
        "creative-strategy": validate_creative_strategy,
        "production-handoff": validate_production_handoff,
    }
    errors = validators[args.kind](text)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"PASS: {args.kind} contract is structurally valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
