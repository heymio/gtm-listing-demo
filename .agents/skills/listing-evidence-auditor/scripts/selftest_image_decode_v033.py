#!/usr/bin/env python3
"""Real-decoder regressions for Global v0.3.3 physical image verification."""

from __future__ import annotations

import importlib.util
import struct
import sys
import zlib
from pathlib import Path
from tempfile import TemporaryDirectory

SCRIPT_DIR = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("global_strict_fingerprint", SCRIPT_DIR / "fingerprint_assets.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load fingerprint_assets.py")
fingerprint = importlib.util.module_from_spec(SPEC)
sys.modules["global_strict_fingerprint"] = fingerprint
SPEC.loader.exec_module(fingerprint)

try:
    from PIL import Image
except Exception as exc:
    raise RuntimeError(f"Pillow is required for this hard-verification selftest: {exc}") from exc


def _chunk(kind: bytes, payload: bytes) -> bytes:
    body = kind + payload
    return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)


def _corrupt_but_structural_png() -> bytes:
    ihdr = struct.pack(">IIBBBBB", 2, 2, 8, 2, 0, 0, 0)
    idat = zlib.compress(b"\x00")
    return b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", idat) + _chunk(b"IEND", b"")


def _save_image(path: Path, fmt: str) -> None:
    image = Image.new("RGB", (3, 2), (10, 20, 30))
    image.save(path, format=fmt)


def test_real_decoder_accepts_valid_png_jpeg_and_webp() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        for filename, fmt in [("valid.png", "PNG"), ("valid.jpg", "JPEG"), ("valid.webp", "WEBP")]:
            path = root / filename
            _save_image(path, fmt)
            result = fingerprint.fingerprint_asset(path, root)
            assert result["errors"] == [], (filename, result)


def test_real_decoder_rejects_structurally_plausible_corrupt_png() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        path = root / "corrupt.png"
        path.write_bytes(_corrupt_but_structural_png())
        assert fingerprint._png_integrity(path.read_bytes()) == []
        result = fingerprint.fingerprint_asset(path, root)
        assert any("real image decode failed" in item for item in result["errors"]), result


def main() -> int:
    tests = [value for name, value in globals().items() if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"PASS: {len(tests)} real-image-decoder tests (Global v0.3.3)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
