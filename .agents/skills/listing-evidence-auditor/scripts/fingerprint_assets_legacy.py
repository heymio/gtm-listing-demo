#!/usr/bin/env python3
"""Recompute physical identity for listing evidence assets from real files."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any


def extension_family(suffix: str) -> str | None:
    value = suffix.lower().lstrip(".")
    if value == "png": return "png"
    if value in {"jpg", "jpeg"}: return "jpeg"
    if value == "webp": return "webp"
    return None


def _jpeg_dimensions(data: bytes) -> tuple[int | None, int | None]:
    if len(data) < 4 or not data.startswith(b"\xff\xd8"):
        return None, None
    sof_markers = {0xC0,0xC1,0xC2,0xC3,0xC5,0xC6,0xC7,0xC9,0xCA,0xCB,0xCD,0xCE,0xCF}
    i = 2
    while i + 1 < len(data):
        if data[i] != 0xFF:
            i += 1; continue
        while i < len(data) and data[i] == 0xFF: i += 1
        if i >= len(data): break
        marker = data[i]; i += 1
        if marker in {0xD8, 0xD9} or 0xD0 <= marker <= 0xD7: continue
        if i + 2 > len(data): break
        segment_length = int.from_bytes(data[i:i+2], "big")
        if segment_length < 2 or i + segment_length > len(data): break
        if marker in sof_markers and segment_length >= 7:
            height = int.from_bytes(data[i+3:i+5], "big")
            width = int.from_bytes(data[i+5:i+7], "big")
            return width, height
        i += segment_length
    return None, None


def _webp_dimensions(data: bytes) -> tuple[int | None, int | None]:
    if len(data) < 30 or data[0:4] != b"RIFF" or data[8:12] != b"WEBP": return None, None
    chunk = data[12:16]
    if chunk == b"VP8X" and len(data) >= 30:
        return 1 + int.from_bytes(data[24:27], "little"), 1 + int.from_bytes(data[27:30], "little")
    if chunk == b"VP8L" and len(data) >= 25 and data[20] == 0x2F:
        value = int.from_bytes(data[21:25], "little")
        return (value & 0x3FFF) + 1, ((value >> 14) & 0x3FFF) + 1
    if chunk == b"VP8 " and len(data) >= 30:
        marker = data.find(b"\x9d\x01\x2a", 20, 30)
        if marker >= 0 and marker + 7 <= len(data):
            return int.from_bytes(data[marker+3:marker+5], "little") & 0x3FFF, int.from_bytes(data[marker+5:marker+7], "little") & 0x3FFF
    return None, None


def inspect_image_bytes(data: bytes) -> tuple[str | None, int | None, int | None]:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        if len(data) >= 24 and data[12:16] == b"IHDR":
            width, height = struct.unpack(">II", data[16:24]); return "png", width, height
        return "png", None, None
    if data.startswith(b"\xff\xd8"):
        width, height = _jpeg_dimensions(data); return "jpeg", width, height
    if len(data) >= 12 and data[0:4] == b"RIFF" and data[8:12] == b"WEBP":
        width, height = _webp_dimensions(data); return "webp", width, height
    return None, None, None


def _require_unique_identifier(packet: dict[str, Any], list_key: str, id_key: str) -> None:
    items = packet.get(list_key, [])
    if not isinstance(items, list): raise ValueError(f"{list_key} must be a list")
    seen: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict): raise ValueError(f"{list_key}[{index}] must be an object")
        value = item.get(id_key)
        if not isinstance(value, str) or not value: raise ValueError(f"{list_key}[{index}].{id_key} must be a non-empty string")
        if value in seen: raise ValueError(f"duplicate {list_key}.{id_key}: {value}")
        seen.add(value)


def validate_audit_packet(packet: dict[str, Any]) -> None:
    if not isinstance(packet, dict): raise ValueError("audit packet root must be an object")
    for list_key, id_key in [("assets","asset_id"),("approval_events","approval_event_id"),("prior_locked_assets","asset_id"),("slots","slot_id"),("expected_visual_roles","asset_id")]:
        _require_unique_identifier(packet, list_key, id_key)


def fingerprint_asset(path: Path, project_root: Path) -> dict[str, Any]:
    root = project_root.resolve(); resolved = path.resolve(); path_allowed = resolved == root or root in resolved.parents
    result: dict[str, Any] = {"resolved_path":str(resolved),"exists":resolved.is_file(),"path_allowed":path_allowed,"sha256":None,"byte_size":None,"signature_family":None,"extension_family":extension_family(resolved.suffix),"width":None,"height":None,"errors":[]}
    if not path_allowed:
        result["errors"].append("path outside allowed project root"); return result
    if not resolved.is_file():
        result["errors"].append("missing file"); return result
    data = resolved.read_bytes(); result["sha256"] = hashlib.sha256(data).hexdigest(); result["byte_size"] = len(data)
    family, width, height = inspect_image_bytes(data); result["signature_family"] = family; result["width"] = width; result["height"] = height
    extension = result["extension_family"]
    if extension is None: result["errors"].append("unsupported image extension")
    if family is None: result["errors"].append("invalid or unsupported image signature")
    elif extension is not None and extension != family: result["errors"].append("extension/signature mismatch")
    if family is not None and (not isinstance(width,int) or isinstance(width,bool) or width <= 0 or not isinstance(height,int) or isinstance(height,bool) or height <= 0):
        result["errors"].append("invalid or missing image dimensions")
    return result


def fingerprint_packet(packet: dict[str, Any], project_root: Path) -> dict[str, Any]:
    validate_audit_packet(packet)
    assets: dict[str, Any] = {}
    for asset in packet.get("assets", []):
        asset_id = asset["asset_id"]; raw_path = Path(str(asset.get("path", ""))); path = raw_path if raw_path.is_absolute() else project_root / raw_path
        result = fingerprint_asset(path, project_root); result["asset_id"] = asset_id; assets[asset_id] = result
    return {"audit_version":packet.get("audit_version"),"project_id":packet.get("project_id"),"checkpoint":packet.get("checkpoint"),"project_root":str(project_root.resolve()),"assets":assets}


def main() -> int:
    parser = argparse.ArgumentParser(description="Fingerprint real asset files for evidence auditing")
    parser.add_argument("audit_input", type=Path); parser.add_argument("project_root", type=Path); parser.add_argument("--output", type=Path); args = parser.parse_args()
    try:
        packet = json.loads(args.audit_input.read_text(encoding="utf-8")); result = fingerprint_packet(packet, args.project_root)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL: invalid audit input: {exc}"); return 1
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output: args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(text + "\n", encoding="utf-8")
    else: print(text)
    return 0

if __name__ == "__main__": raise SystemExit(main())
