"""Reflow verified text-queue groups into bounded pages in appended VM code.

This opening-only profile preserves the original display helpers and branches.
Its conservative full-width geometry still requires visual/runtime acceptance.
"""
import hashlib
import struct

from dialogue_encoding import control_tokens, encode_dialogue
from script_repack import relocate_script
from script_strings import parse_pool
from sn3_vm import instructions

PROFILE = 'opening_fullwidth_paged_v1'
PIXEL_PROFILE = 'opening_latin_pixels_pool192_v2'
PIXEL_PAGE_CAPACITY = 192
# Portrait box: approximately 228 inner pixels, with 16-pixel glyph advance.
# Reserve one cell for the advance icon on the bottom line, using 13 throughout
# the page until per-line layout and narrower Latin glyphs are established.
# Centered screens: 448 pixels within the 480-pixel display. Three lines/page
# also stays below the six-record text queue. These are pilot layout policies,
# not a universal maximum or a completed font solution.
DISPLAY_PROFILES = {2030: (13, 3, 1), 2044: (13, 3, 1),
                    2141: (28, 3, 0), 2180: (28, 3, 0), 2206: (28, 3, 0)}


def operand_instruction(opcode, mode, value):
    if not 0 <= value < 1 << 20:
        raise ValueError('Instruction operand exceeds 20 bits')
    return struct.pack('<HH', opcode | (mode << 6) | ((value >> 16) << 12), value & 65535)


def wrap_words(text, limit):
    """Wrap only at ordinary spaces, rejecting words that cannot fit intact."""
    words = text.split(' ')
    if not text or any(not word for word in words):
        raise ValueError('Reflow requires nonempty text with single ordinary spaces')
    if any(len(word) > limit for word in words):
        raise ValueError('A word exceeds the layout width; do not truncate it')
    lines, current = [], ''
    for word in words:
        combined = current + (' ' if current else '') + word
        if len(combined) <= limit:
            current = combined
        else:
            lines.append(current)
            current = word
    lines.append(current)
    if ' '.join(lines) != text:
        raise ValueError('Wrapping changed target content')
    return lines


def latin_width(text, metrics):
    try:
        return 2 + sum(metrics[char]['proposed_advance_pixels'] for char in text)
    except KeyError as exc:
        raise ValueError('No verified Latin metric for ' + repr(exc.args[0])) from exc


def wrap_pixels(text, width, cells, metrics):
    words = text.split(' ')
    if not text or any(not word for word in words):
        raise ValueError('Pixel wrapping requires single ordinary spaces')
    def fits(line):
        return len(line) <= cells and latin_width(line, metrics) <= width
    if any(not fits(word) for word in words):
        raise ValueError('A word exceeds pixel/cell capacity; do not truncate it')
    lines, current = [], ''
    for word in words:
        combined = current + (' ' if current else '') + word
        if fits(combined):
            current = combined
        else:
            lines.append(current)
            current = word
    lines.append(current)
    if ' '.join(lines) != text:
        raise ValueError('Pixel wrapping changed target content')
    return lines


def verify_page_capacity(lines, capacity):
    if capacity < 1 or any(control_tokens(line) for line in lines):
        raise ValueError('Page requires a known capacity and measured token-free text')
    if sum(len(encode_dialogue(line, '')[1]) for line in lines) > capacity:
        raise ValueError('Page exceeds initialized font-object capacity')


