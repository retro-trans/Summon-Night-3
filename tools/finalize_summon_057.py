"""Preview or save the final local summon-screen verification record."""
import argparse, hashlib, json, re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4*1024*1024), b''): h.update(block)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser(); p.add_argument('--write',action='store_true'); a=p.parse_args()
    build=ROOT/'work/output/0.1.57'; ui=ROOT/'work/ui/summon_0.1.57'
    m=json.loads((build/'manifest.json').read_text())
    def verify(item):
        name,expected=item
        assert digest(ROOT/name)==expected, name
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(verify,m['inputs_sha256'].items()))
    stability=json.loads((build/'stability-report.json').read_text())
    validation=json.loads((ROOT/'work/output/summon-test-v0.1.57/VALIDATION.json').read_text())
    session=json.loads((ROOT/'work/scratch/summon057-runtime/session.json').read_text('utf-8-sig'))
    capture=json.loads((ui/'runtime/craft_corrected.json').read_text())
    assert stability['passed'] and len(stability['checks'])==13
    assert stability['iso_sha256']==m['output_sha256']==validation['patches'][0]['target_sha256']
    assert validation['patches'][0]['roundtrip_verified']
    assert session['fresh_boot'] and not session['save_state_used']
    assert Path(session['iso']).resolve()==build/'Summon_Night_3_EN_0.1.57.iso'
    assert digest(ui/'runtime/craft_corrected.png')==capture['png_sha256']
    log=(ROOT/'work/scratch/summon057-runtime/runtime.log').read_text(errors='replace')
    assert '0.1.57.iso' in log
    faults=re.findall(r'.*(?:Bad memory access|Invalid Memory Access|\[MEMMAP\]).*',log)
    assert not faults, faults
    report=dict(version='0.1.57',created_at_utc=datetime.now(timezone.utc).isoformat(),
        iso_sha256=m['output_sha256'],build_inputs_reverified=len(m['inputs_sha256']),
        regression_groups=13,retro_trans_roundtrip=True,runtime_session=session,
        screenshot='runtime/craft_corrected.png',screenshot_sha256=capture['png_sha256'],
        observed=['Create Summons heading translated','Affinity label translated',
                  'Complete Cast and Dismiss hints with separate button icons'],
        bad_memory_faults=faults,
        limits=['Gravis on the reported page; exact Injecks row not exercised','Not a full playthrough'],
        verification_inputs_sha256={n:digest(ROOT/n) for n in [
            'tools/verify_guards_057.py','tools/verify_stability_057_final.py','tools/finalize_summon_057.py']})
    print(json.dumps(dict(mode='write' if a.write else 'preview',report=report),indent=2),flush=True)
    if a.write:
        (ui/'runtime-validation.json').write_text(json.dumps(report,indent=2)+'\n')
        (ui/'stability-report.json').write_bytes((build/'stability-report.json').read_bytes())

if __name__=='__main__': main()
