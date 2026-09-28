"""Render plausible whole-texture sizes for the tutorial navigation prompt.

Read-only source inspection; output is a scratch contact sheet only.
"""
from pathlib import Path
import json
from PIL import Image, ImageDraw
from sn3_archive import ROOT, GameSource
from sn3_ui_textures import decode_texture

SIZES = {(64, 32), (64, 40), (72, 40), (128, 64), (128, 48), (96, 48), (64, 48), (128, 32)}
OUT = Path(r"C:/Users/Binh/.codex/visualizations/2026/09/26/01a0db63-acc7-7ff0-b061-538dd1602405/next_size_candidates.png")

catalog = json.loads((ROOT / "work/ui/interface_graphics.index.json").read_text())
rows = []
with GameSource() as source:
    for group in catalog["resources"]:
        occurrence = group["occurrences"][0]
        blob = source.read(occurrence["bank"], occurrence["offset"], occurrence["size"])
        for record in group["textures"]:
            if (record["width"], record["height"]) not in SIZES:
                continue
            try:
                rows.append((occurrence["id"], record["number"], decode_texture(blob, record)))
            except ValueError:
                pass

cols, cw, ch = 4, 240, 150
sheet = Image.new("RGB", (cols * cw, ((len(rows) + cols - 1) // cols) * ch), (48, 48, 48))
draw = ImageDraw.Draw(sheet)
for i, (resource_id, sprite, image) in enumerate(rows):
    x, y = (i % cols) * cw, (i // cols) * ch
    thumbnail = image.copy(); thumbnail.thumbnail((232, 118), Image.Resampling.NEAREST)
    sheet.paste(thumbnail.convert("RGB"), (x + 4, y + 25))
    draw.text((x + 4, y + 5), f"{resource_id} #{sprite} {image.width}x{image.height}", fill="white")
OUT.parent.mkdir(parents=True, exist_ok=True)
sheet.save(OUT)
print(json.dumps({"images": len(rows), "output": str(OUT)}))
