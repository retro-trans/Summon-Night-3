"""Read the live matching Assist icon call without editing game memory."""
import base64,json,struct,time
from options_runtime_078 import client
from sn3_archive import ROOT
from dialogue_encoding import encode_dialogue
r=client(19445);m=json.loads((ROOT/'work/output/0.1.81/manifest.json').read_text());fix=m['assist081_fix'];base=0x08804000;pc=base+int(fix['code_address'],16)+fix['labels']['sum']
assert not r('cpu.breakpoint.list')['breakpoints']
r('cpu.breakpoint.add',address=pc,enabled=True,log=False)
try:
 r('cpu.resume');deadline=time.monotonic()+10
 while time.monotonic()<deadline and not r('cpu.status')['stepping']:time.sleep(.03)
 assert r('cpu.status')['pc']==pc
 g=r('cpu.getAllRegs')['categories'][0];regs=dict(zip(g['registerNames'],g['uintValues']))
 def read(p,n):return base64.b64decode(r('memory.read',address=p,size=n)['base64'])
 raw=read(regs['s0'],24);assert raw==encode_dialogue('Assist only ','')[0]
 index,row=read(regs['s3']+0x100,2);assert index==12 and row<3
 result=dict(passed=True,iso_sha256=m['output_sha256'],native_index=index,native_row=row,matched_text='Assist only ',actual_helper_executed=True,memory_writes=False)
 (ROOT/'work/ui/ui_0.1.81/live-helper.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
finally:
 r('cpu.breakpoint.remove',address=pc);r('cpu.resume')
