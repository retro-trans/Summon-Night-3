"""Safely relocate reviewed battle ELF literals into the existing added segment.

This tool does not alter an output build or an ISO.  ``prepare`` is pure; the
CLI first reports a dry run, and --write creates one new scratch candidate.
Only references proven by the PSP relocation records are patched.  Targets
without a direct relocation-backed start reference, with a shared/ambiguous
HI16 pair, or with an interior reference are reported as skipped.
"""
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

from battle_elf_refs import references
from dialogue_encoding import encode_dialogue
from sn3_archive import ROOT
from stages_pupil_names import align, parse_elf, signed16, validate_loader_structure


BASELINE = ROOT / "work/output/0.1.12/EBOOT.elf"
TARGETS = ROOT / "work/translation/en/battle_0.1.13/executable.targets.json"
LAYOUT_REVIEW = ROOT / "work/translation/en/battle_0.1.13/executable.layout_review.json"
MEANING_REVIEW = ROOT / "work/translation/en/battle_0.1.13/meaning_review.json"
INTERFACE_INDEX = ROOT / "work/translation/en/interface.index.json"
DEFAULT_OUTPUT = ROOT / "work/scratch/battle_elf_patch_0.1.13"
ELF_HEADER_SHOFF = 0x20
PROGRAM_HEADER_SIZE = 32
SECTION_HEADER_SIZE = 40


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def word(data, module_address):
    return struct.unpack_from("<I", data, module_address + 0xC0)[0]


def resolved_address(high_word, low_word):
    return ((high_word & 0xFFFF) << 16) + signed16(low_word & 0xFFFF)


def span_contains(spans, offset):
    return any(start <= offset < end for start, end in spans)


FIXED_LABEL_LIMITS = {
    # The stock labels are exceptionally short and are rendered in fixed UI
    # boxes.  A reviewer must provide a compact variant before we relocate one.
    "elf:ui:0021af8c": 8,   # battle-preparation header
    "elf:ui:0021af98": 8,   # start-battle command
    "elf:ui:0021afc8": 8,   # status command
    "elf:ui:0021afdc": 8,   # reposition command
    "elf:ui:0021afe8": 8,   # change-facing command
    "elf:ui:0021b6fc": 8,   # change-facing command, second consumer group
    "elf:ui:0021efa0": 4,   # victory-condition heading
    "elf:ui:0021efac": 4,   # defeat-condition heading
}

# Only these three adjacent choice records have a proven sequential consumer:
# 0x1a31c walks U16 strings to a NUL, then tests the next U16 and repeats.
# The roots come from getter 0x67e08's 0x22847c table (indices 5..7); 0x1bdd8
# assigns the final two strings choice-row type 4.  Other unreferenced tails
# are not relocated until their stride/consumer is proven; in particular, the
# status-abbreviation block must not be expanded.
TRANSLATABLE_TAIL_ROOTS = {0x218260, 0x218288, 0x2182B4}


def indexed_rows(path=INTERFACE_INDEX):
    source = json.loads(path.read_text(encoding="utf-8"))
    return {row["id"]: row for row in source["executable_literals"]}


def target_rows(path=TARGETS, overrides=None):
    """Load immutable drafts and apply optional reviewer-approved field overrides.

    The override document may be a list, or an object with an ``entries`` list.
    Each item must name an existing id; only target text and review metadata are
    accepted, so it cannot silently alter source locations or hashes.
    """
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("build_version") != "0.1.13":
        raise ValueError("Expected the immutable 0.1.13 executable target document")
    rows = [dict(row) for row in document["entries"]]
    override_sources = [LAYOUT_REVIEW, MEANING_REVIEW] if overrides is None else (overrides if isinstance(overrides, list) else [overrides])
    by_id = {row["id"]: row for row in rows}
    allowed = {"target_full", "target_compact", "meaning_status", "meaning_notes"}
    for source in override_sources:
        if isinstance(source, (str, Path)):
            if not Path(source).exists():
                raise FileNotFoundError("Meaning/layout override file is required: " + str(source))
            supplied = json.loads(Path(source).read_text(encoding="utf-8"))
        else:
            supplied = source
        if isinstance(supplied, dict) and "executable_overrides" in supplied:
            supplied = [{"id": key, "target_full": value, "meaning_status": "reviewed"}
                        for key, value in supplied["executable_overrides"].items()]
        else:
            supplied = supplied.get("entries", supplied) if isinstance(supplied, dict) else supplied
        if not isinstance(supplied, list):
            raise ValueError("Meaning overrides must contain an entries list")
        for change in supplied:
            target = by_id.get(change.get("id"))
            if target is None:
                raise ValueError("Meaning override does not name a draft target: " + str(change.get("id")))
            unexpected = set(change) - allowed - {"id"}
            if unexpected:
                raise ValueError("Meaning override cannot alter source metadata: " + ", ".join(sorted(unexpected)))
            target.update({key: value for key, value in change.items() if key != "id"})
    return rows


