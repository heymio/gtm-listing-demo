#!/usr/bin/env python3
"""Regression tests for global listing-production v0.3.2."""

from __future__ import annotations

import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))


def base_packet() -> dict:
    return {
        "asset_id": "G1",
        "role": {"channel": "amazon", "region": "gallery", "slot": "G1", "asset_type": "gallery-native"},
        "objective": {"shopper_task": "understand the core purchase reason", "primary_message": "Core value"},
        "strategy_context": {"consumer_barrier": "unclear value", "core_tension": "benefit vs complexity", "proof_principle": "show direct evidence"},
        "evidence": {"allowed": ["confirmed fact"], "forbidden": ["unsupported claim"]},
        "evidence_mode": "SOURCE_FAITHFUL",
        "product_sources": {"identity_required": ["SRC-ID"], "proof_required": []},
        "benchmark": {"references": ["BENCH-01"], "learn_from": ["hierarchy"], "reuse_asset": False},
        "composition": {"product_role": "hero", "environment": "project-defined", "information_density": "low", "one_image_focus": True},
        "set_context": {
            "page_visual_direction": {
                "asset_id": "G1", "visual_role": "hero-positioning", "scene_family": "clean-stage",
                "composition_family": "centered", "tone": "bright", "product_scale": "large", "proof_form": "product",
            },
            "nearest_neighbors": [],
        },
        "output": {"aspect_ratio": "1:1", "final_role": "Gallery", "quantity": 1},
        "must_preserve": ["product identity"],
        "must_not_generate": ["fictional product structure"],
    }


def handoff() -> dict:
    return {
        "page_plan": {"gallery": ["G1", "G2", "G3"], "enhanced_content": ["A1"], "other_required_regions": []},
        "asset_set": [
            {"asset_id": "G1", "evidence_mode": "SOURCE_FAITHFUL"},
            {"asset_id": "G2", "evidence_mode": "CREATIVE_MOCK"},
            {"asset_id": "G3", "evidence_mode": "PROOF_VISUAL"},
            {"asset_id": "A1", "evidence_mode": "CREATIVE_MOCK"},
        ],
        "page_visual_system": {"asset_directions": [
            {"asset_id": "G1", "visual_role": "hero", "scene_family": "clean", "composition_family": "centered", "tone": "bright", "product_scale": "large", "proof_form": "product"},
            {"asset_id": "G2", "visual_role": "lifestyle", "scene_family": "home", "composition_family": "wide", "tone": "warm", "product_scale": "medium", "proof_form": "lifestyle"},
            {"asset_id": "G3", "visual_role": "proof", "scene_family": "technical", "composition_family": "close", "tone": "neutral", "product_scale": "close-up", "proof_form": "mechanism"},
            {"asset_id": "A1", "visual_role": "scenario", "scene_family": "workspace", "composition_family": "contextual", "tone": "natural", "product_scale": "medium", "proof_form": "scenario-flow"},
        ]},
    }


def direction(asset_id: str, scene: str, comp: str, tone: str, scale: str, proof: str, role: str = "") -> dict:
    return {"asset_id": asset_id, "scene_family": scene, "composition_family": comp, "tone": tone, "product_scale": scale, "proof_form": proof, "message_role": role}


def test_production_files_exist() -> None:
    required = [
        SKILL_DIR / "SKILL.md",
        SKILL_DIR / "scripts" / "project_asset_packet.py",
        SKILL_DIR / "scripts" / "production_state.py",
        SKILL_DIR / "scripts" / "set_level_qa.py",
        SKILL_DIR / "scripts" / "cleanup_policy.py",
        SKILL_DIR / "references" / "production-qa.md",
        SKILL_DIR / "references" / "visual-production.md",
        SKILL_DIR / "templates" / "asset-packet.example.yaml",
        SKILL_DIR / "templates" / "production-freeze.example.yaml",
    ]
    missing = [str(path.relative_to(SKILL_DIR)) for path in required if not path.is_file()]
    assert missing == [], missing


def test_v032_packet_requires_evidence_mode_and_set_context() -> None:
    from project_asset_packet import validate_asset_packet
    packet = base_packet()
    packet.pop("evidence_mode")
    packet.pop("set_context")
    errors = validate_asset_packet(packet)
    assert any("evidence_mode" in e for e in errors)
    assert any("set_context" in e for e in errors)


def test_projection_keeps_production_only_context() -> None:
    from project_asset_packet import project_generation_context
    packet = base_packet()
    packet["project_state_manifest"] = {"status": "COMPLETE"}
    packet["auditor_evidence"] = {"G1": "VERIFIED"}
    projected = project_generation_context(packet)
    encoded = json.dumps(projected).casefold()
    for forbidden in ["project_state", "auditor", "delivery_parity", "gate"]:
        assert forbidden not in encoded


def test_creative_mock_requires_identity_but_can_tolerate_missing_proof() -> None:
    from project_asset_packet import evaluate_source_readiness
    packet = base_packet()
    packet["evidence_mode"] = "CREATIVE_MOCK"
    packet["product_sources"] = {"identity_required": ["SRC-ID"], "proof_required": ["SRC-PROOF"]}
    missing_identity = evaluate_source_readiness(packet, {"SRC-PROOF"})
    assert missing_identity["status"] == "BLOCKED"
    missing_proof = evaluate_source_readiness(packet, {"SRC-ID"})
    assert missing_proof["status"] == "READY_WITH_LIMITATION"


