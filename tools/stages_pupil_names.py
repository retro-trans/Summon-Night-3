"""Relocate the runtime pupil-name literals used by the ▲ dialogue token.

The pure ``prepare_pupil_names`` function accepts only the already-built ELF
bytes.  Its CLI deliberately writes only a scratch candidate when --write is
given; it never changes an output build or the ISO.
"""

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

from dialogue_encoding import encode_dialogue
from sn3_archive import ROOT

sys.stdout.reconfigure(encoding="utf-8")


BASELINE_SHA256 = "c1e5fec7b051dd081d83812395cd79c00f9991b005d2919c017182dbeec9c823"
BASELINE = ROOT / "work/output/0.1.11/EBOOT.elf"
DEFAULT_OUTPUT = ROOT / "work/scratch/stages_pupil_names"
ELF_HEADER_SHOFF = 0x20
PROGRAM_HEADER_SIZE = 32
SECTION_HEADER_SIZE = 40
ADDED_SEGMENT_VA = 0x32DBC0

# State values are returned by 0x56dd8.  "No Pupil" and "Unlisted" retain
# the source fallbacks' generic meanings and stay within the eight-cell token
# budget.  All text is stored using the existing fullwidth dialogue encoding.
NAME_SPECS = (
    ("unset_pupil", "No Pupil", 0x2161F8, 0x56E28, 0x56E2C),
    ("nup", "Nup", 0x216204, 0x56E3C, 0x56E40),
    ("belfrau", "Belfrau", 0x21620C, 0x56E50, 0x56E54),
    ("alieze", "Alieze", 0x216218, 0x56E64, 0x56E68),
    ("will", "Will", 0x216224, 0x56E78, 0x56E7C),
    ("unregistered", "Unlisted", 0x21622C, 0x56E00, 0x56E8C),
)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def align(value, boundary):
    return (value + boundary - 1) // boundary * boundary


def signed16(value):
    return struct.unpack("<h", struct.pack("<H", value & 0xFFFF))[0]


def parse_elf(data):
    if data[:4] != b"\x7fELF" or data[4] != 1 or data[5] != 1:
        raise ValueError("Expected a 32-bit little-endian ELF")
    phoff, shoff = struct.unpack_from("<II", data, 28)
    phentsize, phnum, shentsize, shnum, _ = struct.unpack_from("<5H", data, 42)
    if phentsize != PROGRAM_HEADER_SIZE or shentsize != SECTION_HEADER_SIZE:
        raise ValueError("Unexpected ELF header entry sizes")
    if phoff + phnum * phentsize > len(data) or shoff + shnum * shentsize > len(data):
        raise ValueError("ELF header table lies outside the file")
    phdrs = [list(struct.unpack_from("<8I", data, phoff + index * phentsize))
             for index in range(phnum)]
    sections = [list(struct.unpack_from("<10I", data, shoff + index * shentsize))
                for index in range(shnum)]
    return {"phoff": phoff, "shoff": shoff, "phentsize": phentsize,
            "phnum": phnum, "shentsize": shentsize, "shnum": shnum,
            "phdrs": phdrs, "sections": sections}


def wide(text):
    encoded, display = encode_dialogue(text, "")
    if len(text) > 8:
        raise ValueError("Runtime pupil-name text exceeds the eight-cell budget: " + text)
    if len(encoded) != len(text) * 2:
        raise ValueError("Dialogue display encoding must use two bytes per cell")
    return encoded + b"\0\0", display


def instruction(data, address):
    return struct.unpack_from("<I", data, address + 0xC0)[0]


def resolved_address(high_word, low_word):
    return ((high_word & 0xFFFF) << 16) + signed16(low_word & 0xFFFF)


def span_contains(spans, offset):
    return any(start <= offset < end for start, end in spans)


def validate_loader_structure(data):
    parsed = parse_elf(data)
    load_ranges = []
    for index, header in enumerate(parsed["phdrs"]):
        p_type, p_offset, p_vaddr, _, p_filesz, p_memsz, _, p_align = header
        if p_offset + p_filesz > len(data):
            raise ValueError("Program header %d exceeds ELF file bounds" % index)
        if p_type == 1:
            if p_filesz > p_memsz:
                raise ValueError("PT_LOAD file size exceeds memory size")
            if p_align and (p_offset - p_vaddr) % p_align:
                raise ValueError("PT_LOAD alignment mismatch")
            load_ranges.append((p_vaddr, p_vaddr + p_memsz, index))
    for left, right in zip(sorted(load_ranges), sorted(load_ranges)[1:]):
        if left[1] > right[0]:
            raise ValueError("PT_LOAD virtual ranges overlap")
    return {"program_header_count": parsed["phnum"], "section_header_count": parsed["shnum"],
            "load_ranges": [{"index": index, "start": hex(start), "end": hex(end)}
                            for start, end, index in sorted(load_ranges)]}


