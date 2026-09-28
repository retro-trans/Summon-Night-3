"""Reversible, current-page-only spacing experiment on candidate 0.1.2; preview first."""
import argparse
import base64
from datetime import datetime, timezone
import json
from pathlib import Path
import struct

from capture_framebuffer import capture
from font_metrics import collect, digest
from ppsspp_client import request, ROOT
from probe_opening_dialogue import observe
from verify_runtime_scripts import memory

CONTEXT = 0x08e30910
GLYPHS = CONTEXT + 0x3e0
FONT_HEADER = 0x08c42800


def snapshot():
    if request('version')['version'] != 'v1.20.4' or request('game.status')['game']['id'] != 'NPJH50380':
        raise ValueError('This experiment is bound to the verified PPSSPP/game version')
    if not request('cpu.status')['stepping']:
        raise ValueError('Pause on a fully revealed translated portrait page before previewing')
    if request('cpu.breakpoint.list')['breakpoints']:
        raise ValueError('Existing breakpoints must not be changed by this experiment')
    manifest_path = ROOT / 'work/output/0.1.2/manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    state = observe(manifest['script_changes'][0], check_script=True)
    if state['native_call'] != '0x3052' or state['choice_present']:
        raise ValueError('Expected ordinary dialogue, not a choice or another native call')
    if not 1 <= len(state['lines']) <= 3 or any(not r['id'] or r['nonzero_kinds'] for r in state['lines']):
        raise ValueError('Every current line must be a known token-free translated row')
    metrics, font = collect()
    if memory(FONT_HEADER, len(font)) != font:
        raise ValueError('Live font payload differs from both verified source font copies')
    context = memory(CONTEXT, 0x4be4)
    if struct.unpack_from('<I', context, 4)[0] != 0:
        raise ValueError('Only the observed normal portrait style is supported')
    count = struct.unpack_from('<I', context, 0x4be0)[0]
    if count != sum(row['cell_count'] for row in state['lines']) or not 1 <= count <= 96:
        raise ValueError('Glyph object count differs from processed cells')
    original = context[0x3e0:0x3e0 + count * 0x60]
    replacement = bytearray(original)
    records, lines = [], []
    number = 0
    for line_index, row in enumerate(state['lines']):
        text = row['target_text']
        if len(text) != row['cell_count']:
            raise ValueError('Target characters do not map one-to-one to processed cells')
        pen = 3.0  # Keep a small left inset, independently of each glyph's bearing.
        for column, char in enumerate(text):
            metric = metrics['characters'].get(char)
            if not metric:
                raise ValueError('No accepted Latin metric for ' + repr(char))
            offset = number * 0x60
            obj = struct.unpack_from('<I', original, offset)[0]
            cell = CONTEXT + 0x84 + line_index * 0x8c + 10 + column * 4
            if memory(cell, 4) != bytes.fromhex(metric['cp932_hex']) + b'\0\0':
                raise ValueError('Processed cell differs from the measured glyph')
            if struct.unpack('<I', memory(obj + 0xc8, 4))[0] != cell:
                raise ValueError('Font object points to an unexpected processed cell')
            width, height = struct.unpack_from('<2f', original, offset + 4)
            x, y = struct.unpack_from('<2f', original, offset + 0x40)
            anchor_x, anchor_y = struct.unpack_from('<2f', original, offset + 0x50)
            if (width, height) != (16.0, 16.0) or (x, y) != (anchor_x, anchor_y):
                raise ValueError('Unexpected glyph size or active movement animation')
            if x != 8.0 + column * 16 or original[offset + 0xc] != 0:
                raise ValueError('Unexpected spacing/style; this is not the unmodified pilot page')
            new_x = pen + metric['proposed_center_offset_pixels']
            struct.pack_into('<f', replacement, offset + 0x40, new_x)
            struct.pack_into('<f', replacement, offset + 0x50, new_x)
            records.append({'glyph_index': number, 'line': line_index, 'column': column,
                            'character': char, 'font_object': hex(obj), 'cell_address': hex(cell),
                            'old_x': x, 'new_x': new_x, 'width': width, 'height': height})
            pen += metric['proposed_advance_pixels']
            number += 1
        lines.append({'text': text, 'old_cell_span_pixels': len(text) * 16,
                      'proposed_advance_span_pixels': pen - 3})
    return {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
            'kind': 'temporary RAM geometry experiment; not an ISO build or production font profile',
            'candidate_version': '0.1.2', 'candidate_sha256': manifest['output_sha256'],
            'manifest_sha256': digest(manifest_path.read_bytes()),
            'script_sha256': manifest['script_changes'][0]['decoded_sha256'],
            'font_resource_sha256': metrics['font_resource_sha256'],
            'tool_sha256': digest(Path(__file__).read_bytes()),
            'metrics_tool_sha256': metrics['tool_sha256'], 'state': state,
            'glyph_array_address': hex(GLYPHS), 'glyph_count': count,
            'original_glyph_bytes_hex': original.hex(),
            'original_glyph_sha256': digest(original), 'replacement_glyph_sha256': digest(replacement),
            'changed_fields_only': ['glyph + 0x40: x', 'glyph + 0x50: anchor x'],
            'records': records, 'lines': lines}, original, bytes(replacement)


