"""Capture the isolated Berserk crash replay using the debugger/controller API."""
import argparse,json,time
from sn3_archive import ROOT
from options_runtime_078 import client

def main():
 p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('buttons',nargs='*');p.add_argument('--case',default='berserk083-recovered');p.add_argument('--wait',type=float,default=3);a=p.parse_args()
 assert a.case.startswith('berserk083-') and a.name.replace('_','').isalnum() and 0<=a.wait<=30
 names=['circle','cross','up','down','left','right','start','select','ltrigger','rtrigger','triangle','square'];assert set(a.buttons)<=set(names)
 s=json.loads((ROOT/'work/scratch'/a.case/'session.json').read_text('utf-8-sig'));assert s['port']==19447
 r=client(19447);st=r('cpu.status')
 if st['stepping']:
  assert st['pc'] in [f['address'] for f in r('hle.func.list')['functions'] if f['name']=='zz_sceDisplaySetFrameBuf'];r('cpu.resume')
 else:assert not st['paused'],st
 r('input.buttons.send',buttons={n:False for n in names});time.sleep(.5)
 for n in a.buttons:r('input.buttons.press',button=n,duration=4);time.sleep(1)
 time.sleep(a.wait);st=r('cpu.status');assert not st['paused'],st
 import capture_framebuffer
 capture_framebuffer.request=r;png,report=capture_framebuffer.capture(hold=True);report.update(session=s,buttons=a.buttons,case=a.case)
 d=ROOT/'work/ui/battle_0.1.83/reviewed'/a.name;d.parent.mkdir(parents=True,exist_ok=True);assert not d.with_suffix('.png').exists()
 d.with_suffix('.png').write_bytes(png);d.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(d.with_suffix('.png'),flush=True)

if __name__=='__main__':main()