def prepare_pupil_names(elf: bytes):
    """Return a relocatable pupil-name candidate and its byte-level audit."""
    if sha256(elf) != BASELINE_SHA256:
        raise ValueError("Unexpected 0.1.11 baseline SHA-256")
    source = parse_elf(elf)
    phdrs = [header[:] for header in source["phdrs"]]
    sections = [section[:] for section in source["sections"]]
    added_indices = [index for index, header in enumerate(phdrs)
                     if header[0] == 1 and header[2] == ADDED_SEGMENT_VA]
    if added_indices != [3]:
        raise ValueError("Expected one existing added PT_LOAD segment at 0x32dbc0")
    added_index = added_indices[0]
    added = phdrs[added_index]
    original_added = source["phdrs"][added_index]
    if added[6] != 5 or added[7] != 0x40 or added[4] != added[5]:
        raise ValueError("Unexpected added PT_LOAD permissions, alignment, or sizes")
    insert = added[1] + added[4]
    if not 0 < insert < len(elf):
        raise ValueError("Added segment is not followed by relocations/sections")
    relocation_indices = [index for index, header in enumerate(phdrs) if header[0] == 0x700000A0]
    if len(relocation_indices) != 1:
        raise ValueError("Expected one PSP relocation segment")
    relocation_index = relocation_indices[0]
    relocation = phdrs[relocation_index]
    original_relocation = source["phdrs"][relocation_index]
    if relocation[1] <= insert or relocation[4] % 8:
        raise ValueError("Relocation table does not follow the added segment")
    relocation_bytes = elf[relocation[1]:relocation[1] + relocation[4]]
    relocation_records = list(struct.iter_unpack("<II", relocation_bytes))

    payload = bytearray()
    entries = []
    for key, text, old_address, high_address, low_address in NAME_SPECS:
        while len(payload) % 4:
            payload.append(0)
        new_address = added[2] + added[4] + len(payload)
        encoded, display = wide(text)
        payload.extend(encoded)
        high_word = instruction(elf, high_address)
        low_word = instruction(elf, low_address)
        if high_word >> 26 != 15 or low_word >> 26 != 9:
            raise ValueError("Expected LUI/ADDIU pair for " + key)
        if resolved_address(high_word, low_word) != old_address:
            raise ValueError("Original pupil literal pointer changed for " + key)
        if relocation_records.count((high_address, 5)) != 1 or relocation_records.count((low_address, 6)) != 1:
            raise ValueError("Missing or duplicate HI16/LO16 relocation for " + key)
        entries.append({"key": key, "text": text, "display_text": display,
                        "old_address": old_address, "new_address": new_address,
                        "high_instruction": high_address, "low_instruction": low_address,
                        "encoded_bytes": len(encoded) + 2})
    delta = align(len(payload), 16)
    payload.extend(b"\0" * (delta - len(payload)))
    if delta == 0 or delta % 16:
        raise ValueError("New payload must preserve relocation-table alignment")

    out = bytearray(elf[:insert] + payload + elf[insert:])
    normalized = bytearray(elf[:insert] + b"\0" * delta + elf[insert:])
    new_shoff = source["shoff"] + delta
    struct.pack_into("<I", out, ELF_HEADER_SHOFF, new_shoff)

    changed_spans = [(insert, insert + delta), (ELF_HEADER_SHOFF, ELF_HEADER_SHOFF + 4)]
    for index, header in enumerate(phdrs):
        original = source["phdrs"][index]
        if index != added_index and header[1] >= insert:
            header[1] += delta
            location = source["phoff"] + index * PROGRAM_HEADER_SIZE + 4
            changed_spans.append((location, location + 4))
        if index == added_index:
            header[4] += delta
            header[5] += delta
            location = source["phoff"] + index * PROGRAM_HEADER_SIZE
            changed_spans.extend([(location + 16, location + 20), (location + 20, location + 24)])
        struct.pack_into("<8I", out, source["phoff"] + index * PROGRAM_HEADER_SIZE, *header)

    for index, section in enumerate(sections):
        original = source["sections"][index]
        if section[4] >= insert:
            section[4] += delta
        if original[3] == added[2] and original[4] == added[1]:
            section[5] += delta
        location = new_shoff + index * SECTION_HEADER_SIZE
        if section[4] != original[4]:
            changed_spans.append((location + 16, location + 20))
        if section[5] != original[5]:
            changed_spans.append((location + 20, location + 24))
        struct.pack_into("<10I", out, location, *section)

    for entry in entries:
        high_location = entry["high_instruction"] + 0xC0
        low_location = entry["low_instruction"] + 0xC0
        high_word = instruction(out, entry["high_instruction"])
        low_word = instruction(out, entry["low_instruction"])
        struct.pack_into("<I", out, high_location,
                         (high_word & 0xFFFF0000) | ((entry["new_address"] + 0x8000) >> 16))
        struct.pack_into("<I", out, low_location,
                         (low_word & 0xFFFF0000) | (entry["new_address"] & 0xFFFF))
        changed_spans.extend([(high_location, high_location + 4), (low_location, low_location + 4)])

    # The original added segment contains the pool-192 font, setup Latin, and
    # backlog hooks.  Appending after it is the preservation proof for all of
    # those prior changes.
    if out[added[1]:insert] != elf[added[1]:insert]:
        raise ValueError("Existing added-segment hooks changed")
    updated = parse_elf(out)
    updated_added = updated["phdrs"][added_index]
    updated_relocation = updated["phdrs"][relocation_index]
    if updated_added[1] != original_added[1] or updated_added[2] != original_added[2]:
        raise ValueError("Added segment moved")
    if (updated_added[4] != original_added[4] + delta or
            updated_added[5] != original_added[5] + delta):
        raise ValueError("Added segment was not extended by the payload")
    if updated_relocation[1] != original_relocation[1] + delta:
        raise ValueError("Relocation-table offset did not move with the insertion")
    if out[updated_relocation[1]:updated_relocation[1] + updated_relocation[4]] != relocation_bytes:
        raise ValueError("Existing relocation records changed")
    for entry in entries:
        if resolved_address(instruction(out, entry["high_instruction"]),
                            instruction(out, entry["low_instruction"])) != entry["new_address"]:
            raise ValueError("Relocated pointer does not resolve for " + entry["key"])
        file_offset = updated_added[1] + entry["new_address"] - updated_added[2]
        encoded, _ = wide(entry["text"])
        if out[file_offset:file_offset + len(encoded)] != encoded:
            raise ValueError("Relocated text bytes do not match for " + entry["key"])
        entry["new_file_offset"] = file_offset

    # Compare to the old file with only a deliberate gap inserted.  Every
    # changed byte must belong to a named ELF metadata field, pointer word, or
    # the new payload itself.
    differences = [offset for offset, (before, after) in enumerate(zip(normalized, out))
                   if before != after]
    if any(not span_contains(changed_spans, offset) for offset in differences):
        raise ValueError("Byte changed outside the explicit allowlist")
    loader_checks = validate_loader_structure(out)
    report = {
        "profile": "stages_pupil_names_v1",
        "baseline_elf_sha256": BASELINE_SHA256,
        "patched_elf_sha256": sha256(out),
        "source_bytes": len(elf),
        "patched_bytes": len(out),
        "added_segment": {"index": added_index, "module_address": hex(original_added[2]),
                          "file_offset": original_added[1], "old_bytes": original_added[4],
                          "new_bytes": updated_added[4], "appended_bytes": delta},
        "relocation_segment": {"index": relocation_index, "old_file_offset": original_relocation[1],
                               "new_file_offset": updated_relocation[1],
                               "record_count": len(relocation_records), "records_unchanged": True},
        "entries": [{key: (hex(value) if key.endswith("address") or key.endswith("instruction") or
                            key.endswith("offset") else value)
                     for key, value in entry.items()} for entry in entries],
        "byte_change_allowlist": {"inserted_payload": [insert, insert + delta],
                                  "allowed_changed_byte_count": len(differences),
                                  "allowed_spans": [[start, end] for start, end in changed_spans],
                                  "all_differences_allowlisted": True},
        "structural_checks": loader_checks,
        "prior_added_segment_preserved": True,
        "prior_pool192_setup_latin_backlog_hooks_preserved": True,
        "change_log": ["Relocated six ▲ runtime-name pointers into appended fullwidth CP932 strings; no existing hook, relocation record, script resource, or ISO was changed."],
    }
    return bytes(out), report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    patched, report = prepare_pupil_names(BASELINE.read_bytes())
    print(json.dumps({"mode": "write" if args.write else "dry-run", "baseline": str(BASELINE),
                      "output": str(args.output), "report": report}, ensure_ascii=False, indent=2))
    if args.write:
        if args.output.exists():
            raise FileExistsError("Refusing to overwrite existing scratch output: " + str(args.output))
        args.output.mkdir(parents=True)
        (args.output / "EBOOT.elf").write_bytes(patched)
        (args.output / "manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                                                       encoding="utf-8")


if __name__ == "__main__":
    main()
