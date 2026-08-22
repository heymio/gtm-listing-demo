#!/usr/bin/env python3
"""Regression tests for the global gtm-listing-demo thin router."""

from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[2]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_router_routes_stage_local_execution_planes() -> None:
    routing = read(SKILL_DIR / "references" / "routing.md")
    folded = routing.casefold()
    for phrase in [
        "stage 0–7",
        "listing-planning",
        "stage 7.5–8",
        "listing-production",
        "stage 8.5–10",
        "listing-hardening",
        "listing-evidence-auditor",
    ]:
        assert phrase in folded, phrase


def test_router_preserves_major_checkpoint_and_retry_behavior() -> None:
    text = read(SKILL_DIR / "SKILL.md").casefold()
    for phrase in ["major stage checkpoint", "transition command", "retry budget", "context firewall"]:
        assert phrase in text, phrase


def test_router_default_checkpoint_is_concise() -> None:
    routing = read(SKILL_DIR / "references" / "routing.md")
    for phrase in ["Done:", "Open:", "Next:"]:
        assert phrase in routing, phrase


def test_global_core_has_no_japan_or_product_specific_defaults() -> None:
    paths = [
        SKILL_DIR / "SKILL.md",
        SKILL_DIR / "references" / "routing.md",
    ]
    joined = "\n".join(read(path) for path in paths if path.is_file()).casefold()
    for forbidden in ["amazon.co.jp", "switchbot", "light bars", "s30 mini"]:
        assert forbidden not in joined, forbidden


def test_repository_keeps_one_user_facing_invocation() -> None:
    text = read(SKILL_DIR / "SKILL.md")
    assert "$gtm-listing-demo" in text
    assert "listing-planning" in text
    assert "listing-production" in text
    assert "listing-hardening" in text
    assert "listing-evidence-auditor" in text


def main() -> int:
    tests = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    for test in tests:
        test()
    print(f"PASS: {len(tests)} global-router tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
