"""Preview runtime evidence and cleanup of the isolated test process."""
import argparse,json,hashlib
from sn3_archive import ROOT
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 base=ROOT/'work/output/0.1.62';m=json.loads((base/'manifest.json').read_text());art=ROOT/'work/ui/report_0.1.62/runtime';screens=[]
 for name in ['loaded','mujina_list','mujina_spells']:
  b=(art/(name+'.png')).read_bytes();data=json.loads((art/(name+'.json')).read_text());h=hashlib.sha256(b).hexdigest();assert h==data['png_sha256']
  assert data['cpu']['pc']==0x08a17b9c;screens.append(dict(screen=name,path=str((art/(name+'.png')).relative_to(ROOT)),sha256=h))
 log=(ROOT/'work/scratch/report062-runtime/runtime.log').read_text(encoding='utf8',errors='replace');assert '0.1.62.iso' in log and 'Bad memory access' not in log
 session=json.loads((ROOT/'work/scratch/report062-runtime/session.json').read_text(encoding='utf-8-sig'));assert session['fresh_boot'] and not session['save_state_used']
 evidence=dict(version='0.1.62',iso_sha256=m['output_sha256'],ppsspp='1.20.4',fresh_boot=True,save_state_used=False,normal_save='Copied Chapter 15 battle suspend save',screens=screens,observed='Mujina name, lore and all three spell names display fully. No memory fault in this test.',exact_awakening_screen_verified=False,exact_create_summons_set_screen_verified=False)
 print(json.dumps(dict(mode='write' if a.write else 'preview',destination=str(base/'runtime-validation.json'),evidence=evidence),indent=2),flush=True)
 if a.write:(base/'runtime-validation.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()
