"""Read-only, transient source/English preview at actual VM dialogue boundaries.

Use before drafting and reviewing an 80-row slice. A slice may cut a dialogue
box: read its entire source group and keep the English inside that group.
Do not pad spare fragments with repeated words or punctuation. Empty internal
continuations are supported, but empty complete boxes and menu labels are not.
No source transcript is saved by this tool.
"""
import argparse, json
from chapter_source_014 import load
from sn3_vm import instructions
from story_source_054 import FOLDER


def groups(rows, data):
    at = {i['offset']: i for i in instructions(data)}
    def joined(n):
        if n + 1 >= len(rows):
            return False
        refs = rows[n]['reference_instructions']
        return (len(refs) == 1
                and rows[n + 1]['reference_instructions'] == [refs[0] + 8]
                and at.get(refs[0] + 4, {}).get('target_word') == 2003
                and at.get(refs[0] + 12, {}).get('target_word') == 2003)
    n = 0
    while n < len(rows):
        selected = [n]
        while joined(selected[-1]):
            selected.append(selected[-1] + 1)
        yield selected
        n = selected[-1] + 1


def preview(number, start, count):
    _, rows, data = load(number)
    assert 0 <= start < len(rows) and count > 0
    translated = {}
    for path in sorted((FOLDER / f'{number:04d}').glob('slice_*.targets.json')):
        for target in json.loads(path.read_text('utf8'))['translations'].values():
            assert target['resource_row'] not in translated
            translated[target['resource_row']] = target['text']
    end = min(len(rows), start + count)
    for selected in groups(rows, data):
        if selected[-1] < start or selected[0] >= end:
            continue
        source = [data[rows[n]['source_offset']:rows[n]['source_offset'] +
                       rows[n]['source_byte_length']].decode('cp932') for n in selected]
        target = [translated.get(n) for n in selected]
        yield dict(source_rows=selected, source_fragments=source,
                   english_fragments=target,
                   joined_english=(' '.join(t for t in target if t)
                                   if all(t is not None for t in target) else None),
                   outside_slice_context=[n for n in selected if not start <= n < end])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('resource', type=int)
    parser.add_argument('--start', type=int, required=True)
    parser.add_argument('--count', type=int, default=80)
    args = parser.parse_args()
    for group in preview(args.resource, args.start, args.count):
        print(json.dumps(group, ensure_ascii=False))
