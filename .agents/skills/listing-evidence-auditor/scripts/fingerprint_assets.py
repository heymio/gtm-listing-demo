#!/usr/bin/env python3
"""Global v0.3.3 strict physical fingerprinting and audit-packet validation."""

from __future__ import annotations

import argparse
import importlib.util
import io
import json
import zlib
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
LEGACY_PATH = HERE / "fingerprint_assets_legacy.py"
SPEC = importlib.util.spec_from_file_location("global_listing_fingerprint_legacy", LEGACY_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load legacy fingerprint helpers: {LEGACY_PATH}")
_legacy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(_legacy)

extension_family = _legacy.extension_family
EVIDENCE_MODES = {"SOURCE_FAITHFUL", "CREATIVE_MOCK", "PROOF_VISUAL"}


def _png_integrity(data: bytes) -> list[str]:
    errors: list[str] = []
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ["invalid PNG signature"]
    pos = 8
    saw_ihdr = False
    saw_idat = False
    saw_iend = False
    idat = bytearray()
    while pos < len(data):
        if pos + 12 > len(data):
            errors.append("truncated PNG chunk")
            break
        length = int.from_bytes(data[pos:pos + 4], "big")
        chunk_type = data[pos + 4:pos + 8]
        end = pos + 12 + length
        if end > len(data):
            errors.append("truncated PNG chunk payload")
            break
        payload = data[pos + 8:pos + 8 + length]
        expected_crc = int.from_bytes(data[pos + 8 + length:end], "big")
        actual_crc = zlib.crc32(chunk_type + payload) & 0xFFFFFFFF
        if expected_crc != actual_crc:
            errors.append(f"PNG CRC mismatch in {chunk_type.decode('ascii', 'replace')}")
        if not saw_ihdr:
            if chunk_type != b"IHDR" or length != 13:
                errors.append("PNG must start with a complete 13-byte IHDR")
            else:
                saw_ihdr = True
        if chunk_type == b"IDAT":
            saw_idat = True
            idat.extend(payload)
        if chunk_type == b"IEND":
            if length != 0:
                errors.append("PNG IEND must be empty")
            saw_iend = True
            pos = end
            if pos != len(data):
                errors.append("PNG contains trailing bytes after IEND")
            break
        pos = end
    if not saw_ihdr:
        errors.append("PNG IHDR missing")
    if not saw_idat:
        errors.append("PNG IDAT missing")
    if not saw_iend:
        errors.append("PNG IEND missing")
    if idat:
        try:
            zlib.decompress(bytes(idat))
        except zlib.error:
            errors.append("PNG IDAT zlib stream is invalid")
    return errors


def _jpeg_integrity(data: bytes) -> list[str]:
    errors: list[str] = []
    if not data.startswith(b"\xff\xd8"):
        return ["invalid JPEG SOI"]
    if not data.endswith(b"\xff\xd9"):
        errors.append("JPEG EOI marker missing")
    family, width, height = _legacy.inspect_image_bytes(data)
    if family != "jpeg" or not width or not height:
        errors.append("JPEG SOF dimensions missing or invalid")
    return errors


def _webp_integrity(data: bytes) -> list[str]:
    errors: list[str] = []
    if len(data) < 12 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return ["invalid WebP RIFF/WEBP header"]
    declared = int.from_bytes(data[4:8], "little") + 8
    if declared != len(data):
        errors.append("WebP RIFF size does not match file length")
    family, width, height = _legacy.inspect_image_bytes(data)
    if family != "webp" or not width or not height:
        errors.append("WebP dimensions missing or invalid")
    return errors


def _decoder_integrity(data: bytes, expected_family: str | None) -> list[str]:
    try:
        from PIL import Image, UnidentifiedImageError
    except Exception as exc:
        return [f"real image decoder unavailable (install Pillow): {exc}"]
    format_map = {"PNG": "png", "JPEG": "jpeg", "WEBP": "webp"}
    try:
        with Image.open(io.BytesIO(data)) as image:
            decoded_family = format_map.get((image.format or "").upper())
            decoded_size = image.size
            image.verify()
        with Image.open(io.BytesIO(data)) as image:
            image.load()
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError) as exc:
        return [f"real image decode failed: {exc}"]
    errors: list[str] = []
    if decoded_family != expected_family:
        errors.append(f"real decoder family mismatch: expected {expected_family!r}, decoded {decoded_family!r}")
    width, height = decoded_size
    if not isinstance(width, int) or width <= 0 or not isinstance(height, int) or height <= 0:
        errors.append("real decoder returned invalid image dimensions")
    return errors


