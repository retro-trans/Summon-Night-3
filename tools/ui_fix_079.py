"""Append category translations and scoped gallery layout fixes to immutable 078."""
import json,struct,hashlib
from sn3_archive import ROOT,parse_index,child
from sn3_repack import repack
from menu_hotfix_017 import lines_at
from dialogue_encoding import encode_dialogue
from battle_elf_refs import references
from menu_code_020 import append
from stages_pupil_names import parse_elf,validate_loader_structure
from stat_spacing_026 import _file_offset_for_va
from menus_fix_074 import emit_static_bind
from menus_fix_076 import TAIL_SITES,emit_gallery_strip
from menu_art_075 import descend,replace_tree
from font_patch import Assembler
from report_ui_061 import add
from check_ui_079 import check
BASE=ROOT/'work/output/0.1.78'
TEXT=ROOT/'work/translation/en/ui_0.1.79/targets.json'
sha=lambda b:hashlib.sha256(b).hexdigest()

def prepare_tables(source):
 cfg=json.loads(TEXT.read_text());static=source.resource('02.DAT',3)
 result=check(static,cfg);assert result['passed'],result['issues']
 ix=parse_index(static,len(static));before=child(static,ix,25);out=bytearray(before);allowed=set();changes=[]
 for e in cfg['entries']:
  raw=lines_at(before,e['source_offset'])[0];raw=raw[:1] if e['slot']==8 else raw
  assert sha(b'\0\0'.join(raw))==e['source_sha256']
  payload=b''.join(encode_dialogue(t,'')[0]+bytes(2) for t in e['english'])+bytes(2)
  p=len(out);out.extend(payload)
  for f in e['pointer_fields']:
   assert struct.unpack_from('<I',before,f)[0]==e['source_offset']
   struct.pack_into('<I',out,f,p);allowed.update(range(f,f+4))
  changes.append(dict(e,new_offset=p))
 assert all(i in allowed for i,(a,b) in enumerate(zip(before,out)) if a!=b)
 patched=repack(static,{25:bytes(out)});master=repack(source.resource('00.DAT',44),{7:patched})
 gallery=json.loads((TEXT.parent/'gallery.json').read_text());groups={};gr=[]
 for e in gallery['entries']:groups.setdefault(tuple(e['path']),[]).append(e)
 replacements={3:patched}
 for path,entries in groups.items():
  before=descend(source.resource('02.DAT',path[0]),path[1:]);out=bytearray(before);allowed=set()
  for e in entries:
   assert sha(lines_at(before,e['source_offset'])[0][0])==e['source_sha256']
   p=len(out);out.extend(encode_dialogue(e['english'][0],'')[0]+bytes(4))
   for f in e['pointer_fields']:
    assert struct.unpack_from('<I',before,f)[0]==e['source_offset'];struct.pack_into('<I',out,f,p);allowed.update(range(f,f+4))
   gr.append(dict(e,new_offset=p))
  assert all(i in allowed for i,(a,b) in enumerate(zip(before,out)) if a!=b)
  replacements[path[0]]=replace_tree(replacements.get(path[0],source.resource('02.DAT',path[0])),{path[1:]:bytes(out)})
 return replacements,{},master,dict(entries=len(changes),changes=changes,gallery=gr,numeric_fields_unchanged=True,original_pools_preserved=True)

