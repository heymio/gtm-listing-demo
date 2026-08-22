#!/usr/bin/env python3
"""Regression tests for the generic listing evidence auditor."""

from __future__ import annotations

import hashlib
import importlib
import struct
import sys
import zlib
from pathlib import Path
from tempfile import TemporaryDirectory

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))


def make_png(width: int, height: int) -> bytes:
    signature = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    chunk = b"IHDR" + ihdr_data
    ihdr = struct.pack(">I", len(ihdr_data)) + chunk + struct.pack(">I", zlib.crc32(chunk) & 0xFFFFFFFF)
    return signature + ihdr


def packet_for(asset_id: str, path: str) -> dict:
    return {
        "audit_version": "1",
        "project_id": "fixture",
        "checkpoint": "pre-demo",
        "assets": [{
            "asset_id": asset_id,
            "path": path,
            "claimed_role": "gallery-native",
            "allowed_slots": ["gallery-03"],
            "claimed_approval_event_id": None,
            "claimed_parent_asset_id": None,
            "claimed_transform": None,
        }],
        "slots": [{"slot_id": "gallery-03", "required_asset_ids": [asset_id]}],
        "approval_events": [],
        "prior_locked_assets": [],
        "expected_visual_roles": [{"asset_id": asset_id, "role": "gallery-native"}],
    }


def fingerprints_for(asset_id: str, sha: str) -> dict:
    return {"assets": {asset_id: {
        "asset_id": asset_id, "exists": True, "path_allowed": True, "sha256": sha,
        "byte_size": 123, "signature_family": "png", "extension_family": "png",
        "width": 2000, "height": 2000, "errors": [],
    }}}


def semantic(asset_id: str, actual_role: str, source: str = "independent_context") -> dict:
    return {"assets": {asset_id: {
        "asset_id": asset_id,
        "review_source": source,
        "actual_role": actual_role,
        "role_status": "ROLE_MATCH" if actual_role == "gallery-native" else "ROLE_MISMATCH",
        "notes": "fixture",
    }}}


def test_auditor_files_exist() -> None:
    required = [
        SKILL_DIR / "SKILL.md",
        SCRIPT_DIR / "fingerprint_assets.py",
        SCRIPT_DIR / "reconcile_evidence.py",
    ]
    missing = [str(path.relative_to(SKILL_DIR)) for path in required if not path.is_file()]
    assert missing == [], missing


def test_real_png_fingerprint_recomputes_sha_dimensions_and_path() -> None:
    from fingerprint_assets import fingerprint_asset
    with TemporaryDirectory() as directory:
        root = Path(directory)
        image = root / "asset.png"
        image.write_bytes(make_png(3, 2))
        result = fingerprint_asset(image, root)
        assert result["exists"] is True
        assert result["path_allowed"] is True
        assert result["sha256"] == hashlib.sha256(image.read_bytes()).hexdigest()
        assert (result["width"], result["height"]) == (3, 2)
        assert result["signature_family"] == "png"


def test_missing_path_escape_and_fake_image_are_rejected() -> None:
    from fingerprint_assets import fingerprint_asset
    with TemporaryDirectory() as directory:
        base = Path(directory)
        root = base / "root"
        root.mkdir()
        missing = fingerprint_asset(root / "missing.png", root)
        assert missing["exists"] is False
        outside = base / "outside.png"
        outside.write_bytes(make_png(1, 1))
        assert fingerprint_asset(outside, root)["path_allowed"] is False
        fake = root / "fake.png"
        fake.write_bytes(b"not really png")
        fake_result = fingerprint_asset(fake, root)
        assert fake_result["signature_family"] is None
        assert "invalid or unsupported image signature" in fake_result["errors"]


def test_extension_signature_mismatch_is_rejected() -> None:
    from fingerprint_assets import fingerprint_asset
    with TemporaryDirectory() as directory:
        root = Path(directory)
        image = root / "asset.jpg"
        image.write_bytes(make_png(1, 1))
        result = fingerprint_asset(image, root)
        assert result["signature_family"] == "png"
        assert result["extension_family"] == "jpeg"
        assert "extension/signature mismatch" in result["errors"]


def test_same_name_different_sha_cannot_restore_prior_lock() -> None:
    from reconcile_evidence import reconcile_evidence
    packet = packet_for("G03", "assets/G03.png")
    packet["prior_locked_assets"] = [{
        "asset_id": "G03", "sha256": "a" * 64,
        "approved_role": "gallery-native", "approved_slots": ["gallery-03"],
    }]
    result = reconcile_evidence(packet, fingerprints_for("G03", "b" * 64), semantic("G03", "gallery-native"), True)
    assert result["assets"]["G03"]["provenance"] != "EXACT_RECOVERY_VERIFIED"
    assert result["assets"]["G03"]["effective_status"] != "VERIFIED"


