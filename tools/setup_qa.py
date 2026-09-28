"""Only drive the isolated port-19381 setup QA instance; preview writes and input."""
import argparse,base64,json,time,uuid
from pathlib import Path
import ppsspp_client
from ppsspp_client import websocket,ROOT


def request(event,**params):
    ticket=str(uuid.uuid4())
    c=websocket.create_connection('ws://127.0.0.1:19381/debugger',timeout=20,suppress_origin=True)
    try:
        c.send(json.dumps(dict(params,event=event,ticket=ticket)))
        while True:
            r=json.loads(c.recv())
            if r.get('ticket')==ticket or (event in ('cpu.resume','cpu.stepping') and r.get('event')==event):
                if r.get('event')=='error':raise RuntimeError(r)
                return r
    finally:c.close()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['status','press','capture'])
    p.add_argument('value',nargs='?');p.add_argument('--execute',action='store_true');args=p.parse_args()
    game=request('game.status')
    if args.action=='status':
        print(json.dumps(dict(game=game,cpu=request('cpu.status')),indent=2));return
    print(json.dumps(dict(mode='execute' if args.execute else 'dry run',port=19381,action=args.action,value=args.value,game=game)))
    if not args.execute:return
    if args.action=='press':
        if request('cpu.status')['stepping']:request('cpu.resume')
        for button in args.value.split(','):
            print(request('input.buttons.press',button=button,duration=10))
            time.sleep(3)
        return
    import capture_framebuffer
    capture_framebuffer.request=request
    target=ROOT/'work/ui/setup_runtime_0.1.6'/args.value
    assert target.suffix=='.png' and ROOT in target.resolve().parents and not target.exists()
    png,report=capture_framebuffer.capture(hold=True)
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(png)
    target.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))


if __name__=='__main__':main()
