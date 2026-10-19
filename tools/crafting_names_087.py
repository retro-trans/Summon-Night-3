"""Fit accessory names within the existing proportional crafting column."""
import json,struct
from sn3_archive import ROOT,parse_index,child
from spell_name_059 import label,sha
from dialogue_encoding import encode_dialogue

BASE=ROOT/'work/output/0.1.86'
TEXT=ROOT/'work/translation/en/ui_0.1.87/crafting.json'

def prepare(source):
 cfg=json.loads(TEXT.read_text('utf8'))
 metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text('utf8'))['characters']
 lookup={v['cp932_hex']:v['proposed_advance_pixels'] for v in metrics.values()}
 def width(t):return sum(lookup[encode_dialogue(c,'')[0].hex()] for c in t)*cfg['font_scale']
 static=source.resource('02.DAT',3);si=parse_index(static,len(static));entry=si['entries'][cfg['table']]
 original=child(static,si,cfg['table']);out=bytearray(original);changes=[];allowed=set()
 count=struct.unpack_from('<I',original)[0];assert count==121
 for row in cfg['changes']:
  field=4+row['record']*84+cfg['name_slot']*4
  assert label(original,field)==row['before']
  pos=struct.unpack_from('<I',original,field)[0];span=len(encode_dialogue(row['before'],'')[0])+2
  raw=encode_dialogue(row['after'],'')[0]+bytes(2);assert len(raw)<=span
  # These are English pool entries with one owning row, not shared source text.
  owners=[n for n in range(count) if struct.unpack_from('<I',original,4+n*84+76)[0]==pos]
  assert owners==[row['record']]
  out[pos:pos+span]=raw+bytes(span-len(raw));allowed.update(range(pos,pos+span))
  changes.append(dict(**row,offset=pos,span=span,before_pixels=width(row['before']),after_pixels=width(row['after'])))
 assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,out)))
 audit=[]
 for n in range(count):
  t=label(out,4+n*84+76)
  if not t:continue
  pixels=width(t);assert pixels<=cfg['column_advance_limit_pixels'],(n,t,pixels)
  audit.append(dict(record=n,text=t,advance_pixels=pixels))
 # Replace only the same-length child bytes, including the master cached copy.
 after=bytearray(static);at=entry['offset'];after[at:at+len(out)]=out
 master=source.resource('00.DAT',44);mi=parse_index(master,len(master));assert child(master,mi,7)==static
 cached=bytearray(master);at=mi['entries'][7]['offset'];cached[at:at+len(after)]=after
 assert len(after)==len(static) and len(cached)==len(master)
 report=dict(version='0.1.87',changes=changes,accessory_records=count,nonempty_names=len(audit),width_audit=audit,
  column_advance_limit_pixels=cfg['column_advance_limit_pixels'],font_scale=cfg['font_scale'],
  static_source_sha256=sha(static),static_target_sha256=sha(after),master_source_sha256=sha(master),master_target_sha256=sha(cached),
  original_offsets_and_sizes_preserved=True,executable_unchanged=True,loaded_memory_growth_bytes=0,save_bytes_unchanged=True)
 return {'02.DAT':(3,bytes(after)),'00.DAT':(44,bytes(cached))},report
