"""Rank catalogued small UI textures against the supplied tutorial Next crop.

Read-only by default.  ``--report`` writes only a JSON result outside release
inputs so a long scan can be inspected even when terminal output is truncated.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

from sn3_archive import GameSource, ROOT
from sn3_ui_textures import decode_texture


DEFAULT_CROP = Path(r"C:/Users/Binh/AppData/Local/Temp/codex-clipboard-6cc69a1b-d649-4311-82d7-86cb05625ec7.png")
EXPORT_INDEXES = ("setup_assets_complete", "battle_assets", "menu_discovery")


def candidates_from_exports():
    """Yield already-decoded selected packs, including compressed resources.

    These PNGs are intentionally searched separately: their source payloads are
    outside the raw recursive inventory used by interface_graphics.index.json.
    """
    for folder in EXPORT_INDEXES:
        root = ROOT / "work" / "ui" / folder
        index = json.loads((root / "index.json").read_text())
        for row in index["textures"]:
            yield (Image.open(root / row["image_file"]).convert("RGBA"), {
                "id": row["resource_id"], "bank": "decoded_export",
                "path": [folder, row["image_file"]], "sprite": row["number"],
                "source_sha256": row["source_sha256"],
            })


def append_ranked(found, target, image, info, min_width):
    width, height = image.size
    if not (min_width <= width <= 256 and 8 <= height <= 80):
        return
    for scale in (1.0, 0.5):
        scaled = image if scale == 1.0 else image.resize((round(width * scale), round(height * scale)), Image.Resampling.LANCZOS)
        sw, sh = scaled.size
        if sw > 71 or sh > 40:
            continue
        pixels = np.asarray(scaled, dtype=np.int16)
        mask = pixels[:, :, 3] > 80
        covered = int(mask.sum())
        # Navigation capsules can be fully opaque.  Keep those candidates;
        # only a nearly empty texture has no useful visual evidence.
        if covered < 16:
            continue
        best = (float("inf"), None)
        for y in range(41 - sh):
            for x in range(72 - sw):
                score = float(np.abs(target[y:y + sh, x:x + sw] - pixels[:, :, :3])[mask].mean())
                if score < best[0]:
                    best = (score, [x, y])
        found.append({"error": best[0], **info, "source_size": [width, height],
                      "scale": scale, "rendered_size": [sw, sh], "position": best[1]})


def rank(crop_path, min_width=8):
    target = np.asarray(Image.open(crop_path).convert("RGB").resize((71, 40), Image.Resampling.LANCZOS), dtype=np.int16)
    catalog = json.loads((ROOT / "work/ui/interface_graphics.index.json").read_text())
    seen, found = set(), []
    with GameSource() as source:
        for group in catalog["resources"]:
            occurrence = next((item for item in group["occurrences"] if item["bank"] in ("00.DAT", "01.DAT", "02.DAT", "03.DAT")), None)
            if occurrence is None:
                continue
            data = source.read(occurrence["bank"], occurrence["offset"], occurrence["size"])
            for row in group["textures"]:
                width, height = row["width"], row["height"]
                identity = (group["source_sha256"], row["number"])
                if identity in seen or not (min_width <= width <= 256 and 8 <= height <= 80):
                    continue
                seen.add(identity)
                try:
                    image = decode_texture(data, row)
                except ValueError:
                    continue
                append_ranked(found, target, image, {"id": occurrence["id"], "bank": occurrence["bank"], "path": occurrence["path"], "sprite": row["number"], "source_sha256": group["source_sha256"]}, min_width)
    for image, info in candidates_from_exports():
        append_ranked(found, target, image, info, min_width)
    found.sort(key=lambda row: row["error"])
    return {"crop": str(crop_path), "native_target_size": [71, 40], "candidate_count": len(found), "top": found[:100]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--crop", type=Path, default=DEFAULT_CROP)
    parser.add_argument("--min-width", type=int, default=8)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--contact", type=Path, help="write a contact sheet for the top unique candidates")
    args = parser.parse_args()
    report = rank(args.crop, args.min_width)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n")
    # The contact sheet deliberately uses only the source PNGs that the raw
    # scan could decode.  It makes the numeric matcher auditable without
    # changing a source asset or release input.
    if args.contact:
        catalog = json.loads((ROOT / "work/ui/interface_graphics.index.json").read_text())
        lookup = {}
        with GameSource() as source:
            for group in catalog["resources"]:
                occurrence = group["occurrences"][0]
                blob = source.read(occurrence["bank"], occurrence["offset"], occurrence["size"])
                for row in group["textures"]:
                    try:
                        lookup[(occurrence["id"], row["number"], group["source_sha256"])] = decode_texture(blob, row)
                    except ValueError:
                        pass
        rows, used = [], set()
        for candidate in report["top"]:
            key = (candidate["id"], candidate["sprite"], candidate["source_sha256"])
            if key in used or key not in lookup:
                continue
            used.add(key)
            rows.append((candidate, lookup[key]))
            if len(rows) == 30:
                break
        cell_w, cell_h, columns = 160, 115, 3
        canvas = Image.new("RGBA", (cell_w * columns, cell_h * ((len(rows) + columns - 1) // columns)), (35, 35, 35, 255))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(canvas)
        for i, (candidate, image) in enumerate(rows):
            x, y = (i % columns) * cell_w, (i // columns) * cell_h
            shown = image.resize((image.width * 2, image.height * 2), Image.Resampling.NEAREST)
            canvas.alpha_composite(shown, (x + 4, y + 20))
            draw.text((x + 4, y + 4), f"{candidate['id']} #{candidate['sprite']} e={candidate['error']:.1f}", fill="white")
        args.contact.parent.mkdir(parents=True, exist_ok=True)
        canvas.convert("RGB").save(args.contact)
    print(json.dumps({"candidate_count": report["candidate_count"], "top": report["top"][:10], "report": str(args.report) if args.report else None}, indent=2), flush=True)


if __name__ == "__main__":
    main()
