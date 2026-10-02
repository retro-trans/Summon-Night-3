"""Drive only the isolated 0.1.65 release test; preview input/capture by default."""
import argparse,json,sys,time,struct,base64
from pathlib import Path
from setup_qa import ROOT
namespace={'__name__':'release065_client'}
exec((ROOT/'tools/setup_qa.py').read_text().replace('19381','19402'),namespace)
request=namespace['request']

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('name');p.add_argument('buttons',nargs='*');p.add_argument('--execute',action='store_true');a=p.parse_args()
    game=request('game.status');cpu=request('cpu.status')
    session=json.loads((ROOT/'work/scratch/release065-runtime/session.json').read_text('utf-8-sig'))
    assert Path(session['iso']).resolve()==ROOT/'work/output/0.1.65/Summon_Night_3_EN_0.1.65.iso'
    assert game['game']['id']=='NPJH50380',game
    assert '0.1.65.iso' in (ROOT/'work/scratch/release065-runtime/runtime.log').read_text('utf8',errors='replace')
    assert a.name.replace('_','').isalnum()
    assert set(a.buttons)<=set(['circle','cross','up','down','left','right','start','select','ltrigger','rtrigger'])
    dest=ROOT/'work/ui/release_0.1.65/runtime'/a.name
    print(json.dumps(dict(mode='execute' if a.execute else 'preview',game=game,cpu=cpu,buttons=a.buttons,output=str(dest))),flush=True)
    if not a.execute:return
    if cpu['stepping']:
        display=[f['address'] for f in request('hle.func.list')['functions'] if f['name']=='zz_sceDisplaySetFrameBuf']
        assert display==[cpu['pc']],('Unexpected emulator stop',cpu)
        request('cpu.resume')
    for button in a.buttons:
        request('input.buttons.press',button=button,duration=10);time.sleep(2)
        assert not request('cpu.status')['stepping'],('Stopped after',button)
    import capture_framebuffer
    capture_framebuffer.request=request
    time.sleep(4)
    png,report=capture_framebuffer.capture(hold=True)
    report['buttons']=a.buttons;report['cpu']=request('cpu.status')
    dest.parent.mkdir(parents=True,exist_ok=True)
    assert not dest.with_suffix('.png').exists()
    dest.with_suffix('.png').write_bytes(png)
    dest.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(capture=str(dest.with_suffix('.png')),cpu=report['cpu'])),flush=True)

if __name__=='__main__':main()
