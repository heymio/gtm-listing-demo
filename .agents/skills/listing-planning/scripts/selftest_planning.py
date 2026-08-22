#!/usr/bin/env python3
"""Regression tests for global listing-planning v0.3.2."""

from __future__ import annotations

from datetime import datetime, timezone
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def valid_handoff() -> str:
    return """production_handoff:
  project:
    market: DE
    locale: de-DE
    channel: amazon
    site: amazon.de
    category: project-defined
    product: Example Product
    offer: single
    page_target: single-listing
  page_plan:
    gallery:
      - G1
      - G2
    enhanced_content:
      - A1
    other_required_regions: []
  asset_set:
    - asset_id: G1
      role: gallery-native
      slot: G1
      primary_message: Core positioning
      evidence_mode: SOURCE_FAITHFUL
      status: READY
    - asset_id: G2
      role: gallery-native
      slot: G2
      primary_message: Mechanism proof
      evidence_mode: PROOF_VISUAL
      status: READY
    - asset_id: A1
      role: enhanced-content
      slot: A1
      primary_message: Lifestyle expansion
      evidence_mode: CREATIVE_MOCK
      status: READY
  source_assets:
    - source_id: SRC-P01
      role: real-product-source
      required_by:
        - G1
        - G2
        - A1
  product_invariants:
    - preserve exact product identity
  creative_strategy_ref: creative-strategy.yaml
  global_visual_direction:
    - product-first commercial hierarchy
  visual_benchmark_refs:
    - BENCH-01
  prohibited:
    - unsupported claims
  blocked_assets: []
  page_visual_system:
    asset_directions:
      - asset_id: G1
        visual_role: hero-positioning
        scene_family: clean-product-stage
        composition_family: centered-hero
        tone: bright-neutral
        product_scale: large
        proof_form: source-faithful-product
      - asset_id: G2
        visual_role: mechanism-proof
        scene_family: technical-detail
        composition_family: close-up-explainer
        tone: neutral-technical
        product_scale: close-up
        proof_form: mechanism
      - asset_id: A1
        visual_role: lifestyle-use
        scene_family: realistic-home
        composition_family: wide-lifestyle
        tone: warm-natural
        product_scale: medium
        proof_form: lifestyle
"""


def test_planning_files_exist() -> None:
    required = [
        SKILL_DIR / "SKILL.md",
        SCRIPT_DIR / "validate_planning_contracts.py",
        SCRIPT_DIR / "account_capability.py",
        SKILL_DIR / "templates" / "production-handoff.example.yaml",
        SKILL_DIR / "references" / "planning-qa.md",
        SKILL_DIR / "profiles" / "channels" / "amazon.md",
        SKILL_DIR / "profiles" / "channels" / "dtc-product-page.md",
        SKILL_DIR / "profiles" / "channels" / "retailer-pdp.md",
        SKILL_DIR / "profiles" / "channels" / "generic-marketplace.md",
        SKILL_DIR / "profiles" / "locales" / "ja-JP.md",
        SKILL_DIR / "profiles" / "locales" / "en-US.md",
        SKILL_DIR / "profiles" / "locales" / "de-DE.md",
        SKILL_DIR / "profiles" / "locales" / "it-IT.md",
        SKILL_DIR / "profiles" / "regions" / "eu.md",
    ]
    missing = [str(path.relative_to(SKILL_DIR)) for path in required if not path.is_file()]
    assert missing == [], missing


def test_planning_owns_complete_asset_set_and_global_profile_model() -> None:
    text = read(SKILL_DIR / "SKILL.md").casefold()
    for phrase in [
        "complete demo-required production set",
        "priority proof coverage",
        "page visual system",
        "evidence mode",
        "market",
        "locale",
        "region overlay",
        "channel profile",
        "category overlay",
        "project evidence",
    ]:
        assert phrase in text, phrase


def test_valid_global_handoff_passes() -> None:
    from validate_planning_contracts import validate_production_handoff

    assert validate_production_handoff(valid_handoff()) == []


def test_handoff_rejects_missing_or_invalid_evidence_mode() -> None:
    from validate_planning_contracts import validate_production_handoff

    missing = valid_handoff().replace("      evidence_mode: SOURCE_FAITHFUL\n", "", 1)
    invalid = valid_handoff().replace("SOURCE_FAITHFUL", "NOT_A_MODE", 1)
    assert any("evidence_mode" in error for error in validate_production_handoff(missing))
    assert any("evidence_mode" in error for error in validate_production_handoff(invalid))


