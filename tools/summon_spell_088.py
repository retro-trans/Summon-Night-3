"""Keep summon spell captions within the existing sixteen-cell font cache."""
import json,struct
from sn3_archive import ROOT,parse_index,child
from spell_name_059 import label,sha
from dialogue_encoding import encode_dialogue
from stat_spacing_026 import _file_offset_for_va as elf_offset

BASE=ROOT/'work/output/0.1.87'
TEXT=ROOT/'work/translation/en/ui_0.1.88/summon_spell.json'

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();m=json.loads((BASE/'manifest.json').read_text('utf8'))
 r=m['banner086_fix'];start=int(r['code_address'],16)+r['labels']['table'];at=elf_offset(old,start)
 size=r['compact_dictionary_bytes'];data=old[at:at+size];count,book_count=struct.unpack_from('<HH',data)
 book=struct.unpack_from('<'+'H'*book_count,data,4);lookup={c:i for i,c in enumerate(book)}
 pos=4+book_count*2;entries=[]
 for _ in range(count):
  n=data[pos];cells=[book[i] for i in data[pos+1:pos+1+n]];entries.append(struct.pack('<'+'H'*n,*cells));pos+=n+1
 expected=[encode_dialogue(t,'')[0] for t in r['banner_names']];assert entries==expected
 cfg=json.loads(TEXT.read_text('utf8'));changes=cfg['changes'];names=list(r['banner_names'])
 for row in changes:
  index=names.index(row['before']);names[index]=row['after'];entries[index]=encode_dialogue(row['after'],'')[0]
 payload=bytearray(data[:4+book_count*2])
 for raw in entries:
  cells=[c[0] for c in struct.iter_unpack('<H',raw)];payload.append(len(cells));payload.extend(lookup[c] for c in cells)
 assert len(payload)<=size;payload.extend(bytes(size-len(payload)))
 out=bytearray(old);out[at:at+size]=payload
 assert len(out)==len(old) and out[:at]==old[:at] and out[at+size:]==old[at+size:]
 return bytes(out),dict(source_sha256=sha(old),output_sha256=sha(out),dictionary_address=hex(start),dictionary_bytes=size,
  banner_names=names,banner_count=count,executable_instructions_unchanged=True,loaded_memory_growth_bytes=0)

def prepare(source):
 cfg=json.loads(TEXT.read_text('utf8'))
 metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text('utf8'))['characters']
 lookup={v['cp932_hex']:v['proposed_advance_pixels'] for v in metrics.values()}
 def measure(t):
  raw=encode_dialogue(t,'')[0]
  assert len(raw)==len(t)*2
  # The existing packer preserves a full native cell for symbols such as Omega.
  return len(raw)//2,sum(lookup.get(raw[i:i+2].hex(),16) for i in range(0,len(raw),2))*cfg['font_scale']
 static=source.resource('02.DAT',3);si=parse_index(static,len(static));entry=si['entries'][cfg['table']]
 original=child(static,si,cfg['table']);out=bytearray(original);changes=[];allowed=set()
 count=struct.unpack_from('<I',original)[0];assert count==cfg['record_count']
 fields=[4+n*cfg['record_stride']+cfg['name_slot']*4 for n in range(count)]
 for row in cfg['changes']:
  field=fields[row['record']];assert label(original,field)==row['before']
  pos=struct.unpack_from('<I',original,field)[0];span=len(encode_dialogue(row['before'],'')[0])+2
  raw=encode_dialogue(row['after'],'')[0]+bytes(2);assert len(raw)<=span
  assert [n for n,f in enumerate(fields) if struct.unpack_from('<I',original,f)[0]==pos]==[row['record']]
  out[pos:pos+span]=raw+bytes(span-len(raw));allowed.update(range(pos,pos+span))
  before_cells,before_pixels=measure(row['before']);cells,pixels=measure(row['after'])
  changes.append(dict(**row,offset=pos,span=span,before_cells=before_cells,after_cells=cells,before_pixels=before_pixels,after_pixels=pixels))
 assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,out)))
 audit=[]
 for n,f in enumerate(fields):
  t=label(out,f)
  if not t:continue
  cells,pixels=measure(t)
  assert cells<=cfg['font_cache_limit_cells'],(n,t,cells)
  assert pixels<=cfg['column_advance_limit_pixels'],(n,t,pixels)
  audit.append(dict(record=n,text=t,cells=cells,advance_pixels=pixels))
 after=bytearray(static);at=entry['offset'];after[at:at+len(out)]=out
 master=source.resource('00.DAT',44);mi=parse_index(master,len(master));assert child(master,mi,7)==static
 cached=bytearray(master);at=mi['entries'][7]['offset'];cached[at:at+len(after)]=after
 assert len(after)==len(static) and len(cached)==len(master)
 report=dict(version='0.1.88',changes=changes,spell_records=count,nonempty_names=len(audit),width_audit=audit,
  font_cache_limit_cells=cfg['font_cache_limit_cells'],column_advance_limit_pixels=cfg['column_advance_limit_pixels'],font_scale=cfg['font_scale'],
  static_source_sha256=sha(static),static_target_sha256=sha(after),master_source_sha256=sha(master),master_target_sha256=sha(cached),
  original_offsets_and_sizes_preserved=True,executable_instructions_unchanged=True,loaded_memory_growth_bytes=0,save_bytes_unchanged=True)
 return {'02.DAT':(3,bytes(after)),'00.DAT':(44,bytes(cached))},report
