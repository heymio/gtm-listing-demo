#!/usr/bin/env python3
"""Shared deterministic ZIP helpers for Global release packaging."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)
FILE_MODE = 0o100644


def reject_symlinks(root: Path) -> None:
    if root.is_symlink():
        raise ValueError(f"symlink source root is not allowed: {root}")
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symlink is not allowed in release input: {path}")


def collect_files(root: Path, *, exclude=None) -> list[Path]:
    reject_symlinks(root)
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        relative = path.relative_to(root)
        if exclude and exclude(relative):
            continue
        files.append(path)
    return files


def _info(name: str) -> ZipInfo:
    info = ZipInfo(name, date_time=FIXED_ZIP_TIME)
    info.compress_type = ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = FILE_MODE << 16
    info.flag_bits |= 0x800
    return info


def write_deterministic_zip(output: Path, entries: Iterable[tuple[str, bytes]]) -> None:
    normalized: dict[str, bytes] = {}
    for name, data in entries:
        name = name.replace("\\", "/").lstrip("/")
        if not name or name.endswith("/"):
            raise ValueError(f"invalid ZIP member name: {name!r}")
        if name in normalized:
            raise ValueError(f"duplicate ZIP member: {name}")
        normalized[name] = data
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(normalized):
            archive.writestr(_info(name), normalized[name], compress_type=ZIP_DEFLATED, compresslevel=9)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
