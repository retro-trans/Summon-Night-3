"""Read-only discovery for the reported UI."""
import struct,json
from pathlib import Path
from sn3_archive import ROOT,GameSource,parse_index,child
from sn3_codec import decompress
from sn3_ui_textures import texture_records,decode_texture
from battle_elf_refs import references
from font_patch import REG
NAMES={v:k for k,v in REG.items()}
def asm(w):
 op=w>>26;rs=NAMES[w>>21&31];rt=NAMES[w>>16&31];rd=NAMES[w>>11&31];imm=w&65535;imm=imm-65536 if imm>=32768 else imm
 if op in (2,3):return ('jal' if op==3 else 'j')+' '+hex((w&0x3ffffff)*4)
 if op in (4,5):return ['beq','bne'][op-4]+f' {rs},{rt},{imm}'
 if op in (9,15,32,33,35,36,37,40,41,43):return {9:'addiu',15:'lui',32:'lb',33:'lh',35:'lw',36:'lbu',37:'lhu',40:'sb',41:'sh',43:'sw'}[op]+f' {rt},{imm}({rs})'
 if op==0:return f'R{w&63:x} {rd},{rs},{rt},sa{w>>6&31}'
 return hex(w)
def dump(elf,start,end):
 for va in range(start,end,4):
  w=struct.unpack_from('<I',elf,va+192)[0];print(hex(va),asm(w))
if __name__=='__main__':
 elf=(ROOT/'work/output/0.1.60/EBOOT.elf').read_bytes()
 ref,_,_=references(elf)
 for va in [0x22943c,0x22952c]:print(hex(va),ref.get(va))
 dump(elf,1287252-40,1287356+160)
 with GameSource(ROOT/'work/output/0.1.60/Summon_Night_3_EN_0.1.60.iso') as s:
  for n,key,cs in [(1087,0x9831,[1,2])]:
   raw=s.resource('02.DAT',n);d,u=decompress(raw,key);ix=parse_index(d,len(d))
   for c in cs:
    b=child(d,ix,c);t=texture_records(b)
    print(n,c,[(v['width'],v['height']) for v in t]);decode_texture(b,t[0]).save(ROOT/f'work/ui/report_0.1.61/yard_{n}_{c}_source.png')
  from PIL import Image,ImageDraw
  raw=s.resource('02.DAT',35);ix=parse_index(raw,len(raw));ims=[]
  for e in ix['entries']:
   b=child(raw,ix,e['id'])
   try:rows=texture_records(b)
   except ValueError:continue
   for row in rows:
    if row['width']>256 or row['height']>128:continue
    try:im=decode_texture(b,row)
    except ValueError:continue
    ims.append((f"35/{e['id']}/{row['number']}",im))
  for page,begin in enumerate(range(0,len(ims),48)):
   out=Image.new('RGBA',(1000,960),(80,80,80,255));draw=ImageDraw.Draw(out)
   for k,(label,im) in enumerate(ims[begin:begin+48]):
    x=k%4*250;y=k//4*80;draw.text((x,y),label);out.alpha_composite(im,(x,y+18))
   out.save(ROOT/f'work/ui/report_0.1.61/map35_{page}.png')
  print('map pages',len(ims))
