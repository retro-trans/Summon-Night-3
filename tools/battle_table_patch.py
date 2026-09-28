"""Plan shared battle-table relocation against the 0.1.12 ISO; never writes an ISO."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import unicodedata

from dialogue_encoding import control_tokens, encode_dialogue
from index_interface import source_text
from sn3_archive import ROOT, GameSource, child, parse_index
from sn3_repack import repack


BASELINE = ROOT / "work/output/0.1.12/Summon_Night_3_EN_0.1.12.iso"
CATALOG = ROOT / "work/translation/en/battle_0.1.13/table.targets.json"
INDEX = ROOT / "work/translation/en/interface.index.json"
REVIEW = ROOT / "work/translation/en/battle_0.1.13/meaning_review.json"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def normalized_target(text):
    """Keep catalog wording, normalizing only punctuation before wide encoding."""
    if not text or any(char in text for char in "\0\r\n"):
        raise ValueError("Target text must be nonempty and single line")
    normalized = unicodedata.normalize("NFKC", text.translate(str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-"})))
    if any(ord(char) > 127 for char in normalized):
        raise ValueError("Target must be complete ASCII English before relocation")
    return normalized


def relocate_fullwidth(data, entries, starts, all_targets):
    """Relocate pointer-led pool groups, retaining every adjacent continuation."""
    known = {row["id"]: row for row in entries}
    order = {row["id"]: number for number, row in enumerate(entries)}
    out, changes, preserved = bytearray(data), [], []
    for identity, target in starts.items():
        row = known[identity]
        old = row["source_offset"]
        end = data.index(b"\0", old)
        if digest(data[old:end]) != target["source_sha256"]:
            preserved.append({"id": identity, "reason": "source string differs from indexed baseline"})
            continue
        fields = [reference["pointer_field_offset"] for reference in row["references"]]
        if any(struct.unpack_from("<I", data, field)[0] != old for field in fields):
            preserved.append({"id": identity, "reason": "pointer already differs from indexed baseline"})
            continue
        encoded, display = encode_dialogue(target["text"], data[old:end].decode("cp932"))
        out.extend(bytes((-len(out)) % 2))
        new = len(out)
        out.extend(encoded + b"\0\0")
        tails = []
        position = order[identity] + 1
        while position < len(entries) and entries[position]["ownership_status"] != "direct_pointer":
            tail = entries[position]
            tail_end = data.index(b"\0", tail["source_offset"])
            tail_target = all_targets.get(tail["id"])
            if tail_target and digest(data[tail["source_offset"]:tail_end]) == tail_target["source_sha256"]:
                tail_encoded, tail_display = encode_dialogue(tail_target["text"], data[tail["source_offset"]:tail_end].decode("cp932"))
                out.extend(tail_encoded + b"\0\0")
                tails.append({"id": tail["id"], "mode": "translated", "text": tail_target["text"], "display_text": tail_display})
            else:
                next_start = entries[position + 1]["source_offset"] if position + 1 < len(entries) else len(data)
                out.extend(data[tail["source_offset"]:next_start])
                tails.append({"id": tail["id"], "mode": "raw_preserved"})
            position += 1
        for field in fields:
            struct.pack_into("<I", out, field, new)
        if out[new:new + len(encoded)].decode("cp932") != display:
            raise ValueError("Relocated display text failed CP932 round trip")
        changes.append({"id": identity, "text": target["text"], "display_text": display,
                        "encoding_profile": "dialogue_fullwidth_cp932", "source_sha256": target["source_sha256"],
                        "old_offset": old, "new_offset": new, "old_byte_length": end - old,
                        "new_byte_length": len(encoded), "pointer_fields": fields, "continuations": tails})
    return bytes(out), changes, preserved


def load_catalog(path=CATALOG):
    catalog = json.loads(Path(path).read_text(encoding="utf-8"))
    index_bytes = INDEX.read_bytes()
    if catalog["source_index_sha256"] != digest(index_bytes):
        raise ValueError("Interface index hash differs from target catalog")
    index = json.loads(index_bytes)
    if REVIEW.exists():
        review = json.loads(REVIEW.read_text(encoding="utf-8"))
        overrides = review.get("table_overrides", {})
        existing = {entry["id"]: entry for entry in catalog["entries"]}
        for identity, text in overrides.items():
            if identity not in existing:
                raise ValueError("Review override has no catalog entry: " + identity)
            existing[identity]["target_full"] = text
        rows = {row["id"]: row for table in index["tables"] for row in table["strings"]}
        tables = {table["id"]: table for table in index["tables"]}
        for identity, text in review.get("additions", {}).items():
            if identity in existing or identity not in rows:
                raise ValueError("Invalid review addition: " + identity)
            row = rows[identity]
            table_id = identity.split(":ui:")[0]
            table = tables[table_id]
            existing[identity] = {"id": identity, "target_full": text, "source_sha256": row["source_sha256"],
                                  "source_offset": row["source_offset"], "source_control_tokens": row["source_control_tokens"],
                                  "source_kind": "table", "table_id": table_id, "table_source_sha256": table["source_sha256"],
                                  "references": row["references"]}
        catalog["entries"] = list(existing.values())
    return catalog, index


def plan(source, catalog_path=CATALOG):
    """Pure planning function: return patched resource bytes and a full audit report.

    The caller owns all final bank/ISO writes. Direct pointer-led groups are
    relocated together. Reviewed continuations are translated; unknown adjacent
    strings retain their original bytes.
    """
    catalog, index = load_catalog(catalog_path)
    tables = {table["id"]: table for table in index["tables"]}
    rows = {row["id"]: row for table in index["tables"] for row in table["strings"]}
    static = source.resource("02.DAT", 3)
    master = source.resource("00.DAT", 44)
    master_index = parse_index(master, len(master))
    if child(master, master_index, 7) != static:
        raise ValueError("00:44/7 is not the same baseline static-table payload as 02:3")

    grouped, all_grouped, skipped = {}, {}, []
    for target in catalog["entries"]:
        identity = target["id"]
        row = rows.get(identity)
        if row is None or target.get("source_kind") != "table":
            raise ValueError("Unknown non-table target: " + identity)
        table = tables[row["id"].split(":ui:")[0]]
        if target["table_id"] != table["id"] or target["table_source_sha256"] != table["source_sha256"]:
            raise ValueError("Table identity/hash mismatch: " + identity)
        if target["source_sha256"] != row["source_sha256"] or target["source_offset"] != row["source_offset"]:
            raise ValueError("Target source mismatch: " + identity)
        if target["source_control_tokens"] != row["source_control_tokens"]:
            raise ValueError("Target control-token manifest mismatch: " + identity)
        source_value = source_text(identity, index)
        if control_tokens(source_value) != target["source_control_tokens"]:
            raise ValueError("Source control tokens differ: " + identity)
        try:
            text = normalized_target(target["target_full"])
        except ValueError as exc:
            skipped.append({"id": identity, "reason": str(exc)})
            continue
        accepted = {"source_sha256": target["source_sha256"], "text": text}
        all_grouped.setdefault(table["id"], {})[identity] = accepted
        if row["ownership_status"] == "direct_pointer":
            grouped.setdefault(table["id"], {})[identity] = accepted

    changed_children, reports = {}, []
    static_index = parse_index(static, len(static))
    for table_id, targets in grouped.items():
        table = tables[table_id]
        number = table["resource_path"][1]
        before = child(static, static_index, number)
        entries = table["strings"]
        after, changes, preserved = relocate_fullwidth(before, entries, targets, all_grouped[table_id])
        skipped.extend(preserved)
        changed_children[number] = after
        reports.append({"table_id": table_id, "child": number, "source_sha256": digest(before), "patched_sha256": digest(after), "changes": changes, "preserved": preserved})

    patched_static = repack(static, changed_children)
    patched_master = repack(master, {7: patched_static})
    return {
        "resources": {"02:00003": patched_static, "00:00044": patched_master},
        "report": {
            "baseline": str(BASELINE), "catalog": str(Path(catalog_path)), "selected_entries": sum(len(v) for v in grouped.values()),
            "skipped_entries": len(skipped), "skipped": skipped,
            "table_count": len(reports), "tables": reports,
            "source_static_sha256": digest(static), "patched_static_sha256": digest(patched_static),
            "source_master_sha256": digest(master), "patched_master_sha256": digest(patched_master),
            "shared_copy_verified": True, "writes_performed": False,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, default=BASELINE)
    args = parser.parse_args()
    with GameSource(args.baseline) as source:
        result = plan(source)
    report = result["report"]
    report["samples"] = [
        {key: change[key] for key in ("id", "text", "old_offset", "new_offset", "pointer_fields")}
        for table in report["tables"] for change in table["changes"][:1]
    ]
    summary = {key: report[key] for key in ("baseline", "catalog", "selected_entries", "skipped_entries", "table_count", "source_static_sha256", "patched_static_sha256", "source_master_sha256", "patched_master_sha256", "shared_copy_verified", "writes_performed")}
    summary["skipped_count"] = len(report["skipped"])
    summary["skipped_sample"] = report["skipped"][:8]
    summary["samples"] = report["samples"]
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
