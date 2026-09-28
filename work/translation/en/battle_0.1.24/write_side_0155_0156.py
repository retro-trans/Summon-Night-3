import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'tools'))
from battle_source_024 import load, source_text
from dialogue_encoding import encode_dialogue

OUT = Path(__file__).with_name('side_0155_0156.targets.json')
TEXT = {
    155: ['Raaaargh!!', "Let's go, everyone!", "Let's go, everyone!"],
    156: ["Come on, let's", 'strike back!', 'Come on,', "let's join everyone!", '...Yes!'],
}


def build():
    translations = {}
    for resource, targets in TEXT.items():
        _, rows, data = load(resource)
        for number, target in enumerate(targets):
            row = rows[number]
            encode_dialogue(target, source_text(row, data))
            translations[row['id']] = dict(
                row,
                resource=resource,
                resource_row=number,
                ordered_index=10000 + number,
                text=target,
                status='draft',
                notes='Provisional Chapter 1-8 side-battle candidate; no source control tokens.',
            )
    return {
        'resources': [155, 156],
        'resource_rows': {'155': [0, 1, 2], '156': [0, 1, 2, 3, 4]},
        'translations': translations,
        'uncertainties': ['The text is fully translated, but its Chapter 1-8 side-battle association is provisional and is not proven by the runtime loader.'],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    document = build()
    print(json.dumps({'mode': 'write' if args.write else 'dry-run', 'count': len(document['translations'])}))
    if args.write:
        OUT.write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