def test_selection_lock_blocks_new_candidate_output_and_status_until_reopen() -> None:
    from production_state import add_candidate, select_candidate, set_creative_status
    ledger = add_candidate({}, "G1", "G1-v1", "file:g1-v1")
    ledger = select_candidate(ledger, "G1", "G1-v1")
    for action in [
        lambda: add_candidate(ledger, "G1", "G1-v2", "file:g1-v2"),
        lambda: set_creative_status(ledger, "G1", "REVISE"),
        lambda: set_creative_status(ledger, "G1", "USER_APPROVED", output_ref="file:g1-v2"),
    ]:
        try:
            action()
        except ValueError as exc:
            assert "reopen" in str(exc).casefold()
        else:
            raise AssertionError("selected asset must remain locked until explicit reopen")


def test_reopen_preserves_candidate_history() -> None:
    from production_state import add_candidate, select_candidate, reopen_asset
    ledger = add_candidate({}, "G1", "G1-v1", "file:g1-v1")
    ledger = select_candidate(ledger, "G1", "G1-v1")
    ledger = reopen_asset(ledger, "G1", "user asked for revision")
    ledger = add_candidate(ledger, "G1", "G1-v2", "file:g1-v2")
    assert [row["candidate_id"] for row in ledger["assets"]["G1"]["candidates"]] == ["G1-v1", "G1-v2"]


def test_set_level_qa_flags_repetition() -> None:
    from set_level_qa import evaluate_set
    result = evaluate_set([
        direction("G1", "home", "wide", "warm", "medium", "lifestyle"),
        direction("G2", "home", "wide", "warm", "medium", "lifestyle"),
    ])
    assert result["status"] == "REVISE"


def test_set_level_qa_reviews_repeated_message_role_or_proof_form() -> None:
    from set_level_qa import evaluate_set
    role_result = evaluate_set([
        direction("G1", "s1", "c1", "t1", "large", "product", "core-benefit"),
        direction("G2", "s2", "c2", "t2", "medium", "mechanism", "core-benefit"),
    ])
    assert role_result["status"] == "REVIEW"
    proof_result = evaluate_set([
        direction("G1", "s1", "c1", "t1", "large", "lifestyle"),
        direction("G2", "s2", "c2", "t2", "medium", "lifestyle"),
        direction("G3", "s3", "c3", "t3", "close", "lifestyle"),
    ])
    assert proof_result["status"] == "REVIEW"


def test_scope_delta_removal_keeps_handoff_views_aligned() -> None:
    from production_state import apply_scope_delta
    updated = apply_scope_delta(handoff(), {"added": [], "removed": ["G3"], "changed": [], "reason": ["scope narrowed"]})
    assert [x["asset_id"] for x in updated["asset_set"]] == ["G1", "G2", "A1"]
    assert updated["page_plan"]["gallery"] == ["G1", "G2"]
    assert [x["asset_id"] for x in updated["page_visual_system"]["asset_directions"]] == ["G1", "G2", "A1"]


def test_added_or_changed_scope_returns_to_planning() -> None:
    from production_state import apply_scope_delta
    for delta in [
        {"added": [{"asset_id": "G4"}], "removed": [], "changed": [], "reason": ["new asset"]},
        {"added": [], "removed": [], "changed": [{"asset_id": "G2"}], "reason": ["role changed"]},
    ]:
        try:
            apply_scope_delta(handoff(), delta)
        except ValueError as exc:
            assert "planning" in str(exc).casefold()
        else:
            raise AssertionError("Production must not invent added/changed planning scope")


def approved_ledger() -> dict:
    refs = {asset_id: f"file:{asset_id.lower()}-v1" for asset_id in ["G1", "G2", "G3", "A1"]}
    return {
        "assets": {asset_id: {"status": "USER_APPROVED", "current_output_ref": ref} for asset_id, ref in refs.items()},
        "set_qa": {
            "status": "CLEAR",
            "reviewed_asset_ids": list(refs),
            "reviewed_output_refs": dict(refs),
            "visual_review_ref": "contact-sheet:final-v1",
        },
    }


def test_freeze_requires_current_exact_output_bound_set_review() -> None:
    from production_state import build_production_freeze
    ledger = approved_ledger()
    assert build_production_freeze(handoff(), ledger)["ready_for_hardening"] is True
    ledger["assets"]["G2"]["current_output_ref"] = "file:g2-v2"
    stale = build_production_freeze(handoff(), ledger)
    assert stale["ready_for_hardening"] is False
    assert stale["set_qa_status"] == "STALE"


def test_smallest_sufficient_cleanup() -> None:
    from cleanup_policy import plan_cleanup
    repetition = plan_cleanup("SET_REPETITION", affected_assets=["G1", "G2", "G3"], approved_assets=["G1", "G2"])
    assert repetition["reopen"] == ["G3"]
    mock = plan_cleanup("EVIDENCE_LIMITATION", affected_assets=["A1"], approved_assets=["A1"], evidence_modes={"A1": "CREATIVE_MOCK"})
    assert mock["reopen"] == []


def test_production_core_has_no_japan_specific_defaults() -> None:
    paths = [SKILL_DIR / "SKILL.md"] + sorted((SKILL_DIR / "references").glob("*.md"))
    joined = "\n".join(path.read_text(encoding="utf-8") for path in paths if path.is_file()).casefold()
    for forbidden in ["amazon.co.jp", "switchbot", "light bars", "s30 mini"]:
        assert forbidden not in joined


def main() -> int:
    tests = [value for name, value in globals().items() if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"PASS: {len(tests)} global-production tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
