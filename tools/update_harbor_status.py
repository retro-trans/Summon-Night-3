"""Preview status/documentation reconciliation against the reviewed harbor catalog."""
import argparse
import json
from sn3_archive import ROOT


def prepare():
    catalog = json.loads((ROOT / 'work/translation/en/opening_harbor.reviewed.json').read_text(encoding='utf-8'))
    report = json.loads((ROOT / 'docs/opening_harbor_validation.json').read_text(encoding='utf-8'))
    stats = catalog['statistics']
    status_path = ROOT / 'docs/translation_status.json'
    status = json.loads(status_path.read_text(encoding='utf-8'))
    pools = status['script_pools']
    status['glossary_entries_scope'] = 'Core entities.json entries used by existing builds; UI and harbor glossaries tracked separately.'
    pools.update(drafts=stats['preserved_draft_nonempty_rows'], meaning_reviewed=stats['preserved_draft_nonempty_rows'],
                 assigned_opening_slice_rows=640, opening_slices=report['opening_slices'],
                 unresolved_opening_slice_rows=640-stats['preserved_draft_nonempty_rows'],
                 pending_draft_integration='Original drafts remain immutable. A separate reviewed harbor catalog applies meaning corrections and complete boundary proposals before glossary normalization. It is not a build selection; layout and runtime validation remain pending.')
    status['opening_harbor'] = {
        'catalog': 'work/translation/en/opening_harbor.reviewed.json',
        'documentation': 'docs/OPENING_HARBOR_TRANSLATIONS.md',
        'validation': 'docs/opening_harbor_validation.json',
        'source_opening_rows': [0, 640], 'statistics': stats,
        'glossary': 'work/glossary/opening_harbor.json', 'glossary_entries': 9,
        'screenshots': 'work/ui/harbor_dialogue/index.json',
        'scope': 'Recollection and complete harbor/student branches through departure reflection; next cabin conversation begins at641.',
        'preserved_original_drafts_are_counted_separately': True,
        'new_rows_inserted': 0, 'layout_or_runtime_verified': False,
        'remaining_meaning_uncertainty': 'Quiz rows240–242 retain null targets because the exclusion wording is ambiguous.',
        'next_step': 'Measure and reflow complete reviewed groups; validate helpers, choices, runtime name and musical note, then build a new version with relocation. Identify native location-banner asset.'}
    updates = {status_path: json.dumps(status, ensure_ascii=False, indent=2)+'\n'}
    readme = ROOT / 'README.md'
    content = readme.read_text(encoding='utf-8')
    content = content.replace('- [Setup/options translations]', '- [Opening and harbor translations](docs/OPENING_HARBOR_TRANSLATIONS.md): reviewed dialogue around the four supplied screenshots, including alternate students; not yet inserted.\n- [Setup/options translations]', 1)
    start = content.index('The two opening slices contain')
    end = content.index('Story decompression', start)
    content = content[:start] + (
        f"Eight opening slices contain 640 assigned rows and {stats['preserved_draft_nonempty_rows']} nonempty\n"
        f"independently reviewed original drafts. The separate harbor catalog contains\n"
        f"{stats['reviewed_target_rows']} reviewed English rows across the 641-row scope after meaning and\n"
        "boundary fixes, plus three unresolved quiz rows. These counts include alternate\n"
        "branches and sentence fragments. The new text is not in the playable image.\n"
        "Complete-group layout, runtime tokens, save/load, alternate paths and\n"
        "complete-chapter memory capacity still need verification.\n") + content[end:]
    content = content.replace('[Workspace audit](docs/workspace_audit_2026-09-26_rescan.json): current integrity checks, both reviewed slices, and reconciled resource counts.',
                              '[Workspace audit](docs/workspace_audit_2026-09-26_harbor.json): source/build integrity checks, eight reviewed slices, and reconciled resource counts.')
    updates[readme] = content
    tools = ROOT / 'tools/README.md'
    content = tools.read_text(encoding='utf-8')
    section = '''## Opening and harbor review consolidation

`prepare_harbor_context.py` verifies source and screenshot identities and previews
the nine-entry research glossary plus four screenshot anchors. `--write` creates
new files only. The supplied crops establish inspection dimensions, not the
maximum text width of every dialogue style.

`prepare_harbor_translations.py` checks eight disjoint 80-row assignments, every
independent review's target hash and coverage, then applies accepted meaning and
complete-group boundary proposals. It scans the target corpus for glossary
aliases and normalizes the successor only after meaning edits. It checks source
identities, group completeness, choice indentation, runtime controls and encoding.
After inspecting its samples, `--write` creates the reviewed catalog, readable
English document and static validation report; existing evidence is never replaced.
This is full-meaning text, not a measured layout or ISO selection.

`update_harbor_status.py` previews changes to status and overview counts. Inspect
the preview before `--write`. Then run `audit_workspace.py` and save its passing
preview under a new report name. The harbor audit reconciles eight slices while
preserving the previous two-slice audit as historical evidence.

'''
    content = content.replace('## Current workspace audit', section+'## Current workspace audit', 1)
    updates[tools] = content
    changelog = ROOT / 'CHANGELOG.md'
    content = changelog.read_text(encoding='utf-8')
    needle = '- This translation pass does not create an ISO or change the running emulator.'
    addition = (f"- Consolidated {stats['reviewed_target_rows']} reviewed English source rows in the 641-row scope,\n"
                "  including prior work and two completed boundary rows. Three quiz rows remain\n"
                "  unresolved. Source order includes alternate routes and sentence fragments.\n"
                f"  Applied {stats['meaning_or_boundary_text_changes']} meaning/boundary text changes; glossary scan made\n"
                f"  {stats['name_normalizations']} spelling changes. Checked every source/review identity, complete group,\n"
                "  control token and encoded target. Original drafts and earlier builds remain intact.\n")
    assert needle in content
    updates[changelog] = content.replace(needle, addition+needle, 1)
    return updates, stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    updates, stats = prepare()
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'statistics': stats,
                      'samples': {p.relative_to(ROOT).as_posix(): text[:2000] if p.name != 'translation_status.json' else json.loads(text)['opening_harbor']
                                  for p, text in updates.items()}}, ensure_ascii=False, indent=2))
    if args.write:
        for path, content in updates.items():
            path.write_text(content, encoding='utf-8')


if __name__ == '__main__':
    main()
