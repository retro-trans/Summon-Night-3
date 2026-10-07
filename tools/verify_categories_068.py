"""Execute native skill help formatting and shared staging for category text."""
import argparse,json,struct,unicodedata
from categories_fix_068 import ROOT,BASE,TEXT,MAP,prepare_elf,prepare_tables
from sn3_archive import GameSource,parse_index,child
from dialogue_encoding import encode_dialogue
from verify_guards_057 import AliasCPU,stage
from menu_hotfix_017 import lines_at
from inspect_categories_068 import JP

def native_skill(c,help_raw,master_raw):
 owner=0x500000;buf=owner+0x19f0;hs=0x580000;ms=0x590000;definition=0x5a0000;record=0x5a1000
 c.mem[hs:hs+512]=bytes(512);c.mem[ms:ms+512]=bytes(512)
 c.mem[hs:hs+len(help_raw)]=help_raw;c.mem[ms:ms+len(master_raw)]=master_raw
 c.mem[record:record+48]=bytes(48);c.write(record+40,ms if master_raw else 0)
 c.write(definition,1);c.write(definition+4,record)
 c.mem[buf-32:buf+210]=b'G'*242;c.r=[0]*32;c.r[4]=owner;c.r[6]=1;c.r[9]=bool(master_raw)
 c.r[29]=0x700000;c.r[31]=0x7ffff0;pc=0x65f2c
 for _ in range(30000):
  if pc==0x7ffff0:break
  if pc==0x65fc4:
   c.r[16]=hs;c.write(c.r[29]+0x28,buf);c.write(c.r[29]+0x2c,definition);pc=0x66b08
  elif pc==0x1c2bc0:
   a,v,n=c.r[4:7];c.mem[a:a+n]=bytes([v&255])*n;c.r[2]=a;pc=c.r[31]
  elif pc==0x1e4ac8:c.r[2]=c.strlen(c.r[4]);pc=c.r[31]
  elif pc==0x1e4b50:
   a,b,n=c.r[4:7];c.mem[a:a+n*2]=c.mem[b:b+n*2];c.r[2]=a;pc=c.r[31]
  else:pc=c.step(pc)
 else:raise AssertionError(('native skill budget',hex(pc)))
 assert c.mem[buf-32:buf]==b'G'*32 and c.mem[buf+178:buf+210]==b'G'*32
 rows=[];pos=buf
 # Empty middle rows are intentional native padding before mastery.
 for _ in range(3):
  n=c.strlen(pos);rows.append(c.mem[pos:pos+n*2]);pos+=n*2+2
  if pos>=buf+178:raise AssertionError('writer crossed output')
 while rows and not rows[-1]:rows.pop()
 return rows

def verify():
 elf,er=prepare_elf();metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters']
 with GameSource(BASE/'Summon_Night_3_EN_0.1.67.iso') as src:
  packs,_,_,tr=prepare_tables(src);st=packs[3];ix=parse_index(st,len(st));c=AliasCPU(elf,st)
  entries=json.loads(TEXT.read_text())['entries'];staged=[];names=[];profiles=[]
  for e in entries:
   b=child(st,ix,e['table']);p=struct.unpack_from('<I',b,e['pointer_fields'][0])[0];raw=lines_at(b,p)[0]
   if e['slot']==8:raw=raw[:1]
   ls=[unicodedata.normalize('NFKC',s.decode('cp932')) for s in raw]
   wanted=[unicodedata.normalize('NFKC',encode_dialogue(s,s)[0].decode('cp932')) for s in e['english']]
   assert ls==wanted,(e['table'],e['records'],ls)
   assert not any(JP.search(s) for s in ls)
   if e['slot']==8:
    text=e['english'][0];w=sum(metrics[x]['proposed_advance_pixels'] for x in text)*.875
    assert len(text)<=16 and w<=108,(e['table'],e['records'],text,w);names.append(w)
   elif e['table']==32:
    assert len(ls)==1 and len(ls[0])<=32
   else:
    payload=b''.join(s+b'\0\0' for s in raw)+b'\0\0';r=stage(c,payload)
    assert r['glyphs']==sum(len(s)//2 for s in raw),(e,r)
    assert r['rows']<=3 and r['max_slot']<54
    staged.append(r)
    if e['table']==12:assert len(raw)<=2;profiles.append(e['records'][0])
  combos=[];problems=[];meta=json.loads((ROOT/'work/translation/en/interface.index.json').read_text())['tables']
  touched={(e['table'],rec) for e in entries if e['table'] in (28,31,34) for rec in e['records']}
  for n,rec in sorted(touched):
   b=child(st,ix,n);stride=next(t['record_stride'] for t in meta if t['resource_path']==[3,n]);ptrs=[struct.unpack_from('<I',b,4+rec*stride+slot*4)[0] for slot in (9,10)]
   rr=[lines_at(b,p)[0] if p else [] for p in ptrs]
   help_raw=b''.join(s+b'\0\0' for s in rr[0])+b'\0\0';master_raw=b''.join(s+b'\0\0' for s in rr[1])+b'\0\0' if rr[1] else b''
   rows=native_skill(c,help_raw,master_raw);cells=sum(len(s)//2 for s in rows)
   if len(rows)>3 or max([len(s)//2 for s in rows],default=0)>27 or cells>54:problems.append(dict(table=n,record=rec,english=[unicodedata.normalize('NFKC',s.decode('cp932')) for s in rows],cells=cells))
   expected=[s for group in rr for s in group]
   if [s for s in rows if s and s.decode('cp932').strip()]!=expected:problems.append(dict(table=n,record=rec,issue='truncated help/master',expected=[unicodedata.normalize('NFKC',s.decode('cp932')) for s in expected]))
   payload=b''.join(s+b'\0\0' for s in rows)+b'\0\0';r=stage(c,payload)
   # Empty padding rows terminate generic staging; native draw count still safe.
   assert r['max_slot']<54
   combos.append(dict(table=n,record=rec,cells=cells,rows=len(rows)))
  original=(BASE/'EBOOT.elf').read_bytes();a=parse_index(st,len(st))
  # Existing code/arena and already-correct SELECT hint must be byte identical.
  from stages_pupil_names import parse_elf
  os=parse_elf(original)['phdrs'][3];ns=parse_elf(elf)['phdrs'][3]
  assert original[os[1]:os[1]+os[4]]==elf[ns[1]:ns[1]+os[4]] and ns[6]==7
  maps=json.loads(MAP.read_text())['entries'];assert len(maps)==24
  map_widths=[sum(metrics[c]['proposed_advance_pixels'] for c in e['english'])*.875 for e in maps]
  assert max(map_widths)<=96 and max(len(e['english']) for e in maps)<=16,map_widths
  return dict(passed=not problems,problems=problems,table_entries=len(entries),translated_fields=601,reformatted_english_fields=12,profile_records=len(profiles),skill_names=len(names),max_name_pixels=max(names),shared_staging_cases=len(staged),native_help_master_cases=len(combos),max_combined_cells=max(x['cells'] for x in combos),map_names=len(maps),map_pointer_fields=sum(len(e['pointer_fields']) for e in maps),max_map_pixels=max(map_widths),existing_code_identical=True,numeric_fields_unchanged=True,limits=['Native category formatter branch tested without synthesizing stat/level additions. Exact reported screens require the matching normal save.'],combos=combos)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--report');a=p.parse_args();r=verify();print(json.dumps({k:v for k,v in r.items() if k!='combos'},indent=2))
 if a.report:
  path=(ROOT/a.report).resolve();assert ROOT in path.parents;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(r,indent=2)+'\n')