def test_handoff_rejects_missing_or_unknown_visual_direction() -> None:
    from validate_planning_contracts import validate_production_handoff

    missing = valid_handoff().replace(
        "      - asset_id: A1\n        visual_role: lifestyle-use\n        scene_family: realistic-home\n        composition_family: wide-lifestyle\n        tone: warm-natural\n        product_scale: medium\n        proof_form: lifestyle\n",
        "",
        1,
    )
    unknown = valid_handoff().replace("      - asset_id: A1\n        visual_role: lifestyle-use", "      - asset_id: MISSING-ASSET\n        visual_role: lifestyle-use", 1)
    assert any("missing directions" in error.casefold() for error in validate_production_handoff(missing))
    assert any("MISSING-ASSET" in error for error in validate_production_handoff(unknown))


def test_handoff_rejects_accidental_adjacent_visual_duplicate() -> None:
    from validate_planning_contracts import validate_production_handoff

    text = valid_handoff()
    text = text.replace("scene_family: technical-detail", "scene_family: clean-product-stage", 1)
    text = text.replace("composition_family: close-up-explainer", "composition_family: centered-hero", 1)
    text = text.replace("tone: neutral-technical", "tone: bright-neutral", 1)
    text = text.replace("product_scale: close-up", "product_scale: large", 1)
    text = text.replace("proof_form: mechanism", "proof_form: source-faithful-product", 1)
    errors = validate_production_handoff(text)
    assert any("adjacent visual direction" in error.casefold() for error in errors)


def test_handoff_allows_intentional_adjacent_match_with_note() -> None:
    from validate_planning_contracts import validate_production_handoff

    text = valid_handoff()
    text = text.replace("scene_family: technical-detail", "scene_family: clean-product-stage", 1)
    text = text.replace("composition_family: close-up-explainer", "composition_family: centered-hero", 1)
    text = text.replace("tone: neutral-technical", "tone: bright-neutral", 1)
    text = text.replace("product_scale: close-up", "product_scale: large", 1)
    text = text.replace(
        "proof_form: mechanism",
        "proof_form: source-faithful-product\n        neighbor_contrast_note: Intentional matched pair for comparison",
        1,
    )
    assert validate_production_handoff(text) == []


def test_recent_account_capability_reuses_only_valid_nonconflicted_record() -> None:
    from account_capability import resolve_capability

    profile = {
        "channel": "amazon",
        "account_scope": "brand-account",
        "capabilities": {"enhanced_content": True},
        "verified_at": "2026-08-01",
        "source_ref": "private-team-context",
    }
    reused = resolve_capability(
        profile,
        "enhanced_content",
        now=datetime(2026, 8, 22, tzinfo=timezone.utc),
        max_age_days=90,
        expected_channel="amazon",
    )
    assert reused["status"] == "REUSE"
    assert reused["value"] is True

    conflict = resolve_capability(
        profile,
        "enhanced_content",
        now=datetime(2026, 8, 22, tzinfo=timezone.utc),
        max_age_days=90,
        expected_channel="amazon",
        conflicting=True,
    )
    wrong_channel = resolve_capability(
        profile,
        "enhanced_content",
        now=datetime(2026, 8, 22, tzinfo=timezone.utc),
        max_age_days=90,
        expected_channel="retailer-pdp",
    )
    assert conflict["status"] == "VERIFY"
    assert wrong_channel["status"] == "VERIFY"


def test_planning_core_has_no_japan_or_product_specific_defaults() -> None:
    paths = [SKILL_DIR / "SKILL.md"]
    paths.extend(sorted((SKILL_DIR / "references").glob("*.md")))
    paths.extend(sorted((SKILL_DIR / "profiles" / "channels").glob("*.md")))
    joined = "\n".join(read(path) for path in paths if path.is_file()).casefold()
    for forbidden in ["amazon.co.jp", "switchbot", "light bars", "s30 mini"]:
        assert forbidden not in joined, forbidden


def main() -> int:
    tests = [value for name, value in globals().items() if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"PASS: {len(tests)} global-planning tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
