"""Promote the inspected setup candidate unchanged and record bounded QA; preview first."""
import argparse,json,shutil
from datetime import datetime,timezone
from sn3_archive import ROOT
from build_candidate import hash_file


def prepare():
    candidate=ROOT/'work/scratch/setup_candidate_0.1.6_r2'
    manifest=json.loads((candidate/'manifest.json').read_text(encoding='utf-8'))
    assert manifest['output_sha256']=='8f1e67c6d01d8c263a06f4ad45dcb85b9bd4d6031537e0060080f4032b4263ae'
    assert hash_file(candidate/manifest['output_iso'])==manifest['output_sha256']
    assert hash_file(candidate/'EBOOT.elf')==manifest['executable_patch']['patched_elf_sha256']
    captures=[]
    names=['aty_select','machine','yokai','spirit','beast','name_aty',
           'r2_rexx_select','r2_name_rexx','r2_confirm_rexx','r2_empty','r2_auto_name','r2_opening']
    first=json.loads((ROOT/'work/scratch/setup_candidate_0.1.6/manifest.json').read_text(encoding='utf-8'))
    # The first runtime pass tested precisely the same native graphics as release.
    assert first['setup_ui']==manifest['setup_ui']
    for name in names:
        p=ROOT/'work/ui/setup_runtime_0.1.6'/f'{name}.png'
        metadata=json.loads(p.with_suffix('.json').read_text(encoding='utf-8'))
        assert hash_file(p)==metadata['png_sha256']
        captures.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=metadata['png_sha256'],
                             iso_sha256=manifest['output_sha256'] if name.startswith('r2_') else first['output_sha256']))
    qa=dict(version='0.1.6',tested_on='2026-09-26',emulator='PPSSPP 1.20.4 software rendering',
            candidate_sha256=manifest['output_sha256'],captures=captures,
            passed=['Both protagonist selection graphics', 'All four complete affinity descriptions',
                    'English name-entry labels and default Rexx/Aty names','English keyboard selected on entry',
                    'Name confirmation and Yes/No', 'Delete and empty-name validation',
                    'Auto-Name restores Rexx', 'Confirming the name reaches translated opening dialogue'],
            first_pass_scope='Aty and four affinities were inspected in the first candidate; graphics are byte-identical in release.',
            final_pass_scope='Fresh boot of final ISO: Rexx selection, English keyboard, confirmation punctuation, empty-name message, Auto-Name, opening line.',
            limitations=['Options/battle/status/inventory/save UI and the harbor banner are not included in this setup fix.',
                         'Summon-creature name screen variants were statically repacked but not played through.',
                         'No full-game, long-name, save/load, audio or real-hardware acceptance.'],
            user_emulator_untouched=True)
    manifest['runtime_validation']=qa
    manifest['static_validation'].update(runtime_verified=True,visual_verified=True,
                                        runtime_scope='Bounded setup QA only; see runtime_validation')
    manifest['setup_ui_runtime_verified']=True
    manifest['inputs_sha256']['tools/release_setup.py']=hash_file(ROOT/'tools/release_setup.py')
    status_path=ROOT/'docs/translation_status.json'
    status=json.loads(status_path.read_text(encoding='utf-8'))
    assert status['latest_build']=='0.1.5'
    status['prior_candidate_0_1_5']=status['latest_candidate']
    status.update(latest_build='0.1.6',next_build_version='0.1.7',
                  latest_build_kind='Setup UI fix with bounded in-game QA; 609 prior dialogue entries retained',
                  coverage_counts_baseline='Dialogue totals unchanged from 0.1.5. New setup QA is separately scoped in BUILD_0.1.6.')
    status['latest_candidate']=dict(acceptance='setup_runtime_verified_partial_translation',
        candidate_sha256=manifest['output_sha256'],qa_report='docs/BUILD_0.1.6.md',
        inserted_dialogue_rows=609,inserted_labels=3,modified_native_sprites=68,naming_literals=7,
        compiled_reflow_groups=188,additional_dialogue_pages=41,decoded_script_bytes=234726,
        runtime_verified=True,visual_verified=True,scope_limit=qa['final_pass_scope'],
        retained_japanese_rows_in_harbor_scope=32)
    status['interface_work'].pop('setup_ui_inserted',None)
    status['interface_work'].update(setup_ui_inserted_scope='Character selection, affinities and name entry',
        native_sprite_records_modified=68,native_packs_modified=5,relocated_naming_literals=7,
        setup_runtime_report='work/output/0.1.6/setup_runtime_validation.json',
        next_step='Translate remaining options and interface assets; verify summon-name variants and remaining input states.')
    status['runtime']['latest_build_runtime_verified']=True
    status['runtime']['latest_build_runtime_scope']='Setup flow and opening line only; full dialogue/gameplay not accepted.'
    notes=f'''# Build 0.1.6 — setup screen fix

[Download ISO](../work/output/0.1.6/{manifest['output_iso']})

- SHA-256: `{manifest['output_sha256']}`
- Size: {manifest['output_size_bytes']:,} bytes.
- Adds 68 modified native graphics across five packs: protagonist selection,
  all four affinity headings/descriptions, and normal/highlighted name-entry labels.
- Relocates seven naming literals; Rexx/Aty, confirmation, Yes/No and empty-name
  validation are English. The keyboard opens on ABC/123. Other character tabs remain available.
- Retains the same 609 dialogue/choice entries, three character labels and font
  code from 0.1.5; the decoded dialogue resource is byte-identical.

## Validation

Source and output hashes, all 23 indexes, 32 unchanged ISO files, 3,558 unchanged
bank resources, 2,312 character references, dialogue layout and five native UI
packs passed static verification. Re-encoded textures preserve native palettes,
geometry and all pixels outside the changed regions. ELF literals are relocated;
the original font hook bytes and relocation records are preserved.

PPSSPP 1.20.4 screenshots were inspected for both protagonists and every affinity.
A fresh final-ISO boot verified Rexx selection, English-first keyboard, confirmation
punctuation, blank-name rejection, Delete, Auto-Name and entry into the translated
opening. The Aty/affinity pass used the first candidate's identical graphic packs.
The user's running PPSSPP and saves were not changed.

[Runtime evidence](../work/output/0.1.6/setup_runtime_validation.json) records
each screenshot and the exact ISO used. [Build manifest](../work/output/0.1.6/manifest.json)
records content and source identities.

## Remaining scope

This fixes the reported setup screens. Options, battle/status/inventory/save UI,
the graphical harbor banner and most of the game remain Japanese. Summon-name
variants are statically patched but not yet played through. Full-game, long-name,
audio, save/load and PSP hardware acceptance remain open.

Open this ISO from the title screen or a normal game save. Do not resume an old
emulator save state, which may retain the previous ISO's loaded graphics and code.
'''
    readme=(ROOT/'README.md').read_text(encoding='utf-8')
    start,end=readme.index('Status: **test ISO'),readme.index('Story decompression')
    readme=readme[:start]+'''Status: **test ISO 0.1.6 is built and its setup flow tested in PPSSPP**.
It fixes character selection, all four affinities, name-entry graphics and naming
messages, and opens the English keyboard first. It retains 609 translated
opening/harbor dialogue entries and three character labels from 0.1.5.
See [build notes](docs/BUILD_0.1.6.md) and the
[ISO](work/output/0.1.6/Summon_Night_3_EN_0.1.6.iso).
The next unused version is **0.1.7**. Full gameplay remains unverified; 32 entries
in the 641-row opening/harbor scope and most other game text remain Japanese.

'''+readme[end:]
    readme=readme.replace('the five supplied screens and related variants, independently reviewed; not yet inserted.',
                          'reviewed setup/options catalog; character selection and name entry inserted in 0.1.6.')
    readme=readme.replace('UI translation is not yet present in the playable image.',
                          'Character selection and name entry are present in 0.1.6; other interface work remains pending.')
    readme=readme.replace('docs/workspace_audit_0.1.5.json','docs/workspace_audit_0.1.6.json')
    log=(ROOT/'CHANGELOG.md').read_text(encoding='utf-8')
    entry='''## 0.1.6 — setup screen fix, 2026-09-26

- Inserted native English graphics for both protagonists, all four summon
  affinities and name entry, including normal and highlighted button labels.
- Added English default names, confirmation and empty-name messages; made
  ABC/123 the initial keyboard. Fixed unsupported quote glyphs found in testing.
- Preserved all 609 dialogue/choice entries and the existing font code.
- Verified native texture round trips, unchanged contents and ISO structure.
  Inspected PPSSPP setup screenshots and tested Delete, Auto-Name, confirmation
  and transition to the translated opening. User emulator state was untouched.
- Other interface categories, the harbor banner and most dialogue remain
  Japanese. Full gameplay acceptance remains open; next version is 0.1.7.

'''
    log=log.replace('# Changelog\n\n','# Changelog\n\n'+entry,1)
    return candidate,manifest,qa,{status_path:json.dumps(status,ensure_ascii=False,indent=2)+'\n',
        ROOT/'docs/BUILD_0.1.6.md':notes,ROOT/'README.md':readme,ROOT/'CHANGELOG.md':log}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');args=p.parse_args()
    src,m,qa,updates=prepare();dest=ROOT/'work/output/0.1.6'
    assert not dest.exists()
    print(json.dumps(dict(mode='write' if args.write else 'dry run',destination=str(dest),
                         iso_sha256=m['output_sha256'],runtime_checks=qa['passed'],
                         updated_documents=[str(p.relative_to(ROOT)) for p in updates],
                         build_notes=updates[ROOT/'docs/BUILD_0.1.6.md']),indent=2),flush=True)
    if not args.write:return
    dest.mkdir()
    for name in [m['output_iso'],'EBOOT.elf']:shutil.copyfile(src/name,dest/name)
    assert hash_file(dest/m['output_iso'])==m['output_sha256']
    (dest/'manifest.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
    (dest/'setup_runtime_validation.json').write_text(json.dumps(qa,indent=2)+'\n',encoding='utf-8')
    for p,text in updates.items():p.write_text(text,encoding='utf-8')


if __name__=='__main__':main()