def test_explicit_approval_binds_exact_sha_role_and_scope() -> None:
    from reconcile_evidence import reconcile_evidence
    packet = packet_for("G03", "assets/G03.png")
    packet["approval_events"] = [{
        "approval_event_id": "APP-1", "type": "explicit_user_approval", "asset_id": "G03",
        "sha256": "c" * 64, "approved_role": "gallery-native", "approved_slots": ["gallery-03"],
    }]
    packet["assets"][0]["claimed_approval_event_id"] = "APP-1"
    mismatch = reconcile_evidence(packet, fingerprints_for("G03", "c" * 64), semantic("G03", "enhanced-content-board"), True)
    assert mismatch["assets"]["G03"]["approval_match"] is False
    assert mismatch["assets"]["G03"]["effective_status"] == "INVALIDATED"


def test_same_context_semantic_review_cannot_self_certify() -> None:
    from reconcile_evidence import reconcile_evidence
    packet = packet_for("G03", "assets/G03.png")
    result = reconcile_evidence(packet, fingerprints_for("G03", "d" * 64), semantic("G03", "gallery-native", "same_agent_inline"), False)
    assert result["assets"]["G03"]["semantic_role_status"] in {"ROLE_AMBIGUOUS", "NOT_VISUALLY_AUDITED"}
    assert result["assets"]["G03"]["effective_status"] in {"HUMAN_REVIEW_REQUIRED", "UNVERIFIED"}


def test_duplicate_identifiers_fail_before_dictionary_overwrite() -> None:
    from fingerprint_assets import validate_audit_packet
    cases = []
    packet = packet_for("A1", "a.png"); packet["assets"].append(dict(packet["assets"][0])); cases.append(packet)
    packet = packet_for("A1", "a.png"); packet["slots"].append(dict(packet["slots"][0])); cases.append(packet)
    packet = packet_for("A1", "a.png"); packet["expected_visual_roles"].append(dict(packet["expected_visual_roles"][0])); cases.append(packet)
    packet = packet_for("A1", "a.png"); packet["approval_events"] = [{"approval_event_id": "APP"}, {"approval_event_id": "APP"}]; cases.append(packet)
    for packet in cases:
        try:
            validate_audit_packet(packet)
        except ValueError as exc:
            assert "duplicate" in str(exc).casefold()
        else:
            raise AssertionError("duplicate audit identifiers must fail fast")


def test_real_file_entrypoint_exists_and_cli_cannot_self_assert_independence() -> None:
    module = importlib.import_module("reconcile_evidence")
    assert callable(getattr(module, "reconcile_from_files", None))
    text = (SCRIPT_DIR / "reconcile_evidence.py").read_text(encoding="utf-8")
    assert 'parser.add_argument("project_root"' in text
    assert 'parser.add_argument("fingerprints"' not in text
    assert "--independent-semantic" not in text


def test_required_asset_set_fails_when_one_member_is_not_final_usable() -> None:
    from reconcile_evidence import reconcile_evidence
    packet = packet_for("G1", "assets/G1.png")
    packet["assets"] = []
    packet["slots"] = []
    payload = {"assets": {}}
    reviews = {"assets": {}}
    for asset_id in ["G1", "G2", "G3"]:
        item = packet_for(asset_id, f"assets/{asset_id}.png")["assets"][0]
        item["allowed_slots"] = [f"gallery-{asset_id[-1]}"]
        packet["assets"].append(item)
        packet["slots"].append({"slot_id": f"gallery-{asset_id[-1]}", "required_asset_ids": [asset_id]})
        payload["assets"][asset_id] = fingerprints_for(asset_id, asset_id.lower().encode().hex().ljust(64, "0")[:64])["assets"][asset_id]
        actual_role = "other-role" if asset_id == "G3" else "gallery-native"
        reviews["assets"][asset_id] = semantic(asset_id, actual_role)["assets"][asset_id]
    result = reconcile_evidence(packet, payload, reviews, True)
    assert result["asset_set_gate"]["status"] == "FAIL"


def test_skill_contract_refuses_planner_self_certification() -> None:
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8").casefold()
    for phrase in ["do not trust filenames", "do not trust asset ids", "do not trust agent-authored hashes", "independent context", "human_review_required", "must not repair"]:
        assert phrase in skill, phrase


def main() -> int:
    tests = [value for name, value in globals().items() if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"PASS: {len(tests)} global-evidence-auditor tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
