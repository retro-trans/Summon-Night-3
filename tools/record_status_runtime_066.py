"""Preview then record inspected fresh-boot evidence; exact report remains pending."""
import argparse,json,hashlib
from sn3_archive import ROOT
def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    folder=ROOT/'work/output/0.1.66';ui=ROOT/'work/ui/status_0.1.66';m=json.loads((folder/'manifest.json').read_text());audit=json.loads((folder/'stability-report.json').read_text())
    assert audit['passed'] and len(audit['checks'])==17 and audit['iso_sha256']==m['output_sha256']
    log=(ROOT/'work/scratch/status066-runtime/runtime.log').read_text(encoding='utf8',errors='replace');assert '0.1.66.iso' in log and not any(s in log for s in ('Bad memory access','E[MEMMAP]','Game crashed'))
    evidence=[]
    for name in ('reported.png','native-validation.json','stability-report.json','runtime/boot.png','runtime/boot.json','runtime/battle_menu.png','runtime/battle_menu.json','runtime/menu_ready.png','runtime/menu_ready.json'):
        path=ui/name;evidence.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    report=dict(version='0.1.66',iso_sha256=m['output_sha256'],fresh_boot=True,normal_save=True,save_state_used=False,emulator='PPSSPP 1.20.4',cpu='JIT',graphics='software',ignore_bad_memory_access=False,continue_to_chapter15=True,battle_menu=True,exact_report_screen_verified=False,limitation='Room summon Status and feeding action require a matching normal save; the new labels and SELECT placement are validated by source-bound tables and native execution tests.',evidence=evidence)
    print(json.dumps(dict(mode='write' if a.write else 'preview',report=report),indent=2))
    if a.write:
        for path in (ui/'runtime-validation.json',folder/'runtime-validation.json'):
            assert not path.exists();path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()
