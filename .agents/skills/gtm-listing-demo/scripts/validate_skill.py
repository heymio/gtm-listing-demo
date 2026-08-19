#!/usr/bin/env python3
"""Validate the public gtm-listing-demo skill with the Python standard library."""

from __future__ import annotations

import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[2]
SKILL_FILE = SKILL_DIR / "SKILL.md"

REQUIRED = [
    SKILL_FILE,
    SKILL_DIR / "agents" / "openai.yaml",
    SKILL_DIR / "references" / "workflow.md",
    SKILL_DIR / "references" / "contracts.md",
    SKILL_DIR / "references" / "localization.md",
    SKILL_DIR / "references" / "market-research.md",
    SKILL_DIR / "references" / "visual-evidence.md",
    SKILL_DIR / "references" / "qa.md",
    SKILL_DIR / "profiles" / "channels" / "_template.md",
    SKILL_DIR / "profiles" / "channels" / "amazon.md",
    SKILL_DIR / "profiles" / "channels" / "dtc-product-page.md",
    SKILL_DIR / "profiles" / "channels" / "retailer-pdp.md",
    SKILL_DIR / "profiles" / "channels" / "generic-marketplace.md",
    SKILL_DIR / "profiles" / "locales" / "_template.md",
    SKILL_DIR / "profiles" / "locales" / "ja-JP.md",
    SKILL_DIR / "profiles" / "locales" / "en-US.md",
    SKILL_DIR / "profiles" / "locales" / "de-DE.md",
    SKILL_DIR / "profiles" / "locales" / "it-IT.md",
    SKILL_DIR / "profiles" / "regions" / "_template.md",
    SKILL_DIR / "profiles" / "regions" / "eu.md",
    SKILL_DIR / "profiles" / "categories" / "_template.md",
    SKILL_DIR / "evals" / "core.md",
    SKILL_DIR / "evals" / "multichannel.md",
    SKILL_DIR / "evals" / "multimarket.md",
    SKILL_DIR / "evals" / "cross-category.md",
]

CORE_PATHS = [
    SKILL_FILE,
    *(SKILL_DIR / "references").glob("*.md"),
    *(SKILL_DIR / "profiles" / "channels").glob("*.md"),
    *(SKILL_DIR / "profiles" / "locales").glob("*.md"),
    *(SKILL_DIR / "profiles" / "regions").glob("*.md"),
]

CATEGORY_LEAKAGE = [
    "SwitchBot",
    "Solar PTC",
    "ViewStation",
    "security camera",
    "robot vacuum",
    "smart lock",
    "pet tech",
    "microSD",
    "Pan/Tilt",
    "防犯",
    "玄関",
    "駐車場",
]

PERSONA_LEAKAGE = [
    "users prefer",
    "consumers prefer",
    "customers prefer",
    "用户偏好",
    "消費者は好む",
    "Verbraucher bevorzugen",
    "consumatori preferiscono",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def parse_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.S)
    if not match:
        fail("SKILL.md is missing YAML frontmatter")
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values


def main() -> int:
    missing = [str(path.relative_to(REPO_ROOT)) for path in REQUIRED if not path.exists()]
    if missing:
        fail(f"missing required files: {', '.join(missing)}")

    skill_text = SKILL_FILE.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(skill_text)
    if frontmatter.get("name") != SKILL_DIR.name:
        fail("frontmatter name must match the skill directory")
    description = frontmatter.get("description", "")
    if not description.startswith("Use when "):
        fail("description must start with 'Use when '")
    if len(description) > 500:
        fail("description exceeds 500 characters")

    required_headings = [
        "# GTM Listing Demo",
        "## Core principle",
        "## Configuration layers",
        "## Mandatory rules",
        "## Workflow",
        "## Required outputs",
        "## Stop and escalate",
        "## Quality gate",
    ]
    for heading in required_headings:
        if heading not in skill_text:
            fail(f"missing heading: {heading}")

    all_text = "\n".join(path.read_text(encoding="utf-8") for path in REQUIRED)
    placeholders = re.findall(r"\b(?:TODO|TBD|FIXME)\b", all_text, flags=re.I)
    if placeholders:
        fail(f"placeholder terms found: {sorted(set(placeholders))}")

    for path in CORE_PATHS:
        text = path.read_text(encoding="utf-8")
        for term in CATEGORY_LEAKAGE:
            if term.lower() in text.lower():
                fail(f"category or private leakage in {path.relative_to(REPO_ROOT)}: {term}")

    for path in (SKILL_DIR / "profiles" / "locales").glob("*.md"):
        text = path.read_text(encoding="utf-8")
        for term in PERSONA_LEAKAGE:
            if term.lower() in text.lower():
                fail(f"persona leakage in locale profile {path.name}: {term}")

    region_text = (SKILL_DIR / "profiles" / "regions" / "eu.md").read_text(encoding="utf-8")
    for term in PERSONA_LEAKAGE:
        if term.lower() in region_text.lower():
            fail(f"regional persona leakage: {term}")

    eval_text = "\n".join(path.read_text(encoding="utf-8") for path in (SKILL_DIR / "evals").glob("*.md"))
    for required_phrase in [
        "Message != Module",
        "region overlay",
        "cross-category",
        "offer boundary",
        "mobile preview",
    ]:
        if required_phrase.lower() not in eval_text.lower():
            fail(f"eval coverage missing: {required_phrase}")

    word_count = len(re.findall(r"[\w\u4e00-\u9fff]+", skill_text))
    if word_count > 1200:
        fail(f"SKILL.md is too long: {word_count}")

    print("PASS: public gtm-listing-demo skill is structurally valid")
    print(f"PASS: {len(REQUIRED)} required files exist")
    print("PASS: no category/private leakage in core files")
    print("PASS: no persona leakage in locale or region profiles")
    print(f"PASS: SKILL.md token-like count {word_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
