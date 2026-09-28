import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parents[5] / "tools"))
from chapter_source import chapter_source

resource, rows, data = chapter_source(111)
draft = json.loads((Path(__file__).parent / "slice_1200.targets.json").read_text(encoding="utf-8"))
for number in range(1250, 1276):
    row = rows[number]
    source = data[row["source_offset"]:row["source_offset"] + row["source_byte_length"]].decode("cp932")
    target = next((item["text"] for item in draft["translations"].values() if item["resource_row"] == number), None)
    print(f"{number}\t{row['id']}\tJP={source!r}\tEN={target!r}\trefs={row['reference_instructions']}")