def source_bytes(elf, target, index_row):
    start = target["source_offset"]
    length = index_row["source_byte_length"]
    raw = elf[start:start + length]
    if len(raw) != length or sha256(raw) != target["source_sha256"]:
        raise ValueError("Source literal hash changed: " + target["id"])
    if raw != (ROOT / "work/source/EBOOT.elf").read_bytes()[start:start + length]:
        raise ValueError("0.1.12 changed the selected source literal: " + target["id"])
    return raw


def encoded_target(target, source_raw):
    source = source_raw.decode("cp932", "strict")
    compact = target.get("target_compact")
    maximum = FIXED_LABEL_LIMITS.get(target["id"])
    if maximum is not None:
        if not compact:
            raise ValueError("fixed_width_label_requires_reviewer_compact_variant")
        if len(compact) > maximum:
            raise ValueError("compact_variant_exceeds_fixed_width_limit_" + str(maximum))
        text = compact
    else:
        # Compact text is only an explicit opt-in for an original short label.
        text = compact if compact and len(source) <= 8 else target["target_full"]
    encoded, display = encode_dialogue(text, source)
    return text, display, encoded + b"\0\0", "compact" if text == compact else "full"


def interior_references(reference_map, start, length):
    return {address: refs for address, refs in reference_map.items() if start < address < start + length}


def safe_reference_set(elf, reference_map, users, pairs, target, source_raw):
    start = int(target["module_address"], 16)
    direct = reference_map.get(start, [])
    interiors = interior_references(reference_map, start, len(source_raw))
    if interiors:
        return None, {"reason": "interior_references_require_separate_consumer_proof",
                      "interior_addresses": [hex(address) for address in sorted(interiors)]}
    if not direct:
        return None, {"reason": "no_relocation_backed_start_reference"}
    checked = []
    for ref in direct:
        if ref["kind"] == "pointer":
            location = ref["address"] + 0xC0
            if word(elf, ref["address"]) != start:
                return None, {"reason": "pointer_word_no_longer_matches_start"}
            checked.append({"kind": "pointer", "instruction": ref["address"]})
            continue
        high, low = ref["high"], ref["low"]
        high_word, low_word = word(elf, high), word(elf, low)
        if high_word >> 26 != 15 or low_word >> 26 != 9:
            return None, {"reason": "unexpected_hilo_opcodes", "high": hex(high), "low": hex(low)}
        if resolved_address(high_word, low_word) != start:
            return None, {"reason": "hilo_pair_no_longer_resolves_to_start", "high": hex(high), "low": hex(low)}
        if pairs.get(high) != low:
            return None, {"reason": "hilo_pair_not_ppsspp_next_non_hi_pair", "high": hex(high), "low": hex(low),
                          "paired_low": hex(pairs[high]) if high in pairs else None}
        all_users = users.get(high, [])
        if all_users != [{"low": low, "target": start, "opcode": 9}]:
            return None, {"reason": "shared_hi16_has_unproven_other_low_user", "high": hex(high),
                          "users": all_users}
        checked.append({"kind": "hilo", "high": high, "low": low, "register": ref["register"]})
    return checked, None


