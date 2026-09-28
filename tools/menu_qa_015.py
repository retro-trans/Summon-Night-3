"""Isolated menu QA: validate session, preview inputs, capture and check ELF."""
import argparse,base64,hashlib,json,time
from sn3_archive import ROOT
from chapter_qa_runtime import validate_session
from setup_qa import request
import capture_framebuffer
def main():
 p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');p.add_argument('--press');p.add_argument('--capture');p.add_argument('--session',default='work/scratch/setup_qa_0.1.15/session.json');p.add_argument('--candidate',default='work/scratch/menu_candidate_0.1.15/Summon_Night_3_EN_0.1.15.iso');a=p.parse_args()
 candidate=ROOT/a.candidate;session,game=validate_session(ROOT/a.session,candidate)
 print(json.dumps(dict(mode='execute' if a.execute else 'dry-run',session=session,press=a.press,capture=a.capture)),flush=True)
 if not a.execute:return
 if a.press:
  if request('cpu.status')['stepping']:request('cpu.resume')
  for button in a.press.split(','):
   assert button in ('circle','cross','up','down','left','right','start','select','triangle','square')
   request('input.buttons.press',button=button,duration=10);time.sleep(2)
 m=json.loads(candidate.with_name('manifest.json').read_text());elf=candidate.with_name('EBOOT.elf').read_bytes()
 entries=m.get('menu_text',m['battle_elf'])['entries']
 for e in entries:
  expected=elf[e['new_file_offset']:e['new_file_offset']+e['bundle_bytes']]
  actual=base64.b64decode(request('memory.read',address=0x08804000+int(e['new_address'],16),size=len(expected))['base64']);assert actual==expected,e['id']
 if a.capture:
  folder=ROOT/'work/ui/menu_0.1.15/runtime';folder.mkdir(exist_ok=True)
  path=folder/a.capture;assert path.parent==folder and path.suffix=='.png' and not path.exists()
  capture_framebuffer.request=request;png,meta=capture_framebuffer.capture(hold=False);path.write_bytes(png)
  report=dict(session=session,iso_sha256=m['output_sha256'],menu_text_bundles_verified=len(entries),capture=meta,capture_sha256=hashlib.sha256(png).hexdigest())
  path.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
  print(json.dumps(dict(capture=str(path),verified_bundles=report['menu_text_bundles_verified'])))
if __name__=='__main__':main()
