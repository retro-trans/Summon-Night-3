"""Scoped private pot-crash reproduction client; preview before input."""
import argparse,json,time,sys
from sn3_archive import ROOT
def client(port):
 namespace={'__name__':'pot073_client'}
 exec((ROOT/'tools/setup_qa.py').read_text().replace('19381',str(port)),namespace)
 return namespace['request']
def main():
 p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('buttons',nargs='*');p.add_argument('--execute',action='store_true');p.add_argument('--port',type=int,default=19421);p.add_argument('--case',default='pot073-final');p.add_argument('--delay',type=float,default=2);a=p.parse_args()
 request=client(a.port);game=request('game.status');cpu=request('cpu.status');session=json.loads((ROOT/'work/scratch'/a.case/'session.json').read_text('utf-8-sig'))
 assert session['port']==a.port and 'pot073' in a.case and a.name.replace('_','').isalnum()
 assert set(a.buttons)<=set(['circle','cross','up','down','left','right','start','select','ltrigger','rtrigger','square','triangle'])
 print(json.dumps(dict(mode='execute' if a.execute else 'preview',cpu=cpu,buttons=a.buttons,case=a.case)),flush=True)
 if not a.execute:return
 if cpu['stepping']:
  display=[f['address'] for f in request('hle.func.list')['functions'] if f['name']=='zz_sceDisplaySetFrameBuf']
  assert cpu['pc'] in display,('Unexpected stop',cpu)
  request('cpu.resume')
 for button in a.buttons:
  request('input.buttons.press',button=button,duration=10);time.sleep(a.delay)
  assert not request('cpu.status')['stepping'],('Stopped after',button,request('cpu.status'))
 import capture_framebuffer
 capture_framebuffer.request=request;time.sleep(4);png,report=capture_framebuffer.capture(hold=True)
 report.update(buttons=a.buttons,cpu=request('cpu.status'),case=a.case)
 dest=ROOT/'work/ui/pot_0.1.73'/a.case/a.name;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.with_suffix('.png').exists()
 dest.with_suffix('.png').write_bytes(png);dest.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(capture=str(dest.with_suffix('.png')),cpu=report['cpu'])),flush=True)
if __name__=='__main__':main()

