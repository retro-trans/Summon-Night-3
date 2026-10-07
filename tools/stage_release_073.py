"""Stage only release inputs, related tools, documentation and reviewed UI evidence."""
import argparse, ast, json, re, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
GIT = ['git', '-c', 'safe.directory=' + ROOT.as_posix()]

def selected_paths():
    manifest = json.loads((ROOT / 'work/output/0.1.73/manifest.json').read_text())
    paths = {n for n in manifest['inputs_sha256'] if not n.startswith('work/output/')}
    paths |= {'.gitignore', 'CHANGELOG.md', 'docs/RELEASE_0.1.73.md', 'docs/POT_CRASH_0.1.73.md',
              'tools/package_release_073.py', 'tools/stage_release_073.py',
              'tools/complete_release_assets_073.py', 'tools/verify_retro_trans_live_073.py',
              'work/ui/release_0.1.73/VALIDATION.json'}
    paths |= {p.relative_to(ROOT).as_posix() for p in (ROOT / 'docs').iterdir()
              if re.search(r'0\.1\.(?:6[6-9]|70)\.md$', p.name)}
    for n in ('status_runtime_066.py', 'status_runtime_067.py', 'record_status_runtime_066.py',
              'record_status_067.py', 'finalize_status_066.py', 'launch_status_066.ps1',
              'launch_status_067.ps1', 'categories_runtime_068.py', 'categories_runtime_069.py',
              'categories_runtime_070.py'):
        paths.add('tools/' + n)
    report = json.loads((ROOT / 'work/ui/release_0.1.73/VALIDATION.json').read_text())
    for item in report['evidence']:
        paths.add(item['capture'])
        paths.add(str(Path(item['capture']).with_suffix('.json')).replace('\\', '/'))
    # Include local module dependencies without adding unrelated working files.
    pending = [n for n in paths if n.endswith('.py')]
    while pending:
        n = pending.pop()
        tree = ast.parse((ROOT / n).read_text(encoding='utf-8-sig'))
        for node in ast.walk(tree):
            modules = [x.name for x in node.names] if isinstance(node, ast.Import) else ([node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
            for module in modules:
                name = 'tools/' + module.split('.')[0] + '.py'
                if (ROOT / name).is_file() and name not in paths:
                    paths.add(name); pending.append(name)
    return paths

def main():
    p = argparse.ArgumentParser(); p.add_argument('--write', action='store_true'); a = p.parse_args()
    paths = selected_paths()
    for name in sorted(paths):
        path = ROOT / name
        assert path.is_file(), name
        assert not name.startswith(('work/incoming/', 'incoming/', 'work/scratch/', 'work/source/', 'work/output/')), name
        assert path.suffix.lower() not in ('.zip', '.iso', '.elf', '.bin', '.xdelta', '.ppst', '.sav', '.pem', '.key'), name
        if path.suffix in ('.py', '.ps1', '.json', '.md'):
            text = path.read_text(encoding='utf-8-sig')
            assert not re.search(r'-----BEGIN (?:RSA )?PRIVATE KEY-----|"(?:private_key|refresh_token)"\s*:\s*"', text), name
            assert sum('\u3040' <= c <= '\u9fff' for c in text) < 10000, ('Extensive original text', name)
    staged = set(subprocess.check_output(GIT + ['diff', '--cached', '--name-only'], text=True).splitlines())
    assert staged <= paths, ('Unrelated staged files', sorted(staged - paths))
    untracked = set(subprocess.check_output(GIT + ['ls-files', '--others', '--exclude-standard'], text=True).splitlines())
    modified = set(subprocess.check_output(GIT + ['diff', '--name-only'], text=True).splitlines())
    selected = sorted(paths & (untracked | modified | staged))
    print(json.dumps(dict(mode='stage' if a.write else 'preview', count=len(selected), files=selected), indent=2))
    if a.write:
        subprocess.run(GIT + ['add', '--'] + selected, check=True)

if __name__ == '__main__':
    main()
