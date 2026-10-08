"""Capture one fresh-save QA state after bounded controller updates."""
import argparse,json,time
from options_runtime_078 import client
from sn3_archive import ROOT

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('name');p.add_argument('buttons',nargs='*');p.add_argument('--case',default='ui081-reviewed');p.add_argument('--delay',type=float,default=.5);a=p.parse_args()
 assert a.case.startswith('ui081-') and a.name.replace('_','').isalnum()
 names=['circle','cross','up','down','left','right','start','select','ltrigger','rtrigger','triangle','square']
 assert set(a.buttons)<=set(names)
 session=json.loads((ROOT/'work/scratch'/a.case/'session.json').read_text('utf-8-sig'));assert session['fresh_boot'] and not session['save_state_used'] and session['port']==19445
 request=client(19445);cpu=request('cpu.status')
 if cpu['stepping']:
  assert cpu['pc'] in [f['address'] for f in request('hle.func.list')['functions'] if f['name']=='zz_sceDisplaySetFrameBuf']
  request('cpu.resume')
 request('input.buttons.send',buttons={n:False for n in names});time.sleep(1)
 for n in a.buttons:request('input.buttons.press',button=n,duration=10 if n in ('up','down','left','right','ltrigger','rtrigger') else 20);time.sleep(a.delay)
 time.sleep(2)
 import capture_framebuffer
 capture_framebuffer.request=request;png,report=capture_framebuffer.capture(hold=True)
 report.update(session=session,buttons=a.buttons,input_method='10 updates for directions/triggers; 20 for action buttons',case=a.case)
 dest=ROOT/'work/ui/ui_0.1.81/reviewed'/a.name;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.with_suffix('.png').exists()
 dest.with_suffix('.png').write_bytes(png);dest.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(dest.with_suffix('.png'),flush=True)

if __name__=='__main__':main()

