"""Normalize verified proper names in the active 0.1.13 battle drafts.

Run without --write to preview every exact replacement.  Only the current
battle target and meaning-review catalogs are in scope; releases are excluded.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = (
    ROOT / "work/translation/en/battle_0.1.13/executable.targets.json",
    ROOT / "work/translation/en/battle_0.1.13/table.targets.json",
    ROOT / "work/translation/en/battle_0.1.13/meaning_review.json",
    ROOT / "work/translation/en/battle_0.1.13/encounter_art.targets.json",
)
LITERALS = {
    "НハイネルのDielgo": "НHeinel's Dielgo",
    "Нヴァルゼルド": "НVAR-Xe-LD",
}
WORDS = {
    "Azria": "Azlier",
    "Biju": "Vijue",
    "Fraise": "Phlaiz",
    "Gareo": "Galleor",
    "Isla": "Ishlar",
    "Kunnon": "Cunnon",
    "Ordraik": "Ordreik",
    "Sonora": "Sonolar",
    "Jakyne": "Jakinie",
    "Jakini": "Jakinie",
    "Okyne": "Oukinie",
    "Owkinie": "Oukinie",
    "Maruruu": "Marurur",
    "Ardylia": "Ardyllia",
    "Zirkoda": "Jilcooda",
}


def normalize(value: str) -> str:
    for old, new in LITERALS.items():
        value = value.replace(old, new)
    for old, new in WORDS.items():
        value = re.sub(rf"(?<![A-Za-z]){re.escape(old)}(?![A-Za-z])", new, value)
    return value


def walk(value: object, path: str = "") -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            if isinstance(child, str):
                revised = normalize(child)
                if revised != child:
                    changes.append({"path": child_path, "before": child, "after": revised})
                    value[key] = revised
            else:
                changes.extend(walk(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            changes.extend(walk(child, f"{path}[{index}]"))
    return changes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report: list[dict[str, object]] = []
    for file_path in FILES:
        data = json.loads(file_path.read_text(encoding="utf-8"))
        changes = walk(data)
        report.append({"file": str(file_path.relative_to(ROOT)).replace("\\", "/"), "changes": changes})
        if args.write and changes:
            file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"mode": "write" if args.write else "dry-run", "files": report}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
