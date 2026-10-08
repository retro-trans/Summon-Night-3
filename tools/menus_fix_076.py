"""Relocate gallery tables, shorten Options help, and fit purchase names."""
import json,struct,hashlib
from sn3_archive import ROOT,GameSource,parse_index,child
from sn3_repack import repack
from dialogue_encoding import encode_dialogue
from menu_hotfix_017 import lines_at
from battle_elf_refs import references
from menu_code_020 import append
from stages_pupil_names import parse_elf,validate_loader_structure
from stat_spacing_026 import _file_offset_for_va
from menus_fix_074 import emit_static_bind
from font_patch import Assembler
from report_ui_061 import add
BASE=ROOT/'work/output/0.1.75';TEXT=ROOT/'work/translation/en/menus_0.1.76'
sha=lambda b:hashlib.sha256(b).hexdigest()
TAIL_SITES=(0x198620,0x19869c,0x1986fc,0x198764,0x198784,0x1987c8,0x1987f0,0x19881c,0x198840,0x198858,0x1989bc,0x1989e4)
POPUP_SITES=(0x13ec0c,0x13ecb8,0x13ecf0,0x13eda0,0x13ee48,
             0x14024c,0x1402f8,0x140398,0x140440,0x1404e8)
CONTROL_SITES=(0x19fea8,0x19ff30,0x19ffb0,0x1a0124,0x1a01ac,
               0x1a7748,0x1ac818,0x1ac880,0x1ac8e0)
ENDING_NAME_SITE=0x1a1598
NIGHT_NAME_SITE=0x1ad440
NIGHT_CAPTION_SITE=0x1ad47c

