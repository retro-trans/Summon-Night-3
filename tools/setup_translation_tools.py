"""Download portable upstream tools into the workspace; preview by default."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = {
    'pspdecrypt-1.0': 'https://github.com/John-K/pspdecrypt/releases/download/1.0/pspdecrypt-1.0-windows.zip',
    'ppsspp-1.20.4': 'https://github.com/hrydgard/ppsspp/releases/download/v1.20.4/PPSSPP-v1.20.4-Windows-x64.zip',
    'capstone-5.0.9': 'https://files.pythonhosted.org/packages/50/e6/6f06fdb6a9ed32b2f7cd9c036b92d5324112c3ef7080f2c71efc367d40dd/capstone-5.0.9-py3-none-win_amd64.whl',
    'websocket-client-1.9.2': 'https://files.pythonhosted.org/packages/d5/d2/cc4dc1271e464942db7ee278baae2daa99ee77cb2af744025c04da585a3e/websocket_client-1.9.2-py3-none-any.whl',
    'pyelftools-0.33': 'https://files.pythonhosted.org/packages/46/2a/f9697576603dae937727827505a6126a066affb227034e77e6f9068910da/pyelftools-0.33-py3-none-any.whl',
}
EXPECTED_HASHES = {
    'capstone-5.0.9': '732cedbbb56d42e723f14d7af6387f1454194a820b4b96b56d1e53f865ef85d0',
    'websocket-client-1.9.2': 'e1a673830a9c7bfa47b1cd3d5e4178f4c9651d80a4eab02c9c23a1c3ec6250ce',
    'pyelftools-0.33': 'f215ad5f47d3f1373a21496a6c9e0707c622840d0622f23ff7ce08678b020036',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'downloads': [
        {'url': url, 'destination': str(ROOT / 'tools/vendor' / name),
         'exists': (ROOT / 'tools/vendor' / name).exists()} for name, url in PACKAGES.items()]}, indent=2), flush=True)
    if not args.write:
        return
    manifest = ROOT / 'tools/vendor/download_manifest.json'
    records = json.loads(manifest.read_text()) if manifest.exists() else []
    for name, url in PACKAGES.items():
        destination = ROOT / 'tools/vendor' / name
        if destination.exists() and any(record['name'] == name for record in records):
            print('Already present: ' + name, flush=True)
            continue
        with urllib.request.urlopen(url, timeout=45) as response:
            payload = response.read()
        if name in EXPECTED_HASHES and hashlib.sha256(payload).hexdigest() != EXPECTED_HASHES[name]:
            raise ValueError('Package SHA-256 mismatch: ' + name)
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            for member in archive.infolist():
                path = (destination / member.filename).resolve()
                if destination.resolve() not in path.parents and path != destination.resolve():
                    raise ValueError('Unsafe archive path')
                if path.is_file() and path.read_bytes() != archive.read(member):
                    raise ValueError('Existing tool file differs from upstream: ' + str(path))
            for member in archive.infolist():
                if not (destination / member.filename).exists():
                    archive.extract(member, destination)
            records.append({'name': name, 'url': url, 'zip_sha256': hashlib.sha256(payload).hexdigest(),
                            'files': [entry.filename for entry in archive.infolist()]})
        print(json.dumps({'installed': name, 'bytes_downloaded': len(payload)}), flush=True)
        manifest.write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
