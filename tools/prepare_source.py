"""Create a verified working ISO; default mode only previews the operation."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'docs/source_scan.json').read_text(encoding='utf-8'))['source']
    source = ROOT / manifest['source_name']
    target = ROOT / 'work/source/original.iso'
    preview = {'mode': 'write' if args.write else 'dry run', 'source': str(source),
               'destination': str(target), 'size_bytes': manifest['iso_size_bytes'],
               'expected_sha256': manifest['iso_sha256'], 'already_exists': target.exists(),
               'free_bytes': shutil.disk_usage(ROOT).free}
    print(json.dumps(preview, indent=2), flush=True)
    if not args.write:
        return
    if target.exists():
        raise SystemExit('Working ISO already exists; refusing to overwrite it.')
    if shutil.disk_usage(ROOT).free < manifest['iso_size_bytes']:
        raise SystemExit('Insufficient disk space')
    source_hash = hashlib.sha256()
    with source.open('rb') as stream:
        while chunk := stream.read(4 * 1024 * 1024):
            source_hash.update(chunk)
    if source_hash.hexdigest() != manifest['source_sha256']:
        raise SystemExit('Source ZIP hash mismatch')
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_suffix('.iso.partial')
    digest = hashlib.sha256()
    total = 0
    with zipfile.ZipFile(source) as archive, archive.open(manifest['iso_name']) as stream, partial.open('xb') as output:
        while chunk := stream.read(4 * 1024 * 1024):
            digest.update(chunk)
            total += len(chunk)
            output.write(chunk)
    if digest.hexdigest() != manifest['iso_sha256'] or total != manifest['iso_size_bytes']:
        raise SystemExit('Working ISO verification failed; partial file retained for inspection')
    partial.rename(target)
    print(json.dumps({'verified': True, 'bytes': total, 'sha256': digest.hexdigest()}))


if __name__ == '__main__':
    main()