def layout_dialogue(data, targets, groups, profile=PROFILE):
    """Relocate targets and reflow explicit complete groups when needed.

    targets: original source byte offsets -> reviewed translation records.
    groups: {id, source_offsets}, in source display order. Choice queues are
    deliberately excluded: their selection IDs and return values stay intact.
    Returns bytes, logical changes, and physical layout-group evidence.
    """
    if profile not in (PROFILE, PIXEL_PROFILE):
        raise ValueError('Unknown dialogue layout profile')
    metrics = None
    if profile == PIXEL_PROFILE:
        from font_metrics import collect
        metrics = collect()[0]['characters']
    parsed = parse_pool(data)
    source_rows = {row['source_offset']: row for row in parsed['strings']}
    decoded = instructions(data)
    by_position = {i['offset']: i for i in decoded}
    entry = struct.unpack_from('<I', data, 16)[0] * 2
    destinations = {i['target_word'] * 2 for i in decoded if 'target_word' in i} | {entry}
    original_pool = parsed['pool_offset']
    if decoded[-1]['opcode'] not in (1, 9, 10):
        raise ValueError('Original code could fall through into appended code')
    seen_sources, seen_ids, plans = set(), set(), []
    for group in groups:
        identity, offsets = group['id'], group['source_offsets']
        if identity in seen_ids or not offsets or len(offsets) != len(set(offsets)):
            raise ValueError('Duplicate or empty layout group')
        seen_ids.add(identity)
        if set(offsets) & seen_sources or set(offsets) - set(targets):
            raise ValueError('Layout groups overlap or lack complete targets')
        seen_sources.update(offsets)
        rows = [source_rows[offset] for offset in offsets]
        if any(len(row['reference_instructions']) != 1 for row in rows):
            raise ValueError('Layout group needs exactly one reference per source row')
        positions = [row['reference_instructions'][0] for row in rows]
        start = positions[0]
        if positions != list(range(start, start + 8 * len(rows), 8)):
            raise ValueError('Layout group is not a consecutive text-queue sequence')
        for row, position in zip(rows, positions):
            push, call = by_position[position], by_position.get(position + 4, {})
            if (push.get('string_word') != row['pool_word_offset'] or push['size'] != 4 or
                    call.get('opcode') != 7 or call.get('mode') != 1 or call.get('target_word') != 2003):
                raise ValueError('Layout group does not use the mapped normal-text helper')
        tail_start = positions[-1] + 8
        cursor, arguments = tail_start, 0
        while by_position[cursor]['opcode'] == 5:
            inst = by_position[cursor]
            if inst['mode'] not in (5, 9, 10):
                raise ValueError('Display arguments must be side-effect-free constants')
            arguments += 1
            cursor += inst['size']
        display = by_position[cursor]
        helper = display.get('target_word')
        if display['opcode'] != 7 or helper not in DISPLAY_PROFILES:
            raise ValueError('Unmapped display helper or incomplete sentence group')
        width, height, argc = DISPLAY_PROFILES[helper]
        pixel_width = (208 if helper in (2030, 2044) else 448) if metrics else None
        if metrics:
            width = 31  # Retain a zero cell; visible pixel capacity is independent.
        if display['mode'] != argc or arguments != argc:
            raise ValueError('Display argument count differs from the mapped helper')
        end = cursor + display['size']
        if end not in by_position or any(start < dest < end for dest in destinations):
            raise ValueError('Control flow enters the middle of a layout group')
        text_rows = [targets[offset]['text'] for offset in offsets]
        for offset, text in zip(offsets, text_rows):
            row = source_rows[offset]
            source = data[offset:offset + row['source_byte_length']].decode('cp932')
            if control_tokens(text) or control_tokens(source):
                raise ValueError('Runtime tokens need a measured expansion profile')
            if targets[offset].get('encoding_profile') != 'dialogue_fullwidth_cp932':
                raise ValueError('Reflow requires the mapped two-byte display profile')
            encode_dialogue(text, source)
        combined = ' '.join(text_rows)
        if metrics:
            lines = wrap_pixels(combined, pixel_width, width, metrics)
            if lines == text_rows and len(rows) <= height:
                verify_page_capacity(lines, PIXEL_PAGE_CAPACITY)
                continue
        else:
            if all(len(text) <= width for text in text_rows) and len(rows) <= height:
                continue
            lines = wrap_words(combined, width)
        pages = [lines[n:n + height] for n in range(0, len(lines), height)]
        if metrics:
            for page in pages:
                verify_page_capacity(page, PIXEL_PAGE_CAPACITY)
        tail = data[tail_start:end]
        plans.append({'id': identity, 'source_offsets': offsets, 'source_reference_instructions': positions,
                      'original_span': [start, end], 'original_span_sha256': hashlib.sha256(data[start:end]).hexdigest(),
                      'display_helper_word': helper, 'max_display_units': width, 'max_lines_per_page': height,
                      'text': combined, 'page_texts': pages, 'tail': tail,
                      'code_size': len(lines) * 8 + len(pages) * len(tail) + 4})
        if metrics:
            plans[-1].update(layout_profile=profile, max_pixel_width=pixel_width,
                             max_font_objects_per_page=PIXEL_PAGE_CAPACITY)
    plans.sort(key=lambda plan: plan['original_span'][0])
    if any(a['original_span'][1] > b['original_span'][0] for a, b in zip(plans, plans[1:])):
        raise ValueError('Layout instruction spans overlap')
    moved, changes = relocate_script(data, targets)
    if not plans:
        return moved, changes, []
    growth = sum(plan['code_size'] for plan in plans)
    new_pool = original_pool + growth
    out = bytearray(moved[:original_pool] + bytes(growth) + moved[original_pool:])
    struct.pack_into('<I', out, 20, new_pool // 2)
    for change in changes:
        change['new_offset'] += growth
    cursor, reports = original_pool, []
    for plan in plans:
        code, pages = bytearray(), []
        start, end = plan['original_span']
        for page_index, texts in enumerate(plan['page_texts']):
            fragments = []
            for line_index, text in enumerate(texts):
                encoded, display = encode_dialogue(text, '')
                offset = len(out)
                word = (offset - new_pool) // 2
                reference = cursor + len(code)
                out.extend(encoded + b'\0\0')
                code.extend(operand_instruction(5, 4, word))
                code.extend(operand_instruction(7, 1, 2003))
                fragments.append({'id': '%s:page:%d:line:%d' % (plan['id'], page_index, line_index),
                                  'text': text, 'display_text': display, 'new_offset': offset,
                                  'new_byte_length': len(encoded), 'pool_word_offset': word,
                                  'reference_instructions': [reference]})
            code.extend(plan['tail'])
            pages.append(fragments)
        code.extend(operand_instruction(10, 0, end // 2))
        if len(code) != plan['code_size']:
            raise ValueError('Appended code size mismatch')
        out[cursor:cursor + len(code)] = code
        out[start:end] = operand_instruction(10, 0, cursor // 2) + bytes(end - start - 4)
        for change in changes:
            if change['old_offset'] in plan['source_offsets']:
                change['original_reference_instructions'] = change['reference_instructions']
                change['reference_instructions'] = []
                change['layout_group_id'] = plan['id']
        report = {key: value for key, value in plan.items() if key not in ('tail', 'page_texts')}
        report.update(trampoline_offset=cursor, return_instruction=end, pages=pages)
        reports.append(report)
        cursor += len(code)
    if out[new_pool:new_pool + len(data) - original_pool] != data[original_pool:]:
        raise ValueError('Original string pool was not preserved after movement')
    allowed = {n for plan in plans for n in range(*plan['original_span'])} | set(range(20, 24))
    if any(out[n] != moved[n] for n in range(original_pool) if n not in allowed):
        raise ValueError('Code outside the declared spans changed')
    verify_layout(bytes(out), changes, reports)
    return bytes(out), changes, reports


def verify_layout(data, changes, groups):
    """Check logical text storage, actual fragment references, and page content."""
    parsed = parse_pool(data)
    by_offset = {row['source_offset']: row for row in parsed['strings']}
    records = changes + [row for group in groups for page in group['pages'] for row in page]
    for record in records:
        row = by_offset[record['new_offset']]
        if row['reference_instructions'] != record['reference_instructions']:
            raise ValueError('Reflow references differ from the manifest')
        end = record['new_offset'] + record['new_byte_length']
        if data[record['new_offset']:end].decode('cp932') != record['display_text'] or data[end:end + 2] != b'\0\0':
            raise ValueError('Reflow text or terminator differs from the manifest')
    metrics = None
    if any('max_pixel_width' in group for group in groups):
        from font_metrics import collect
        metrics = collect()[0]['characters']
    for group in groups:
        texts = [row['text'] for page in group['pages'] for row in page]
        if group.get('layout_profile') == PIXEL_PROFILE:
            if group.get('max_font_objects_per_page') != PIXEL_PAGE_CAPACITY:
                raise ValueError('Layout lacks the required font-pool capacity binding')
            for page in group['pages']:
                verify_page_capacity([row['text'] for row in page], PIXEL_PAGE_CAPACITY)
        if ' '.join(texts) != group['text']:
            raise ValueError('Reflow dropped or changed target content')
        if any(not 1 <= len(page) <= group['max_lines_per_page'] for page in group['pages']):
            raise ValueError('Page exceeds the line limit')
        if any(len(row['display_text']) > group['max_display_units'] for page in group['pages'] for row in page):
            raise ValueError('Line exceeds the glyph limit')
        if 'max_pixel_width' in group and any(latin_width(row['text'], metrics) > group['max_pixel_width']
                                             for page in group['pages'] for row in page):
            raise ValueError('Line exceeds measured pixel capacity')
