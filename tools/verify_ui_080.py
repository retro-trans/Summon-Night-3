"""Execute the new dispatch at two relocated bases and stage every condition help."""
import json,struct
from sn3_archive import ROOT,GameSource
from ui_fix_080 import BASE,TEXT,prepare_tables,prepare_elf
from verify_guards_049 import AliasCPU,stage
from verify_guards_050 import GuardCPU
from list_vwf_020 import name_pairs
from dialogue_encoding import encode_dialogue

def verify():
 with GameSource(BASE/'Summon_Night_3_EN_0.1.79.iso') as s:tables,_,_,tr=prepare_tables(s)
 elf,r=prepare_elf(tables[3]);cfg=json.loads(TEXT.read_text());cpu=AliasCPU(elf,tables[3]);hc=0
 for e in cfg['entries']:
  if e['table']!=46 or e['slot'] not in (8,13,14,15,16):continue
  ls=e['english'];result=stage(cpu,b''.join(encode_dialogue(t,'')[0]+bytes(2) for t in ls)+bytes(2))
  assert result['glyphs']==sum(map(len,ls)) and result['rows']==len(ls) and result['max_slot']<54,(e,result);hc+=1
 cases=[(src,dst,True) for src,dst in name_pairs()[0]]+[(encode_dialogue(t,'')[0],encode_dialogue(t,'')[0],True) for t in cfg['popup_vwf_names']]+[(encode_dialogue('CustomName','')[0],encode_dialogue('CustomName','')[0],False)]
 runs=prof_cases=pool_cases=0
 for base in (0x08804000,0x0890c000):
  m=GuardCPU(elf,r,base);owner=0x09400000;rows=0x09700000;ptr=0x09800000;stop=0x08801234;code=base+int(r['code_address'],16)
  for src,dst,matched in cases:
   m.store(ptr,src+bytes(4));m.store(owner,bytes(0x100));m.write(owner+0x30,rows);m.write(rows,ptr);m.write(owner+0x34,0x09710000);m.write(owner+0x3c,1);m.write(owner+0x64,9,1)
   m.r=[0x12500000+i for i in range(32)];m.r[0]=0;m.r[4:8]=[owner,99,88,77];m.r[29]=0x09f00000;m.r[31]=stop;before=m.r.copy();pc=code+r['labels']['draw'];calls=0
   for _ in range(100000):
    if pc==stop:break
    if pc==base+r['prior_draw']:
     assert m.r[4:8]==before[4:8] and m.read(owner+0x34)==(0 if matched else 0x09710000)
     dp=m.read(rows);actual=bytes(m.read(dp+i,1) for i in range(len(dst)));assert actual==dst
     calls+=1;pc=m.r[31];continue
    pc=m.step(pc)
   assert pc==stop and calls==1 and m.r[16:24]==before[16:24] and m.r[28:32]==before[28:32] and m.read(owner+0x34)==0x09710000 and m.read(owner+0x64,1)==9
   runs+=1
  for skill,lines,accepted in [(0xbdb,['Hit+30% CR+10%', 'Cntr+10%','M: Snipe','M: Snipe'],True),(0xbdb,['Hit+30% CR+10%','Cntr+10% M: Snipe ','M: Snipe'],True),(0xbd1,['AT+25 CR+10%','Cntr+10%','M: Rare CR KO','M: Rare CR KO'],True),(0xbd3,['AT+20 CR+10%','Cntr+10%','M: Foe cntr down','M: AT+5'],True),(0xbd0,['Original unrelated help.'],False),(0xbdb,['X'*60],False)]:
   payload=b''.join(encode_dialogue(t,'')[0]+bytes(2) for t in lines)+bytes(2);m.store(ptr,payload)
   m.r=[0x12500000+i for i in range(32)];m.r[0]=0;m.r[4:10]=[owner,ptr,11,skill,123,456];m.r[29]=0x09f00000;m.r[31]=stop;before=m.r.copy();pc=code+r['labels']['prof_reflow'];calls=0
   for _ in range(100000):
    if pc==stop:break
    if pc==base+r['prior_guard']:
     assert m.r[4]==owner and m.r[6:10]==before[6:10]
     if accepted:
      dp=m.r[5];ls=[]
      for _ in range(3):
       raw=bytearray()
       while m.read(dp,2):raw.extend(m.read(dp,2).to_bytes(2,'little'));dp+=2
       dp+=2
       if not raw:break
       ls.append(bytes(raw))
      assert max(map(lambda x:len(x)//2,ls))<=27 and sum(len(x)//2 for x in ls)<=54
      result=stage(cpu,b''.join(x+bytes(2) for x in ls)+bytes(2));assert result['glyphs']==sum(len(x)//2 for x in ls)
      if skill==0xbdb:assert sum(x.count(encode_dialogue('Snipe','')[0]) for x in ls)==1,ls
     else:assert m.r[5]==ptr
     calls+=1;pc=m.r[31];continue
    pc=m.step(pc)
   assert pc==stop and calls==1 and m.r[16:24]==before[16:24] and m.r[28:32]==before[28:32];prof_cases+=1
  # No texture or descriptor allocation grows. Merge only a free, contiguous
  # pair; retain existing/owned large strips and reject occupied/cross-row pairs.
  for count,descs,owned,merged in [(12,[(0,128,8,0),(128,128,8,0)],0,True),(12,[(0,128,16,0),(256,128,8,0)],0,False),(12,[(0,128,8,1),(128,128,8,0)],0,False),(12,[(384,128,8,0),(0,144,8,0)],0,False),(7,[(0,128,8,0),(128,128,8,0)],0,False),(12,[(0,128,8,0),(128,128,8,0)],16,False)]:
   font=0x09500000;pool=0x09600000;original=b''.join(struct.pack('<4H',*d) for d in descs);m.store(pool,original);m.write(base+0x22a340,font);m.write(font+0xcac+0x1c,pool);m.write(font+0xcac+0x20,len(descs));m.write(owner+0xc0,0)
   if owned:m.write(owner+0xc0,pool+64);m.write(pool+68,owned,2)
   m.r=[0x12500000+i for i in range(32)];m.r[0]=0;m.r[4:7]=[owner,ptr,1];m.r[29]=0x09f00000;m.r[31]=stop;before=m.r.copy();pc=code+r['labels']['learn_bind'];calls=0
   for _ in range(10000):
    if pc==stop:break
    if pc==base+0x1e4ac8:m.r[2]=count;pc=m.r[31];continue
    if pc==base+0x347b5c:assert m.r[4:7]==before[4:7];calls+=1;pc=m.r[31];continue
    pc=m.step(pc)
   got=bytes(m.read(pool+i,1) for i in range(len(original)))
   assert pc==stop and calls==1 and m.r[16:24]==before[16:24] and m.r[28:32]==before[28:32]
   if merged:assert struct.unpack('<8H',got)==(0,128,16,0,128,128,0,1)
   else:assert got==original
   pool_cases+=1
  # Exercise the rebuilt protected tail, including the expanded condition pools.
  source=0x09600000;size=r['static_arena_bytes'];tail=source+r['static_tail_offset'];arena=base+r['static_arena_address'];context=base+r['static_arena_context']
  m.store(source,tables[3]);m.store(arena-8,b'G'*8+bytes(size)+b'G'*8);m.r=[0]*32;m.r[4:6]=[owner,source];m.r[29]=0x09f00000;m.r[31]=stop;pc=code+r['labels']['static_bind'];calls=0
  for _ in range(1000):
   if pc==stop:break
   if pc==base+0x1c2b80:
    assert m.r[4:7]==[arena,tail,size];m.store(arena,tables[3][r['static_tail_offset']:]);m.r[2]=arena;pc=m.r[31];continue
   if pc==base+0x197f90:calls+=1;pc=m.r[31];continue
   pc=m.step(pc)
  assert pc==stop and calls==1 and m.read(context)==tail and bytes(m.read(arena+size+i,1) for i in range(8))==b'G'*8
 return dict(passed=True,condition_fields=132,mastery_fields=13,actual_help_staging_cases=hc,relocated_dispatch_cases=runs,proficiency_reflow_cases=prof_cases,skill_strip_allocation_cases=pool_cases,load_bases=2,protected_tail_cases=2,native_translation_groups=len(r['entries']),summon_name_pairs=r['summon_name_pairs'],numeric_fields_and_original_pools_preserved=True)

if __name__=='__main__':
 result=verify();dest=ROOT/'work/ui/ui_0.1.80';dest.mkdir(parents=True,exist_ok=True);(dest/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))


