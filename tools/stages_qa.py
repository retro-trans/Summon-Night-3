"""Inspect and drive only the isolated0.1.12 emulator; preview before execution."""
import argparse,base64,hashlib,json,struct,time,unicodedata
from setup_qa import request,ROOT
import capture_framebuffer
def memory(address,size):
    assert 0x08800000<=address<address+size<=0x0a000000
    return base64.b64decode(request('memory.read',address=address,size=size)['base64'])
def wide(address,limit):
    data=memory(address,(limit+1)*2);end=next(n for n in range(0,len(data),2) if data[n:n+2]==b'\0\0');assert end<=limit*2
    return data[:end].decode('cp932')
def observe(report,check=False,context=0x08e31910):
    paused=request('cpu.status')['stepping']
    if not paused:request('cpu.stepping')
    try:
        vm=struct.unpack('<15I',memory(0x08a3a9e4,60))
        if check:assert hashlib.sha256(memory(vm[7],report['decoded_size'])).hexdigest()==report['decoded_sha256']
        state=memory(context,0x3d4);count=struct.unpack_from('<I',state,0x3cc)[0];assert count<=6
        nameptrs=struct.unpack('<3I',memory(context+0x4be8,12));tokens={}
        for c,ptr,limit in zip('●▲■',nameptrs,(6,8,8)):
            if 0x08800000<=ptr<0x0a000000:tokens[c]=wide(ptr,limit)
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
                for c,t in tokens.items():expected=expected.replace(c,t)
                assert raw==expected.encode('cp932'),(target['id'],shown,expected)
                assert len(kinds)<=31
            lines.append(dict(id=target['id'] if target else None,text=target['text'] if target else None,rendered=unicodedata.normalize('NFKC',shown) if target else None,pointer=hex(ptr),units=len(kinds),selectable=bool(state[b+8]),choice=choice,kinds=kinds))
        return dict(pc=vm[1],native=hex(vm[12]),script_base=hex(vm[7]),lines=lines,choice=any(r['selectable'] for r in lines),names={c:unicodedata.normalize('NFKC',t) for c,t in tokens.items()})
    finally:
        if not paused:request('cpu.resume')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--advance',type=int,default=0);p.add_argument('--until',default='stages_')
    p.add_argument('--press');p.add_argument('--capture');p.add_argument('--tag',default='inspect');p.add_argument('--execute',action='store_true');p.add_argument('--boot',action='store_true')
    p.add_argument('--auto-opening',action='store_true');p.add_argument('--candidate',default='work/output/0.1.12');p.add_argument('--context',type=lambda x:int(x,0),default=0x08e31910);p.add_argument('--delay',type=float,default=.65);a=p.parse_args()
    assert 0<=a.advance<=60 and .2<=a.delay<=5
    session=json.loads((ROOT/'work/scratch/setup_qa_0.1.12/session.json').read_text(encoding='utf-8-sig'))
    assert '0.1.12' in session['game'] and request('game.status')['game']['id']=='NPJH50380'
    manifest=json.loads((ROOT/a.candidate/'manifest.json').read_text());report=manifest['script_changes'][0]
    def inspect(check=False):return observe(report,check,a.context)
    state={} if a.boot else inspect(True)
    print(json.dumps(dict(mode='execute' if a.execute else 'dry run',advance=a.advance,until=a.until,state=state,press=a.press,capture=a.capture)),flush=True)
    if not a.execute:return
    def press(button,duration=10,delay=1.5):
        if request('cpu.status')['stepping']:request('cpu.resume')
        request('input.buttons.press',button=button,duration=duration);time.sleep(delay)
    states=[] if a.boot else [state];actions=[]
    if a.press:
        for b in a.press.split(','):press(b,delay=3 if a.boot else 1.5);actions.append(b)
        if not a.boot:state=inspect();states.append(state)
    for n in range(a.advance):
        if any(a.until in (r['id'] or '') for r in state['lines']):break
        if state['choice']:
            header=state['lines'][0]['id'];time.sleep(1.5)
            if a.auto_opening and header=='00:00065:text:0002691a':press('circle');actions.append('recollection:first')
            elif a.auto_opening and header=='00:00065:text:0002884a':press('circle');actions.append('girl:refined')
            else:break
        else:press('circle',2,a.delay);actions.append('advance')
        new=inspect()
        if new!=state:states.append(new);print(json.dumps(dict(step=n+1,text=[r['text'] for r in new['lines']],choice=new['choice'])),flush=True)
        state=new
    if a.capture:
        if request('cpu.status')['stepping']:request('cpu.resume')
        time.sleep(5)
        if not a.boot:state=inspect()
        capture_framebuffer.request=request;png,meta=capture_framebuffer.capture(hold=True)
        target=ROOT/'work/ui/stages_0.1.12/runtime'/a.capture
        assert ROOT in target.resolve().parents and target.suffix=='.png' and not target.exists()
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(png);target.with_suffix('.json').write_text(json.dumps(dict(state=state,capture=meta),indent=2)+'\n')
    dest=ROOT/'work/ui/stages_0.1.12/runtime'/(a.tag+'.trace.json');assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(dict(session=session,candidate_sha256=manifest['output_sha256'],live_script_sha256=report['decoded_sha256'],states=states,actions=actions),indent=2)+'\n')
    print(json.dumps(dict(final=state,trace=str(dest))),flush=True)
if __name__=='__main__':main()
