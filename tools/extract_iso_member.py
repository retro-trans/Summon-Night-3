"""Extract one known ISO member; default mode previews without writing."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('member')
    parser.add_argument('destination', type=Path)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'docs/source_scan.json').read_text())
    entry = next(row for row in manifest['files'] if row['path'] == args.member)
    destination = args.destination.resolve()
    if ROOT not in destination.parents:
        raise ValueError('Destination must be in the workspace')
    with (ROOT / 'work/source/original.iso').open('rb') as stream:
        stream.seek(entry['sector'] * 2048)
        data = stream.read(entry['size_bytes'])
    if len(data) != entry['size_bytes']:
        raise ValueError('Short ISO read')
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'source_member': args.member,
                      'destination': str(destination), 'size_bytes': len(data),
                      'sha256': hashlib.sha256(data).hexdigest(), 'first_16_bytes': data[:16].hex()}, indent=2))
    if args.write:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('xb') as output:
            output.write(data)


if __name__ == '__main__':
    main()
