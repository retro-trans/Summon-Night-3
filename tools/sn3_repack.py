"""Rebuild known resource packs and relocate strings without in-place limits."""
import hashlib
import struct
from sn3_archive import parse_index, parse_v4


def padded(data, unit):
    return data + bytes((-len(data)) % unit)


def repack(data, replacements):
    """Reconstruct every index/payload, retaining untouched bytes and padding."""
    try:
        index = parse_index(data, len(data))
        kind = 'indexed'
    except ValueError:
        index = parse_v4(data)
        kind = 'v4'
    entries = index['entries']
    if set(replacements) - {entry['id'] for entry in entries}:
        raise ValueError('Replacement refers to an unknown child')
    starts = [entry['offset'] for entry in entries if entry['offset']]
    if not starts or index['indexed_end'] is None:
        if kind != 'v4' or any(entry['offset'] or entry['size'] for entry in entries) or replacements:
            raise ValueError('Cannot add payloads to an empty container')
        # All slots are missing: there are no payload bytes or offsets to move.
        return bytes(bytearray(data))
    out = bytearray(data[:min(starts)])
    for entry in entries:
        number = entry['id']
        if kind == 'v4' and entry['offset'] == 0 and entry['size'] == 0:
            if number in replacements:
                raise ValueError('Adding a missing V4 resource is not supported')
            continue
        payload = replacements.get(number, data[entry['offset']:entry['offset'] + entry['size']])
        payload = padded(payload, index['unit_bytes'])
        offset_units = len(out) // index['unit_bytes']
        size_units = len(payload) // index['unit_bytes']
        if kind == 'indexed':
            struct.pack_into('<II', out, 8 + number * 8, offset_units, size_units)
        else:
            if max(offset_units, size_units) >= 1 << 24:
                raise ValueError('V4 offset/length exceeds its 24-bit field')
            position = index['table_offset'] + number * 8
            out[position:position + 3] = offset_units.to_bytes(3, 'big')
            out[position + 3:position + 6] = size_units.to_bytes(3, 'big')
        out.extend(payload)
    out.extend(data[index['indexed_end']:])
    return bytes(out)


def relocate_labels(data, entries, targets):
    known = {entry['id']: entry for entry in entries}
    if set(targets) - set(known):
        raise ValueError('Unknown target label')
    out = bytearray(data)
    changes = []
    for identity, target in targets.items():
        entry = known[identity]
        old = entry['source_offset']
        end = data.index(b'\0', old)
        digest = hashlib.sha256(data[old:end]).hexdigest()
        if digest != target['source_sha256'] or digest != entry['source_sha256']:
            raise ValueError('Source hash mismatch for ' + identity)
        text = target['text']
        if not text or any(c in text for c in '\0\r\n'):
            raise ValueError('Character labels must be nonempty single-line text')
        encoded = text.encode('cp932', 'strict')
        out.extend(bytes((-len(out)) % 2))
        new = len(out)
        out.extend(encoded + b'\0')
        fields = []
        for reference in entry['references']:
            field = reference['pointer_field_offset']
            if struct.unpack_from('<I', data, field)[0] != old:
                raise ValueError('Source pointer mismatch for ' + identity)
            struct.pack_into('<I', out, field, new)
            fields.append(field)
        changes.append({'id': identity, 'text': text, 'source_sha256': digest,
                        'old_offset': old, 'new_offset': new, 'old_byte_length': end - old,
                        'new_byte_length': len(encoded), 'pointer_fields': fields})
    return bytes(out), changes


def plan_bank(source, bank, replacements):
    index = source.indexes[bank]
    location = source.index_locations[bank]
    table = bytearray(source.read(location['bank'], location['offset'], location['size']))
    if set(replacements) - {row['id'] for row in index['entries']}:
        raise ValueError('Unknown bank resource')
    unit = index['unit_bytes']
    cursor = index['entries'][0]['offset']
    rows = []
    for entry in index['entries']:
        replacement = replacements.get(entry['id'])
        size = entry['size'] if replacement is None else len(padded(replacement, unit))
        struct.pack_into('<II', table, 8 + entry['id'] * 8,
                         cursor // unit + index['bias_units'], size // unit)
        rows.append(dict(entry, source_offset=entry['offset'], source_size=entry['size'], offset=cursor, size=size))
        cursor += size
    if index['bias_units'] == 0:
        prefix = bytearray(source.read(bank, 0, index['entries'][0]['offset']))
        prefix[:len(table)] = table
        prefix = bytes(prefix)
    else:
        prefix = source.read(bank, 0, index['entries'][0]['offset'])
    parse_index(table, cursor, allow_external=bool(index['bias_units']))
    return {'bank': bank, 'old_size': source.files[bank]['size_bytes'], 'new_size': cursor,
            'index_bytes': bytes(table), 'prefix': prefix, 'entries': rows, 'replacements': replacements}


def write_bank(source, plan, output):
    start = output.tell()
    output.write(plan['prefix'])
    for row in plan['entries']:
        if output.tell() - start != row['offset']:
            raise ValueError('Bank writer position mismatch')
        replacement = plan['replacements'].get(row['id'])
        if replacement is not None:
            output.write(replacement)
            output.write(bytes(row['size'] - len(replacement)))
        else:
            offset, remaining = row['source_offset'], row['source_size']
            while remaining:
                amount = min(4 * 1024 * 1024, remaining)
                output.write(source.read(plan['bank'], offset, amount))
                offset += amount
                remaining -= amount
    if output.tell() - start != plan['new_size']:
        raise ValueError('Bank writer length mismatch')
