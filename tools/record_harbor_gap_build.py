"""Record verified 0.1.10 evidence and advance workspace status; preview first."""
import argparse,copy,json
from pathlib import Path
from datetime import datetime,timezone
from build_candidate import ROOT,hash_file

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
    runtime=ROOT/'work/ui/harbor_gaps_0.1.10/runtime'
    manifest=read('work/output/0.1.10/manifest.json');status=read('docs/translation_status.json')
    intro=read('work/ui/harbor_gaps_0.1.10/runtime/introduction.json')['state']['lines']
    assert [r['rendered'] for r in intro]==['Ah, yes.','My name is Rexx.']
    menu=read('work/ui/harbor_gaps_0.1.10/runtime/choice.json')['state']['lines']
    assert [r['text'] for r in menu]==['Surely...',"\u3000Maybe he's mischievous?","\u3000Seems polite. It'll be fine."]
    evidence={p.relative_to(ROOT).as_posix():hash_file(p) for p in runtime.iterdir() if p.is_file()}
    qa=dict(version='0.1.10',checked_at_utc=datetime.now(timezone.utc).isoformat(),iso_sha256=manifest['output_sha256'],
        emulator='Isolated PPSSPP 1.20.4, software renderer, fresh boot, natural input; no user saves or emulator state used.',
        decoded_live_script_sha256=manifest['script_changes'][0]['decoded_sha256'],
        checks=['Fresh boot, naming and opening transitions','Nup-route centered choices preserve complete translated text and fit native bounds',
                'Player-name substitution renders Ah, yes. / My name is Rexx. on two lines',
                'Introduction returns normally to Salome dialogue','Salome generated nameplate displays without Japanese remnants or background patch',
                'All five quantized native English name sprites visually inspected'],
        tested_player_name='Rexx',max_name_bound=dict(glyphs=6,maximum_expanded_pixels=197,available_pixels=208,
            evidence='Original executable protagonist-name branch loads six at 0x129cac/0x129cb4/0x129cc8, stores at context+4200 at 0x129cd0, and validates at 0x129d30. Conservative 16px per runtime name glyph.'),
        limits=['Belfrau/Alieze/Will routes and alternate copies statically checked, not replayed in this run.',
                'The longest girl-route choice is 251px including indentation, below the measured native menu space; the boy-route live maximum checked is 217px.',
                'Maximum six-glyph player-name expansion is statically bounded; runtime test used default Rexx.',
                'Audio retained byte-for-byte; playback and full-game routes not retested. Translation remains partial.'],
        evidence_sha256=evidence)
    manifest['runtime_validation']=dict(report='work/output/0.1.10/harbor_gap_runtime_validation.json',
        fresh_boot=True,runtime_verified=True,visual_verified=True,scope=qa['checks'],limits=qa['limits'])
    manifest['static_validation'].update(runtime_verified=True,visual_verified=True)
    manifest['script_changes'][0]['runtime_allocation_verified']=True
    manifest['script_changes'][0]['runtime_allocation_scope']='Complete live opening script hash matches; natural startup through Nup/Salome introduction only.'
    manifest['inputs_sha256']['tools/harbor_gap_qa.py']=hash_file(ROOT/'tools/harbor_gap_qa.py')
    manifest['known_limits'].append('0.1.10 extends opening coverage to624/641 rows;17 remain Japanese. New nameplate assets cover five named characters; most other nameplates remain Japanese.')
    status['prior_candidate_0_1_9']=copy.deepcopy(status['latest_candidate'])
    status.update(latest_build='0.1.10',next_build_version='0.1.11',latest_build_kind='Missing harbor choices, player-name introduction and native English nameplates',
        coverage_counts_baseline='0.1.10 adds15 source fragments to609 prior entries, plus5 graphical names in20 native layers across10 packs. Historical runtime counts remain scoped to their evidence.')
    status['script_pools']['inserted']=624;status['script_pools']['compiled_reflow_groups']=189
    status['latest_candidate'].update(acceptance='harbor_gaps_verified_partial_translation',candidate_sha256=manifest['output_sha256'],qa_report='docs/BUILD_0.1.10.md',
        inserted_dialogue_rows=624,modified_native_sprites=119,compiled_reflow_groups=189,decoded_script_bytes=235336,
        scope_limit='Fresh boot and natural Nup-route harbor choices, Salome nameplate, dynamic Rexx introduction and continuation. Other branches statically checked.',
        retained_japanese_rows_in_harbor_scope=17,imagegen_assets=37,imagegen_sprite_instances=55,generated_character_names=5)
    status['opening_harbor'].update(total_rows_inserted=624,build='0.1.10',build_selection='work/translation/en/opening_harbor_0.1.10.targets.json',
        retained_japanese_rows=17,latest_added_rows=15,layout_or_runtime_verified=True,
        runtime_scope='Nup-route choices and player-name introduction, with static checks across other menu variants.',
        next_step='Translate remaining special display helpers and musical note after profiling; resolve quiz rows240-242. Other dialogue, location banners and nameplates remain pending.')
    status['harbor_nameplates']=dict(names=['Nup','Belfrau','Alieze','Will','Salome'],packs=10,layers=20,report='work/ui/nameplates_0.1.10/import_report.json')
    buildnotes='''# Build 0.1.10 — harbor translation gaps

[ISO](../work/output/0.1.10/Summon_Night_3_EN_0.1.10.iso) · [Introduction](../work/ui/harbor_gaps_0.1.10/runtime/introduction.png) · [Salome nameplate](../work/ui/harbor_gaps_0.1.10/runtime/salome.png)

Translated the missing centered harbor choices for both protagonists and both
pupil genders (12 source rows), plus the three-part player introduction.
The introduction now displays “Ah, yes. / My name is [player name].” on two lines.
The original player-name token, display helper, arguments and continuation are
preserved. The old source strings remain intact; English strings are relocated.

The choice shown in the report is “Surely...” followed by “Probably a refined
young lady.” and “Let's not overthink it.” The longest choice measures251 pixels
including indentation, within the approximately280-pixel native centered menu.
This wider menu has a separate limit from the narrower portrait speech window.

Replaced the native graphical names for Belfrau, Salome, Nup, Alieze and Will.
Built-in imagegen supplied matching cream/plum transparent lettering from original
sprite references. Generated words were cropped, uniformly downsampled and mapped
to the game's existing palettes; no rectangle was painted over the nameplate.
Both the lettering and its silhouette layer are replaced in all10 matching packs
(20 sprite layers). Portraits, other pack children and the ornamental frame remain
unchanged. [Exact prompts and assets](../work/ui/nameplates_0.1.10/generation.json).

## Checks

- Independent meaning review covered100 surrounding rows for the15 gaps.
- Verified source hashes, 624 logical targets, all existing reflowed strings,
  preserved runtime token, two-line execution and unchanged helper arguments.
- Compressed script and portrait packs round-trip. The main script is235,336 bytes,
  below its mapped491,520-byte region. Maximum six-glyph name expansion is bounded
  at197 pixels in a208-pixel speech line; default Rexx was tested live.
- All34 unrelated ISO files, including executable/audio, are byte-identical to
  0.1.9. Checked all23 bank indexes and4,404 untouched resources in changed banks.
- Fresh-boot PPSSPP reached the harbor naturally. Checked the boy-route choices,
  the player's substituted name, Salome's nameplate and normal continuation.
  Complete live script bytes match the build. All five native name sprites were
  visually inspected after palette conversion.

The girl-route251-pixel choice and alternate character packs have static checks;
those routes were not replayed here. Audio playback and the full game were not
retested. This is still a partial translation: 624 of641 source rows in this
opening/harbor scope are included; 17 remain Japanese, as does most later text.

Restart PPSSPP's game with the new ISO. Old emulator save states can restore the
old script and textures; ordinary in-game saves are preferable after a fresh boot.

SHA-256: `774c16772b035d3023665b005c6ca1b45b567aa8094ffbfe27e510581e1928ad`.
Next unused version: **0.1.11**.
'''
    # Keep number/unit spacing natural in the human-readable report.
    import re
    buildnotes=re.sub(r'(?<=[a-zA-Z])(?=\d)|(?<=\d)(?=[a-zA-Z])',' ',buildnotes)
    # Hash strings must remain exact; the substitutions above only target prose.
    buildnotes=buildnotes[:buildnotes.index('SHA-256:')]+f"SHA-256: `{manifest['output_sha256']}`.\nNext unused version: **0.1.11**.\n"
    changelog=(ROOT/'CHANGELOG.md').read_text(encoding='utf-8')
    entry='''## 0.1.10 — harbor gaps and character nameplates, 2026-09-26

- Added 12 harbor choice rows across protagonist/pupil branches and the three-part
  player-name introduction; retained the runtime name and complete meaning.
- Generated five native English nameplates (Belfrau, Salome, Nup, Alieze, Will),
  replacing both name and silhouette layers in all 10 matching portrait packs.
- Checked fresh boot, harbor choices, name substitution, Salome's nameplate and
  normal continuation in isolated PPSSPP. Other routes remain statically checked.
- Preserved 34 unrelated ISO files and 4,404 other resources in changed banks,
  including prior audio, chapter cards and the 0.1.9 backlog fix.
- Opening/harbor coverage: 624/641 source rows. Next version: 0.1.11.

'''
    assert '## 0.1.10 ' not in changelog;changelog=changelog.replace('# Changelog\n\n','# Changelog\n\n'+entry,1)
    readme=(ROOT/'README.md').read_text(encoding='utf-8');start=readme.index('Status: **');end=readme.index('\nStory decompression',start)
    readme=readme[:start]+'''Status: **test ISO 0.1.10 translates the missing harbor choices, player-name
introduction, and five character nameplates**. It retains the backlog spacing fix,
chapter-title artwork and prior setup/interface translations.
Fresh-boot PPSSPP checks cover the boy-route choices, player-name substitution,
Salome's nameplate and normal continuation. Other character branches have static
checks. See [build notes](docs/BUILD_0.1.10.md) and the
[ISO](work/output/0.1.10/Summon_Night_3_EN_0.1.10.iso).
The next unused version is **0.1.11**. The opening/harbor scope now includes
624 of 641 source rows; 17 remain Japanese. Most later game text remains untranslated.
''' +readme[end:]
    readme=readme.replace('docs/workspace_audit_0.1.9.json','docs/workspace_audit_0.1.10.json')
    writes={'work/output/0.1.10/manifest.json':json.dumps(manifest,indent=2)+'\n',
            'work/output/0.1.10/harbor_gap_runtime_validation.json':json.dumps(qa,indent=2)+'\n',
            'docs/translation_status.json':json.dumps(status,indent=2)+'\n','docs/BUILD_0.1.10.md':buildnotes,
            'CHANGELOG.md':changelog,'README.md':readme}
    print(json.dumps(dict(mode='write' if a.write else 'dry run',files=list(writes),checks=qa['checks'],limits=qa['limits'],latest_candidate=status['latest_candidate']),indent=2))
    if a.write:
        for path,text in writes.items():(ROOT/path).write_text(text,encoding='utf-8')

if __name__=='__main__':main()
