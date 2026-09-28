"""Read-only descriptor audit for rejected battle-art texture candidates."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sn3_archive import GameSource, child, parse_index
from sn3_codec import decoded_size, decompress
from sn3_ui_textures import texture_records


TARGETS = [(2, number) for number in range(77, 85)] + [(1, 1029)]


def main() -> None:
    report = []
    with GameSource() as source:
        for bank, number in TARGETS:
            raw = source.resource(f"{bank:02d}.DAT", number)
            data = raw
            try:
                if 0 < decoded_size(raw) <= 16 * 1024 * 1024:
                    data, _ = decompress(raw, 0x9831, 16 * 1024 * 1024)
            except ValueError:
                pass
            try:
                texture_records(data)
                entries = [(0, data)]
            except ValueError:
                try:
                    pack = parse_index(data, len(data))
                    entries = [(entry["id"], child(data, pack, entry["id"])) for entry in pack["entries"]]
                except ValueError as exc:
                    report.append({"id": f"{bank:02d}:{number:05d}", "unreadable": str(exc), "header_hex": data[:32].hex()})
                    continue
            for entry_id, payload in entries:
                if not payload:
                    continue
                try:
                    rows = texture_records(payload)
                except ValueError:
                    continue
                for row in rows:
                    row_bytes = row["pitch"] if row["format"] == 5 else (row["pitch"] + 1) // 2
                    stored_height, remainder = divmod(row["data_size"], row_bytes)
                    if (bank == 2 and 77 <= number <= 84) or (bank == 1 and number == 1029 and entry_id == 3):
                        report.append({
                            "id": f"{bank:02d}:{number:05d}/{entry_id:05d}:sprite:{row['number']:03d}",
                            "format": row["format"], "width": row["width"], "height": row["height"],
                            "pitch": row["pitch"], "swizzled": row["swizzled"],
                            "data_size": row["data_size"], "row_bytes": row_bytes,
                            "stored_height": stored_height, "remainder": remainder,
                        })
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
