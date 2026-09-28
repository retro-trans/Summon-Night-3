import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parents[5] / "tools"))
from chapter_source import chapter_source

start, end = map(int, sys.argv[1:3])
r, rows, data = chapter_source(111)
for number in range(start - 20, end + 21):
    row = rows[number]
    source = data[row["source_offset"]:row["source_offset"] + row["source_byte_length"]].decode("cp932")
    print(f"JP\t{number}\t{row['id']}\t{source!r}")

target = json.loads((Path(__file__).parent / f"slice_{start:04d}.targets.json").read_text(encoding="utf-8"))
for source_id, item in target["translations"].items():
    if start <= item["resource_row"] <= end:
        print(f"EN\t{item['resource_row']}\t{source_id}\t{item['text']!r}")
