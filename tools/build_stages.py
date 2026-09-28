"""Build 0.1.12 from 0.1.11 with all staged story and ship-name changes."""

import argparse
import copy
import json
import struct
from datetime import datetime, timezone

from stages_patch import FOLDER, PRIOR, TARGET, prepare, read, sha
from stages_names import prepare_names
from build_candidate import ROOT, copy_range, directory_records, extent_hash, hash_file
from scan_source import inventory
from sn3_archive import GameSource, child, parse_index
from sn3_repack import plan_bank, repack, write_bank

try:
    from stages_pupil_names import prepare_pupil_names
except ImportError:
    prepare_pupil_names = None


VERSION = "0.1.12"
EBOOT_PATH = "/PSP_GAME/SYSDIR/EBOOT.BIN"


def relative(path):
    return str(path.relative_to(ROOT)).replace("\\", "/")


def strip_inherited_execution_validation(value):
    if isinstance(value, dict):
        return {
            key: strip_inherited_execution_validation(item)
            for key, item in value.items()
            if "runtime" not in key.lower() and "visual" not in key.lower()
        }
    if isinstance(value, list):
        return [strip_inherited_execution_validation(item) for item in value]
    return value


def reviewed_inputs(selection):
    accepted_path = FOLDER / "accepted_review.json"
    accepted = read(accepted_path)
    all_inputs = dict(accepted["draft_inputs_sha256"])
    all_inputs.update(accepted["review_inputs_sha256"])
    all_inputs[relative(accepted_path)] = hash_file(accepted_path)
    expected_stage_inputs = dict(accepted["draft_inputs_sha256"])
    expected_stage_inputs[relative(accepted_path)] = hash_file(accepted_path)
    assert all(selection["review_inputs_sha256"].get(k)==v for k,v in expected_stage_inputs.items())
    for name, digest in all_inputs.items():
        assert hash_file(ROOT / name) == digest, name
    return all_inputs


def make_bank_plans(source, script, replacements):
    plan02 = plan_bank(source, "02.DAT", replacements)
    master = source.resource("00.DAT", 44)
    new_master = repack(master, {1: plan02["index_bytes"]})
    plan00 = plan_bank(source, "00.DAT", {44: new_master, 65: script})
    for plan in (plan00, plan02):
        file = source.files[plan["bank"]]
        plan.update(
            kind="bank",
            start=file["sector"] * 2048,
            end=file["sector"] * 2048 + file["size_bytes"],
            old_span=file["size_bytes"],
            new_span=plan["new_size"],
            path="/PSP_GAME/USRDIR/" + plan["bank"],
        )
        assert plan["new_size"] % 2048 == plan["old_size"] % 2048 == 0
    return [plan00, plan02], master, new_master


def make_eboot_plan(source, files):
    if prepare_pupil_names is None:
        raise RuntimeError("tools/stages_pupil_names.py is required before this builder can create 0.1.12")
    previous_elf = (PRIOR / "EBOOT.elf").read_bytes()
    eboot = next(row for row in files if row["path"] == EBOOT_PATH)
    assert extent_hash(source, eboot["sector"], eboot["size_bytes"]) == sha(previous_elf)
    patched, report = prepare_pupil_names(previous_elf)
    assert patched and report
    start = eboot["sector"] * 2048
    old_span = (eboot["size_bytes"] + 2047) // 2048 * 2048
    new_span = (len(patched) + 2047) // 2048 * 2048
    return {
        "kind": "eboot",
        "path": EBOOT_PATH,
        "start": start,
        "end": start + old_span,
        "old_size": eboot["size_bytes"],
        "new_size": len(patched),
        "old_span": old_span,
        "new_span": new_span,
        "data": patched,
        "report": report,
    }


