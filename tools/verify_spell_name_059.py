"""Verify the compact label in the finished ISO; preview before writing evidence."""
import argparse,json,struct
from datetime import datetime,timezone
from sn3_archive import ROOT,GameSource,parse_index,child
from spell_name_059 import prepare_tables,label
from build_candidate import hash_file

def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    build=ROOT/'work/output/0.1.59';ui=ROOT/'work/ui/spell_name_0.1.59'
    m=json.loads((build/'manifest.json').read_text());iso=build/m['output_iso']
    assert hash_file(iso)==m['output_sha256']
    with GameSource(ROOT/'work/output/0.1.58/Summon_Night_3_EN_0.1.58.iso') as old,GameSource(iso) as new:
        expected,_,r=prepare_tables(old)
        static=new.resource('02.DAT',3)
        assert static[:len(expected[3])]==expected[3] and not any(static[len(expected[3]):])
        master=new.resource('00.DAT',44)
        assert child(master,parse_index(master,len(master)),7)==static
        table=child(static,parse_index(static,len(static)),13)
        assert label(table,9356)=='Crush! L.Gen.Sword'
    assert (build/'EBOOT.elf').read_bytes()==(ROOT/'work/output/0.1.58/EBOOT.elf').read_bytes()
    stability=json.loads((build/'stability-report.json').read_text())
    assert stability['passed'] and len(stability['checks'])==13 and stability['iso_sha256']==m['output_sha256']
    patch=json.loads((ROOT/'work/output/spell-name-test-v0.1.59/VALIDATION.json').read_text())
    assert patch['patches'][0]['roundtrip_verified'] and patch['patches'][0]['target_sha256']==m['output_sha256']
    r.update(iso_sha256=m['output_sha256'],created_at_utc=datetime.now(timezone.utc).isoformat(),
        actual_iso_label_verified=True,executable_unchanged=True,regression_groups=13,
        retro_trans_roundtrip=True,runtime_verified=False,
        limits=['Exact spell-list runtime view has not been verified; fit uses the reported geometry and inherited font scale.'],
        verification_inputs_sha256={str(path.relative_to(ROOT)).replace('\\','/'):hash_file(path) for path in [
            ROOT/'tools/verify_spell_name_059.py',ROOT/'tools/verify_stability_057_final.py',
            ROOT/'tools/verify_guards_057.py',ROOT/'tools/package_test_spell_name_059.py']})
    sample={k:v for k,v in r.items() if k!='spell_name_audit'}
    sample['audited_spell_names']=len(r['spell_name_audit'])
    print(json.dumps(dict(mode='write' if a.write else 'preview',report=sample),indent=2))
    if a.write:
        (ui/'validation.json').write_text(json.dumps(r,indent=2)+'\n')
        (ui/'stability-report.json').write_bytes((build/'stability-report.json').read_bytes())

if __name__=='__main__':main()
