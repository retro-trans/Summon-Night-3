"""Native Cooking staging and relocated VWF position checks, without an emulator save."""
import json,struct,unicodedata
from cooking_046 import *
from verify_descriptions_021 import CPU as NativeCPU
from verify_menu_vwf_020 import CPU
from font_patch import CODE_VA

def verify(elf,static):
 targets=json.loads((FOLDER/'targets.json').read_text())['entries'];index=json.loads((ROOT/'work/translation/en/interface.index.json').read_text());si=parse_index(static,len(static));metrics=collect()[0]['characters'];checks=[];recipes=[]
 for e in targets:
  t=next(t for t in index['tables'] if t['resource_path']==[3,e['table']]);row=next(r for r in t['strings'] if r['id']==e['id']);tb=child(static,si,e['table']);raw=[encode_dialogue(s,'')[0] for s in e['lines']];payload=b''.join(s+b'\0\0' for s in raw)+b'\0\0'
  for ref in row['references']:
   p=struct.unpack_from('<I',tb,ref['pointer_field_offset'])[0];assert tb[p:p+len(payload)]==payload
  widths=[sum(metrics[c]['proposed_advance_pixels'] for c in s)*.875 for s in e['lines']]
  if e['kind']=='name':assert len(e['lines'])==1 and len(e['lines'][0])<=16 and widths[0]<=(102 if e['table']==20 else 138),(e,widths)
  elif e['kind']=='help':assert len(raw)<=2 and max(map(len,raw))<=54 and sum(map(len,raw))<=108
  else:
   assert len(raw)==6 and all(1<=len(s)//2<=13 for s in raw);assert all(s.startswith('    ') for s in e['lines'][:3]);recipes.append(e)
  checks.append(dict(id=e['id'],kind=e['kind'],widths=widths))
 # Execute the unchanged native per-glyph staging loop; graphic binding/render
 # calls are boundaries. It must populate exactly the requested row/column slots.
 c=NativeCPU(elf,static);owner=0x500000;src=0x600000;guard=owner+0x4770;native_cases=0
 for e in recipes:
  raw=[encode_dialogue(s,'')[0] for s in e['lines']];payload=b''.join(s+b'\0\0' for s in raw)+b'\0\0';c.mem[src:src+len(payload)]=payload;c.mem[guard-16:guard+156+16]=b'G'*188;c.mem[guard:guard+156]=bytes(156)
  c.r=[0]*32;c.r[20]=owner;c.r[21]=src;pc=0x12287c;bound=[]
  for _ in range(10000):
   if pc==0x122944:break
   if pc==0x1cbe48:
    obj,p,count,style=c.r[4:8];assert count==style==1;slot=(obj-owner-0x330)//0xe0;assert 0<=slot<78;bound.append((slot,c.read(p,2)));pc=c.r[31]
   elif pc==0x1228d4:pc=0x12291c # only scale/color/visibility virtual calls
   else:pc=c.step(pc)
  else:raise AssertionError('Cooking staging instruction limit')
  expected=[(r*13+i,int.from_bytes(s[i*2:i*2+2],'little')) for r,s in enumerate(raw) for i in range(len(s)//2)]
  assert bound==expected and c.mem[guard-16:guard]==b'G'*16 and c.mem[guard+156:guard+172]==b'G'*16
  native_cases+=1
 _,report=prepare_elf();helper=report['recipe_position'];cases=0
 def sf(m,n,v):m.fp[n]=int.from_bytes(struct.pack('<f',v),'little')
 def ff(m,n):return struct.unpack('<f',struct.pack('<I',m.fp[n]))[0]
 # Distinct source lines, every character, both relocated load bases.
 linecases=sorted({(r,s) for e in recipes for r,s in enumerate(e['lines'])})
 linecases += [(5,'AB?'),(4,'あAB')]
 for base in [0x08804000,0x0890c000]:
  m=CPU(elf,helper,base);obj=0x09000000;cb=base+0x1000;m.store(obj,bytes(0x4900));m.store(0x09effe00,b'G'*1024)
  for row,text in linecases:
   raw=encode_dialogue(text,'')[0];m.store(obj+0x4770+row*26,raw+bytes(28-len(raw)))
   for col in range(len(text)):
    m.reg=[0]*32;m.fp=[0]*32;m.set('sp',0x09f00000)
    for n in list(range(16,29))+[30]:m.reg[n]=0x55500000+n
    m.set('s0',obj);m.set('s2',row);m.set('s3',col);m.set('s4',row*13);m.set('a0',obj+0x100);m.set('a2',cb)
    sf(m,12,261+col*14);sf(m,13,65+row*18);sf(m,14,1);sf(m,15,77);sf(m,20,2)
    saved=m.reg[16:31].copy();fp=m.fp.copy();seen=[]
    m.native_handlers={cb:lambda q:(seen.append((q.reg[4],ff(q,12),ff(q,13))) or {})}
    m.run(int(helper['code_address'],16)-CODE_VA+helper['labels']['recipe_position'])
    prefix=0
    for i,ch in enumerate(text[:col]):prefix+=14 if (row<3 and i<4 and ch==' ') or ch not in metrics else metrics[ch]['proposed_advance_pixels']*.875
    cur=metrics.get(text[col]);correction=(3-(cur['ink_bounds_inclusive'][0] if cur['ink_bounds_inclusive'] else 0))*.875 if cur else 0
    assert seen==[(obj+0x100,261+prefix+correction,65+row*18)],(row,text,col,seen,prefix,correction)
    assert m.reg[16:24]+m.reg[26:31]==saved[:8]+saved[10:] and m.fp[13:16]==fp[13:16] and m.fp[20:]==fp[20:], ([(i+16,hex(a),hex(b)) for i,(a,b) in enumerate(zip(m.reg[16:31],saved)) if a!=b],[(i,hex(a),hex(b)) for i,(a,b) in enumerate(zip(m.fp,fp)) if a!=b])
    assert m.bytes(0x09effe00,0x1b0)==b'G'*0x1b0 and m.bytes(0x09f00000,0x200)==b'G'*0x200
    cases+=1
 for site in VWF_SITES:assert struct.unpack_from('<I',elf,site+192)[0]==3<<26|0x347b5c>>2
 # All original object counts and line/column bounds remain exact.
 old=(BASE/'EBOOT.elf').read_bytes()
 for site in [0x121f7c,0x121f8c,0x121f94,0x122628,0x122640,0x12288c,0x122898,0x122930]:assert elf[site+192:site+196]==old[site+192:site+196]
 from system_menu_044 import verify as verify_system
 return dict(text_checks=checks,native_staging_cases=native_cases,position_cases=cases,load_bases=2,original_pool_and_grid_unchanged=True,gameplay_fields_unchanged=True,prior_regression=verify_system(elf,static))
if __name__=='__main__':
 elf,_=prepare_elf()
 with GameSource(next(BASE.glob('*.iso'))) as source:tables,_,_,_=prepare_tables(source)
 report=verify(elf,tables[3]);(ART/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['text_checks','prior_regression']},indent=2))