def inspect_image_bytes(data: bytes) -> tuple[str | None, int | None, int | None]:
    return _legacy.inspect_image_bytes(data)


def _require_unique_identifier(packet: dict[str, Any], list_key: str, id_key: str) -> None:
    items = packet.get(list_key, [])
    if not isinstance(items, list):
        raise ValueError(f"{list_key} must be a list")
    seen: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"{list_key}[{index}] must be an object")
        value = item.get(id_key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"{list_key}[{index}].{id_key} must be a non-empty string")
        if value in seen:
            raise ValueError(f"duplicate {list_key}.{id_key}: {value}")
        seen.add(value)


def _validate_claim_bindings(asset: dict[str, Any], index: int) -> None:
    mode = asset.get("evidence_mode", "SOURCE_FAITHFUL")
    if mode not in EVIDENCE_MODES:
        raise ValueError(f"assets[{index}].evidence_mode invalid: {mode!r}")
    if mode != "PROOF_VISUAL":
        return
    bindings = asset.get("claim_bindings")
    if not isinstance(bindings, list) or not bindings:
        raise ValueError(f"assets[{index}] PROOF_VISUAL requires non-empty claim_bindings")
    seen: set[str] = set()
    for binding_index, binding in enumerate(bindings):
        if not isinstance(binding, dict):
            raise ValueError(f"assets[{index}].claim_bindings[{binding_index}] must be an object")
        claim_id = binding.get("claim_id")
        fact = binding.get("fact")
        sources = binding.get("authoritative_source_ids")
        if not isinstance(claim_id, str) or not claim_id.strip():
            raise ValueError(f"assets[{index}].claim_bindings[{binding_index}].claim_id missing")
        if claim_id in seen:
            raise ValueError(f"duplicate claim_id in PROOF_VISUAL binding: {claim_id}")
        seen.add(claim_id)
        if not isinstance(fact, str) or not fact.strip():
            raise ValueError(f"assets[{index}].claim_bindings[{binding_index}].fact missing")
        if not isinstance(sources, list) or not sources or any(not isinstance(x, str) or not x.strip() for x in sources):
            raise ValueError(f"assets[{index}].claim_bindings[{binding_index}].authoritative_source_ids must be non-empty")


def validate_audit_packet(packet: dict[str, Any]) -> None:
    if not isinstance(packet, dict):
        raise ValueError("audit packet root must be an object")
    for list_key, id_key in [
        ("assets", "asset_id"),
        ("approval_events", "approval_event_id"),
        ("prior_locked_assets", "asset_id"),
        ("slots", "slot_id"),
        ("expected_visual_roles", "asset_id"),
    ]:
        _require_unique_identifier(packet, list_key, id_key)
    for index, asset in enumerate(packet.get("assets", [])):
        _validate_claim_bindings(asset, index)


def fingerprint_asset(path: Path, project_root: Path) -> dict[str, Any]:
    result = _legacy.fingerprint_asset(path, project_root)
    if not result.get("exists") or not result.get("path_allowed"):
        return result
    resolved = Path(str(result.get("resolved_path")))
    try:
        data = resolved.read_bytes()
    except OSError as exc:
        result.setdefault("errors", []).append(f"could not reread image bytes: {exc}")
        return result
    family = result.get("signature_family")
    if family == "png":
        result["errors"].extend(_png_integrity(data))
    elif family == "jpeg":
        result["errors"].extend(_jpeg_integrity(data))
    elif family == "webp":
        result["errors"].extend(_webp_integrity(data))
    result["errors"].extend(_decoder_integrity(data, family))
    return result


def fingerprint_packet(packet: dict[str, Any], project_root: Path) -> dict[str, Any]:
    validate_audit_packet(packet)
    assets: dict[str, Any] = {}
    for asset in packet.get("assets", []):
        asset_id = asset["asset_id"]
        raw_path = Path(str(asset.get("path", "")))
        path = raw_path if raw_path.is_absolute() else project_root / raw_path
        result = fingerprint_asset(path, project_root)
        result["asset_id"] = asset_id
        assets[asset_id] = result
    return {
        "audit_version": packet.get("audit_version"),
        "project_id": packet.get("project_id"),
        "checkpoint": packet.get("checkpoint"),
        "project_root": str(project_root.resolve()),
        "assets": assets,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Fingerprint real asset files for evidence auditing")
    parser.add_argument("audit_input", type=Path)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        packet = json.loads(args.audit_input.read_text(encoding="utf-8"))
        result = fingerprint_packet(packet, args.project_root)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL: invalid audit input: {exc}")
        return 1
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
