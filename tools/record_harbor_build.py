"""Preview current documentation/status changes for the verified 0.1.5 ISO."""
import argparse
import json
from sn3_archive import ROOT


def prepare():
    folder = ROOT / 'work/output/0.1.5'
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    layout = json.loads((ROOT / 'docs/harbor_build_layout_0.1.5.json').read_text(encoding='utf-8'))
    assert manifest['version'] == '0.1.5' and manifest['static_validation']['relocated_dialogue_strings'] == 609
    assert manifest['script_changes'][0]['decoded_sha256'] == layout['decoded_script_sha256']
    status_path = ROOT / 'docs/translation_status.json'
    status = json.loads(status_path.read_text(encoding='utf-8'))
    assert status['latest_build'] == '0.1.4', 'Record each build once'
    status['prior_candidate_0_1_4'] = status['latest_candidate']
    status.update(latest_build='0.1.5', next_build_version='0.1.6',
                  latest_build_kind='opening/harbor test ISO; static checks passed; runtime not yet verified',
                  previous_runtime_baseline='0.1.4',
                  coverage_counts_baseline='Inserted counts: 0.1.5. Runtime/visual counts remain historical 0.1.4 evidence; no new gameplay verification.')
    status['latest_candidate'] = {
        'acceptance': 'static_verified_runtime_pending', 'candidate_sha256': manifest['output_sha256'],
        'qa_report': 'docs/BUILD_0.1.5.md', 'inserted_dialogue_rows':609, 'inserted_labels':3,
        'compiled_reflow_groups':188, 'additional_dialogue_pages':41,
        'decoded_script_bytes':234726, 'runtime_verified':False, 'visual_verified':False,
        'retained_japanese_rows_in_harbor_scope':32,
        'scope_limit':'Four long-choice menus, six special-display groups, musical-note and runtime-name groups, and the unresolved quiz retain original Japanese. Setup textures/banner remain Japanese.'}
    status['script_pools'].update(inserted=609, compiled_reflow_groups=188, additional_dialogue_pages=41,
                                  layout_validation_report='docs/harbor_build_layout_0.1.5.json',
                                  expanded_script_runtime_scope='Historical 0.1.4 opening test only; the larger 0.1.5 script has static verification but no runtime acceptance.')
    status['opening_harbor'].update(new_rows_inserted=531, total_rows_inserted=609,
                                    build='0.1.5', build_selection='work/translation/en/opening_harbor_0.1.5.targets.json',
                                    retained_japanese_rows=32,
                                    next_step='Test 0.1.5 in game; add measured profiles for deferred displays, long choices, musical note and player name. Identify/repack the native location banner.')
    status['runtime']['evidence_version'] = '0.1.4; historical evidence, not the latest 0.1.5 image'
    status['runtime']['latest_build_runtime_verified'] = False
    updates = {status_path:json.dumps(status,ensure_ascii=False,indent=2)+'\n'}
    readme = ROOT / 'README.md'
    text = readme.read_text(encoding='utf-8')
    start, end = text.index('Status: candidate'), text.index('Story decompression')
    text = text[:start] + '''Status: **test ISO 0.1.5 is built** with 609 translated opening/harbor
dialogue and choice entries plus three character labels. It adds 531 entries
over 0.1.4. The source image, untouched files/resources, relocated text and
generated dialogue pages passed static verification. This image has not yet
been tested in game. The next unused build version is **0.1.6**.

Of the 641-row harbor scope, 32 entries remain Japanese: three uncertain quiz
rows and 29 entries requiring additional display/name/choice support. Setup
graphics and the harbor banner remain Japanese. The reviewed catalog contains
638 English entries; its originals and independent reviews are preserved.
See [build notes](docs/BUILD_0.1.5.md) and the
[ISO](work/output/0.1.5/Summon_Night_3_EN_0.1.5.iso).

The prior 0.1.4 passed a font-pool crash regression and selected later pages;
those runtime and visual counts are historical evidence, not 0.1.5 acceptance.
Complete-group layout, runtime names, save/load, alternate paths and memory
lifecycle still need in-game verification.
''' + text[end:]
    text = text.replace('including alternate students; not yet inserted.', 'including alternate students; 609 entries included in 0.1.5.')
    text = text.replace('docs/workspace_audit_2026-09-26_harbor.json', 'docs/workspace_audit_0.1.5.json')
    updates[readme] = text
    readable = ROOT / 'docs/OPENING_HARBOR_TRANSLATIONS.md'
    text = readable.read_text(encoding='utf-8').replace(
        '**Not yet inserted into the game.** The playable image remains 0.1.4. English below is full-meaning text, not final measured line breaks.',
        '**Test build 0.1.5 includes 609 of these entries.** Across the 641-row scope, 32 rows remain Japanese: the 3 unresolved quiz rows and 29 rows awaiting additional display/choice/name support. English below is full-meaning text; the build wraps and paginates supported groups. The location banner is not yet inserted. See [build notes](BUILD_0.1.5.md).')
    updates[readable] = text
    notes = f'''# Build 0.1.5 — opening and harbor test ISO

File: [Summon_Night_3_EN_0.1.5.iso](../work/output/0.1.5/Summon_Night_3_EN_0.1.5.iso)

- Size: {manifest['output_size_bytes']:,} bytes.
- SHA-256: `{manifest['output_sha256']}`.
- 609 translated dialogue/choice source entries, including both protagonists and all four student branches, plus three existing character labels. This adds 531 entries over 0.1.4.
- 188 reflowed groups, 41 added continuation pages; longest generated page 76 glyphs against the 192-object pool.
- The three dialogue passages in the supplied screenshots are included. The graphical Adnias Harbor banner and setup UI graphics are not.

## Verification

The builder verified source identity, ISO file/extents, unchanged files/resources,
all label references, script compression round-trip, relocated text and generated
page contents. Every generated group was simulated to check display arguments,
balanced stack and return to the original continuation. Branch and menu code,
including excluded Japanese references, is unchanged.

The decoded opening script is 234,726 bytes, below the existing mapped 0x78000
next-start bound. This is a static bound, not proof of runtime allocation or
save/load behavior. The font patch is unchanged from 0.1.4. No emulator state was
changed for this build; **in-game testing remains pending**.

## Japanese retained within the opening/harbor scope

- 12 rows in four long-choice menus exceed the current conservative single-line limit.
- 12 rows in six special-display groups use an unvalidated display helper.
- Two rows containing a musical note need a verified glyph metric.
- Three rows around the player name need measured runtime expansion.
- Three quiz rows remain unresolved in meaning review.

Complete groups/menus are retained without shortening the English drafts.
The rest of the game and untranslated interface assets remain Japanese.

Use this ISO for testing. Start from the title screen or a normal game save;
an emulator save state may retain script memory from the previous ISO.

Evidence: [layout and exclusions](harbor_build_layout_0.1.5.json),
[build manifest](../work/output/0.1.5/manifest.json),
[workspace integrity audit](workspace_audit_0.1.5.json).
'''
    updates[ROOT / 'docs/BUILD_0.1.5.md'] = notes
    changes = ROOT / 'CHANGELOG.md'
    text = changes.read_text(encoding='utf-8')
    entry = '''## 0.1.5 — opening and harbor test ISO, 2026-09-26

- Built 609 reviewed dialogue/choice entries plus three character labels; 531 more
  dialogue entries than 0.1.4. Includes the three supplied dialogue screenshots.
- Reflowed 188 complete groups and added 41 continuation pages without shortening
  text. Simulated every generated group and verified unchanged branch/menu code.
- Retained 32 source rows in Japanese: 29 awaiting display/choice/name support and
  three unresolved quiz rows. Setup graphics and the location banner remain Japanese.
- Verified the complete ISO structure, unchanged contents, labels, script
  compression, text references, page bounds and review provenance. Reused the
  existing 192-object font patch. Runtime/gameplay testing remains pending.
- Preserved all earlier builds; next unused version is 0.1.6.

'''
    updates[changes] = text.replace('# Changelog\n\n', '# Changelog\n\n'+entry, 1)
    return updates, manifest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    updates,manifest=prepare()
    print(json.dumps({'mode':'write' if args.write else 'dry run','version':manifest['version'],
                      'iso_sha256':manifest['output_sha256'],
                      'files':[str(p.relative_to(ROOT)) for p in updates],
                      'build_notes':updates[ROOT/'docs/BUILD_0.1.5.md'],
                      'status':json.loads(updates[ROOT/'docs/translation_status.json'])['latest_candidate']},indent=2))
    if args.write:
        if (ROOT/'docs/BUILD_0.1.5.md').exists():
            raise ValueError('Build notes already exist')
        for p,text in updates.items():p.write_text(text,encoding='utf-8')


if __name__=='__main__':main()
