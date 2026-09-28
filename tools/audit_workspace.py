"""Audit saved translation metadata and build integrity without exporting scripts."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def read_json(relative):
    return json.loads((ROOT / relative).read_text(encoding='utf-8'))


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def audit():
    inventory = read_json('docs/resource_inventory.json')
    scripts = read_json('work/translation/en/script_strings.index.json')
    status = read_json('docs/translation_status.json')
    draft_paths = sorted(path for path in (ROOT / 'work/translation/en').glob('opening_*.targets.json')
                         if re.fullmatch(r'opening_\d{3}\.targets\.json', path.name))
    labels = read_json('work/translation/en/character_labels.index.json')
    label_targets = read_json('work/translation/en/character_labels.targets.json')
    glossary = read_json('work/glossary/entities.json')
    versions = sorted((p.name for p in (ROOT / 'work/output').iterdir()
                       if p.is_dir() and re.fullmatch(r'0\.\d+\.\d+', p.name)),
                      key=lambda name: tuple(map(int, name.split('.'))))
    latest = versions[-1]
    build_dir = Path('work/output') / latest
    manifest = read_json(build_dir / 'manifest.json')
    candidates = [read_json(name) for name in manifest['inputs_sha256']
                  if name.startswith('work/translation/en/') and name.endswith('.targets.json')
                  and name != 'work/translation/en/character_labels.targets.json']
    selections = [row for row in candidates if 'resource_id' in row and 'translations' in row]
    if len(selections) != 1:
        raise ValueError('Expected one script selection in the current build manifest')
    selection = selections[0]
    checks = []

    def check(name, expected, actual):
        checks.append({'check': name, 'expected': expected, 'actual': actual,
                       'passed': expected == actual})

    check('latest version agrees with status', status['latest_build'], latest)
    source_hash = read_json('docs/source_scan.json')['source']['iso_sha256']
    for name, metadata in [('inventory', inventory), ('script index', scripts),
                           ('build', manifest), ('selection', selection)]:
        check(name + ' source identity', source_hash, metadata['source_iso_sha256'])
    files = dict(manifest['inputs_sha256'])
    files.update(selection['review_inputs_sha256'])
    files['work/source/original.iso'] = source_hash
    files[(build_dir / manifest['output_iso']).as_posix()] = manifest['output_sha256']
    files[(build_dir / 'EBOOT.elf').as_posix()] = manifest['executable_patch']['patched_elf_sha256']
    for relative, expected in files.items():
        path = ROOT / relative
        check('sha256:' + relative, expected, sha256(path) if path.is_file() else None)

    nodes = {node['id']: node for node in inventory['nodes']}
    resources = scripts['resources']
    script_ids = {resource['id'] for resource in resources}
    check('unique inventory IDs', len(inventory['nodes']), len(nodes))
    check('unique script resource IDs', len(resources), len(script_ids))
    mismatch = []
    for resource in resources:
        node = nodes.get(resource['id'])
        if node is None or any(resource[key] != node[key]
                               for key in ('bank', 'path', 'offset', 'size', 'sha256')):
            mismatch.append(resource['id'])
    check('script to inventory identity mismatches', [], mismatch)
    rows = [row for resource in resources for row in resource['strings']]
    counts = {
        'script_resources': len(resources),
        'compressed_script_resources': sum(r['compression'] is not None for r in resources),
        'resources_with_strings': sum(bool(r['strings']) for r in resources),
        'string_occurrences': len(rows),
        'japanese_occurrences': sum(row['contains_japanese'] for row in rows),
        'unique_japanese_strings': len({r['source_sha256'] for r in rows if r['contains_japanese']}),
        'occurrences_without_reference': sum(not r['reference_instructions'] for r in rows),
    }
    for key, value in counts.items():
        check('recount:' + key, scripts['statistics'][key], value)
    remaining = [node for node in inventory['nodes']
                 if node['kind'] == 'unclassified' and node['id'] not in script_ids]
    reconciled = Counter('recognized_script' if node['id'] in script_ids else node['kind']
                         for node in inventory['nodes'])
    check('reconciled node total', len(inventory['nodes']), sum(reconciled.values()))
    indexed_rows = {row['id']: row for row in rows}
    indexed_resources = {resource['id']: resource for resource in resources}
    assigned_ids, drafted_ids, reviewed_ids = set(), set(), set()
    slices = []
    for path in draft_paths:
        relative = path.relative_to(ROOT).as_posix()
        drafts = read_json(relative)
        targets = drafts['translations']
        resource = indexed_resources[drafts['resource_id']]
        review_path = path.with_name(path.name.replace('.targets.json', '.meaning_review.json'))
        review = read_json(review_path.relative_to(ROOT))
        coverage = {row['id']: row for row in review['coverage']}
        check('slice assigned count:' + relative, drafts['rows_in_slice'], len(targets))
        check('slice resource identity:' + relative, resource['sha256'], drafts['source_resource_sha256'])
        check('slice overlap:' + relative, [], sorted(assigned_ids.intersection(targets)))
        check('review target hash:' + relative, review['reviewed_target_sha256'], sha256(path))
        check('independent review:' + relative, True, review['independent_review'])
        check('review coverage:' + relative, sorted(targets), sorted(coverage))
        mismatches = []
        for key, row in targets.items():
            original = indexed_rows.get(key)
            if (original is None or row['id'] != key
                    or any(row[field] != original[field]
                           for field in ('source_sha256', 'reference_instructions'))
                    or coverage.get(key, {}).get('source_sha256') != row['source_sha256']):
                mismatches.append(key)
        check('slice source/review row identities:' + relative, [], mismatches)
        nonempty = {key for key, row in targets.items() if row.get('text')}
        check('review draft count:' + relative,
              review['verdict']['existing_draft_rows_reviewed'], len(nonempty))
        assigned_ids.update(targets)
        drafted_ids.update(nonempty)
        reviewed_ids.update(nonempty.intersection(coverage))
        slices.append({'file': relative, 'sha256': sha256(path),
                       'review_file': review_path.relative_to(ROOT).as_posix(),
                       'review_sha256': sha256(review_path),
                       'assigned': len(targets), 'drafted': len(nonempty),
                       'meaning_reviewed': len(nonempty.intersection(coverage)),
                       'rows_examined_by_translator': drafts['rows_examined'],
                       'rows_examined_by_reviewer': review['rows_examined'],
                       'required_meaning_edits': len(review['required_meaning_edits']),
                       'cross_slice_proposals': len(review.get('coordinated_completion_proposals', []))})
    drafted = len(drafted_ids)
    check('draft count agrees with status', status['script_pools']['drafts'], drafted)
    check('assigned count agrees with status', status['script_pools']['assigned_opening_slice_rows'], len(assigned_ids))
    check('reviewed count agrees with status', status['script_pools']['meaning_reviewed'], len(reviewed_ids))
    check('selected count agrees with status', status['script_pools']['inserted'], len(selection['translations']))
    check('glossary count agrees with status', status['glossary_entries'], len(glossary['entries']))
    return {
        'schema_version': 2,
        'audited_at_utc': datetime.now(timezone.utc).isoformat(),
        'scope': 'Saved metadata reconciliation and selected-file integrity. No new binary decoding, runtime test, or meaning review.',
        'git_directory_present': (ROOT / '.git').exists(),
        'build_versions': versions,
        'latest_build': latest,
        'script_counts': counts,
        'inventory_reconciliation': {
            'node_count': len(inventory['nodes']),
            'original_kind_counts': dict(Counter(n['kind'] for n in inventory['nodes'])),
            'recognized_scripts_previously_unclassified': sum(nodes[r]['kind'] == 'unclassified' for r in script_ids if r in nodes),
            'reconciled_kind_counts': dict(reconciled),
            'remaining_unclassified_by_bank': dict(Counter(n['bank'] for n in remaining)),
            'remaining_unclassified_nodes': len(remaining),
            'limit': 'Resource nodes are not text counts; unknown nodes may contain nontext data or further containers. Original inventory is preserved.',
        },
        'translation_counts': {
            'opening_assigned': len(assigned_ids),
            'opening_nonempty_drafts': drafted,
            'opening_meaning_reviewed': len(reviewed_ids),
            'opening_without_drafts': len(assigned_ids - drafted_ids),
            'opening_slices': slices,
            'opening_selected': len(selection['translations']),
            'japanese_labels_indexed': labels['japanese_string_count'],
            'label_targets': len(label_targets['translations']),
            'glossary_entries': len(glossary['entries']),
        },
        'integrity_checks': checks,
        'checks_passed': sum(c['passed'] for c in checks),
        'checks_failed': sum(not c['passed'] for c in checks),
        'not_revalidated': ['Original ZIP hash/CRC', 'Older build image hashes',
                            'Runtime behavior and visual coverage', 'Full-game text completeness'],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--report', default='docs/workspace_audit_2026-09-26.json')
    args = parser.parse_args()
    destination = (ROOT / args.report).resolve()
    try:
        destination.relative_to(ROOT)
    except ValueError:
        parser.error('Report must be inside the workspace')
    if args.write and destination.exists():
        parser.error('Refusing to overwrite existing evidence')
    report = audit()
    print(json.dumps({'mode': 'write' if args.write else 'dry run',
                      'destination': str(destination), **report}, indent=2))
    if report['checks_failed']:
        raise SystemExit('Audit failed; no report written')
    if args.write:
        with destination.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
