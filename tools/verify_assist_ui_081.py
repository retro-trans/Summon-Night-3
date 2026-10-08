"""Execute the Assist icon helper and check the inherited VWF field ABI."""
import json,struct
from assist_ui_081 import prepare_elf,BASE,FIELDS
from sn3_archive import ROOT
from verify_menu_vwf_020 import CPU
from font_patch import CODE_VA
from dialogue_encoding import encode_dialogue
from stat_spacing_026 import _file_offset_for_va as off
from verify_guards_050 import GuardCPU

def verify():
 elf,r=prepare_elf();old=(BASE/'EBOOT.elf').read_bytes()
 metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters']
 raw=encode_dialogue('Assist only ','')[0];width=sum(metrics[c]['proposed_advance_pixels'] for c in 'Assist only ')*.875
 cases=bindcases=0
 for base in (0x08804000,0x0890c000):
  for row,index,match in [(i,12,True) for i in range(3)]+[(1,12,False),(1,11,True),(1,27,True),(3,12,True)]:
   c=CPU(elf,r,base);ctx=0x09000000;desc=0x09002000;cb=base+0x1000
   c.store(ctx,bytes(0x200));c.store(ctx+0x4c+row*58,raw if match else encode_dialogue('Different UI','')[0]);c.store(desc,bytes(0x110));c.store(desc+0x100,bytes([index,row]));c.store(0x09effe00,b'G'*1024)
   for i in range(16,31):c.reg[i]=0x55500000+i
   c.set('sp',0x09f00000);c.set('s2',ctx);c.set('s3',desc);c.set('a0',desc);c.set('a2',cb)
   for n in range(32):c.fp[n]=int.from_bytes(struct.pack('<f',n+.25),'little')
   c.fp[12]=int.from_bytes(struct.pack('<f',118+index*13),'little');saved=c.reg[16:31].copy();fs=c.fp.copy();seen=[]
   def record(tag,m):seen.append((tag,m.reg[4],struct.unpack('<f',struct.pack('<I',m.fp[12]))[0]));return {}
   c.native_handlers={cb:lambda m:record('callback',m),base+r['fallback']:lambda m:record('fallback',m)}
   c.run(int(r['code_address'],16)-CODE_VA+r['labels']['assist_icon'])
   corrected=row<3 and index==12 and match
   assert seen==[('callback' if corrected else 'fallback',desc,118+(width if corrected else index*13))],seen
   assert c.reg[16:24]+c.reg[26:31]==saved[:8]+saved[10:] and c.fp[13:]==fs[13:]
   assert c.bytes(0x09effe00,0x1c0)==b'G'*0x1c0 and c.bytes(0x09f00000,0x200)==b'G'*0x200
   cases+=1
  for text in ('Protagonist','Magna / Toris','Kyuuma','Keina','Misumi','Minis','MyName','Guardian Beast','A'*16,'A'*17):
   m=GuardCPU(elf,r,base);obj=0x09400000;src=0x09800000;stop=0x08801234;payload=encode_dialogue(text,'')[0]+bytes(2);m.store(src,payload)
   m.r=[0]*32;m.r[4:7]=[obj,src,1];m.r[29]=0x09f00000;m.r[31]=stop;pc=base+0x347b5c;seen=[]
   for _ in range(100000):
    if pc==stop:break
    if pc==base+0x1e4ac8:m.r[2]=len(text);pc=m.r[31];continue
    if pc==base+0x32e060:assert m.r[4:8]==[obj,src,len(text),1];seen.append('vwf');pc=m.r[31];continue
    if pc==base+0x1cbdec:assert m.r[4:7]==[obj,src,1];seen.append('native');pc=m.r[31];continue
    pc=m.step(pc)
   assert pc==stop and seen==['vwf' if len(text)<=16 else 'native'],(text,hex(pc),seen)
   assert bytes(m.read(src+i,1) for i in range(len(payload)))==payload
   bindcases+=1
 for site in FIELDS:assert struct.unpack_from('<I',elf,site+192)[0]==3<<26|0x347b5c>>2
 # No preexisting appended code/data changed; only two calls and icon hook.
 from stages_pupil_names import parse_elf
 os=parse_elf(old)['phdrs'][3];ns=parse_elf(elf)['phdrs'][3]
 assert old[os[1]:os[1]+os[4]]==elf[ns[1]:ns[1]+os[4]]
 return dict(passed=True,version='0.1.81',relocated_icon_cases=cases,vwf_field_cases=bindcases,load_bases=2,assist_prefix_pixels=width,original_icon_prefix_pixels=156,buffer_guards=True,custom_name_buffers_preserved=True,inherited_code_data_preserved=True,output_elf_sha256=r['output_sha256'])

if __name__=='__main__':
 result=verify();dest=ROOT/'work/ui/ui_0.1.81';dest.mkdir(parents=True,exist_ok=True);(dest/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
