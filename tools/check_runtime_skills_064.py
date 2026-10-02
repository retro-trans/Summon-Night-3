"""Read-only fresh-boot checks, with optional evidence export."""
import argparse,json
from sn3_archive import ROOT
from skills_runtime_064 import request
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 session=json.loads((ROOT/'work/scratch/skills064-runtime/session.json').read_text(encoding='utf-8-sig'))
 assert session['fresh_boot'] and not session['save_state_used']
 assert session['iso'].replace('\\','/')==(ROOT/'work/output/0.1.64/Summon_Night_3_EN_0.1.64.iso').as_posix()
 game=request('game.status');assert game['game']['id']=='NPJH50380'
 cpu=request('cpu.status');display=[f['address'] for f in request('hle.func.list')['functions'] if f['name']=='zz_sceDisplaySetFrameBuf']
 assert cpu['stepping'] and display==[cpu['pc']],('Unexpected emulator stop',cpu)
 log=(ROOT/'work/scratch/skills064-runtime/runtime.log').read_text(encoding='utf8',errors='replace');assert '0.1.64.iso' in log and 'Bad memory access' not in log
 capture=ROOT/'work/ui/skills_0.1.64/runtime/title.png';assert capture.exists()
 r=dict(version='0.1.64',ppsspp='1.20.4',fresh_boot=True,save_state_used=False,title_screen_verified=True,screenshot=capture.relative_to(ROOT).as_posix(),exact_learn_skills_screen_verified=False)
 dest=ROOT/'work/output/0.1.64/runtime-validation.json';print(json.dumps(dict(mode='write' if a.write else 'preview',destination=str(dest),evidence=r),indent=2),flush=True)
 if a.write:dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()
