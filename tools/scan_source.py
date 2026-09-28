"""Read-only PSP ISO inventory; optionally save a metadata-only JSON report.

Default mode prints a preview and writes nothing. No game assets or dialogue
are extracted. Supports an ISO or a ZIP containing exactly one ISO.
"""

import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct
import zipfile


SECTOR = 2048
SAMPLE_LIMIT = 128 * 1024
MAGICS = (b"RIFF", b"PSMF", b"MIG.", b"TIM2", b"PPHD", b"PPPG")


@contextmanager
def open_iso(source):
    if source.suffix.lower() == ".zip":
        with zipfile.ZipFile(source) as archive:
            members = [entry for entry in archive.infolist()
                       if entry.filename.lower().endswith(".iso")]
            if len(members) != 1:
                raise ValueError("Expected exactly one ISO in the ZIP")
            member = members[0]
            with archive.open(member) as stream:
                yield stream, {
                    "iso_name": member.filename,
                    "iso_size_bytes": member.file_size,
                    "zip_member_crc32": f"{member.CRC:08x}",
                    "zip_compressed_size_bytes": member.compress_size,
                }
    else:
        with source.open("rb") as stream:
            yield stream, {"iso_name": source.name,
                           "iso_size_bytes": source.stat().st_size}


def read_exact(stream, offset, size):
    stream.seek(offset)
    result = stream.read(size)
    if len(result) != size:
        raise ValueError(f"Short read at {offset:#x}: wanted {size} bytes")
    return result


