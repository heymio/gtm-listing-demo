#!/usr/bin/env python3
"""Package the repository skill for Personal Skill upload."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[2]
DIST_DIR = REPO_ROOT / "dist"
OUTPUT = DIST_DIR / "gtm-listing-demo.skill.zip"


def main() -> None:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as archive:
        for path in sorted(SKILL_DIR.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                archive.write(path, Path(SKILL_DIR.name) / path.relative_to(SKILL_DIR))
    print(OUTPUT)


if __name__ == "__main__":
    main()
