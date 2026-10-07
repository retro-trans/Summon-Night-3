"""Scoped private pot-crash reproduction client; preview before input."""
import argparse,json,time,sys
from sn3_archive import ROOT
def client(port):
 namespace={'__name__':'menus075_client'}
 exec((ROOT/'tools/setup_qa.py').read_text().replace('19381',str(port)),namespace)
 return namespace['request']
def main():
 p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('buttons',nargs='*');p.add_argument('--execute',action='store_true');p.add_argument('--port',type=int,default=19435);p.add_argument('--case',default='menus075-diag');p.add_argument('--delay',type=float,default=2);a=p.parse_args()
 request=client(a.port);game=request('game.status');cpu=request('cpu.status');session=json.loads((ROOT/'work/scratch'/a.case/'session.json').read_text('utf-8-sig'))
 assert session['port']==a.port and a.case.startswith('menus075') and a.name.replace('_','').isalnum()
 assert set(a.buttons)<=set(['circle','cross','up','down','left','right','start','select','ltrigger','rtrigger','square','triangle'])
 print(json.dumps(dict(mode='execute' if a.execute else 'preview',cpu=cpu,buttons=a.buttons,case=a.case)),flush=True)
 if not a.execute:return
 request('input.buttons.send',buttons={button:False for button in ['circle','cross','up','down','left','right','start','select','ltrigger','rtrigger','square','triangle']})
 if cpu['stepping']:
  display=[f['address'] for f in request('hle.func.list')['functions'] if f['name']=='zz_sceDisplaySetFrameBuf']
  assert cpu['pc'] in display,('Unexpected stop',cpu)
  request('cpu.resume')
  time.sleep(.25)
 for button in a.buttons:
  request('input.buttons.press',button=button,duration=10);time.sleep(a.delay)
  assert not request('cpu.status')['stepping'],('Stopped after',button,request('cpu.status'))
 import capture_framebuffer
 capture_framebuffer.request=request;time.sleep(4);png,report=capture_framebuffer.capture(hold=True)
 report.update(buttons=a.buttons,cpu=request('cpu.status'),case=a.case)
 dest=ROOT/'work/ui/menus_0.1.75'/a.case/a.name;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.with_suffix('.png').exists()
 dest.with_suffix('.png').write_bytes(png);dest.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(capture=str(dest.with_suffix('.png')),cpu=report['cpu'])),flush=True)
if __name__=='__main__':main()


