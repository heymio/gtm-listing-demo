#!/usr/bin/env python3
"""Regression tests for one-file standalone final Demo delivery."""

from __future__ import annotations

import importlib.util
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_DIR / "scripts" / "validate_demo_html.py"


def load_validator():
    assert VALIDATOR.is_file(), "validate_demo_html.py must exist"
    spec = importlib.util.spec_from_file_location("validate_demo_html", VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def valid_demo() -> str:
    return """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{box-sizing:border-box} img{display:block;max-width:100%;height:auto}.demo{width:100%;max-width:1200px;margin:auto}[data-carousel]{overflow:hidden;width:100%}[data-carousel-slide]{width:100%}@media(max-width:600px){.demo{padding:8px}}
</style></head><body><main class="demo"><section data-carousel>
<button type="button" data-carousel-prev>Prev</button>
<div data-carousel-slide><img alt="one" src="data:image/png;base64,iVBORw0KGgo="></div>
<div data-carousel-slide hidden><img alt="two" src="data:image/png;base64,iVBORw0KGgo="></div>
<button type="button" data-carousel-next>Next</button></section></main>
<script>document.querySelectorAll('[data-carousel]').forEach((root)=>{root.querySelector('[data-carousel-prev]').addEventListener('click',()=>{});root.querySelector('[data-carousel-next]').addEventListener('click',()=>{});});</script>
</body></html>"""


def static_demo() -> str:
    return """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{box-sizing:border-box} img{display:block;max-width:100%;height:auto}.demo{width:100%;max-width:1200px;margin:auto}@media(max-width:600px){.demo{padding:8px}}
</style></head><body><main class="demo"><section>
<img alt="static product visual" src="data:image/png;base64,iVBORw0KGgo=">
</section></main></body></html>"""


def test_valid_standalone_demo_passes_static_contract() -> None:
    result = load_validator().validate_html_text(valid_demo())
    assert result["status"] == "PASS", result


def test_static_demo_without_planned_carousel_can_pass() -> None:
    result = load_validator().validate_html_text(static_demo())
    assert result["status"] == "PASS", result
    assert result["checks"]["carousel_contract"] == "N/A"


def test_final_delivery_path_must_be_html_not_zip() -> None:
    result = load_validator().validate_delivery_path(Path("demo.zip"))
    assert result["status"] == "FAIL"


def test_external_image_script_stylesheet_and_css_url_fail() -> None:
    validator = load_validator()
    cases = [
        valid_demo().replace('src="data:image/png;base64,iVBORw0KGgo="', 'src="assets/hero.png"', 1),
        valid_demo().replace("<script>", '<script src="assets/app.js">', 1),
        valid_demo().replace("</head>", '<link rel="stylesheet" href="assets/app.css"></head>', 1),
        valid_demo().replace(".demo{", '.external{background:url("assets/bg.png")}.demo{', 1),
    ]
    for html in cases:
        assert validator.validate_html_text(html)["status"] == "FAIL"


def test_mixed_external_srcset_and_source_srcset_fail() -> None:
    validator = load_validator()
    mixed = valid_demo().replace(
        'src="data:image/png;base64,iVBORw0KGgo=">',
        'src="data:image/png;base64,iVBORw0KGgo=" srcset="data:image/png;base64,iVBORw0KGgo= 1x, assets/hero@2x.png 2x">',
        1,
    )
    source = valid_demo().replace(
        '<img alt="one" src="data:image/png;base64,iVBORw0KGgo=">',
        '<picture><source srcset="assets/hero.webp 1x"><img alt="one" src="data:image/png;base64,iVBORw0KGgo="></picture>',
        1,
    )
    assert validator.validate_html_text(mixed)["status"] == "FAIL"
    assert validator.validate_html_text(source)["status"] == "FAIL"


def test_literal_blob_resource_fails_portable_contract() -> None:
    validator = load_validator()
    html = valid_demo().replace('<body>', '<body><video src="blob:session-only"></video>', 1)
    assert validator.validate_html_text(html)["status"] == "FAIL"


def test_mobile_contract_requires_viewport_breakpoint_and_responsive_images() -> None:
    validator = load_validator()
    html = valid_demo().replace('<meta name="viewport" content="width=device-width, initial-scale=1">', "").replace("@media(max-width:600px)", ".mobile-placeholder").replace("max-width:100%", "width:auto")
    result = validator.validate_html_text(html)
    assert result["status"] == "FAIL"
    folded = "\n".join(result["errors"]).casefold()
    assert "viewport" in folded and ("responsive" in folded or "@media" in folded)


def test_carousel_requires_controls_slides_and_inline_click_wiring_when_present() -> None:
    validator = load_validator()
    html = valid_demo().replace("addEventListener('click'", "noop('click'")
    result = validator.validate_html_text(html)
    assert result["status"] == "FAIL"
    assert any("carousel" in item.casefold() for item in result["errors"])


def test_partial_carousel_markup_still_fails() -> None:
    validator = load_validator()
    html = static_demo().replace("<section>", "<section data-carousel>", 1)
    result = validator.validate_html_text(html)
    assert result["status"] == "FAIL"
    assert any("carousel" in item.casefold() for item in result["errors"])


def test_demo_contract_requires_runtime_1440_and_390_and_blocked_without_browser() -> None:
    combined = "\n".join([
        (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8") if (SKILL_DIR / "SKILL.md").is_file() else "",
        (SKILL_DIR / "references" / "final-qa.md").read_text(encoding="utf-8") if (SKILL_DIR / "references" / "final-qa.md").is_file() else "",
        (SKILL_DIR / "references" / "demo-output.md").read_text(encoding="utf-8") if (SKILL_DIR / "references" / "demo-output.md").is_file() else "",
    ]).casefold()
    for phrase in ["single standalone html", "1440px", "390px", "horizontal overflow", "broken images", "if browser/runtime verification cannot be performed", "blocked"]:
        assert phrase in combined, phrase


def main() -> int:
    tests = [value for name, value in globals().items() if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"PASS: {len(tests)} global-standalone-demo tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
