"""Extend backlog labels for the Chapter 2/3 cast without touching stage labels.

``prepare_names(source)`` follows the same pure API as ``stages_names`` and
returns replacement packed resources plus an audit report.  It only changes
pointer fields whose original CP932 labels are listed in ``NAMES``.
"""
import struct

from sn3_archive import parse_index, child
from sn3_repack import repack
from sn3_codec import decompress, compress
from dialogue_encoding import encode_dialogue
from stages_patch import sha


NAMES = {
    # Previously encountered cast remains available in backlog history.
    'カイル': 'Kyle', 'ソノラ': 'Sonolar', 'スカーレル': 'Scarrel',
    'ヤード': 'Yard', 'アズリア': 'Azlier', 'ギャレオ': 'Galleor',
    'ビジュ': 'Vijue',
    # Island Guardians and companions.
    'アルディラ': 'Ardylia', 'キュウマ': 'Kyuuma', 'ファルゼン': 'Falzen',
    'ヤッファ': 'Yafha', 'クノン': 'Cunnon', 'ミスミ': 'Misumi', 'スバル': 'Subaru',
    'マルルゥ': 'Marurur', 'アール': 'R', 'テコ': 'Teco', 'オニビ': 'Onibi',
    'キユピー': 'Quiupy', 'フレイズ': 'Phlaiz',
}


def prepare_names(source):
    replacements, reports = {}, []
    # These are the three localized backlog-label banks used by the stage
    # implementation.  Keep all unrecognized labels and child resources byte
    # identical, including optional/alternate fields.
    for resource in (85, 86, 87):
        data = decompress(source.resource('02.DAT', resource), 0x9831)[0]
        index = parse_index(data, len(data)); table = child(data, index, 22)
        out = bytearray(table); changes = []; count = struct.unpack_from('<I', table)[0]
        assert count == 255
        for field in range(4, 4 + count * 8, 4):
            old = struct.unpack_from('<I', table, field)[0]
            if not old:
                continue
            assert 4 + count * 8 <= old < len(table)
            end = old
            while table[end:end + 2] != b'\0\0':
                end += 2
            raw = table[old:end]; name = raw.decode('cp932')
            if name not in NAMES:
                continue
            encoded, display = encode_dialogue(NAMES[name], name)
            new = len(out); out.extend(encoded + b'\0\0'); struct.pack_into('<I', out, field, new)
            changes.append(dict(pointer_field=field, old_offset=old, new_offset=new,
                                source_sha256=sha(raw), text=NAMES[name], display_text=display))
        updated = repack(data, {22: bytes(out)}); updated_index = parse_index(updated, len(updated))
        for number in range(index['count']):
            if number != 22:
                assert child(data, index, number) == child(updated, updated_index, number)
        packed = compress(updated, 0x9831); assert decompress(packed, 0x9831)[0] == updated
        replacements[resource] = packed
        reports.append(dict(resource='02:%05d/00022' % resource, changes=changes,
                            table_sha256=sha(child(updated, updated_index, 22)),
                            table_size=len(child(updated, updated_index, 22)), decoded_sha256=sha(updated)))
    return replacements, dict(names=sorted(NAMES.values()), packs=reports,
                              glossary='work/glossary/island_0.1.12.json')
