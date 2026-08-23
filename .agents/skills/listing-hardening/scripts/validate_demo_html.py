#!/usr/bin/env python3
"""Global v0.3.3 standalone Demo static preflight.

Static HTML inspection is a preflight only. Carousel interaction is never marked
hard-PASS here; actual interaction PASS requires browser runtime evidence.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable

HERE = Path(__file__).resolve().parent
LEGACY_PATH = HERE / "validate_demo_html_legacy.py"
SPEC = importlib.util.spec_from_file_location("global_demo_html_legacy", LEGACY_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load legacy Demo validator: {LEGACY_PATH}")
_legacy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(_legacy)


def _embedded(value: str) -> bool:
    value = value.strip().casefold()
    return value.startswith("data:") or value.startswith("#")


def _css_urls(style_text: str) -> list[str]:
    return [m.group(2).strip() for m in re.finditer(r"url\(\s*(['\"]?)(.*?)\1\s*\)", style_text, flags=re.I | re.S)]


class ExtraParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.inline_styles: list[str] = []
        self.svg_resource_refs: list[tuple[str, str, str]] = []
        self.carousel_markers = 0

    @staticmethod
    def _attrs(attrs: Iterable[tuple[str, str | None]]) -> dict[str, str]:
        return {key.casefold(): value or "" for key, value in attrs}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.casefold()
        values = self._attrs(attrs)
        if values.get("style"):
            self.inline_styles.append(values["style"])
        if tag in {"image", "use"}:
            for attr in ("href", "xlink:href"):
                if values.get(attr):
                    self.svg_resource_refs.append((tag, attr, values[attr]))
        if any(key in values for key in ("data-carousel", "data-carousel-slide", "data-carousel-prev", "data-carousel-next")):
            self.carousel_markers += 1


def validate_delivery_path(path: Path) -> dict[str, object]:
    return _legacy.validate_delivery_path(path)


def validate_html_text(text: str) -> dict[str, object]:
    result = _legacy.validate_html_text(text)
    errors = list(result.get("errors", []))
    parser = ExtraParser()
    parser.feed(text)
    parser.close()

    if parser.carousel_markers == 0:
        errors = [error for error in errors if not error.startswith("Carousel validation requires")]

    for style in parser.inline_styles:
        for target in _css_urls(style):
            if target and not _embedded(target):
                errors.append(f"Inline style url() dependency must be embedded as data:; found: {target}")
    for tag, attr, value in parser.svg_resource_refs:
        if not _embedded(value):
            errors.append(f"Standalone Demo cannot depend on external/local SVG resource: <{tag}> {attr}={value!r}")

    checks = dict(result.get("checks", {}))
    if parser.carousel_markers == 0:
        checks["carousel_static_contract"] = "N/A"
        checks["carousel_contract"] = "N/A"
    elif any("carousel" in error.casefold() for error in errors):
        checks["carousel_static_contract"] = "FAIL"
        checks["carousel_contract"] = "FAIL"
    else:
        checks["carousel_static_contract"] = "PASS"
        checks["carousel_contract"] = "RUNTIME_REQUIRED"

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "checks": checks,
        "note": "static preflight only; browser runtime evidence is required for interaction hard verification",
    }


def validate_file(path: Path) -> dict[str, object]:
    path_result = validate_delivery_path(path)
    if path_result["status"] != "PASS":
        return path_result
    if not path.is_file():
        return {"status": "FAIL", "errors": [f"Demo HTML file not found: {path}"]}
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return {"status": "FAIL", "errors": ["Demo HTML must be UTF-8 text."]}
    return validate_html_text(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate_file(args.html)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"{result['status']}: standalone Demo static preflight")
        for error in result.get("errors", []):
            print(f"- {error}")
        print(result.get("note", ""))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
