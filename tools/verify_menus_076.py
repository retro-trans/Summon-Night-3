"""Execute protected-tail helpers and check gallery pointers and Options limits."""
import json,struct
from sn3_archive import ROOT,GameSource,parse_index,child
from menus_fix_076 import prepare_elf,prepare_tables,BASE,TEXT,POPUP_SITES
from menu_art_076 import prepare as prepare_art
from menu_art_075 import descend
from dialogue_encoding import encode_dialogue
from menu_hotfix_017 import lines_at
from verify_guards_050 import GuardCPU

def verify():
 elf,r=prepare_elf();cases=0;name_cases=0;row_cases=0;strip_cases=0;night_cases=0;row_payloads=[]
 with GameSource(BASE/'Summon_Night_3_EN_0.1.75.iso') as s:
  tables,_,_,tr=prepare_tables(s);static=tables[3];ix=parse_index(static,len(static))
  for table in tr['tables']:
   b=child(static,ix,table['table'])
   for e in table['changes']:
    p=e['new_offset'];expected=encode_dialogue(e['english'][0],'')[0]+bytes(4);assert b[p:p+len(expected)]==expected
    assert lines_at(b,p)[0]==[expected[:-4]],'Adjacent gallery titles joined'
    row_payloads.append(expected)
    for f in e['pointer_fields']:assert struct.unpack_from('<I',b,f)[0]==p
  art,ar=prepare_art(s)
  for e in ar['gallery_captions']:
   b=descend(art['02.DAT'][e['path'][0]],e['path'][1:]);text=encode_dialogue(e['english'][0],'')[0]+bytes(4)
   assert b[e['new_offset']:e['new_offset']+len(text)]==text
   assert lines_at(b,e['new_offset'])[0]==[text[:-4]],'Adjacent gallery captions joined'
   row_payloads.append(text)
   for f in e['pointer_fields']:assert struct.unpack_from('<I',b,f)[0]==e['new_offset']
 for base in (0x08804000,0x0890c000):
  m=GuardCPU(elf,r,base);owner=0x09400000;source=0x09600000;stop=0x08801234;arena=base+r['static_arena_address'];context=base+r['static_arena_context'];tail=source+r['static_tail_offset'];size=r['static_arena_bytes']
  # Long exact gallery captions must bypass the fixed per-character pool.
  known=r['gallery_strip_names'];tests=[([t],True) for t in known]+[(known[:2],True),(known[:4],True),(known[:21],True),(known[:38],True),(known[:190],True),(known[:256],True),(['Custom Name'],False),([known[0]+'X'],False),([known[0],'Custom Name'],True),(['????????',known[0]],True),(known[:257],False)]
  for texts,matched in tests:
   records=0x09700000;m.store(owner,bytes(0x100));m.write(owner,3);m.write(owner+0x30,records);m.write(owner+0x34,0x09710000);m.write(owner+0x3c,len(texts));m.write(owner+0x64,9,1)
   for i,text in enumerate(texts):
    ptr=0x09800000+256*i;m.store(ptr,encode_dialogue(text,'')[0]+bytes(4));m.write(records+16*i,ptr)
   m.r=[0x12500000+i for i in range(32)];m.r[0]=0;m.r[4:8]=[owner,99,88,77];m.r[29]=0x09f00000;m.r[31]=stop;before=m.r.copy();pc=base+int(r['code_address'],16)+r['labels']['gallery_strip'];draws=0
   for _ in range(500000):
    if pc==stop:break
    if pc==base+0x35272c:
     assert m.r[4:8]==before[4:8];assert m.read(owner+0x34)==(0 if matched else 0x09710000)
     assert m.read(owner+0x64,1)==(255 if matched else 9)
     if matched:assert m.read(owner)&0x400
     draws+=1;pc=m.r[31];continue
    pc=m.step(pc)
   assert pc==stop and draws==1 and m.r[16:32]==before[16:32]
   assert m.read(owner+0x34)==0x09710000 and m.read(owner+0x64,1)==9
   strip_cases+=1
  # The Night Talks column fits the widest visible caption and restores scale.
  for start in (0,1,4):
   texts=['A Short Title','Those Are Separate Matters','????????','Thunder General, Wind Princess','A Wish from the Past']
   records=0x09700000;m.store(owner,bytes(0x100));m.write(owner+0x30,records);m.write(owner+0x20,start);m.write(owner+0x24,3);m.write(owner+0x3c,len(texts));m.write(owner+0x54,struct.unpack('<I',struct.pack('<f',14.0))[0])
   for i,text in enumerate(texts):
    ptr=0x09800000+256*i;m.store(ptr,encode_dialogue(text,'')[0]+bytes(4));m.write(records+16*i,ptr)
   metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters'];widths=[14.0]
   for text in texts[start:start+3]:
    if text not in known:continue
    adv=sum(metrics[c]['proposed_advance_pixels'] for c in text);last=metrics[text[-1]];b=last['ink_bounds_inclusive'];ink=adv-last['proposed_advance_pixels']+(b[2]-b[0]+1 if b else 0);widths.append(min(14.0,2240.0/max(adv,ink)))
   expected=struct.unpack('<I',struct.pack('<f',min(widths)))[0]
   m.r=[0x12500000+i for i in range(32)];m.r[0]=0;m.r[4:8]=[owner,99,88,77];m.r[29]=0x09f00000;m.r[31]=stop;before=m.r.copy();pc=base+int(r['code_address'],16)+r['labels']['night_captions'];draws=0
   for _ in range(500000):
    if pc==stop:break
    if pc==base+int(r['code_address'],16)+r['labels']['gallery_strip']:
     assert m.read(owner+0x54)==expected and m.r[4:8]==before[4:8];draws+=1;pc=m.r[31];continue
    pc=m.step(pc)
   assert pc==stop and draws==1 and m.r[16:32]==before[16:32] and m.read(owner+0x54)==0x41600000;night_cases+=1
  # Translate the UI's copied default-name row pointers, leaving save text intact.
  records=0x09700000;m.store(owner,bytes(0x100));m.write(owner+0x30,records);m.write(owner+0x3c,3)
  for i,text in enumerate(['レックス','アティ','Custom Name']):
   ptr=0x09800000+256*i;m.store(ptr,encode_dialogue(text,'')[0]+bytes(4));m.write(records+16*i,ptr)
  m.r=[0x12500000+i for i in range(32)];m.r[0]=0;m.r[4:8]=[owner,99,88,77];m.r[29]=0x09f00000;m.r[31]=stop;before=m.r.copy();pc=base+int(r['code_address'],16)+r['labels']['night_names']
  for _ in range(500000):
   if pc==stop:break
   if pc==base+int(r['code_address'],16)+r['labels']['gallery_strip']:
    assert m.r[4:8]==before[4:8]
    for i,text in enumerate(['Rexx','Aty','Custom Name']):
     raw=encode_dialogue(text,'')[0]+bytes(2);p=m.read(records+16*i);assert bytes(m.read(p+j,1) for j in range(len(raw)))==raw
    assert m.read(records+32)==0x09800200
    pc=m.r[31];continue
   pc=m.step(pc)
  assert pc==stop and m.r[16:32]==before[16:32];night_cases+=1
  # Execute the native row walker, modeling only its graphics-binding callee.
  m.store(base+0x1a31c,elf[0x1a31c+192:0x1a3a4+192]);m.write(base+0x1a354,3<<26|(base+0x1a2f0)>>2)
  joined=encode_dialogue('First','')[0]+bytes(2)+encode_dialogue('Second','')[0]+bytes(4)
  for payload,expected_rows in [(p,1) for p in row_payloads]+[(joined,2)]:
   ptr=0x09800000;m.store(ptr,payload+bytes(8));m.r=[0]*32;m.r[4:8]=[owner,ptr,1,0];m.r[29]=0x09f00000;m.r[31]=stop;pc=base+0x1a31c;bound=[]
   for _ in range(5000):
    if pc==stop:break
    if pc==base+0x1a2f0:bound.append(m.r[5]);pc=m.r[31];continue
    pc=m.step(pc)
   assert pc==stop and len(bound)==expected_rows and m.r[29]==0x09f00000,(payload,len(bound))
   if expected_rows==1:row_cases+=1
  m.store(source,static);m.store(arena-8,b'G'*8+bytes(size)+b'G'*8)
  m.r=[0]*32;m.r[4:6]=[owner,source];m.r[29]=0x09f00000;m.r[31]=stop
  for i in range(16,29):m.r[i]=0x12500000+i
  before=m.r.copy();pc=base+int(r['code_address'],16)+r['labels']['static_bind'];calls=[]
  for _ in range(1000):
   if pc==stop:break
   if pc==base+0x1c2b80:
    dst,src,n=m.r[4:7];assert (dst,src,n)==(arena,tail,size)
    m.store(dst,bytes(m.read(src+i,1) for i in range(n)));m.r[2]=dst;pc=m.r[31];continue
   if pc==base+0x197f90:
    assert m.r[4:6]==[owner,source];calls.append(pc);pc=m.r[31];continue
   pc=m.step(pc)
  assert pc==stop and len(calls)==1 and m.r[16:32]==before[16:32]
  assert m.read(context)==tail and bytes(m.read(arena+i,1) for i in range(size))==static[r['static_tail_offset']:]
  assert bytes(m.read(arena+size+i,1) for i in range(8))==b'G'*8;cases+=1
  for ptr in [tail-2048]+[source+ix['entries'][n]['offset'] for n in range(37,49)]+[tail+size]:
   m.r=[0]*32;m.r[4:6]=[owner,37];m.r[29]=0x09f00000;m.r[31]=stop;before=m.r.copy();pc=base+int(r['code_address'],16)+r['labels']['static_child']
   for _ in range(200):
    if pc==stop:break
    if pc==base+0x1e6bd4:m.r[2]=ptr;pc=m.r[31];continue
    pc=m.step(pc)
   assert pc==stop;expected=arena+ptr-tail if tail<=ptr<tail+size else ptr;assert m.r[2]==expected and m.r[16:32]==before[16:32];cases+=1
  for source_text,target_text in [('レックス','Rexx'),('アティ','Aty'),('テスト','テスト'),('レックスＸ','レックスＸ'),('What We Inherit','What We Inherit')]:
   raw=encode_dialogue(source_text,'')[0]+b'\0\0';wanted=encode_dialogue(target_text,'')[0]+b'\0\0';ptr=0x09800000;m.store(ptr,raw+bytes(100))
   for row in (0,1):
    m.r=[0x12500000+i for i in range(32)];m.r[0]=0;m.r[4:8]=[owner,ptr,1,row];m.r[29]=0x09f00000;m.r[31]=stop;before=m.r.copy();pc=base+int(r['code_address'],16)+r['labels']['gallery_name']
    for _ in range(100000):
     if pc==base+0x1a2f0:break
     pc=m.step(pc)
    assert pc==base+0x1a2f0 and m.r[4]==owner and m.r[6:8]==before[6:8] and m.r[16:32]==before[16:32]
    assert bytes(m.read(m.r[5]+i,1) for i in range(len(wanted)))==wanted
    if source_text==target_text:assert m.r[5]==ptr,'Custom name pointer changed'
    assert bytes(m.read(ptr+i,1) for i in range(len(raw)))==raw,'Stored name changed'
    name_cases+=1
 for p in POPUP_SITES:assert struct.unpack_from('<I',elf,p+192)[0]==3<<26|0x34a0c8>>2
 cfg=json.loads((TEXT/'native.json').read_text());assert all(max(map(len,e['english']))<=27 for e in cfg['entries'])
 controls=[e['english'][0] for e in cfg['entries'] if 0x21f7b4<=e['source_address']<=0x21f7e4]
 assert len(controls)==6 and struct.unpack_from('<I',elf,0x1a7008+192)[0]==0x3c044110
 footer_end=22+sum(len(t)*9+15+10 for t in controls);assert footer_end<=480
 assert strip_cases>=400
 return dict(passed=True,tail_execution_cases=cases,gallery_name_execution_cases=name_cases,night_column_execution_cases=night_cases,gallery_native_row_execution_cases=row_cases,gallery_strip_execution_cases=strip_cases,gallery_strip_overflow_prevented=True,custom_names_preserved=True,load_bases=2,protected_tail_bytes=size,gallery_fields=tr['entries'],sound_tracks=38,night_talk_titles=ar['night_talk_titles'],ending_titles=ar['ending_titles'],gallery_caption_pointers=sum(len(e['pointer_fields']) for e in ar['gallery_captions']),translated_sprites=ar['translated_sprites'],native_messages=len(cfg['entries']),options_help_max_cells=max(max(map(len,e['english'])) for e in cfg['entries'][:5]),gallery_empty_row_terminators_verified=True,original_pools_and_numeric_fields_preserved=True,popup_item_names_use_existing_bounded_renderer=True)
if __name__=='__main__':
 r=verify();(ROOT/'work/ui/menus_0.1.76/validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
