"""System menu labels and all conditional Status help branches on 0.1.43."""
import json,struct,hashlib
from PIL import Image
from sn3_archive import ROOT,parse_index,child,GameSource
from sn3_repack import repack
from menu_art_015 import descend,replace_tree
from menu_code_020 import append
from stages_pupil_names import parse_elf
from dialogue_encoding import encode_dialogue
from sn3_ui_textures import texture_records,decode_texture
from setup_ui_patch import encode_texture
from verify_descriptions_021 import CPU
BASE=ROOT/'work/output/0.1.43'
ART=ROOT/'work/ui/system_0.1.44'
TARGETS=ROOT/'work/translation/en/system_0.1.44/targets.json'
sha=lambda b:hashlib.sha256(b).hexdigest()

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();rows=json.loads(TARGETS.read_text())['entries'];payload=bytearray();entries=[]
 for row in rows:
  raw,_=encode_dialogue(row['text'],'');assert len(raw)//2<=27
  payload.extend(bytes(-len(payload)%4));entries.append(dict(row,table_offset=len(payload)));payload.extend(raw+b'\0\0\0\0')
 def emit(a):a.ret()
 data,report=append(old,emit,{},bytes(payload));out=bytearray(data);base=int(report['code_address'],16)+report['labels']['table']
 for e in entries:
  address=base+e['table_offset'];source=e['offset']-192;hi,lo=e['high']+192,e['low']+192
  w1,w2=struct.unpack_from('<I',out,hi)[0],struct.unpack_from('<I',out,lo)[0]
  assert w1==0x3c060022 and w2>>16==0x24c6
  assert ((w1&65535)<<16)+((w2&65535)-65536)==source
  struct.pack_into('<I',out,hi,(w1&0xffff0000)|((address+0x8000)>>16))
  struct.pack_into('<I',out,lo,(w2&0xffff0000)|(address&65535))
  e['new_address']=hex(address)
 return bytes(out),dict(entries=entries,append=report,conditional_branches=4)

def prepare_tables(source):
 catalog=json.loads((ROOT/'work/ui/interface_graphics.index.json').read_text());atlas=json.loads((ART/'atlas.json').read_text());im=Image.open(ART/atlas['image']).convert('RGBA')
 targets={};report=[];native_dir=ART/'native';native_dir.mkdir(exist_ok=True)
 with GameSource(ROOT/'work/source/original.iso') as original:
  for row in atlas['rows']:
   path=row['path'];before=descend(original.resource('02.DAT',path[0]),path[1:]);h=sha(before)
   group=next(g for g in catalog['resources'] if g['source_sha256']==h)
   rr=texture_records(before);assert len(rr)==1;old=decode_texture(before,rr[0]);assert old.size==(112,24)
   art=im.crop(row['crop']).resize(old.size,Image.Resampling.LANCZOS);art.putalpha(old.getchannel('A'))
   after,native,_=encode_texture(before,rr[0],art);assert len(after)==len(before)
   assert native.getchannel('A').tobytes()==old.getchannel('A').tobytes()
   uses=[]
   for o in group['occurrences']:
    assert o['bank']=='02.DAT';p=tuple(o['path']);current=descend(source.resource('02.DAT',p[0]),p[1:]);assert current==before
    targets[p]=after;uses.append(o['id'])
   name=row['label'].lower()+'_'+str(row['state'])+'.png';native.save(native_dir/name)
   report.append(dict(**row,occurrences=uses,source_sha256=h,output_sha256=sha(after),native=name))
 packs={n:replace_tree(source.resource('02.DAT',n),{p[1:]:v for p,v in targets.items() if p[0]==n}) for n in {p[0] for p in targets}}
 return {3:source.resource('02.DAT',3),**packs},{},source.resource('00.DAT',44),dict(units=[],tables=[],graphics=report,texture_copies=len(targets))

def verify(elf,static):
 import unicodedata
 cases=[]
 for skills in [False,True]:
  for summon in [0,1,2]:
   c=CPU(elf,static);owner=0x500000;buf=owner+0xeef0;stack=0x700000
   c.r[17]=owner;c.r[29]=stack;c.mem[buf-16:buf+172+16]=b'G'*204;pc=0x160bfc
   for _ in range(100000):
    if pc==0x160cd4:break
    if pc==0x1c2bc0:
     a,v,n=c.r[4:7];c.mem[a:a+n]=bytes([v&255])*n;c.r[2]=a;pc=c.r[31]
    elif pc in [0x599b0,0x570fc,0x599dc]:
     c.r[2]=int({0x599b0:skills,0x570fc:summon!=0,0x599dc:summon==2}[pc]);pc=c.r[31]
    elif pc==0x1e4ac8:c.r[2]=c.strlen(c.r[4]);pc=c.r[31]
    elif pc==0x1e4b50:
     a,b,n=c.r[4:7];c.mem[a:a+n*2]=c.mem[b:b+n*2];c.r[2]=a;pc=c.r[31]
    else:pc=c.step(pc)
   else:raise AssertionError(('System writer limit',hex(pc)))
   assert c.mem[buf-16:buf]==b'G'*16 and c.mem[buf+172:buf+188]==b'G'*16
   lines=[];p=buf
   while c.read(p,2):
    n=c.strlen(p);lines.append(unicodedata.normalize('NFKC',c.mem[p:p+n*2].decode('cp932')));p+=n*2+2
   expected=['Status/gear; learn skills.' if skills else 'View status; change gear.']
   if summon:expected.append('Train summoned units.' if summon==2 else 'View summoned unit status.')
   assert lines==expected,(skills,summon,lines)
   assert len(lines)<=2 and max(map(len,lines))<=27 and sum(map(len,lines))<=54
   cases.append(dict(skills=skills,summon=summon,lines=lines,guards=True))
 from brave_fix_042 import verify as brave
 return dict(native_system_help=cases,brave_regression=brave(elf,static))

if __name__=='__main__':
 elf,_=prepare_elf()
 with GameSource(next(BASE.glob('*.iso'))) as src:tables,_,_,r=prepare_tables(src)
 r['verification']=verify(elf,tables[3]);print(json.dumps(r,indent=2))