def write_change(source, plan, out):
    if plan["kind"] == "bank":
        write_bank(source, plan, out)
        return
    out.write(plan["data"])
    out.write(bytes(plan["new_span"] - len(plan["data"])))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--dest", default="work/output/0.1.12")
    args = parser.parse_args()

    previous = read(PRIOR / "manifest.json")
    prior = PRIOR / previous["output_iso"]
    assert hash_file(prior) == previous["output_sha256"]
    destination = (ROOT / args.dest).resolve()
    assert ROOT in destination.parents
    iso = destination / "Summon_Night_3_EN_0.1.12.iso"

    with GameSource(prior) as source, prior.open("rb") as src:
        script, script_report, selection, stages_checks = prepare(source)
        replacements, stage_names = prepare_names(source)
        assert read(ROOT / TARGET) == selection
        review_hashes = reviewed_inputs(selection)
        bank_plans, master, new_master = make_bank_plans(source, script, replacements)
        _, directories, records = directory_records(src)
        _, files = inventory(src, prior.stat().st_size)
        eboot_plan = make_eboot_plan(src, files)
        plans = sorted(bank_plans + [eboot_plan], key=lambda plan: plan["start"])
        assert all(plan["end"] <= next_plan["start"] for plan, next_plan in zip(plans, plans[1:]))
        assert all(sector * 2048 + size < plans[0]["start"] for sector, size in directories)

        print(json.dumps({
            "mode": "write" if args.write else "dry run",
            "output": str(iso),
            "stages_checks": stages_checks,
            "stage_backlog_names": stage_names["names"],
            "banks": [{"bank": plan["bank"], "old": plan["old_size"], "new": plan["new_size"]} for plan in bank_plans],
            "executable": eboot_plan["report"],
            "preserve": "The 0.1.11 executable is the pupil-name patch baseline; all other ISO files, audio, and unrelated resources are verified unchanged.",
        }, indent=2), flush=True)
        if not args.write:
            return

        destination.mkdir()
        partial = iso.with_suffix(".iso.partial")
        with partial.open("xb") as out:
            cursor = 0
            for plan in plans:
                copy_range(src, out, cursor, plan["start"] - cursor)
                write_change(source, plan, out)
                cursor = plan["end"]
            copy_range(src, out, cursor, prior.stat().st_size - cursor)

        sizes = {plan["path"]: plan["new_size"] for plan in plans}
        with partial.open("r+b") as out:
            for record in records:
                delta = sum(
                    plan["new_span"] - plan["old_span"]
                    for plan in plans
                    if plan["end"] <= record["sector"] * 2048
                )
                sector = record["sector"] + delta // 2048
                size = sizes.get(record["path"], record["size_bytes"])
                out.seek(record["record_offset"] + 2)
                out.write(struct.pack("<I", sector) + struct.pack(">I", sector))
                out.seek(record["record_offset"] + 10)
                out.write(struct.pack("<I", size) + struct.pack(">I", size))
            sectors = partial.stat().st_size // 2048
            out.seek(16 * 2048 + 80)
            out.write(struct.pack("<I", sectors) + struct.pack(">I", sectors))

        verified = []
        with partial.open("rb") as out:
            _, actual = inventory(out, partial.stat().st_size)
            expected = {record["path"]: record for record in files}
            assert set(expected) == {record["path"] for record in actual}
            for record in actual:
                digest = extent_hash(out, record["sector"], record["size_bytes"])
                old = expected[record["path"]]
                if record["path"] not in sizes:
                    assert digest == extent_hash(src, old["sector"], old["size_bytes"]), record["path"]
                elif record["path"] == EBOOT_PATH:
                    assert digest == sha(eboot_plan["data"])
                verified.append({
                    "path": record["path"],
                    "sha256": digest,
                    "bytes": record["size_bytes"],
                    "changed": record["path"] in sizes,
                })

        unchanged_bank_resources = 0
        with GameSource(partial) as candidate:
            assert len(candidate.indexes) == 23
            for plan in bank_plans:
                for row in source.indexes[plan["bank"]]["entries"]:
                    number = row["id"]
                    data = candidate.resource(plan["bank"], number)
                    if number in plan["replacements"]:
                        expected_data = plan["replacements"][number]
                        assert data[:len(expected_data)] == expected_data and not any(data[len(expected_data):])
                    else:
                        assert data == source.resource(plan["bank"], number)
                        unchanged_bank_resources += 1
            old_index = parse_index(master, len(master))
            new_index = parse_index(new_master, len(new_master))
            for number in range(old_index["count"]):
                if number != 1:
                    assert child(master, old_index, number) == child(new_master, new_index, number)

        partial.rename(iso)
        manifest = copy.deepcopy(previous)
        for key in list(manifest):
            if "runtime" in key.lower() or "visual" in key.lower():
                manifest.pop(key)
        manifest.update(
            version=VERSION,
            built_at_utc=datetime.now(timezone.utc).isoformat(),
            output_iso=iso.name,
            output_size_bytes=iso.stat().st_size,
            output_sha256=hash_file(iso),
            previous_build_sha256=previous["output_sha256"],
            script_changes=[script_report],
            stage_backlog_names=stage_names,
            stages_checks=stages_checks,
            pupil_name_patch=eboot_plan["report"],
        )
        manifest["static_validation"] = {
            "prior_validation": strip_inherited_execution_validation(previous["static_validation"]),
            "comparison_build": "0.1.11",
            "iso_file_count": len(actual),
            "validated_bank_indexes": 23,
            "unchanged_iso_files": len(actual) - len(sizes),
            "unchanged_resources_in_changed_banks": unchanged_bank_resources,
            "changed_files": list(sizes),
            "per_file_validation": verified,
            "runtime_verified": False,
            "visual_verified": False,
        }
        manifest["inputs_sha256"].pop("work/translation/en/opening_harbor_0.1.11.targets.json", None)
        manifest["inputs_sha256"].update(review_hashes)
        for name in [
            TARGET,
            "tools/stages_patch.py",
            "tools/accept_stages_review.py",
            "tools/stages_names.py",
            "tools/stages_pupil_names.py",
            "tools/build_stages.py",
            "work/glossary/ship_0.1.12.json",
        ]:
            manifest["inputs_sha256"][name] = hash_file(ROOT / name)
        (destination / "EBOOT.elf").write_bytes(eboot_plan["data"])
        assert hash_file(destination / "EBOOT.elf") == sha(eboot_plan["data"])
        (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({
            "built": str(iso),
            "sha256": manifest["output_sha256"],
            "unchanged_files": len(actual) - len(sizes),
            "unchanged_bank_resources": unchanged_bank_resources,
        }, indent=2))


if __name__ == "__main__":
    main()
