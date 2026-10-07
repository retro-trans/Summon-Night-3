"""Execute native skill help, check retained stat descriptions and startup pixels."""
import argparse,json,struct,unicodedata
from categories_fix_070 import ROOT,BASE,prepare_elf,prepare_tables
from sn3_archive import GameSource,parse_index,child
from verify_guards_057 import AliasCPU,stage
from dialogue_encoding import encode_dialogue
from menu_hotfix_017 import lines_at
from sn3_ui_textures import texture_records,decode_texture
norm=lambda b:unicodedata.normalize('NFKC',b.decode('cp932'))

def native(c,skill,record,levels=1,level=1,master=False,charges=False):
 owner=0x500000;buf=owner+0x19f0;definition=0x5a0000;rec=0x5a1000;params=0x5a2000
 c.mem[rec:rec+48]=record;c.write(rec+44,params if skill>=0xbd1 else 0);c.mem[params:params+8]=bytes(8)
 c.write(definition,levels);c.write(definition+4,rec)
 c.mem[buf-32:buf+210]=b'G'*242;c.r=[0]*32;c.r[4]=owner;c.r[6]=skill;c.r[9]=master;c.r[10]=level
 c.r[29]=0x700000;c.r[31]=0x7ffff0;pc=0x65f2c
 c.r[7]=0x540000;c.r[8]=charges;c.mem[0x540000:0x540100]=bytes(256)
 for _ in range(50000):
  if pc==0x7ffff0:break
  if pc==0x198d40:c.r[2]=definition;pc=c.r[31]
  elif pc==0x198d88:c.r[2]=rec;pc=c.r[31]
  elif pc==0x4587c:c.r[2]=999;pc=c.r[31]
  elif pc==0x1c2bc0:
   a,v,n=c.r[4:7];c.mem[a:a+n]=bytes([v&255])*n;c.r[2]=a;pc=c.r[31]
  elif pc==0x1e4ac8:c.r[2]=c.strlen(c.r[4]);pc=c.r[31]
  elif pc==0x1e4b50:
   a,b,n=c.r[4:7];c.mem[a:a+n*2]=c.mem[b:b+n*2];c.r[2]=a;pc=c.r[31]
  elif pc==0x1e4dd8:
   raw=encode_dialogue(str(c.r[4]),'')[0];c.mem[0x5b0000:0x5b0100]=bytes(256);c.mem[0x5b0000:0x5b0000+len(raw)]=raw;c.r[2]=0x5b0000;pc=c.r[31]
  else:pc=c.step(pc)
 else:raise AssertionError(('Native skill instruction budget',hex(pc)))
 assert c.mem[buf-32:buf]==b'G'*32 and c.mem[buf+178:buf+210]==b'G'*32
 pos=buf;rows=[]
 for _ in range(3):
  n=c.strlen(pos);assert n<=27,(skill,n,norm(c.mem[pos:pos+n*2]));rows.append(norm(c.mem[pos:pos+n*2]));pos+=n*2+2
 while rows and not rows[-1]:rows.pop()
 assert sum(len(s) for s in rows)<=54,rows
 return rows

def verify():
 elf,er=prepare_elf()
 with GameSource(BASE/'Summon_Night_3_EN_0.1.69.iso') as source:
  packs,_,_,tr=prepare_tables(source);st=packs[3];ix=parse_index(st,len(st));c=AliasCPU(elf,st)
  # Execute all 13 equipment skill IDs through their actual switch and native wrapper.
  cases=[]
  for skill in range(0xbd1,0xbde):
   rec=bytearray(48)
   # Also exercise a full three-digit probability with percent suffix.
   if skill in (0xbd9,0xbd5):struct.pack_into('<I',rec,12,63<<22)
   elif skill in (0xbd2,0xbd3):struct.pack_into('<I',rec,12,63<<12)
   rows=native(c,skill,rec);cases.append(dict(skill=skill,rows=rows))
   assert not any(any('\u3040'<=ch<='\u30ff' or '\u3400'<=ch<='\u9fff' for ch in s) for s in rows),cases[-1]
  transform=[]
  for charges in (False,True):
   rows=native(c,1010,bytes(48),charges=charges);assert rows[0]=='Dragon/humanoid transform.'
   if charges:assert rows[1]=='Uses left: 999'
   transform.append(dict(charges_shown=charges,rows=rows))
  # All common stat/resistance help pointers must still target current English.
  table=child(st,ix,34);meta=json.loads((ROOT/'work/translation/en/categories_0.1.68/targets.json').read_text())
  stat=[]
  for e in meta['entries']:
   if e['table']!=34 or e['slot']!=9:continue
   if not any('/level' in s for s in e['english']):continue
   for row in e['records']:
    rec=bytearray(table[4+row*48:4+(row+1)*48]);ptr=struct.unpack_from('<I',rec,36)[0]
    raw=lines_at(table,ptr)[0];english=[norm(x) for x in raw];assert english==e['english'],(row,english)
    address=0x5c0000;payload=b''.join(x+b'\0\0' for x in raw)+b'\0\0';c.mem[address:address+len(payload)]=payload;struct.pack_into('<I',rec,36,address);struct.pack_into('<I',rec,40,0)
    rows=native(c,2000,rec);assert [s for s in rows if s.strip()]==english,(row,rows,english)
    stat.append(dict(record=row,english=english))
  assert any(e['english']==['Max MP +10/level.'] for e in stat)
  pack=packs[25];p=child(pack,parse_index(pack,len(pack)),0);im=decode_texture(p,texture_records(p)[0]);assert im.size==(480,272)
  im.save(ROOT/'work/ui/categories_0.1.70/notice_native.png')
  return dict(passed=True,new_native_fragments=len(er['entries']),native_equipment_cases=cases,native_transform_cases=transform,retained_native_stat_cases=stat,startup_notice=tr['startup_notice'],boundary_stubs=['definition and record lookup','remaining use count','memset','U16 length/copy','integer formatting'],actual_skill_type_switch_and_wrap=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');p.add_argument('--report');a=p.parse_args()
 if not a.execute:print(json.dumps(dict(mode='preview',scope='Native skill cases, existing stat helps and startup palette round trip.')))
 else:
  r=verify();print(json.dumps(r,indent=2))
  if a.report:(ROOT/a.report).write_text(json.dumps(r,indent=2)+'\n')