def gallery_strip_payload():
 # Match exact translated gallery titles, never arbitrary gameplay text.
 names={'Rexx','Aty'}
 for filename in ('titles.json','gallery_captions.json'):
  names.update(e['english'][0] for e in json.loads((TEXT/filename).read_text())['entries'])
 metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters']
 names=sorted(names);out=bytearray(4+12*len(names));struct.pack_into('<I',out,0,len(names))
 for i,name in enumerate(names):
  raw=encode_dialogue(name,'')[0];assert 0<len(raw)//2<=32
  advance=sum(metrics[c]['proposed_advance_pixels'] for c in name)
  last=metrics[name[-1]];bounds=last['ink_bounds_inclusive'];ink=advance-last['proposed_advance_pixels']+(bounds[2]-bounds[0]+1 if bounds else 0)
  width=min(14.0,140.0*16/max(advance,ink))
  struct.pack_into('<IIf',out,4+12*i,len(out),len(raw)//2,width);out.extend(raw+bytes(2))
 out.extend(bytes(-len(out)%4));return bytes(out),names

def emit_gallery_strip(a):
 a.label('caption_match');a.branch(4,'a0','zero','caption_unmatched');a.table_address('t0')
 a.i(35,'t1','t0',0);a.i(9,'t2','t0',4)
 a.label('caption_candidate');a.branch(4,'t1','zero','caption_unmatched')
 a.i(35,'t3','t2',0);add(a,'t3','t0','t3');a.i(35,'v1','t2',4)
 a.move('t4','a0');a.move('t5','v1')
 a.label('caption_compare');a.i(37,'t6','t3',0);a.i(37,'t7','t4',0)
 a.branch(5,'t6','t7','caption_next');a.branch(4,'t6','zero','caption_matched')
 a.branch(4,'t5','zero','caption_next');a.i(9,'t5','t5',-1)
 a.i(9,'t3','t3',2);a.i(9,'t4','t4',2);a.branch(4,'zero','zero','caption_compare')
 a.label('caption_next');a.i(9,'t2','t2',12);a.i(9,'t1','t1',-1);a.branch(4,'zero','zero','caption_candidate')
 a.label('caption_matched');a.move('v0','v1');a.i(35,'v1','t2',8);a.ret()
 a.label('caption_unmatched');a.move('v0','zero');a.ret()
 a.label('gallery_strip');a.i(9,'sp','sp',-96)
 for reg,off in [('ra',92),('s0',64),('s1',68),('s2',72),('s3',76),('a0',32),('a1',36),('a2',40),('a3',44)]:a.i(43,reg,'sp',off)
 a.move('s0','a0');a.move('s1','zero');a.branch(4,'s0','zero','gallery_draw')
 a.i(35,'t0','s0',0x34);a.branch(4,'t0','zero','gallery_draw');a.i(43,'t0','sp',48)
 a.i(36,'t0','s0',0x64);a.i(43,'t0','sp',52)
 a.i(35,'s3','s0',0x3c);a.branch(4,'s3','zero','gallery_draw')
 a.i(11,'t0','s3',257);a.branch(4,'t0','zero','gallery_draw')
 a.i(35,'s2','s0',0x30);a.branch(4,'s2','zero','gallery_draw')
 a.label('gallery_rows');a.i(35,'a0','s2',0);a.jump('caption_match');a.branch(5,'v0','zero','gallery_matched')
 a.i(9,'s2','s2',16);a.i(9,'s3','s3',-1);a.branch(5,'s3','zero','gallery_rows')
 a.branch(4,'zero','zero','gallery_draw')
 # Bind one bounded strip per row instead of writing beyond the native glyph pool.
 # A paired locked or custom-name row shares the same translated widget.
 a.label('gallery_matched')
 a.i(43,'zero','s0',0x34);a.i(9,'t0','zero',-1);a.i(40,'t0','s0',0x64);a.i(9,'s1','zero',1)
 a.i(35,'t0','s0',0);a.i(13,'t0','t0',0x400);a.i(43,'t0','s0',0)
 a.label('gallery_draw')
 for reg,off in [('a0',32),('a1',36),('a2',40),('a3',44)]:a.i(35,reg,'sp',off)
 a.jump(0x35272c) # Keep the previously verified spell-banner wrapper.
 a.branch(4,'s1','zero','gallery_return');a.i(35,'t0','sp',48);a.i(43,'t0','s0',0x34)
 a.i(35,'t0','sp',52);a.i(40,'t0','s0',0x64)
 a.label('gallery_return')
 for reg,off in [('s0',64),('s1',68),('s2',72),('s3',76),('ra',92)]:a.i(35,reg,'sp',off)
 a.i(9,'sp','sp',96);a.ret()

def emit_night_strips(a):
 # These two call sites render the Night Talks name and title columns only.
 # Row pointers belong to the UI; the saved player-name buffer is never written.
 a.label('night_names');a.i(9,'sp','sp',-64)
 for reg,off in [('ra',60),('s0',40),('s1',44),('s2',48),('a0',16),('a1',20),('a2',24),('a3',28)]:a.i(43,reg,'sp',off)
 a.move('s0','a0');a.i(35,'s1','s0',0x30);a.i(35,'s2','s0',0x3c)
 a.label('night_name_rows');a.branch(4,'s2','zero','night_names_draw')
 a.i(35,'a0','s1',0);a.jump(name_lookup_entry());a.i(43,'v0','s1',0)
 a.i(9,'s1','s1',16);a.i(9,'s2','s2',-1);a.branch(4,'zero','zero','night_name_rows')
 a.label('night_names_draw')
 for reg,off in [('a0',16),('a1',20),('a2',24),('a3',28)]:a.i(35,reg,'sp',off)
 a.jump('gallery_strip')
 for reg,off in [('s0',40),('s1',44),('s2',48),('ra',60)]:a.i(35,reg,'sp',off)
 a.i(9,'sp','sp',64);a.ret()
 a.label('night_captions');a.i(9,'sp','sp',-80)
 for reg,off in [('ra',76),('s0',48),('s1',52),('s2',56),('s3',60),('a0',16),('a1',20),('a2',24),('a3',28)]:a.i(43,reg,'sp',off)
 a.move('s0','a0');a.i(35,'s3','s0',0x54);a.i(43,'s3','sp',32)
 a.i(35,'t0','s0',0x20);a.i(35,'s2','s0',0x3c);a.emit(8<<16|8<<11|4<<6);a.i(35,'s1','s0',0x30);add(a,'s1','s1','t0')
 a.i(35,'t0','s0',0x20);a.emit(18<<21|8<<16|18<<11|0x23)
 a.i(35,'t0','s0',0x24);a.emit(8<<21|18<<16|9<<11|0x2b);a.branch(4,'t1','zero','night_caption_rows');a.move('s2','t0')
 a.label('night_caption_rows');a.branch(4,'s2','zero','night_captions_draw')
 a.i(35,'a0','s1',0);a.jump('caption_match');a.branch(4,'v0','zero','night_caption_next')
 a.emit(3<<21|19<<16|8<<11|0x2b);a.branch(4,'t0','zero','night_caption_next');a.move('s3','v1')
 a.label('night_caption_next');a.i(9,'s1','s1',16);a.i(9,'s2','s2',-1);a.branch(4,'zero','zero','night_caption_rows')
 a.label('night_captions_draw');a.i(43,'s3','s0',0x54)
 for reg,off in [('a0',16),('a1',20),('a2',24),('a3',28)]:a.i(35,reg,'sp',off)
 a.jump('gallery_strip');a.i(35,'t0','sp',32);a.i(43,'t0','s0',0x54)
 for reg,off in [('s0',48),('s1',52),('s2',56),('s3',60),('ra',76)]:a.i(35,reg,'sp',off)
 a.i(9,'sp','sp',80);a.ret()

def name_lookup_entry():
 m=json.loads((ROOT/'work/output/0.1.20/manifest.json').read_text())
 r=m['menu020_text']['list_vwf']
 return int(r['code_address'],16)+r['labels']['saved_name']

def emit_gallery_name(a):
 # Translate the saved-name string before the gallery creates its text strip.
 # The later virtual row setters receive textures, not character strings.
 # Translate complete default names for display; unmatched custom names pass.
 a.label('gallery_name');a.i(9,'sp','sp',-32)
 for reg,off in [('ra',28),('a0',16),('a2',20),('a3',24)]:a.i(43,reg,'sp',off)
 a.move('a0','a1');a.jump(name_lookup_entry());a.move('a1','v0')
 for reg,off in [('a0',16),('a2',20),('a3',24),('ra',28)]:a.i(35,reg,'sp',off)
 a.i(9,'sp','sp',32);a.jump(0x1a2f0,link=False)

def prepare_tables(source):
 cfg=json.loads((TEXT/'titles.json').read_text());static=source.resource('02.DAT',3);ix=parse_index(static,len(static));replacements={};reports=[]
 for n in sorted({e['table'] for e in cfg['entries']}):
  before=child(static,ix,n);out=bytearray(before);allowed=set();rows=[];dedup={}
  for e in (e for e in cfg['entries'] if e['table']==n):
   raw=lines_at(before,e['source_offset'])[0][0];assert sha(raw)==e['source_sha256']
   text=encode_dialogue(e['english'][0],'')[0]+bytes(4);assert len(text)//2<=34
   if text not in dedup:dedup[text]=len(out);out.extend(text)
   p=dedup[text]
   for f in e['pointer_fields']:
    assert struct.unpack_from('<I',before,f)[0]==e['source_offset'];struct.pack_into('<I',out,f,p);allowed.update(range(f,f+4))
   rows.append(dict(e,new_offset=p))
  assert all(i in allowed for i,(a,b) in enumerate(zip(before,out)) if a!=b)
  replacements[n]=bytes(out);reports.append(dict(table=n,changes=rows,numeric_fields_unchanged=True,original_pool_preserved=True))
 patched=repack(static,replacements);master=repack(source.resource('00.DAT',44),{7:patched})
 return {3:patched},{},master,dict(entries=len(cfg['entries']),tables=reports,units=[],numeric_fields_unchanged=True,original_pools_preserved=True)

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();cfg=json.loads((TEXT/'native.json').read_text());refs,users,_=references(old);entries={e['source_address']:e for e in cfg['entries']};targets=set(entries)
 while True:
  more={u['target'] for va in targets for r in refs.get(va,[]) if r['kind']=='hilo' for u in users[r['high']]}
  if more<=targets:break
  targets|=more
 assert len(targets)<60
 # Keep each shared HI cohort in one signed-low address page.
 with GameSource(BASE/'Summon_Night_3_EN_0.1.75.iso') as s:static=prepare_tables(s)[0][3]
 tail=parse_index(static,len(static))['entries'][37]['offset'];size=len(static)-tail
 native=bytearray();offsets={};rows=[]
 for va in sorted(targets):
  e=entries.get(va);raw=lines_at(old,_file_offset_for_va(old,va))[0][:e['source_lines'] if e else 3]
  if e:assert sha(b'\0\0'.join(raw))==e['source_sha256'] and refs[va]==e['bindings']
  text=[encode_dialogue(t,'')[0] for t in e['english']] if e else raw
  offsets[va]=len(native);native.extend(b''.join(t+b'\0\0' for t in text)+b'\0\0')
  rows.append(dict(source_address=va,english=e['english'] if e else None,shared_sibling_preserved=e is None))
 def emitted(a,arena):
  emit_static_bind(a,arena,tail,size);emit_gallery_name(a);emit_gallery_strip(a);emit_night_strips(a)
 probe=Assembler();emitted(probe,0);seg=parse_elf(old)['phdrs'][3];table=seg[2]+seg[4]+len(probe.words)*4
 start=((table+0x8000+0xffff)//0x10000)*0x10000-0x8000;pad=start-table
 caption_payload,caption_names=gallery_strip_payload();assert len(caption_payload)<=pad
 payload=bytearray(caption_payload)+bytes(pad-len(caption_payload))+native;payload.extend(bytes(-len(payload)%4));arena=len(payload);payload.extend(bytes(size+16))
 hooks={p:(0x34a0c8,3<<26|0x1cbdec>>2) for p in POPUP_SITES+CONTROL_SITES}
 hooks[0x13a44]=('static_bind',struct.unpack_from('<I',old,0x13a44+192)[0])
 hooks.update({p:('static_child',struct.unpack_from('<I',old,p+192)[0]) for p in TAIL_SITES})
 hooks[ENDING_NAME_SITE]=('gallery_name',3<<26|0x1a2f0>>2)
 hooks[NIGHT_NAME_SITE]=('night_names',3<<26|0x1b0f8>>2)
 hooks[NIGHT_CAPTION_SITE]=('night_captions',3<<26|0x1b0f8>>2)
 hooks[0x1b0f8]=('gallery_strip',2<<26|0x35272c>>2)
 data,report=append(old,lambda a:emitted(a,arena),hooks,bytes(payload));out=bytearray(data);words={};highs={}
 struct.pack_into('<I',out,0x1b0f8+192,2<<26|(int(report['code_address'],16)+report['labels']['gallery_strip'])>>2)
 # The artwork footer advances by source cells, independently of glyph packing.
 # Nine pixels per English cell leaves room for all six compact controls.
 assert struct.unpack_from('<I',old,0x1a7008+192)[0]==0x3c044160
 struct.pack_into('<I',out,0x1a7008+192,0x3c044110)
 assert int(report['code_address'],16)+report['labels']['table']==table
 for va in sorted(targets):
  new=start+offsets[va]
  for r in refs[va]:
   if r['kind']=='pointer':words[r['address']]=new;continue
   hi,lo=r['high'],r['low'];hv=(new+0x8000)>>16
   assert all(u['target'] in targets for u in users[hi]);assert hi not in highs or highs[hi]==hv;highs[hi]=hv
   for at,value in [(hi,hv),(lo,new&65535)]:words[at]=(struct.unpack_from('<I',old,at+192)[0]&0xffff0000)|value
 for at,value in words.items():struct.pack_into('<I',out,at+192,value)
 assert validate_loader_structure(out)
 report.update(entries=rows,output_sha256=sha(out),static_tail_offset=tail,static_arena_bytes=size,static_arena_context=table+arena,static_arena_address=table+arena+16,original_pools_preserved=True,changed_native_words={hex(k):hex(v) for k,v in words.items()},popup_call_sites=[hex(p) for p in POPUP_SITES],gallery_control_sites=[hex(p) for p in CONTROL_SITES],ending_name_site=hex(ENDING_NAME_SITE),gallery_default_name_lookup=name_lookup_entry(),custom_names_preserved=True)
 report.update(gallery_strip_names=caption_names,gallery_strip_max_cells=32,gallery_strip_max_rows=256,gallery_strip_keeps_prior_banner_wrapper=True,artwork_footer_cell_advance=9,artwork_footer_pitch_site='0x1a7008')
 report.update(night_caption_column_pixels=140,night_caption_fit_visible_rows=True,night_name_site=hex(NIGHT_NAME_SITE),night_caption_site=hex(NIGHT_CAPTION_SITE))
 return bytes(out),report
if __name__=='__main__':
 e,r=prepare_elf();print(json.dumps(dict(native=len(r['entries']),tail=r['static_arena_bytes'],bytes_added=r['code_bytes'])))
