"""Keep symbolic stat labels native; allow ordinary mode-6 text to use VWF."""
import hashlib
from font_patch import REG
from menu_code_020 import append

HOOK=0x642c0
PRIOR=0x34a0a8
VWF=0x347be0

def emit(a):
 a.label('help_dispatch')
 a.i(35,'t0','s4',0x34)
 a.i(9,'t1','zero',6)
 a.branch(5,'t0','t1','vwf')
 a.i(9,'t0','s4',0x4c)
 a.branch(4,'t0','zero','native')
 a.i(36,'t1','t0',0)
 a.i(9,'t2','zero',0x83)
 a.branch(5,'t1','t2','vwf')
 a.i(36,'t1','t0',1)
 a.i(9,'t1','t1',-0x9f)
 a.i(11,'t1','t1',0x18)
 a.branch(4,'t1','zero','vwf')
 a.label('native')
 a.emit(REG['a2']<<21|8);a.emit(0)
 a.label('vwf')
 a.jump(VWF,link=False)

def prepare(data):
 out,r=append(data,emit,{HOOK:('help_dispatch',3<<26|PRIOR>>2)})
 r['rule']='Native only for mode 6 beginning with a CP932 uppercase Greek stat symbol (839f..83b6); other text uses existing help VWF.'
 r['source_sha256']=hashlib.sha256(data).hexdigest()
 return out,r
