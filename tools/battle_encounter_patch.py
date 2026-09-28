"""Plan native encounter-title texture replacements in 01.DAT without writing an ISO.

The generated artwork index is deliberately separate from this importer.  Each
entry names its rendered PNG and one or more reviewed source textures.  This
module finds byte-identical 01.DAT occurrences by source hash, patches every
such occurrence, and reports matching payloads in other banks as unsupported.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

from sn3_archive import ROOT, GameSource, child, parse_v4
from sn3_repack import repack
from sn3_ui_textures import decode_texture, texture_records
from setup_ui_patch import encode_texture


BASELINE = ROOT / "work/output/0.1.12/Summon_Night_3_EN_0.1.12.iso"
DISCOVERY = ROOT / "work/ui/battle_0.1.13/intro_discovery_01_00004_00064_full/index.json"
GLOBAL_INDEX = ROOT / "work/ui/interface_graphics.index.json"
GENERATED = ROOT / "work/ui/battle_0.1.13/encounter_generated/index.json"
PREVIEWS = ROOT / "work/ui/battle_0.1.13/encounter_generated/previews"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path):
    if not path.exists():
        raise FileNotFoundError("Required reviewed encounter-art index is missing: " + str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def occurrence_id(path: list[int]) -> str:
    if len(path) != 2:
        raise ValueError("Only two-level 01.DAT resource paths are supported: " + repr(path))
    return "01:%05d/%05d" % tuple(path)


def alpha_range(image: Image.Image) -> tuple[int, int]:
    alpha = np.asarray(image.convert("RGBA"), dtype=np.uint8)[..., 3]
    return int(alpha.min()), int(alpha.max())


def resized_rgba(path: Path, expected_sha: str, size: tuple[int, int]) -> Image.Image:
    raw = path.read_bytes()
    if sha(raw) != expected_sha:
        raise ValueError("Generated image hash differs from approved index: " + str(path))
    with Image.open(path) as opened:
        image = opened.convert("RGBA")
    if image.size != size:
        image = image.resize(size, Image.Resampling.LANCZOS)
    low, high = alpha_range(image)
    if low != 0 or high != 255:
        raise ValueError("Encounter output must retain fully transparent and opaque pixels: " + str(path))
    return image


def prepare(source, generated_path: Path = GENERATED):
    """Return ``(top_resource_replacements, previews, report)`` without writing.

    ``replacements`` maps a top-level 01.DAT resource number to its repacked V4
    bytes.  ``previews`` contains decoded, palette-quantized RGBA images ready
    for the optional CLI preview writer.
    """
    discovery = load_json(DISCOVERY)
    global_index = load_json(GLOBAL_INDEX)
    generated = load_json(generated_path)
    if discovery.get("source_index_sha256") != sha(GLOBAL_INDEX.read_bytes()):
        raise ValueError("Encounter discovery was made against a different global graphics index")
    entries = generated.get("entries", generated.get("artwork", []))
    if not isinstance(entries, list) or not entries:
        raise ValueError("Encounter generated index must contain a nonempty entries list")

    discovery_rows = {row["id"]: row for row in discovery["candidates"]}
    groups = {row["source_sha256"]: row for row in global_index["resources"]}
    planned: dict[tuple[int, int, int], dict] = {}
    approved_target_count = 0
    supported_occurrence_count = 0
    unsupported, entry_reports = [], []

    for entry in entries:
        required = {"key", "file", "sha256", "prompt", "targets"}
        missing = required - set(entry)
        if missing:
            raise ValueError("Generated entry is missing required fields: " + ", ".join(sorted(missing)))
        if not isinstance(entry["targets"], list) or not entry["targets"]:
            raise ValueError("Generated entry has no reviewed targets: " + entry["key"])
        asset = (generated_path.parent / entry["file"]).resolve()
        if generated_path.parent.resolve() not in asset.parents:
            raise ValueError("Generated image must stay within encounter_generated: " + entry["file"])
        if not asset.is_file():
            raise FileNotFoundError("Generated encounter image is missing: " + str(asset))

        entry_targets = []
        for target in entry["targets"]:
            needed = {"resource_id", "number", "source_sha256"}
            if needed - set(target):
                raise ValueError("Target lacks resource_id, number, or source_sha256: " + entry["key"])
            sprite_id = target["resource_id"] + ":sprite:%03d" % target["number"]
            discovered = discovery_rows.get(sprite_id)
            if discovered is None:
                raise ValueError("Target is not an approved encounter discovery sprite: " + sprite_id)
            if discovered["source_sha256"] != target["source_sha256"]:
                raise ValueError("Target source hash differs from encounter discovery: " + sprite_id)
            resource_group = groups.get(target["source_sha256"])
            if resource_group is None:
                raise ValueError("Target source hash is absent from global graphics index: " + sprite_id)
            image = resized_rgba(asset, entry["sha256"], (discovered["width"], discovered["height"]))
            approved_target_count += 1
            for occurrence in resource_group["occurrences"]:
                if occurrence["bank"] != "01.DAT":
                    unsupported.append({"key": entry["key"], "source_sha256": target["source_sha256"],
                                        "occurrence": occurrence["id"], "bank": occurrence["bank"],
                                        "reason": "same_payload_in_other_bank_not_patched"})
                    continue
                if len(occurrence["path"]) != 2:
                    unsupported.append({"key": entry["key"], "source_sha256": target["source_sha256"],
                                        "occurrence": occurrence["id"], "bank": occurrence["bank"],
                                        "reason": "unsupported_nested_01_path"})
                    continue
                top, child_number = occurrence["path"]
                plan_key = (top, child_number, int(target["number"]))
                prior = planned.get(plan_key)
                if prior and (prior["asset_sha256"], prior["entry_key"]) != (entry["sha256"], entry["key"]):
                    raise ValueError("Two generated entries target the same 01.DAT sprite: " + repr(plan_key))
                planned[plan_key] = {"entry_key": entry["key"], "prompt": entry["prompt"],
                                     "asset": asset, "asset_sha256": entry["sha256"], "source_sha256": target["source_sha256"],
                                     "resource_id": occurrence_id(occurrence["path"]), "top": top,
                                     "child": child_number, "number": int(target["number"]), "image": image}
                supported_occurrence_count += 1
            entry_targets.append({"sprite_id": sprite_id, "source_sha256": target["source_sha256"],
                                  "source_bounds": [discovered["width"], discovered["height"]]})
        entry_reports.append({"key": entry["key"], "file": entry["file"], "sha256": entry["sha256"],
                              "prompt": entry["prompt"], "targets": entry_targets})

    by_top: dict[int, list[dict]] = defaultdict(list)
    for plan in planned.values():
        by_top[plan["top"]].append(plan)
    replacements, previews, records = {}, [], []
    for top, changes in sorted(by_top.items()):
        original_outer = source.resource("01.DAT", top)
        outer_index = parse_v4(original_outer)
        children: dict[int, bytes] = {}
        for change in sorted(changes, key=lambda row: (row["child"], row["number"])):
            original_payload = child(original_outer, outer_index, change["child"])
            if sha(original_payload) != change["source_sha256"]:
                raise ValueError("01.DAT occurrence source hash differs from approved target: " + change["resource_id"])
            payload = children.get(change["child"], original_payload)
            row = next((item for item in texture_records(payload) if item["number"] == change["number"]), None)
            if row is None:
                raise ValueError("Target sprite number is absent from 01.DAT payload: " + change["resource_id"])
            before = decode_texture(payload, row)
            if before.size != change["image"].size:
                raise ValueError("Resized encounter image does not match native texture bounds")
            identity, _, _ = encode_texture(payload, row, before.copy())
            if identity != payload:
                raise ValueError("Native texture identity re-encode changed bytes: " + change["resource_id"])
            patched, decoded, changed = encode_texture(payload, row, change["image"])
            low, high = alpha_range(decoded)
            if low != 0 or high != 255:
                raise ValueError("Palette-quantized encounter output lost alpha extrema: " + change["resource_id"])
            children[change["child"]] = patched
            preview_name = "%s__01_%05d_%05d_sprite_%03d.png" % (change["entry_key"], top, change["child"], change["number"])
            previews.append((preview_name, decoded))
            records.append({"key": change["entry_key"], "resource_id": change["resource_id"], "number": change["number"],
                            "source_sha256": change["source_sha256"], "generated_file": str(change["asset"].relative_to(generated_path.parent)),
                            "generated_sha256": change["asset_sha256"], "source_bounds": list(before.size),
                            "resized": list(Image.open(change["asset"]).size) != list(before.size),
                            "changed_pixels": changed, "alpha_min": low, "alpha_max": high,
                            "decoded_rgba_sha256": sha(decoded.tobytes()), "preview": preview_name})
        packed = repack(original_outer, children)
        check_index = parse_v4(packed)
        for item in outer_index["entries"]:
            original_child = child(original_outer, outer_index, item["id"])
            rebuilt_child = child(packed, check_index, item["id"])
            if item["id"] in children:
                if rebuilt_child != children[item["id"]]:
                    raise ValueError("Repacked changed 01.DAT child differs from planned bytes")
            elif rebuilt_child != original_child:
                raise ValueError("Repack altered an untouched 01.DAT child")
        replacements[top] = packed

    report = {"schema_version": 1, "version": "0.1.13", "scope": "Reviewed encounter title/condition graphics in 01.DAT only.",
              "inputs_sha256": {str(DISCOVERY.relative_to(ROOT)).replace("\\", "/"): sha(DISCOVERY.read_bytes()),
                                str(GLOBAL_INDEX.relative_to(ROOT)).replace("\\", "/"): sha(GLOBAL_INDEX.read_bytes()),
                                str(generated_path.relative_to(ROOT)).replace("\\", "/"): sha(generated_path.read_bytes()),
                                "tools/battle_encounter_patch.py": sha(Path(__file__).read_bytes())},
              "generated_entries": entry_reports, "approved_target_count": approved_target_count,
              "targeted_sprite_count": len(planned), "supported_01_occurrence_count": supported_occurrence_count,
              "top_resource_count": len(replacements), "duplicate_01_occurrence_count": max(0, supported_occurrence_count - approved_target_count),
              "unsupported_other_bank_occurrences": unsupported,
              "unsupported_other_bank_count": len(unsupported), "records": records,
              "replacements": [{"top_resource": top, "source_sha256": sha(source.resource("01.DAT", top)),
                                  "patched_sha256": sha(data), "bytes": len(data)} for top, data in sorted(replacements.items())],
              "native_palette_and_geometry_preserved": True, "untouched_pixels_preserved": True,
              "identity_encode_verified": True, "alpha_extrema_verified": True, "writes_performed": False}
    return replacements, previews, report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write only decoded preview PNGs; never write an ISO or resource binary.")
    args = parser.parse_args()
    with GameSource(BASELINE) as source:
        replacements, previews, report = prepare(source)
    summary = {"mode": "write_previews_only" if args.write else "dry_run", "targeted_sprite_count": report["targeted_sprite_count"],
               "top_resource_count": report["top_resource_count"], "duplicate_01_occurrence_count": report["duplicate_01_occurrence_count"],
               "unsupported_other_bank_count": report["unsupported_other_bank_count"], "replacements": report["replacements"],
               "records": report["records"]}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.write:
        if PREVIEWS.exists():
            raise FileExistsError("Preview directory already exists: " + str(PREVIEWS))
        PREVIEWS.mkdir(parents=True)
        for name, image in previews:
            image.save(PREVIEWS / name)
        (PREVIEWS / "index.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
