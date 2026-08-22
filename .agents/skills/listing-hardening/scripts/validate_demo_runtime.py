#!/usr/bin/env python3
"""Run no-network browser QA for an exact standalone Global Demo HTML.

Exit codes: 0 PASS, 1 FAIL, 2 BLOCKED (browser runtime unavailable).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _blocked(reason: str, digest: str | None = None) -> dict:
    return {"status": "BLOCKED", "reason": reason, "demo_sha256": digest}


def _viewport_checks(page, width: int, height: int) -> dict:
    page.set_viewport_size({"width": width, "height": height})
    page.wait_for_timeout(100)
    return page.evaluate(
        """() => {
          const all = Array.from(document.querySelectorAll('img'));
          const broken = all.filter(img => !img.complete || img.naturalWidth === 0).length;
          const overflow = document.documentElement.scrollWidth > window.innerWidth + 1;
          const primary = Array.from(document.querySelectorAll('h1,h2,h3,button,[data-primary-copy],[data-carousel-prev],[data-carousel-next]'));
          const clipped = primary.filter(el => {
            const r = el.getBoundingClientRect();
            if (r.width <= 0 || r.height <= 0) return true;
            const cs = getComputedStyle(el);
            const horizontalClip = (cs.overflowX === 'hidden' || cs.overflow === 'hidden') && el.scrollWidth > el.clientWidth + 1;
            const verticalClip = (cs.overflowY === 'hidden' || cs.overflow === 'hidden') && el.scrollHeight > el.clientHeight + 1;
            return horizontalClip || verticalClip;
          }).length;
          return {horizontal_overflow: overflow, broken_images: broken, clipped_primary_elements: clipped};
        }"""
    )


def _carousel_checks(page) -> dict:
    roots = page.locator('[data-carousel]')
    if roots.count() == 0:
        return {"present": False, "next_verified": True, "prev_verified": True}
    root = roots.first
    slides = root.locator('[data-carousel-slide]')
    prev = root.locator('[data-carousel-prev]')
    nxt = root.locator('[data-carousel-next]')
    if slides.count() < 2 or prev.count() < 1 or nxt.count() < 1:
        return {"present": True, "next_verified": False, "prev_verified": False, "reason": "incomplete carousel structure"}

    def visible_signature() -> list[int]:
        return root.locator('[data-carousel-slide]').evaluate_all(
            "els => els.map((el,i) => { const s=getComputedStyle(el); const r=el.getBoundingClientRect(); return (!el.hidden && s.display!=='none' && s.visibility!=='hidden' && r.width>0 && r.height>0) ? i : -1; }).filter(i=>i>=0)"
        )

    before = visible_signature()
    nxt.first.click()
    page.wait_for_timeout(50)
    after_next = visible_signature()
    prev.first.click()
    page.wait_for_timeout(50)
    after_prev = visible_signature()
    return {
        "present": True,
        "next_verified": after_next != before,
        "prev_verified": after_prev == before,
        "before": before,
        "after_next": after_next,
        "after_prev": after_prev,
    }


def validate_runtime(path: Path) -> dict:
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        return _blocked(f"Playwright runtime unavailable: {exc}", digest)

    requests: list[str] = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.on("request", lambda request: requests.append(request.url) if request.url.startswith(("http://", "https://")) else None)
            page.route("http://**/*", lambda route: route.abort())
            page.route("https://**/*", lambda route: route.abort())
            page.goto(path.resolve().as_uri(), wait_until="load")
            viewports = {
                "1440": _viewport_checks(page, 1440, 1000),
                "390": _viewport_checks(page, 390, 844),
            }
            carousel = _carousel_checks(page)
            browser.close()
    except Exception as exc:
        return {"status": "FAIL", "reason": f"browser runtime error: {exc}", "demo_sha256": digest}

    errors: list[str] = []
    if requests:
        errors.append(f"network requests observed: {len(requests)}")
    for width, row in viewports.items():
        if row.get("horizontal_overflow"):
            errors.append(f"{width}px horizontal overflow")
        if row.get("broken_images") != 0:
            errors.append(f"{width}px broken images: {row.get('broken_images')}")
        if row.get("clipped_primary_elements") != 0:
            errors.append(f"{width}px clipped primary elements: {row.get('clipped_primary_elements')}")
    if carousel.get("present") and (not carousel.get("next_verified") or not carousel.get("prev_verified")):
        errors.append("carousel next/previous runtime transition failed")

    return {
        "status": "FAIL" if errors else "PASS",
        "validator": "browser-runtime",
        "demo_sha256": digest,
        "network_requests": len(requests),
        "viewports": viewports,
        "carousel": carousel,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.html.is_file():
        result = {"status": "FAIL", "reason": f"Demo file not found: {args.html}"}
    else:
        result = validate_runtime(args.html)
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if result.get("status") == "PASS" else (2 if result.get("status") == "BLOCKED" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
