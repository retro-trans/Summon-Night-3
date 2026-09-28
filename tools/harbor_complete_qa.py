"""Drive only the isolated0.1.11 session, stopping at known choice or target."""
import argparse,json,time
from harbor_gap_qa import observe
from setup_qa import request,ROOT
import capture_framebuffer

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--advance',type=int,default=0);p.add_argument('--until',default='harbor_complete_585')
    p.add_argument('--press');p.add_argument('--capture');p.add_argument('--tag',default='inspect');p.add_argument('--execute',action='store_true')
    p.add_argument('--auto-opening',action='store_true');p.add_argument('--candidate',default='work/output/0.1.11');a=p.parse_args()
    assert 0<=a.advance<=60
    session=json.loads((ROOT/'work/scratch/setup_qa_0.1.11_final/session.json').read_text(encoding='utf-8-sig'))
    assert '0.1.11' in session['game'] and request('game.status')['game']['id']=='NPJH50380'
    manifest=json.loads((ROOT/a.candidate/'manifest.json').read_text());report=manifest['script_changes'][0]
    state=observe(report,True)
    print(json.dumps(dict(mode='execute' if a.execute else 'dry run',advance=a.advance,until=a.until,state=state,
        auto_opening=a.auto_opening,press=a.press,capture=a.capture,policy='Automate only first recollection/refined-pupil options. Other menus require explicit input and visual inspection.')),flush=True)
    if not a.execute:return
    def press(button,duration=10,delay=1.5):
        if request('cpu.status')['stepping']:request('cpu.resume')
        request('input.buttons.press',button=button,duration=duration);time.sleep(delay)
    states=[state];actions=[]
    if a.press:
        for b in a.press.split(','):press(b);actions.append(b)
        state=observe(report);states.append(state)
    for n in range(a.advance):
        if any(a.until in (r['id'] or '') for r in state['lines']):break
        if state['choice']:
            header=state['lines'][0]['id'];time.sleep(1.5)
            if a.auto_opening and header=='00:00065:text:0002691a':press('circle');actions.append('recollection:first')
            # The first directional press can activate the cursor without moving
            # it. Select gender manually and inspect the highlight before confirming.
            elif a.auto_opening and header=='00:00065:text:0002884a':press('circle');actions.append('girl:refined')
            else:break
        else:press('circle',2,.65);actions.append('advance')
        new=observe(report)
        if new!=state:
            states.append(new);print(json.dumps(dict(step=n+1,text=[r['text'] for r in new['lines']],choice=new['choice'])),flush=True)
        state=new
    if a.capture:
        if request('cpu.status')['stepping']:request('cpu.resume')
        time.sleep(5);state=observe(report);capture_framebuffer.request=request;png,meta=capture_framebuffer.capture(hold=True)
        target=ROOT/'work/ui/harbor_complete_0.1.11/runtime'/a.capture
        assert ROOT in target.resolve().parents and target.suffix=='.png' and not target.exists()
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(png);target.with_suffix('.json').write_text(json.dumps(dict(state=state,capture=meta),indent=2)+'\n')
    dest=ROOT/'work/ui/harbor_complete_0.1.11/runtime'/(a.tag+'.trace.json');assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(dict(session=session,candidate_sha256=manifest['output_sha256'],live_script_sha256=report['decoded_sha256'],states=states,actions=actions),indent=2)+'\n')
    print(json.dumps(dict(final=state,trace=str(dest))),flush=True)

if __name__=='__main__':main()