def inventory(stream, iso_size):
    pvd = read_exact(stream, 16 * SECTOR, SECTOR)
    if pvd[:7] != b"\x01CD001\x01":
        raise ValueError("Expected an ISO9660 primary volume descriptor")
    root = pvd[156:190]
    pending = [(struct.unpack_from("<I", root, 2)[0],
                struct.unpack_from("<I", root, 10)[0], "")]
    seen = set()
    files = []
    while pending:
        pending.sort(reverse=True)
        sector, size, parent = pending.pop()
        if (sector, size) in seen:
            continue
        seen.add((sector, size))
        if sector * SECTOR + size > iso_size:
            raise ValueError("Directory extends beyond ISO")
        data = read_exact(stream, sector * SECTOR, size)
        position = 0
        while position < len(data):
            length = data[position]
            if not length:
                position = (position // SECTOR + 1) * SECTOR
                continue
            record = data[position:position + length]
            if len(record) != length or length < 34:
                raise ValueError("Invalid directory record")
            position += length
            name_length = record[32]
            if 33 + name_length > length:
                raise ValueError("Invalid ISO file name length")
            name_bytes = record[33:33 + name_length]
            if name_bytes in (b"\0", b"\1"):
                continue
            name = name_bytes.decode("ascii", "replace").split(";")[0]
            entry = {
                "path": parent + "/" + name,
                "sector": struct.unpack_from("<I", record, 2)[0],
                "size_bytes": struct.unpack_from("<I", record, 10)[0],
            }
            if entry["sector"] * SECTOR + entry["size_bytes"] > iso_size:
                raise ValueError(f"File extends beyond ISO: {entry['path']}")
            if record[25] & 0x80:
                raise ValueError("Multi-extent files are not supported")
            if record[25] & 2:
                pending.append((entry["sector"], entry["size_bytes"], entry["path"]))
            else:
                files.append(entry)
    return {
        "system_identifier": pvd[8:40].decode("ascii", "replace").strip(),
        "volume_identifier": pvd[40:72].decode("ascii", "replace").strip(),
        "directory_count": len(seen),
        "file_count": len(files),
    }, sorted(files, key=lambda entry: entry["sector"])


def collect_samples_and_hash(stream, files, expected_size):
    """One sequential pass verifies ZIP CRC, hashes ISO, and samples headers."""
    windows = []
    for entry in files:
        sample_size = entry["size_bytes"] if entry["path"].endswith("/BOOT.BIN") else min(
            SAMPLE_LIMIT, entry["size_bytes"])
        start = entry["sector"] * SECTOR
        windows.append((start, start + sample_size, entry["path"]))
    samples = {entry["path"]: bytearray() for entry in files}
    digest = hashlib.sha256()
    stream.seek(0)
    offset = 0
    while chunk := stream.read(4 * 1024 * 1024):
        digest.update(chunk)
        end = offset + len(chunk)
        for left, right, path in windows:
            if left < end and right > offset:
                samples[path].extend(chunk[max(0, left - offset):min(len(chunk), right - offset)])
        offset = end
    if offset != expected_size:
        raise ValueError("ISO byte count does not match source metadata")
    return {key: bytes(value) for key, value in samples.items()}, digest.hexdigest()


def parse_sfo(data):
    if data[:4] != b"\0PSF":
        raise ValueError("Invalid PARAM.SFO signature")
    _, _, key_start, data_start, count = struct.unpack_from("<5I", data)
    result = {}
    for i in range(count):
        key_offset, kind, length, _, value_offset = struct.unpack_from("<HHIII", data, 20 + i * 16)
        key = data[key_start + key_offset:].split(b"\0", 1)[0].decode("ascii")
        value = data[data_start + value_offset:data_start + value_offset + length]
        result[key] = struct.unpack("<I", value)[0] if kind == 0x404 else value.rstrip(b"\0").decode("utf-8", "replace")
    return result


def probe(data, file_size):
    result = {"sample_size_bytes": len(data), "header_hex": data[:64].hex(" ")}
    if data.startswith(b"~PSP"):
        result["signature"] = "PSP executable wrapper; not a plain ELF"
    elif data.startswith(b"\x7fELF"):
        result["signature"] = "ELF"
    elif data.startswith(b"RIFF") and data[8:12] == b"WAVE":
        result["signature"] = "RIFF/WAVE"
        result["first_riff_size_bytes"] = struct.unpack_from("<I", data, 4)[0] + 8
    elif data.startswith(b"PSMF"):
        result["signature"] = "PSMF video"
    elif data and not any(data):
        result["signature"] = "all sampled bytes are zero"
    else:
        result["signature"] = "unidentified binary data"
    found = {}
    for magic in MAGICS:
        positions = []
        start = 0
        while (position := data.find(magic, start)) >= 0:
            positions.append(position)
            start = position + 1
        if positions:
            found[magic.decode("ascii")] = {"count_in_sample": len(positions),
                                           "first_offsets": positions[:8]}
    result["magic_matches"] = found
    if len(data) >= 8:
        count, tag, shift = struct.unpack_from("<HHI", data)
        if tag == 1 and 0 < count <= 10000 and shift <= 16 and 8 + count * 8 <= len(data):
            pairs = [struct.unpack_from("<II", data, 8 + i * 8) for i in range(count)]
            scale = 1 << shift
            end = max(offset + length for offset, length in pairs) * scale
            result["candidate_index"] = {
                "status": "structural hypothesis; payload meanings unverified",
                "entry_count": count,
                "unit_bytes": scale,
                "empty_entry_count": sum(length == 0 for _, length in pairs),
                "first_pairs": pairs[:4], "last_pairs": pairs[-4:],
                "all_entries_within_file": all((offset + length) * scale <= file_size for offset, length in pairs),
                "entries_contiguous": all(offset + length == next_offset for (offset, length), (next_offset, _) in zip(pairs, pairs[1:])),
                "first_payload_after_table": pairs[0][0] * scale >= 8 + count * 8,
                "indexed_end_bytes": end,
                "covers_full_file": end == file_size,
            }
    return result


def scan(source):
    with open_iso(source) as (stream, source_info):
        volume, files = inventory(stream, source_info["iso_size_bytes"])
        samples, iso_hash = collect_samples_and_hash(stream, files, source_info["iso_size_bytes"])
    with source.open("rb") as handle:
        source_digest = hashlib.sha256()
        while chunk := handle.read(4 * 1024 * 1024):
            source_digest.update(chunk)
        source_hash = source_digest.hexdigest()
    source_info.update({"source_name": source.name, "source_size_bytes": source.stat().st_size,
                        "source_sha256": source_hash, "iso_sha256": iso_hash,
                        "zip_crc_verified": source.suffix.lower() == ".zip"})
    for entry in files:
        if entry["path"].endswith((".DAT", "/EBOOT.BIN", "/BOOT.BIN")):
            entry["probe"] = probe(samples[entry["path"]], entry["size_bytes"])
    return {
        "report_schema": 1,
        "scanned_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Full ISO hash and ISO9660 inventory; bounded header probes, complete BOOT.BIN zero check. No dialogue extraction or runtime testing.",
        "source": source_info, "volume": volume,
        "param_sfo": parse_sfo(samples["/PSP_GAME/PARAM.SFO"]),
        "files": files,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--report", type=Path, default=Path("docs/source_scan.json"))
    parser.add_argument("--write", action="store_true", help="Write the metadata report after previewing a dry run")
    args = parser.parse_args()
    source = args.source.resolve()
    target = args.report.resolve()
    if target == source:
        parser.error("The report must not overwrite the source")
    report = scan(source)
    summary = {"mode": "write report" if args.write else "dry run; no files written",
               "report_path": str(target), "source": report["source"],
               "volume": report["volume"], "disc_id": report["param_sfo"]["DISC_ID"],
               "usrdir_signature_counts": dict(Counter(entry["probe"]["signature"] for entry in report["files"]
                                                        if entry["path"].startswith("/PSP_GAME/USRDIR/") and "probe" in entry)),
               "sample_findings": [{"path": entry["path"], "probe": entry["probe"]} for entry in report["files"]
                                   if entry["path"] in {"/PSP_GAME/SYSDIR/BOOT.BIN", "/PSP_GAME/USRDIR/00.DAT", "/PSP_GAME/USRDIR/01.DAT", "/PSP_GAME/USRDIR/02.DAT", "/PSP_GAME/USRDIR/03.DAT"}]}
    print(json.dumps(summary, indent=2, ensure_ascii=True))
    if args.write:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
