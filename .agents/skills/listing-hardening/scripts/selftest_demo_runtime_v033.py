#!/usr/bin/env python3
"""Real no-network browser regressions for Global v0.3.3 Demo runtime verification."""

from __future__ import annotations

import base64
import importlib.util
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

SCRIPT_DIR = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("global_demo_runtime", SCRIPT_DIR / "validate_demo_runtime.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load validate_demo_runtime.py")
runtime = importlib.util.module_from_spec(SPEC)
sys.modules["global_demo_runtime"] = runtime
SPEC.loader.exec_module(runtime)

SVG = base64.b64encode(b'<svg xmlns="http://www.w3.org/2000/svg" width="2" height="2"><rect width="2" height="2" fill="black"/></svg>').decode("ascii")


def working_html(extra_script: str = "") -> str:
    return f'''<!doctype html><html><head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>*{{box-sizing:border-box}}img{{max-width:100%;height:auto}}[data-carousel-slide][hidden]{{display:none}}@media(max-width:600px){{body{{margin:0}}}}</style>
</head><body><main><h1>Runtime fixture</h1><section data-carousel>
<button type="button" data-carousel-prev>Prev</button>
<div data-carousel-slide><img alt="one" src="data:image/svg+xml;base64,{SVG}"></div>
<div data-carousel-slide hidden><img alt="two" src="data:image/svg+xml;base64,{SVG}"></div>
<button type="button" data-carousel-next>Next</button></section></main>
<script>
const root=document.querySelector('[data-carousel]');
const slides=[...root.querySelectorAll('[data-carousel-slide]')];let index=0;
function show(){{slides.forEach((el,i)=>el.hidden=i!==index);}}
root.querySelector('[data-carousel-next]').addEventListener('click',()=>{{index=(index+1)%slides.length;show();}});
root.querySelector('[data-carousel-prev]').addEventListener('click',()=>{{index=(index-1+slides.length)%slides.length;show();}});
{extra_script}
</script></body></html>'''


def test_real_browser_verifies_both_carousel_directions_no_network() -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "demo.html"
        path.write_text(working_html(), encoding="utf-8")
        result = runtime.validate_runtime(path)
    assert result["status"] == "PASS", result
    assert result["network_requests"] == 0, result
    assert result["carousel"]["next_verified"] is True, result
    assert result["carousel"]["prev_verified"] is True, result


def test_real_browser_rejects_dead_carousel_controls() -> None:
    html = working_html()
    start = html.index("<script>")
    end = html.index("</script>", start)
    html = html[:start] + "<script>const unused=\"data-carousel click addEventListener\";</script>" + html[end + len("</script>"):]
    with TemporaryDirectory() as directory:
        path = Path(directory) / "dead.html"
        path.write_text(html, encoding="utf-8")
        result = runtime.validate_runtime(path)
    assert result["status"] == "FAIL", result
    assert any("carousel" in item.casefold() for item in result["errors"]), result


def test_real_browser_rejects_network_request() -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "network.html"
        path.write_text(working_html("fetch('https://example.com/ping').catch(()=>{});"), encoding="utf-8")
        result = runtime.validate_runtime(path)
    assert result["status"] == "FAIL", result
    assert result["network_requests"] > 0, result


def main() -> int:
    tests = [value for name, value in globals().items() if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"PASS: {len(tests)} real-browser-runtime tests (Global v0.3.3)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
