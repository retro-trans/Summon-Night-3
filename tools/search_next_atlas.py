"""Rank subrectangles in catalogued texture atlases against the tutorial 送る glyphs.

Read-only source analysis.  The target is cropped from the supplied 2x runtime
capture and compared as an edge map at native and doubled source scale.  A
contact sheet is intentionally left to the caller after inspecting the report.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

from sn3_archive import GameSource, ROOT
from sn3_ui_textures import decode_texture

CROP = Path(r"C:/Users/Binh/AppData/Local/Temp/codex-clipboard-6cc69a1b-d649-4311-82d7-86cb05625ec7.png")


def edges(image):
    gray = np.asarray(image.convert("L"), dtype=np.float32)
    dx = np.abs(np.diff(gray, axis=1, prepend=gray[:, :1]))
    dy = np.abs(np.diff(gray, axis=0, prepend=gray[:1, :]))
    return np.clip(dx + dy, 0, 255)


def fast_edges(data, row):
    """Vectorized equivalent of the verified single-palette decoder, for QA."""
    if row["format"] not in (4, 5) or row["swizzled"] not in (0, 1):
        raise ValueError("unsupported texture")
    import struct
    fmt, pitch, height = row["format"], row["pitch"], row["height"]
    row_bytes = pitch if fmt == 5 else (pitch + 1) // 2
    stored_height, remainder = divmod(row["data_size"], row_bytes)
    if remainder or stored_height not in (height, height + 8):
        raise ValueError("bad storage")
    values = np.frombuffer(data[row["data_offset"]:row["data_offset"] + row["data_size"]], dtype=np.uint8)
    if row["swizzled"]:
        if row_bytes % 16 or stored_height % 8:
            raise ValueError("bad swizzle")
        values = values.reshape(stored_height // 8, row_bytes // 16, 8, 16).transpose(0, 2, 1, 3).reshape(stored_height, row_bytes)
    else:
        values = values.reshape(stored_height, row_bytes)
    if fmt == 4:
        values = np.stack((values & 15, values >> 4), axis=-1).reshape(stored_height, pitch)
    base = row["palette_base"]
    count = struct.unpack_from("<I", data, base)[0]
    offset, size, pal_fmt, colors = struct.unpack_from("<4I", data, base + 4)
    if count != 1 or row["palette"] or pal_fmt != 3 or size != colors * 4 or colors not in (16, 256):
        raise ValueError("unsupported palette")
    palette = np.frombuffer(data[base + offset:base + offset + size], dtype=np.uint8).reshape(colors, 4)
    if int(values.max()) >= colors:
        raise ValueError("bad index")
    rgba = palette[values][:height, :row["width"]]
    gray = rgba[:, :, :3].mean(axis=2).astype(np.float32)
    return np.clip(np.abs(np.diff(gray, axis=1, prepend=gray[:, :1])) + np.abs(np.diff(gray, axis=0, prepend=gray[:1, :])), 0, 255)


def ncc_map(source, template):
    """Non-negative edge correlation with an integral-image normalization."""
    h, w = template.shape
    if source.shape[0] < h or source.shape[1] < w:
        return None
    # Cross correlation by FFT; template has only edge energy, so beige/alpha
    # backgrounds do not dominate the score.
    shape = (source.shape[0] + h - 1, source.shape[1] + w - 1)
    product = np.fft.irfftn(np.fft.rfftn(source, shape) * np.fft.rfftn(template[::-1, ::-1], shape), shape)
    dot = product[h - 1:source.shape[0], w - 1:source.shape[1]]
    # Float64 avoids accumulated-sum cancellation on 512px atlases, which can
    # otherwise produce an impossible correlation score above one.
    sq = np.pad((source * source).astype(np.float64), ((1, 0), (1, 0))).cumsum(0).cumsum(1)
    energy = sq[h:, w:] - sq[:-h, w:] - sq[h:, :-w] + sq[:-h, :-w]
    denom = np.sqrt(np.maximum(energy * float((template * template).sum()), 1.0))
    return dot / denom


def rank(checkpoint):
    # The word itself, excluding controller ring and most parchment capsule.
    capture = Image.open(CROP).convert("RGBA")
    glyphs = capture.crop((62, 12, 133, 65))
    templates = [("2x", edges(glyphs)), ("1x", edges(glyphs.resize((36, 26), Image.Resampling.LANCZOS)))]
    catalog = json.loads((ROOT / "work/ui/interface_graphics.index.json").read_text())
    result, seen = [], set()
    scanned = 0
    with GameSource() as source:
        for group in catalog["resources"]:
            occurrence = group["occurrences"][0]
            blob = source.read(occurrence["bank"], occurrence["offset"], occurrence["size"])
            for row in group["textures"]:
                key = (group["source_sha256"], row["number"])
                if key in seen:
                    continue
                seen.add(key)
                # Whole small sprites were scanned separately.  This pass is
                # specifically for source atlases whose runtime UV may select
                # an unknown subrectangle.
                if not (row["width"] > 256 or row["height"] > 80):
                    continue
                try:
                    source_edges = fast_edges(blob, row)
                except ValueError:
                    continue
                for scale in (1,):
                    for label, template in templates:
                        scores = ncc_map(source_edges, template)
                        if scores is None:
                            continue
                        y, x = np.unravel_index(np.argmax(scores), scores.shape)
                        result.append({"score": float(scores[y, x]), "id": occurrence["id"], "bank": occurrence["bank"],
                                       "path": occurrence["path"], "sprite": row["number"], "source_size": [row["width"], row["height"]],
                                       "source_scale": scale, "template": label, "xy": [int(x), int(y)],
                                       "source_sha256": group["source_sha256"]})
                scanned += 1
                if scanned % 100 == 0:
                    result.sort(key=lambda item: item["score"], reverse=True)
                    checkpoint.write_text(json.dumps({"status": "running", "supported_large_textures_scanned": scanned, "top": result[:100]}, indent=2) + "\n")
    # Selected decoded exports cover compressed UI resources that are absent
    # from the raw recursive catalog (notably 02:00027–00029).
    for folder in ("setup_assets_complete", "battle_assets", "menu_discovery"):
        root = ROOT / "work/ui" / folder
        index = json.loads((root / "index.json").read_text())
        for row in index["textures"]:
            if not (row["width"] > 256 or row["height"] > 80):
                continue
            image = Image.open(root / row["image_file"]).convert("RGBA")
            source_edges = edges(image)
            for label, template in templates:
                scores = ncc_map(source_edges, template)
                if scores is None:
                    continue
                y, x = np.unravel_index(np.argmax(scores), scores.shape)
                result.append({"score": float(scores[y, x]), "id": row["resource_id"], "bank": "decoded_export",
                               "path": [folder, row["image_file"]], "sprite": row["number"],
                               "source_size": [row["width"], row["height"]], "source_scale": 1, "template": label,
                               "xy": [int(x), int(y)], "source_sha256": row["source_sha256"]})
    result.sort(key=lambda item: item["score"], reverse=True)
    return {"status": "complete", "target_crop": [62, 12, 133, 65], "result_count": len(result), "top": result[:100]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = rank(args.report)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"result_count": report["result_count"], "top": report["top"][:10], "report": str(args.report)}, indent=2))


if __name__ == "__main__":
    main()
