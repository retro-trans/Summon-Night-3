"""Execute Deployment position helpers at two relocated PSP load bases."""
import json,struct
from deployment_029 import prepare_elf,PROMPT
from verify_menu_vwf_020 import CPU
from font_patch import CODE_VA
from sn3_archive import ROOT
from dialogue_encoding import encode_dialogue

def verify():
 data,r=prepare_elf();r=r['helpers'];cases=0
 metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters']
 advances={int.from_bytes(bytes.fromhex(v['cp932_hex']),'little'):v['proposed_advance_pixels']*.875 for v in metrics.values()}
 def widths(raw,n,fallback=13):return sum(advances.get(int.from_bytes(raw[i:i+2],'little'),fallback) for i in range(0,n*2,2))
 def sf(c,n,v):c.fp[n]=int.from_bytes(struct.pack('<f',v),'little')
 def ff(c,n):return struct.unpack('<f',struct.pack('<I',c.fp[n]))[0]
 for base in [0x08804000,0x0890c000]:
  def new():
   c=CPU(data,r,base);c.store(0x09effe00,b'G'*1024);c.set('sp',0x09f00000)
   for i in list(range(16,29))+[30]:c.reg[i]=0x55500000+i
   for i in range(32):sf(c,i,i+.25)
   return c
  def check(c,saved,fs):
   assert c.reg[16:24]+c.reg[26:31]==saved[:8]+saved[10:]
   assert c.fp[13:16]==fs[13:16] and c.fp[20:]==fs[20:]
   assert c.bytes(0x09effe00,0x1c0)==b'G'*0x1c0 and c.bytes(0x09f00000,0x200)==b'G'*0x200
  for text in ['Search for ingredients.','Wide W / thin i','あAB']:
   raw=encode_dialogue(text,'')[0]
   for prefix in sorted(set(range(0,len(raw)//2+1,8))|{len(raw)//2}):
    c=new();src=0x09000000;c.store(src,raw+b'\0\0');c.set('s5',src);c.set('s4',prefix);c.set('a0',0x09001000);sf(c,24,124);seen=[]
    saved=c.reg[16:31].copy();fs=c.fp.copy()
    c.native_handlers={base+0x1e6140:lambda m:(seen.append((m.reg[4],ff(m,12))) or {})}
    c.run(int(r['code_address'],16)-CODE_VA+r['labels']['support_position']);check(c,saved,fs)
    assert seen==[(0x09001000,124+widths(raw,prefix,14))];cases+=1
  raw=b'\0\0'+encode_dialogue('Deploy ','')[0]+b'\0\0'+encode_dialogue('Status/Gear ','')[0]+b'\0\0'+encode_dialogue('Map','')[0]
  for match in [True,False,'copy']:
   for row in [0,1]:
    for prefix in [0,8,22]:
     c=new();ctx=0x09000000;desc=0x09002000;cb=base+0x1000;c.store(ctx,bytes(0x200));c.store(ctx+0x44,struct.pack('<I',base+PROMPT+(0 if match else 4)));c.store(ctx+0x4c+row*58,raw);c.store(desc,bytes(0x110));c.store(desc+0x100,bytes([prefix,row]));c.set('s2',ctx);c.set('s3',desc);c.set('a0',desc);c.set('a2',cb);sf(c,12,120+prefix*13);seen=[]
     
     if match=='copy':c.store(0x09010000,c.bytes(base+PROMPT,64));c.store(ctx+0x44,struct.pack('<I',0x09010000))
     saved=c.reg[16:31].copy();fs=c.fp.copy();c.native_handlers={cb:lambda m:(seen.append((m.reg[4],ff(m,12))) or {})}
     c.run(int(r['code_address'],16)-CODE_VA+r['labels']['shortcut_icons']);check(c,saved,fs)
     assert seen==[(desc,120+(widths(raw,prefix) if match else prefix*13))],seen;cases+=1
 return dict(actual_mips_cases=cases,load_bases=2,scope_fallback=True,stack_guards=True,preserved_y_z_and_callee_saved_registers=True)
if __name__=='__main__':print(json.dumps(verify(),indent=2))
