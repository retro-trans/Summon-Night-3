"""Bounded input and read-only display inspection in isolated 0.1.10 PPSSPP."""
import argparse,base64,hashlib,json,struct,time,unicodedata
from setup_qa import request,ROOT
import capture_framebuffer

def memory(address,size):
    assert 0x08800000<=address<address+size<=0x0a000000
    return base64.b64decode(request('memory.read',address=address,size=size)['base64'])

def observe(report,check=False):
    paused=request('cpu.status')['stepping']
    if not paused:request('cpu.stepping')
    try:
        vm=struct.unpack('<15I',memory(0x08a3a9e4,60))
        if check:assert hashlib.sha256(memory(vm[7],report['decoded_size'])).hexdigest()==report['decoded_sha256']
        # Fresh 0.1.10 boot: validated from the processed first-line pointer.
        state=memory(0x08e31910,0x3d4);count=struct.unpack_from('<I',state,0x3cc)[0];assert count<=6
        records=[r for r in report['changes'] if r['reference_instructions']]+[r for g in report['layout_groups'] for p in g['pages'] for r in p]
        by={r['new_offset']:r for r in records};lines=[]
        for i in range(count):
            b=0x84+i*0x8c;ptr,choice=struct.unpack_from('<2I',state,b);raw=b'';kinds=[]
            for j in range(32):
                c,k=struct.unpack_from('<2H',state,b+10+j*4)
                if not c:break
                raw+=struct.pack('<H',c);kinds.append(k)
            target=by.get(ptr-vm[7]);shown=raw.decode('cp932',errors='replace')
            if target:
                expected=target['display_text']
                if '\u25cf' not in expected:assert raw==expected.encode('cp932'),(target['id'],shown)
                else:
                    prefix,suffix=expected.split('\u25cf');assert shown.startswith(prefix) and shown.endswith(suffix)
                    name=shown[len(prefix):len(shown)-len(suffix)];assert 1<=len(name)<=6
            lines.append(dict(id=target['id'] if target else None,text=target['text'] if target else None,
                rendered=unicodedata.normalize('NFKC',shown) if target else None,pointer=hex(ptr),units=len(kinds),
                selectable=bool(state[b+8]),choice=choice,kinds=kinds))
        return dict(pc=vm[1],native=hex(vm[12]),lines=lines,choice=any(r['selectable'] for r in lines))
    finally:
        if not paused:request('cpu.resume')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--advance',type=int,default=0);p.add_argument('--until',default='harbor_player_introduction_0.1.10')
    p.add_argument('--capture');p.add_argument('--press');p.add_argument('--execute',action='store_true');p.add_argument('--tag',default='inspection');a=p.parse_args()
    assert 0<=a.advance<=40
    session=json.loads((ROOT/'work/scratch/setup_qa_0.1.10/session.json').read_text(encoding='utf-8-sig'))
    game=request('game.status');assert game['game']['id']=='NPJH50380' and '0.1.10' in session['game'],game
    report=json.loads((ROOT/'work/output/0.1.10/manifest.json').read_text())['script_changes'][0]
    state=observe(report,check=True);print(json.dumps(dict(mode='execute' if a.execute else 'dry run',state=state,advance=a.advance,until=a.until,capture=a.capture,press=a.press)),flush=True)
    if not a.execute:return
    states=[state]
    if a.press:
        if request('cpu.status')['stepping']:request('cpu.resume')
        for button in a.press.split(','):
            request('input.buttons.press',button=button,duration=10);time.sleep(1.5)
        state=observe(report);states.append(state)
    for n in range(a.advance):
        if state['choice'] or any(a.until in (r['id'] or '') for r in state['lines']):break
        if request('cpu.status')['stepping']:request('cpu.resume')
        request('input.buttons.press',button='circle',duration=2);time.sleep(.65)
        new=observe(report)
        if new!=state:print(json.dumps(dict(press=n+1,state=new)),flush=True);states.append(new)
        state=new
    if a.capture:
        if request('cpu.status')['stepping']:request('cpu.resume')
        time.sleep(1.5)
        capture_framebuffer.request=request;png,meta=capture_framebuffer.capture(hold=True)
        path=ROOT/'work/ui/harbor_gaps_0.1.10/runtime'/a.capture
        assert path.suffix=='.png' and ROOT in path.resolve().parents and not path.exists()
        path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(png)
        path.with_suffix('.json').write_text(json.dumps(dict(capture=meta,state=state),indent=2)+'\n')
    destination=ROOT/'work/ui/harbor_gaps_0.1.10/runtime'/(a.tag+'.trace.json')
    assert not destination.exists();destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(dict(session=session,states=states),indent=2)+'\n')
    print(json.dumps(dict(final=state,trace=str(destination))),flush=True)

if __name__=='__main__':main()
