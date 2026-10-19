"""Observe a naturally dispatched VWF banner after ending the isolated QA turn."""
import base64,json,struct,time
from sn3_archive import ROOT
from options_runtime_078 import client

def main():
 request=client(19452);base=0x08804000;pc=base+0x35269c+328
 assert not request('cpu.breakpoint.list')['breakpoints'];request('cpu.breakpoint.add',address=pc,enabled=True,log=False,condition='s1 == 1')
 assert request('cpu.status')['stepping'];request('cpu.resume');time.sleep(.3)
 request('input.buttons.press',button='up',duration=8);time.sleep(.6);request('input.buttons.press',button='circle',duration=8);found=False
 try:
  deadline=time.monotonic()+25
  while time.monotonic()<deadline:
   status=request('cpu.status')
   if status['stepping']:
    assert status['pc']==pc;g=request('cpu.getAllRegs')['categories'][0];g=dict(zip(g['registerNames'],g['uintValues']));owner=g['s0']
    read=lambda a,n:base64.b64decode(request('memory.read',address=a,size=n)['base64'])
    b=read(owner,128);rows=struct.unpack_from('<I',b,0x30)[0];pointer=struct.unpack('<I',read(rows,4))[0];raw=read(pointer,70);end=next(i for i in range(0,70,2) if raw[i:i+2]==bytes(2))
    result=dict(owner=owner,rows=rows,pointer=pointer,text=raw[:end].decode('cp932'),mode=struct.unpack_from('<I',b,0x34)[0],cell_selector=b[0x64],game_memory_writes=False)
    (ROOT/'work/scratch/ui086-battle/banner-probe.json').write_text(json.dumps(result,indent=2)+'\n','utf8');print(json.dumps(result),flush=True);found=True;break
   time.sleep(.1)
 finally:
  request('cpu.breakpoint.remove',address=pc)
  if request('cpu.status')['stepping']:request('cpu.resume')
 if found:
  import capture_framebuffer
  capture_framebuffer.request=request;png,report=capture_framebuffer.capture(hold=True);d=ROOT/'work/ui/ui_0.1.86/reviewed/liveBanner';d.with_suffix('.png').write_bytes(png);d.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
 print(json.dumps(dict(found=found)),flush=True)

if __name__=='__main__':main()
