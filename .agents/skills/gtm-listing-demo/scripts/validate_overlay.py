#!/usr/bin/env python3
"""Validate the global v0.3.2 overlay/distribution shape and leakage boundary."""

from __future__ import annotations

from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[2]
SKILLS_ROOT = REPO_ROOT / ".agents" / "skills"
INTERNAL = ["listing-planning", "listing-production", "listing-hardening", "listing-evidence-auditor"]
FORBIDDEN_GENERIC_DEFAULTS = ["amazon.co.jp", "switchbot", "light bars", "s30 mini"]
PROFILE_MIRRORS = [
    ("channels", "_template.md"),
    ("channels", "amazon.md"),
    ("channels", "dtc-product-page.md"),
    ("channels", "generic-marketplace.md"),
    ("channels", "retailer-pdp.md"),
    ("locales", "_template.md"),
    ("locales", "ja-JP.md"),
    ("locales", "en-US.md"),
    ("locales", "de-DE.md"),
    ("locales", "it-IT.md"),
    ("regions", "_template.md"),
    ("regions", "eu.md"),
    ("categories", "_template.md"),
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def main() -> int:
    version = REPO_ROOT / "VERSION"
    if not version.is_file() or version.read_text(encoding="utf-8").strip() != "0.3.2":
        fail("VERSION must be exactly 0.3.2 for this migration")

    for name in ["gtm-listing-demo", *INTERNAL]:
        skill = SKILLS_ROOT / name / "SKILL.md"
        if not skill.is_file():
            fail(f"missing sibling Skill: {name}")

    # The user-facing Skill keeps discoverable compatibility profile copies,
    # while listing-planning owns runtime profile loading. They must never drift.
    public_profiles = SKILLS_ROOT / "gtm-listing-demo" / "profiles"
    planning_profiles = SKILLS_ROOT / "listing-planning" / "profiles"
    for group, filename in PROFILE_MIRRORS:
        public_path = public_profiles / group / filename
        planning_path = planning_profiles / group / filename
        if not public_path.is_file():
            fail(f"missing public compatibility profile: {group}/{filename}")
        if not planning_path.is_file():
            fail(f"missing Planning profile mirror: {group}/{filename}")
        if public_path.read_text(encoding="utf-8") != planning_path.read_text(encoding="utf-8"):
            fail(f"profile mirror drift: {group}/{filename}")

    package_text = (SKILL_DIR / "scripts" / "package_skill.py").read_text(encoding="utf-8").casefold()
    for name in INTERNAL:
        if name not in package_text:
            fail(f"compatibility package does not include {name}")
    for filename in ["validate_demo_html.py", "fingerprint_assets.py", "production_state.py", "validate_planning_contracts.py", "single_context_limitation"]:
        if filename not in package_text:
            fail(f"compatibility package contract missing {filename}")

    codex_script = REPO_ROOT / "scripts" / "package_codex_bundle.py"
    if not codex_script.is_file():
        fail("scripts/package_codex_bundle.py missing")
    codex_text = codex_script.read_text(encoding="utf-8").casefold()
    for name in ["gtm-listing-demo", *INTERNAL]:
        if name not in codex_text:
            fail(f"Codex bundle contract does not include {name}")

    generic_paths = [
        SKILLS_ROOT / "gtm-listing-demo" / "SKILL.md",
        SKILLS_ROOT / "listing-planning" / "SKILL.md",
        SKILLS_ROOT / "listing-production" / "SKILL.md",
        SKILLS_ROOT / "listing-hardening" / "SKILL.md",
        SKILLS_ROOT / "listing-evidence-auditor" / "SKILL.md",
    ]
    for root in ["listing-planning", "listing-production", "listing-hardening", "listing-evidence-auditor"]:
        generic_paths.extend((SKILLS_ROOT / root / "references").glob("*.md"))
    joined = "\n".join(path.read_text(encoding="utf-8") for path in generic_paths if path.is_file()).casefold()
    for forbidden in FORBIDDEN_GENERIC_DEFAULTS:
        if forbidden in joined:
            fail(f"generic core leakage: {forbidden}")

    print("PASS: global five-Skill overlay/distribution contract is valid")
    print(f"PASS: {len(PROFILE_MIRRORS)} public/Planning profile mirrors are identical")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
