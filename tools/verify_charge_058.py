"""Verify the finished Charge label and record the limits of runtime coverage."""
import argparse,json,struct,hashlib
from datetime import datetime,timezone
from sn3_archive import ROOT,GameSource,parse_index,child
from charge_058 import prepare_tables
from build_candidate import hash_file

def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    build=ROOT/'work/output/0.1.58';ui=ROOT/'work/ui/charge_0.1.58'
    m=json.loads((build/'manifest.json').read_text());iso=build/m['output_iso']
    assert hash_file(iso)==m['output_sha256']
    with GameSource(ROOT/'work/output/0.1.57/Summon_Night_3_EN_0.1.57.iso') as old,GameSource(iso) as new:
        expected,_,report=prepare_tables(old)
        static=new.resource('02.DAT',3);assert static[:len(expected[3])]==expected[3] and not any(static[len(expected[3]):])
        master=new.resource('00.DAT',44);assert child(master,parse_index(master,len(master)),7)==static
        table=child(static,parse_index(static,len(static)),28);ptr=struct.unpack_from('<I',table,2436)[0]
        assert table[ptr:ptr+14]=='Ｃｈａｒｇｅ'.encode('cp932')+b'\0\0'
    assert (build/'EBOOT.elf').read_bytes()==(ROOT/'work/output/0.1.57/EBOOT.elf').read_bytes()
    stability=json.loads((build/'stability-report.json').read_text())
    assert stability['passed'] and len(stability['checks'])==13 and stability['iso_sha256']==m['output_sha256']
    patch=json.loads((ROOT/'work/output/charge-test-v0.1.58/VALIDATION.json').read_text())
    assert patch['patches'][0]['roundtrip_verified'] and patch['patches'][0]['target_sha256']==m['output_sha256']
    session=json.loads((ROOT/'work/scratch/charge058-runtime/session.json').read_text('utf-8-sig'))
    assert session['fresh_boot'] and not session['save_state_used'] and '0.1.58.iso' in session['iso']
    log=(ROOT/'work/scratch/charge058-runtime/runtime.log').read_text(errors='replace')
    assert '0.1.58.iso' in log and not any(t in log for t in ['Bad memory access','Invalid Memory Access','[MEMMAP]'])
    capture=json.loads((ui/'runtime/special_menu.json').read_text())
    assert hash_file(ui/'runtime/special_menu.png')==capture['png_sha256']
    report.update(iso_sha256=m['output_sha256'],created_at_utc=datetime.now(timezone.utc).isoformat(),
        actual_iso_label_verified=True,executable_unchanged=True,regression_groups=13,
        retro_trans_roundtrip=True,runtime_session=session,
        runtime_coverage='Fresh boot, normal save load, Unit List, protagonist Special menu; Charge unavailable on that unit.',
        runtime_banner_verified=False,no_bad_memory_faults_logged=True,
        verification_inputs_sha256={str(p.relative_to(ROOT)).replace('\\','/'):hash_file(p) for p in [
            ROOT/'tools/verify_charge_058.py',ROOT/'tools/verify_stability_057_final.py',
            ROOT/'tools/verify_guards_057.py',ROOT/'tools/charge_runtime_058.py',
            ROOT/'tools/launch_charge_058.ps1',ROOT/'tools/package_test_charge_058.py']})
    print(json.dumps(dict(mode='write' if a.write else 'preview',report=report),indent=2,ensure_ascii=False))
    if a.write:
        (ui/'validation.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
        (ui/'stability-report.json').write_bytes((build/'stability-report.json').read_bytes())

if __name__=='__main__':main()