def caption_payload():
 names=json.loads((TEXT.parent/'gallery.json').read_text())['match_names']
 metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters'];out=bytearray(4+12*len(names));struct.pack_into('<I',out,0,len(names))
 for i,name in enumerate(names):
  raw=encode_dialogue(name,'')[0];advance=sum(metrics[c]['proposed_advance_pixels'] for c in name)
  width=min(14.0,2240/max(advance,1));struct.pack_into('<IIf',out,4+i*12,len(out),len(raw)//2,width);out.extend(raw+bytes(2))
 out.extend(bytes(-len(out)%4));return bytes(out)

def previous_gallery():
 r=json.loads((ROOT/'work/output/0.1.76/manifest.json').read_text())['menus076_fix']['elf']
 return {k:int(r['code_address'],16)+r['labels'][k] for k in ('caption_match','gallery_strip')}

def emit_layout(a,ok):
 prior=previous_gallery()
 a.label('night_captions');a.i(9,'sp','sp',-80)
 for reg,off in [('ra',76),('s0',48),('s1',52),('s2',56),('s3',60),('a0',16),('a1',20),('a2',24),('a3',28)]:a.i(43,reg,'sp',off)
 a.move('s0','a0');a.i(35,'s3','s0',0x54);a.i(43,'s3','sp',32)
 a.i(35,'t0','s0',0x58);a.i(43,'t0','sp',36)
 a.i(35,'t0','s0',0x20);a.i(35,'s2','s0',0x3c);a.emit(8<<16|8<<11|4<<6);a.i(35,'s1','s0',0x30);add(a,'s1','s1','t0')
 a.i(35,'t0','s0',0x20);a.emit(18<<21|8<<16|18<<11|0x23)
 a.i(35,'t0','s0',0x24);a.emit(8<<21|18<<16|9<<11|0x2b);a.branch(4,'t1','zero','rows');a.move('s2','t0')
 a.label('rows');a.branch(4,'s2','zero','draw')
 a.i(35,'a0','s1',0);a.jump('caption_match');a.branch(4,'v0','zero','next')
 a.emit(3<<21|19<<16|8<<11|0x2b);a.branch(4,'t0','zero','next');a.move('s3','v1')
 a.label('next');a.i(9,'s1','s1',16);a.i(9,'s2','s2',-1);a.branch(4,'zero','zero','rows')
 a.label('draw');a.i(43,'s3','s0',0x54);a.i(43,'s3','s0',0x58)
 for reg,off in [('a0',16),('a1',20),('a2',24),('a3',28)]:a.i(35,reg,'sp',off)
 a.jump('gallery_strip')
 for off,field in [(32,0x54),(36,0x58)]:a.i(35,'t0','sp',off);a.i(43,'t0','s0',field)
 for reg,off in [('s0',48),('s1',52),('s2',56),('s3',60),('ra',76)]:a.i(35,reg,'sp',off)
 a.i(9,'sp','sp',80);a.ret()
 a.label('night_ok');a.table_address('a1');a.i(9,'a1','a1',ok);a.jump(0x34a0c8,link=False)

def prepare_elf(static):
 old=(BASE/'EBOOT.elf').read_bytes();cfg=json.loads(TEXT.read_text());refs,users,_=references(old)
 entries={e['source_address']:e for e in cfg['menus']};targets=set(entries)
 while True:
  more={u['target'] for va in targets for r in refs[va] if r['kind']=='hilo' for u in users[r['high']]}
  if more<=targets:break
  targets|=more
 assert all(0x215000<=v<0x220000 for v in targets)
 tail=parse_index(static,len(static))['entries'][37]['offset'];size=len(static)-tail
 native=bytearray();offsets={};rows=[]
 for va in sorted(targets):
  e=entries.get(va);raw=lines_at(old,_file_offset_for_va(old,va))[0][:e['source_lines'] if e else 3]
  if e:assert sha(b'\0\0'.join(raw))==e['source_sha256'] and refs[va]==e['bindings']
  texts=[encode_dialogue(t,'')[0] for t in e['english']] if e else raw
  offsets[va]=len(native);native.extend(b''.join(t+bytes(2) for t in texts)+bytes(2))
  rows.append(dict(source_address=va,english=e['english'] if e else None,shared_sibling_preserved=e is None))
 captions=caption_payload();ok=len(captions)
 def emit(a,arena):emit_static_bind(a,arena,tail,size);emit_gallery_strip(a);emit_layout(a,ok)
 probe=Assembler();emit(probe,0);seg=parse_elf(old)['phdrs'][3];table=seg[2]+seg[4]+len(probe.words)*4
 start=((table+0x8000+0xffff)//0x10000)*0x10000-0x8000
 payload=bytearray(captions+encode_dialogue('OK','')[0]+bytes(4));assert len(payload)<start-table;payload.extend(bytes(start-table-len(payload)));payload.extend(native)
 payload.extend(bytes(-len(payload)%4));arena=len(payload);payload.extend(bytes(size+16))
 hooks={p:('static_child',struct.unpack_from('<I',old,p+192)[0]) for p in TAIL_SITES}
 hooks.update({0x13a44:('static_bind',struct.unpack_from('<I',old,0x13a44+192)[0]),0x1ad47c:('night_captions',struct.unpack_from('<I',old,0x1ad47c+192)[0]),0x1ac818:('night_ok',3<<26|0x34a0c8>>2)})
 data,r=append(old,lambda a:emit(a,arena),hooks,bytes(payload));assert int(r['code_address'],16)+r['labels']['table']==table
 out=bytearray(data);words={};highs={}
 for va in sorted(targets):
  new=start+offsets[va]
  for ref in refs[va]:
   if ref['kind']=='pointer':words[ref['address']]=new;continue
   hi,lo=ref['high'],ref['low'];hv=(new+0x8000)>>16
   assert all(u['target'] in targets for u in users[hi]) and (hi not in highs or highs[hi]==hv);highs[hi]=hv
   for at,value in [(hi,hv),(lo,new&65535)]:words[at]=(struct.unpack_from('<I',old,at+192)[0]&0xffff0000)|value
 for at,value in words.items():struct.pack_into('<I',out,at+192,value)
 assert validate_loader_structure(out)
 r.update(entries=rows,changed_native_words={hex(k):hex(v) for k,v in words.items()},static_tail_offset=tail,static_arena_bytes=size,static_arena_context=table+arena,static_arena_address=table+arena+16,proportional_night_title_scale=True,night_footer_label='OK',output_sha256=sha(out),original_pools_preserved=True)
 return bytes(out),r

