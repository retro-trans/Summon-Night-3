"""Decode high-probability battle-intro word-art candidates for visual review."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

from sn3_archive import ROOT, GameSource
from sn3_ui_textures import decode_texture, texture_records


OUT = ROOT / "work/ui/battle_0.1.13/intro_discovery_01_00004_00064_full"
INDEX = ROOT / "work/ui/interface_graphics.index.json"


def sha(data): return hashlib.sha256(data).hexdigest()


def collect():
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    chosen = []
    for group in index["resources"]:
        occurrence = next((item for item in group["occurrences"] if item["bank"] == "01.DAT" and len(item["path"]) == 2 and 4 <= item["path"][0] <= 64), None)
        if occurrence is None:
            continue
        rows = group["textures"]
        chosen.extend((occurrence, row) for row in rows)
    chosen.sort(key=lambda pair: pair[0]["path"])
    report = {"schema_version": 1, "scope": "Every indexed texture in 01.DAT resources 00004-00064; full encounter-card family inspection.",
              "source_index_sha256": sha(INDEX.read_bytes()), "candidates": [], "rejected": []}
    images = []
    with GameSource() as source:
        for occurrence, row in chosen:
            data = source.read(occurrence["bank"], occurrence["offset"], occurrence["size"])
            if sha(data) != occurrence["sha256"]:
                raise ValueError("Source resource changed: " + occurrence["id"])
            try:
                image = decode_texture(data, row)
            except ValueError as exc:
                report["rejected"].append({"id": occurrence["id"], "reason": str(exc)})
                continue
            record = {"id": occurrence["id"] + ":sprite:%03d" % row["number"], "resource_id": occurrence["id"],
                      "source_sha256": occurrence["sha256"], "path": occurrence["path"],
                      "width": row["width"], "height": row["height"], "format": row["format"]}
            report["candidates"].append(record); images.append((record, image))
    report["candidate_count"] = len(report["candidates"])
    return report, images


def write(report, images):
    OUT.mkdir(parents=True, exist_ok=False)
    for record, image in images:
        name = record["id"].replace(":", "_").replace("/", "_") + ".png"
        image.save(OUT / name); record["image_file"] = name; record["image_sha256"] = sha((OUT / name).read_bytes())
    contacts = []
    for page_number, start in enumerate(range(0, len(images), 80)):
        batch = images[start:start + 80]
        page = Image.new("RGB", (1600, ((len(batch) + 9) // 10) * 120), (96, 96, 96)); draw = ImageDraw.Draw(page)
        for number, (record, image) in enumerate(batch):
            x, y = number % 10 * 160, number // 10 * 120
            draw.text((x + 3, y + 2), record["id"], fill="white")
            preview = image.copy(); preview.thumbnail((154, 96)); page.paste(preview.convert("RGB"), (x + 3, y + 20))
        contact = "contact_%02d.png" % page_number
        page.save(OUT / contact); contacts.append(contact)
    report["contact_sheets"] = contacts
    (OUT / "index.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--write", action="store_true"); args = parser.parse_args()
    report, images = collect()
    print(json.dumps({"mode": "write" if args.write else "dry_run", "destination": str(OUT), "candidate_count": len(images), "rejected": report["rejected"], "sample_ids": [r["id"] for r in report["candidates"][:8]]}, indent=2))
    if args.write: write(report, images)


if __name__ == "__main__": main()