def write_memory(data):
    if not request('cpu.status')['stepping']:
        raise ValueError('CPU must be held for geometry writes')
    request('memory.write', address=GLYPHS, base64=base64.b64encode(data).decode('ascii'))
    if memory(GLYPHS, len(data)) != data:
        raise ValueError('Geometry write did not verify')


def capture_settled(destination, name):
    # The first frame may have been prepared before the geometry change.
    for _ in range(2):
        request('cpu.resume')
        png, metadata = capture(hold=True)
    metadata['experiment_stage'] = name
    metadata['not_a_build_screenshot'] = True
    (destination / (name + '.png')).write_bytes(png)
    (destination / (name + '.json')).write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    return metadata['png_sha256']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    destination = args.output.resolve()
    if ROOT / 'work/ui' not in destination.parents or destination.exists():
        raise ValueError('Use a new experiment directory under work/ui')
    plan, original, replacement = snapshot()
    print(json.dumps({'mode': 'execute' if args.execute else 'dry run', 'output': str(destination),
                      'glyph_count': plan['glyph_count'], 'lines': plan['lines'],
                      'sample_changes': plan['records'][:6],
                      'changed_fields_only': plan['changed_fields_only'],
                      'restoration': 'Restore original x and anchor x in finally, verify, and capture restored page.'}, indent=2), flush=True)
    if not args.execute:
        return
    destination.mkdir()
    (destination / 'backup.json').write_text(json.dumps(plan, indent=2) + '\n', encoding='utf-8')
    result = {'started_at_utc': plan['checked_at_utc'], 'restored': False, 'screenshots': {}}
    attempted_write = False
    try:
        result['screenshots']['before'] = capture_settled(destination, 'before')
        current_plan, current_original, current_replacement = snapshot()
        if current_plan['state'] != plan['state'] or current_plan['records'] != plan['records']:
            raise ValueError('Dialogue changed during baseline capture; no geometry written')
        attempted_write = True
        write_memory(current_replacement)
        result['screenshots']['after'] = capture_settled(destination, 'after')
    finally:
        if not request('cpu.status')['stepping']:
            request('cpu.stepping')
        if attempted_write:
            current = bytearray(memory(GLYPHS, len(original)))
            # Restore only the changed coordinates; retain legitimate animation updates.
            for record in plan['records']:
                offset = record['glyph_index'] * 0x60
                if struct.unpack_from('<I', current, offset)[0] != int(record['font_object'], 16):
                    raise ValueError('Glyph identity changed; preserve backup for manual recovery')
                for field in (0x40, 0x50):
                    current[offset + field:offset + field + 4] = original[offset + field:offset + field + 4]
            write_memory(current)
            result['restored'] = True
            result['screenshots']['restored'] = capture_settled(destination, 'restored')
            restored_plan, _, _ = snapshot()
            result['same_dialogue_after_restore'] = restored_plan['state'] == plan['state']
            result['same_coordinates_after_restore'] = restored_plan['records'] == plan['records']
        result['completed_at_utc'] = datetime.now(timezone.utc).isoformat()
        (destination / 'result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
