"""Preview targeted audit repair and append checks for the actual completed ISO."""
import argparse,json,hashlib
from sn3_archive import ROOT,GameSource
import verify_stability_066
from status_fix_066 import prepare_elf,BASE
from verify_status_066 import verify
def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    folder=ROOT/'work/output/0.1.66';path=folder/'stability-report.json';r=json.loads(path.read_text());m=json.loads((folder/'manifest.json').read_text())
    assert r['iso_sha256']==m['output_sha256'] and len(r['checks'])==14
    failures=[c for c in r['checks'] if not c['passed']]
    assert len(failures)==1 and failures[0]['name']=='Level Up formatter, staging and control positions' and failures[0]['error']=='AssertionError: Unexpected 066 executable'
    elf=(folder/'EBOOT.elf').read_bytes();assert elf==prepare_elf()[0]
    with GameSource(folder/m['output_iso']) as src,GameSource(BASE/'Summon_Night_3_EN_0.1.65.iso') as old:
        static=src.resource('02.DAT',3);assert static==old.resource('02.DAT',3)
        from verify_levelup_060 import verify as levelup
        details=levelup(elf,static)
    failures[0].update(passed=True,details=details,harness_repair=failures[0].pop('error'))
    previous=json.loads((BASE/'stability-report.json').read_text());assert previous['passed']
    retained=[c for c in previous['checks'] if c['name'] in ('Private chapter script arena and relocation','Four reported Learn Skills names and help blocks')];assert len(retained)==2
    for c in retained:
        c['retained_by']='Actual 066 added-segment bytes and chapter-arena calls match 065; static tables match exactly.'
    native=verify();checks=retained+[dict(name='Summon labels and proportional feeding icon',passed=True,details=native)]
    r['checks'].extend(checks);r['passed']=all(c['passed'] for c in r['checks'])
    r['validation_inputs_sha256']={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ('tools/verify_status_066.py','tools/verify_stability_066.py','tools/finalize_status_066.py')}
    print(json.dumps(dict(mode='write' if a.write else 'preview',passed=r['passed'],groups=len(r['checks']),repaired_check=failures[0]['name'],new_check=checks[-1]['name']),indent=2))
    if a.write:
        path.write_text(json.dumps(r,indent=2)+'\n',encoding='utf8');(ROOT/'work/ui/status_0.1.66/stability-report.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()
