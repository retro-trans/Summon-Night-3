"""Operate only the isolated menu-crash reproduction session; preview first."""
import argparse,json,time
from sn3_archive import ROOT
from chapter_qa_runtime import validate_session
from setup_qa import request
import capture_framebuffer

def main():
 p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');p.add_argument('--press');p.add_argument('--capture');p.add_argument('--status',action='store_true');a=p.parse_args()
 session,game=validate_session(ROOT/'work/scratch/setup_qa_crash017/session.json',ROOT/'work/output/0.1.16/Summon_Night_3_EN_0.1.16.iso')
 print(json.dumps(dict(mode='execute' if a.execute else 'dry-run',session=session,press=a.press,capture=a.capture,cpu=request('cpu.status')),indent=2),flush=True)
 if not a.execute:return
 if a.press:
  for b in a.press.split(','):
   assert b in ('start','circle','cross','up','down','left','right','select','triangle','square')
   request('input.buttons.press',button=b,duration=5);time.sleep(1)
 if a.capture:
  capture_framebuffer.request=request;png,meta=capture_framebuffer.capture(hold=False)
  folder=ROOT/'work/ui/crash_0.1.17';folder.mkdir(exist_ok=True)
  out=folder/a.capture;assert out.parent==folder and out.suffix=='.png' and not out.exists()
  out.write_bytes(png);out.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
  print(str(out))
 if a.status:print(json.dumps(request('cpu.getAllRegs')))
if __name__=='__main__':main()
