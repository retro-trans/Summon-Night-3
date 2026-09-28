"""Isolated 0.1.25 runtime QA connection. Port 19382 only."""
import json,uuid,time
from setup_qa import websocket
from sn3_archive import ROOT
import capture_framebuffer
def request(event,**params):
    ticket=str(uuid.uuid4())
    c=websocket.create_connection('ws://127.0.0.1:19382/debugger',timeout=20,suppress_origin=True)
    try:
        c.send(json.dumps(dict(params,event=event,ticket=ticket)))
        while True:
            r=json.loads(c.recv())
            if r.get('ticket')==ticket or (event in ('cpu.resume','cpu.stepping') and r.get('event')==event):
                if r.get('event')=='error':raise RuntimeError(r)
                return r
    finally:c.close()

def capture(name):
    capture_framebuffer.request=request
    png,report=capture_framebuffer.capture(hold=True)
    folder=ROOT/'work/ui/battle_ui_0.1.25/runtime';folder.mkdir(exist_ok=True)
    path=folder/(name+'.png');path.write_bytes(png);path.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
    return path

def press(button,wait=.7):
    if request('cpu.status')['stepping']:request('cpu.resume');time.sleep(.1)
    request('input.buttons.press',button=button,duration=5);time.sleep(wait)



