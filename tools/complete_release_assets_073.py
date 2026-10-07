"""Add release documentation and checksums to the verified two-patch package."""
import argparse, hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def main():
    p = argparse.ArgumentParser(); p.add_argument('--write', action='store_true'); a = p.parse_args()
    out = ROOT / 'work/output/release-v0.1.73'
    manifest = json.loads((out / 'BUILD-MANIFEST.json').read_text())
    assert manifest['version'] == '0.1.73'
    assert sorted(p.name for p in out.glob('*.xdelta')) == ['SN3-English-v0.1.65-to-v0.1.73.xdelta', 'SN3-English-v0.1.73.xdelta']
    files = {'README-v0.1.73.txt': (ROOT / 'docs/RELEASE_0.1.73.md').read_bytes(),
             'CHANGELOG-v0.1.73.txt': (ROOT / 'CHANGELOG.md').read_bytes(),
             'GAMEPLAY-VALIDATION-v0.1.73.json': (ROOT / 'work/ui/release_0.1.73/VALIDATION.json').read_bytes()}
    names = sorted({p.name for p in out.iterdir() if p.is_file()} | set(files))
    for algorithm in ('sha1', 'sha256'):
        files[algorithm.upper() + 'SUMS-v0.1.73.txt'] = ''.join(
            hashlib.new(algorithm, files[n] if n in files else (out / n).read_bytes()).hexdigest() + '  ' + n + '\n'
            for n in names).encode()
    print(json.dumps(dict(mode='write' if a.write else 'preview', assets=list(files)), indent=2))
    if a.write:
        for name, data in files.items():
            path = out / name; assert not path.exists(), name; path.write_bytes(data)

if __name__ == '__main__':
    main()
