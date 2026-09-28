"""Add native setup translations to the verified 0.1.5 dialogue selection; preview first."""
import argparse
from datetime import datetime,timezone
import json
from build_candidate import *
from setup_elf_patch import patch


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    parser.add_argument('--destination',type=Path,default=ROOT/'work/output/0.1.6')
    args=parser.parse_args();dest=args.destination.resolve()
    assert ROOT in dest.parents and not dest.exists()
    olddir=ROOT/'work/output/0.1.5'
    old=json.loads((olddir/'manifest.json').read_text(encoding='utf-8'))
    uid=ROOT/'work/ui/setup_0.1.6_r2';ui=json.loads((uid/'index.json').read_text(encoding='utf-8'))
    packs={r['number']:(uid/f"pack_{r['number']:05d}.bin").read_bytes() for r in ui['packs']}
    for r in ui['packs']:assert hashlib.sha256(packs[r['number']]).hexdigest()==r['sha256']
    for name,h in ui['inputs_sha256'].items():assert hash_file(ROOT/name)==h
    executable,font_report=build_patch()
    assert executable==(olddir/'EBOOT.elf').read_bytes()
    executable,elf_report=patch(executable)
    font_report['patched_elf_sha256']=elf_report['sha256'];font_report['patched_bytes']=len(executable)
    font_report['setup_literals']=elf_report
    target=ROOT/'work/translation/en/opening_harbor_0.1.5.targets.json'
    with GameSource() as source:
        plans,changes,entries=prepare(source)
        scripts,reports=prepare_scripts(source,target,FONT_PROFILE)
        assert reports[0]['decoded_sha256']==old['script_changes'][0]['decoded_sha256']
        plan02=plan_bank(source,'02.DAT',packs)
        combined=dict(plans[0]['replacements']);combined.update(scripts)
        combined[44]=repack(combined[44],{1:plan02['index_bytes']})
        plans[0]=plan_bank(source,'00.DAT',combined);plans.append(plan02)
        summary=dict(mode='write' if args.write else 'dry run',version='0.1.6',output=str(dest),
                     native_sprites=ui['sprite_count'],native_packs=ui['packs'],naming_literals=elf_report,
                     dialogue_count=len(reports[0]['changes']),dialogue_sha256=reports[0]['decoded_sha256'],
                     banks=[{k:p[k] for k in ('bank','old_size','new_size')} for p in plans])
        print(json.dumps(summary,indent=2),flush=True)
        if not args.write:return
        assert hash_file(ROOT/'work/source/original.iso')==source.manifest['source']['iso_sha256']
        dest.mkdir(parents=True)
        iso=dest/'Summon_Night_3_EN_0.1.6.iso';partial=iso.with_suffix('.iso.partial')
        files={'/PSP_GAME/SYSDIR/EBOOT.BIN':executable}
        write_iso(source,plans,partial,files)
        validation=verify_candidate(partial,source,changes,entries,reports,files,{'02.DAT':packs})
        partial.rename(iso)
        inputs=dict(old['inputs_sha256'])
        for name in list(inputs):inputs[name]=hash_file(ROOT/name)
        for name in ['tools/build_setup.py','tools/setup_elf_patch.py','tools/setup_ui_patch.py',
                     'work/ui/setup_0.1.6_r2/index.json','work/translation/en/setup_ui.targets.json',
                     'work/translation/en/setup_ui.compact_review.json']:
            inputs[name]=hash_file(ROOT/name)
        manifest=dict(schema_version=1,version='0.1.6',kind='partial_technical_candidate',
                      built_at_utc=datetime.now(timezone.utc).isoformat(),source_iso_sha256=old['source_iso_sha256'],
                      output_iso=iso.name,output_size_bytes=iso.stat().st_size,output_sha256=hash_file(iso),
                      changes=changes,script_changes=reports,static_validation=validation,executable_patch=font_report,
                      inputs_sha256=inputs,setup_ui=ui,known_limits=[
                          'Setup graphics and naming prompts plus the previous 609 dialogue entries; not a complete game translation.',
                          'Japanese input characters remain available in the naming keyboard.',
                          'Other interface screens and harbor location graphic remain untranslated.',
                          'Full gameplay and hardware acceptance are not claimed.'])
        (dest/'EBOOT.elf').write_bytes(executable)
        (dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(built=str(iso),sha256=manifest['output_sha256'],validation=validation),indent=2))


if __name__=='__main__':main()