def prepare(elf: bytes, targets=None, index=None):
    """Return patched ELF bytes and an audit report without writing files."""
    baseline_sha = sha256(elf)
    if not BASELINE.exists() or baseline_sha != sha256(BASELINE.read_bytes()):
        raise ValueError("Input must be the current 0.1.12 EBOOT baseline")
    index = indexed_rows() if index is None else index
    targets = target_rows() if targets is None else targets
    refs, users, pairs = references(elf)
    by_start = {int(target["module_address"], 16): target for target in targets}
    direct_starts = sorted(address for address in by_start if address in refs)
    selected, skipped = [], []
    for target in targets:
        row = index.get(target["id"])
        if row is None or row["module_address"] != target["module_address"]:
            raise ValueError("Target/index mismatch: " + target["id"])
        raw = source_bytes(elf, target, row)
        checked, reason = safe_reference_set(elf, refs, users, pairs, target, raw)
        if reason:
            skipped.append({"id": target["id"], "module_address": target["module_address"], **reason})
            continue
        try:
            text, display, encoded, variant = encoded_target(target, raw)
        except (UnicodeError, ValueError) as exc:
            skipped.append({"id": target["id"], "module_address": target["module_address"],
                            "reason": "target_encoding_or_control_token_not_safe", "detail": str(exc)})
            continue
        selected.append({"id": target["id"], "module_address": int(target["module_address"], 16),
                         "source_offset": target["source_offset"], "source_sha256": target["source_sha256"],
                         "source_bytes": raw, "text": text, "display_text": display,
                         "encoded": encoded, "variant": variant, "references": checked})

    # A relocated prompt root can be followed by choices without their own
    # relocation.  Keep those literals and the original padding as one bundle;
    # otherwise a native consumer that walks the prompt record can reach stale
    # source text.  A tail with unsafe encoding blocks its root rather than
    # leaving a partly relocated record behind.
    kept, bundled_skips = [], []
    for entry in selected:
        start = entry["module_address"]
        next_root = next((address for address in direct_starts if address > start), None)
        literal_starts = [start] + [address for address in sorted(by_start)
                                    if start < address < (next_root if next_root is not None else 0xFFFFFFFF)
                                    and address not in refs]
        if len(literal_starts) > 1 and start not in TRANSLATABLE_TAIL_ROOTS:
            bundled_skips.append({"id": entry["id"], "module_address": hex(start),
                                  "reason": "adjacent_literals_consumer_or_stride_not_proven",
                                  "tail_ids": [by_start[address]["id"] for address in literal_starts[1:]]})
            continue
        bundle = bytearray()
        tail_entries = []
        blocked = None
        for position, literal_start in enumerate(literal_starts):
            target = by_start[literal_start]
            row = index.get(target["id"])
            try:
                raw = entry["source_bytes"] if literal_start == start else source_bytes(elf, target, row)
                preserved_source = False
                if literal_start == start:
                    encoded, text, display, variant = entry["encoded"], entry["text"], entry["display_text"], entry["variant"]
                elif start not in TRANSLATABLE_TAIL_ROOTS:
                    encoded, text, display, variant = raw, None, None, "source_preserved_unproven_consumer"
                    preserved_source = True
                else:
                    text, display, encoded, variant = encoded_target(target, raw)
                bundle.extend(encoded)
                if literal_start != start:
                    tail_entries.append({"id": target["id"], "module_address": literal_start,
                                         "source_sha256": target["source_sha256"], "text": text,
                                         "display_text": display, "encoded_bytes": len(encoded), "variant": variant})
                next_literal = literal_starts[position + 1] if position + 1 < len(literal_starts) else next_root
                if next_literal is not None:
                    gap = elf[literal_start + len(raw) + 0xC0:next_literal + 0xC0]
                    # Translated text already has its two-byte terminator.  The
                    # old gap starts with that terminator, followed only by any
                    # alignment padding; copying it whole would create an empty
                    # choice before the next bundled string.
                    if not preserved_source:
                        if gap[:2] != b"\0\0":
                            raise ValueError("translated bundle literal has no source terminator")
                        gap = gap[2:]
                    bundle.extend(gap)
            except (UnicodeError, ValueError) as exc:
                blocked = {"id": entry["id"], "module_address": hex(start),
                           "reason": "unreferenced_tail_not_safe_to_bundle", "tail_id": target["id"], "detail": str(exc)}
                break
        if blocked:
            bundled_skips.append(blocked)
        else:
            entry["bundle"] = bytes(bundle)
            entry["tail_entries"] = tail_entries
            kept.append(entry)
    selected, skipped = kept, skipped + bundled_skips

    parsed = parse_elf(elf)
    phdrs = [header[:] for header in parsed["phdrs"]]
    sections = [section[:] for section in parsed["sections"]]
    added_indices = [n for n, header in enumerate(phdrs) if header[0] == 1 and header[2] == 0x32DBC0]
    if added_indices != [3]:
        raise ValueError("Expected the existing added PT_LOAD segment at 0x32dbc0")
    added_index = added_indices[0]
    added_original = parsed["phdrs"][added_index]
    added = phdrs[added_index]
    if added[6] != 5 or added[7] != 0x40 or added[4] != added[5]:
        raise ValueError("Unexpected existing added PT_LOAD shape")
    insert = added[1] + added[4]
    relocation_indices = [n for n, header in enumerate(phdrs) if header[0] == 0x700000A0]
    if len(relocation_indices) != 1:
        raise ValueError("Expected one PSP relocation segment")
    relocation_index = relocation_indices[0]
    relocation_original = parsed["phdrs"][relocation_index]
    relocation_bytes = elf[relocation_original[1]:relocation_original[1] + relocation_original[4]]
    if not selected:
        raise ValueError("No targets have proven relocation-backed references")

    payload = bytearray()
    for entry in selected:
        while len(payload) % 4:
            payload.append(0)
        entry["new_address"] = added[2] + added[4] + len(payload)
        payload.extend(entry["bundle"])
    delta = align(len(payload), 16)
    payload.extend(b"\0" * (delta - len(payload)))
    out = bytearray(elf[:insert] + payload + elf[insert:])
    normalized = bytearray(elf[:insert] + b"\0" * delta + elf[insert:])
    new_shoff = parsed["shoff"] + delta
    struct.pack_into("<I", out, ELF_HEADER_SHOFF, new_shoff)
    changed_spans = [(insert, insert + delta), (ELF_HEADER_SHOFF, ELF_HEADER_SHOFF + 4)]

    for n, header in enumerate(phdrs):
        if n != added_index and header[1] >= insert:
            header[1] += delta
            changed_spans.append((parsed["phoff"] + n * PROGRAM_HEADER_SIZE + 4,
                                  parsed["phoff"] + n * PROGRAM_HEADER_SIZE + 8))
        if n == added_index:
            header[4] += delta
            header[5] += delta
            location = parsed["phoff"] + n * PROGRAM_HEADER_SIZE
            changed_spans.extend([(location + 16, location + 20), (location + 20, location + 24)])
        struct.pack_into("<8I", out, parsed["phoff"] + n * PROGRAM_HEADER_SIZE, *header)
    for n, section in enumerate(sections):
        original = parsed["sections"][n]
        if section[4] >= insert:
            section[4] += delta
        if original[3] == added[2] and original[4] == added[1]:
            section[5] += delta
        location = new_shoff + n * SECTION_HEADER_SIZE
        if section[4] != original[4]: changed_spans.append((location + 16, location + 20))
        if section[5] != original[5]: changed_spans.append((location + 20, location + 24))
        struct.pack_into("<10I", out, location, *section)

    for entry in selected:
        for reference in entry["references"]:
            if reference["kind"] == "pointer":
                location = reference["instruction"] + 0xC0
                struct.pack_into("<I", out, location, entry["new_address"])
                changed_spans.append((location, location + 4))
            else:
                high_location, low_location = reference["high"] + 0xC0, reference["low"] + 0xC0
                high_word, low_word = word(out, reference["high"]), word(out, reference["low"])
                struct.pack_into("<I", out, high_location,
                                 (high_word & 0xFFFF0000) | ((entry["new_address"] + 0x8000) >> 16))
                struct.pack_into("<I", out, low_location,
                                 (low_word & 0xFFFF0000) | (entry["new_address"] & 0xFFFF))
                changed_spans.extend([(high_location, high_location + 4), (low_location, low_location + 4)])

    updated = parse_elf(out)
    updated_added, updated_relocation = updated["phdrs"][added_index], updated["phdrs"][relocation_index]
    if out[added[1]:insert] != elf[added[1]:insert]:
        raise ValueError("Existing added-segment code/data changed")
    if updated_added[1] != added_original[1] or updated_added[2] != added_original[2] or updated_added[4] != added_original[4] + delta:
        raise ValueError("Added segment did not receive an append-only extension")
    if updated_relocation[1] != relocation_original[1] + delta or out[updated_relocation[1]:updated_relocation[1] + updated_relocation[4]] != relocation_bytes:
        raise ValueError("Existing relocation records changed")
    for entry in selected:
        file_offset = updated_added[1] + entry["new_address"] - updated_added[2]
        if out[file_offset:file_offset + len(entry["bundle"])] != entry["bundle"]:
            raise ValueError("Appended encoded string mismatch: " + entry["id"])
        for reference in entry["references"]:
            if reference["kind"] == "pointer":
                if word(out, reference["instruction"]) != entry["new_address"]:
                    raise ValueError("Patched pointer mismatch: " + entry["id"])
            elif resolved_address(word(out, reference["high"]), word(out, reference["low"])) != entry["new_address"]:
                raise ValueError("Patched HI/LO mismatch: " + entry["id"])
        entry["new_file_offset"] = file_offset
    differences = [n for n, (left, right) in enumerate(zip(normalized, out)) if left != right]
    if any(not span_contains(changed_spans, n) for n in differences):
        raise ValueError("Byte changed outside the explicit allowlist")

    def public(entry):
        return {"id": entry["id"], "module_address": hex(entry["module_address"]),
                "source_offset": entry["source_offset"], "source_sha256": entry["source_sha256"],
                "target_variant": entry["variant"], "target_text": entry["text"],
                "display_text": entry["display_text"], "encoded_bytes": len(entry["encoded"]),
                "bundle_bytes": len(entry["bundle"]), "unreferenced_tails": entry["tail_entries"],
                "new_address": hex(entry["new_address"]), "new_file_offset": entry["new_file_offset"],
                "references": [{key: (hex(value) if isinstance(value, int) else value) for key, value in ref.items()}
                               for ref in entry["references"]]}
    report = {"profile": "battle_elf_patch_0.1.13", "baseline_elf_sha256": baseline_sha,
              "patched_elf_sha256": sha256(out), "source_bytes": len(elf), "patched_bytes": len(out),
              "targets_total": len(targets), "targets_patched": len(selected), "targets_skipped": len(skipped),
              "skipped": skipped, "entries": [public(entry) for entry in selected],
              "added_segment": {"index": added_index, "module_address": hex(added_original[2]),
                                "file_offset": added_original[1], "old_bytes": added_original[4],
                                "new_bytes": updated_added[4], "appended_bytes": delta},
              "relocation_segment": {"index": relocation_index, "records_unchanged": True,
                                    "old_file_offset": relocation_original[1], "new_file_offset": updated_relocation[1]},
              "audit": {"mapped_start_reference_count": sum(len(x["references"]) for x in selected),
                        "interior_reference_targets_skipped": sum(x["reason"].startswith("interior") for x in skipped),
                        "shared_hi16_pairs_proven_safe": sum(ref["kind"] == "hilo" for x in selected for ref in x["references"]),
                        "bundled_unreferenced_tail_count": sum(len(x["tail_entries"]) for x in selected),
                        "all_differences_allowlisted": True, "allowed_changed_byte_count": len(differences)},
              "structural_checks": validate_loader_structure(out),
              "change_log": ["Relocated only source-hash-verified battle literals with proven direct relocation references; preserved opaque prefixes/control tokens, existing hooks, and all existing relocation records."]}
    return bytes(out), report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--meaning-overrides", type=Path,
                        help="Optional reviewed text/compact-variant overrides; never alters the draft document")
    args = parser.parse_args()
    patched, report = prepare(BASELINE.read_bytes(), targets=target_rows(overrides=args.meaning_overrides))
    print(json.dumps({"mode": "write" if args.write else "dry-run", "baseline": str(BASELINE),
                      "output": str(args.output), "report": report}, ensure_ascii=False, indent=2))
    if args.write:
        if args.output.exists():
            raise FileExistsError("Refusing to overwrite scratch candidate: " + str(args.output))
        args.output.mkdir(parents=True)
        (args.output / "EBOOT.elf").write_bytes(patched)
        (args.output / "manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
