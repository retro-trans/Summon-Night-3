"""Execute actual Level Up formatter, staging, and proportional positions."""
import json,struct,unicodedata
from sn3_archive import ROOT,GameSource
from levelup_060 import prepare_elf,BASE
from verify_descriptions_021 import CPU
from verify_guards_057 import AliasCPU,stage
from verify_menu_vwf_020 import CPU as PositionCPU
from stages_pupil_names import parse_elf
from font_patch import CODE_VA
from dialogue_encoding import encode_dialogue

def verify(elf,static):
 expected,report=prepare_elf();assert elf==expected
 rows=[];renderer=AliasCPU(elf,static)
 for available in (0,1):
  for allocation in (0,1):
   for skills in (0,1):
    c=CPU(elf,static);owner=0x500000;buf=owner+0x19f0
    c.mem[buf-32:buf+210]=b'G'*242
    c.r=[0]*32;c.r[4:8]=[owner,available,allocation,skills]
    c.r[29]=0x700000;c.r[31]=0x7ffff0;pc=0x63b60
    for _ in range(100000):
     if pc==0x7ffff0:break
     if pc==0x1c2bc0:
      a,v,n=c.r[4:7];c.mem[a:a+n]=bytes([v&255])*n;c.r[2]=a;pc=c.r[31]
     elif pc==0x1e4ac8:c.r[2]=c.strlen(c.r[4]);pc=c.r[31]
     elif pc==0x1e4b50:
      a,b,n=c.r[4:7];c.mem[a:a+n*2]=c.mem[b:b+n*2];c.r[2]=a;pc=c.r[31]
     else:pc=c.step(pc)
    else:raise AssertionError('Level Up instruction budget')
    assert c.mem[buf-32:buf]==b'G'*32 and c.mem[buf+178:buf+210]==b'G'*32
    payload=c.mem[buf:buf+178];pos=0;lines=[]
    while c.read(buf+pos,2):
     end=pos
     while c.read(buf+end,2):end+=2
     lines.append(unicodedata.normalize('NFKC',payload[pos:end].decode('cp932')));pos=end+2
    wanted=['Allocate bonus points.','АConfirm'] if allocation else [
     'Choose a unit to level up.' if available else 'No units can level up.',
     'АOK БEnd'+(' Й     Learn Skills' if skills else '')]
    assert lines==wanted,(lines,wanted)
    assert max(map(len,lines))<=27 and sum(map(len,lines))<=54
    staged=stage(renderer,payload);assert staged['rows']==2
    rows.append(dict(available=available,allocation=allocation,skills=skills,lines=lines,staging=staged))
 metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters']
 p=parse_elf(elf)['phdrs'];seg=p[3];rel=p[2]
 records=list(struct.iter_unpack('<II',elf[rel[1]:rel[1]+rel[4]]))
 pr=dict(added_segment_file_offset=seg[1],added_segment_bytes=seg[4],extra_relocation_records=[x for x in records if x[1]>>8&255==3])
 text='АOK БEnd Й     Learn Skills';positions=[]
 for base in (0x08804000,0x0890c000):
  xs=[]
  for i,ch in enumerate(text):
   c=PositionCPU(elf,pr,base);row=0x09000000;obj=0x09010000;callback=base+0x1000
   c.store(0x09effe00,b'G'*1024);c.set('sp',0x09f00000)
   c.store(row,bytes(0x4c)+encode_dialogue(text,text)[0]+b'\0\0')
   for r,v in [('s4',row),('s3',i),('a0',obj),('a2',callback)]:c.set(r,v)
   c.fp[15]=int.from_bytes(struct.pack('<f',120.),'little');calls=[]
   def position(m):calls.append(struct.unpack('<f',struct.pack('<I',m.fp[12]))[0]);return {}
   c.native_handlers={callback:position};c.run(0x347be0-CODE_VA)
   x=120+sum(metrics[k]['proposed_advance_pixels']*.875 if k in metrics else 13 for k in text[:i])
   if ch in metrics:x+=(3-(metrics[ch]['ink_bounds_inclusive'][0] if metrics[ch]['ink_bounds_inclusive'] else 0))*.875
   assert calls==[x],(base,i,calls,x);xs.append(x)
   assert c.bytes(0x09effe00,0x1a0)==b'G'*0x1a0 and c.bytes(0x09f00000,0x200)==b'G'*0x200
  icon=text.index('Й');learn=text.index('Learn');assert xs[learn]-xs[icon]>=30
  assert max(xs)<480
  positions.append(dict(base=hex(base),select_x=xs[icon],learn_x=xs[learn],end=max(xs)))
 return dict(passed=True,native_formatter_cases=rows,position_cases=len(text)*2,positions=positions,buffer_guards=True,exact_screen_runtime_verified=False)

if __name__=='__main__':
 elf,_=prepare_elf()
 with GameSource(BASE/'Summon_Night_3_EN_0.1.59.iso') as s:r=verify(elf,s.resource('02.DAT',3))
 print(json.dumps(r,indent=2))
