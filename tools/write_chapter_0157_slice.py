"""Create one reviewed-format target slice for Chapter 5 resource 157."""
import argparse
import json
from pathlib import Path

from chapter_source import chapter_source

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'work/translation/en/chapters_0.1.14/0157'


def document(start, texts, examined_start, examined_end, uncertainties=None):
    resource, rows, _ = chapter_source(157)
    if isinstance(texts, dict):
        expected = list(range(start, start + min(80, len(rows) - start)))
        assert set(expected).issubset(map(int, texts))
        texts = [texts[str(n)] if str(n) in texts else texts[n] for n in expected]
    assert len(texts) == min(80, len(rows) - start)
    entries = {}
    for number, text in enumerate(texts, start):
        row = rows[number]
        entries[row['id']] = {
            'id': row['id'],
            'source_sha256': row['source_sha256'],
            'source_offset': row['source_offset'],
            'source_byte_length': row['source_byte_length'],
            'reference_instructions': row['reference_instructions'],
            'resource_row': number,
            'text': text,
            'status': 'draft',
            'notes': 'Translation drafted with adjacent dialogue context; control tokens preserved.'
        }
    return {
        'resource_id': resource['id'],
        'assigned_range': [start, start + len(texts) - 1],
        'rows_examined': {
            'ranges_inclusive': [[examined_start, examined_end]],
            'count': examined_end - examined_start + 1
        },
        'uncertainties': uncertainties or [],
        'translations': entries
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=Path, help='JSON with start, texts, and examination bounds')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    source = json.loads(args.input.read_text(encoding='utf-8'))
    result = document(source['start'], source['texts'], source['examined_start'], source['examined_end'], source.get('uncertainties'))
    target = OUT / f"slice_{source['start']:04d}.targets.json"
    print(json.dumps({'target': str(target.relative_to(ROOT)), 'assigned_range': result['assigned_range'], 'rows': len(result['translations']), 'rows_examined': result['rows_examined']}, indent=2))
    if args.write:
        OUT.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
