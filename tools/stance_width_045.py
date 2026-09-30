"""Compact long stance names to fit the shared status field; no code changes."""
import json,struct,hashlib,unicodedata
from sn3_archive import ROOT,parse_index,child,GameSource
from sn3_repack import repack
from dialogue_encoding import encode_dialogue
from menu_hotfix_017 import lines_at
from font_metrics import collect
BASE=ROOT/'work/output/0.1.44'
TARGETS=ROOT/'work/translation/en/stance_width_0.1.45/targets.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
def catalog():
 index=json.loads((ROOT/'work/translation/en/interface.index.json').read_text())
 return next(t for t in index['tables'] if t['resource_path']==[3,31])['strings']
def text_at(table,offset):
 return unicodedata.normalize('NFKC',lines_at(table,offset)[0][0].decode('cp932'))
def prepare_elf():
 data=(BASE/'EBOOT.elf').read_bytes()
 return data,dict(entries=[],unchanged_sha256=sha(data))
def prepare_tables(source):
 targets=json.loads(TARGETS.read_text())['entries'];rows={r['id']:r for r in catalog()}
 static=source.resource('02.DAT',3);si=parse_index(static,len(static));before=child(static,si,31);out=bytearray(before);changes=[];fields=set()
 for e in targets:
  row=rows[e['id']];refs=row['references'];assert all(r['slot']==8 for r in refs)
  for ref in refs:
   f=ref['pointer_field_offset'];prior=struct.unpack_from('<I',before,f)[0];assert text_at(before,prior)==e['previous']
  raw,_=encode_dialogue(e['text'],'');out.extend(bytes(-len(out)%2));new=len(out);out.extend(raw+b'\0\0\0\0')
  for ref in refs:
   f=ref['pointer_field_offset'];struct.pack_into('<I',out,f,new);fields.update(range(f,f+4))
  changes.append(dict(e,new_offset=new,references=refs))
 assert all(a==b or i in fields for i,(a,b) in enumerate(zip(before,out)))
 patched=repack(static,{31:bytes(out)});master=source.resource('00.DAT',44);mi=parse_index(master,len(master));assert child(master,mi,7)==static
 return {3:patched},{},repack(master,{7:patched}),dict(units=[],tables=[dict(child=31,changes=changes)],gameplay_fields_unchanged=True)
def verify(elf,static):
 assert elf==(BASE/'EBOOT.elf').read_bytes()
 cfg=json.loads(TARGETS.read_text());metrics=collect()[0]['characters'];tb=child(static,parse_index(static,len(static)),31);checks=[];seen=set()
 for row in catalog():
  refs=[r for r in row['references'] if 100<=r['record']<=176 and r['slot']==8]
  if not refs:continue
  labels=set()
  for ref in refs:
   p=struct.unpack_from('<I',tb,ref['pointer_field_offset'])[0];labels.add(text_at(tb,p));seen.add(ref['record'])
  assert len(labels)==1;label=labels.pop();width=sum(metrics[c]['proposed_advance_pixels'] for c in label)*cfg['layout']['native_scale']
  assert width<=cfg['layout']['max_advance_pixels'],(label,width)
  checks.append(dict(id=row['id'],text=label,advance_pixels=width,right_edge=216+width,records=[r['record'] for r in refs]))
 for e in cfg['entries']:assert next(c for c in checks if c['id']==e['id'])['text']==e['text']
 assert seen=={100,101,102,107,112,117,122,127,132,137,142,147,152,157,162,167,172},sorted(seen)
 from system_menu_044 import verify as system_verify
 return dict(stance_names=checks,records_checked=len(seen),max_advance_pixels=70,executable_unchanged=True,prior_regression=system_verify(elf,static))
if __name__=='__main__':
 elf,_=prepare_elf()
 with GameSource(next(BASE.glob('*.iso'))) as source:tables,_,_,report=prepare_tables(source)
 report['verification']=verify(elf,tables[3]);print(json.dumps(report,indent=2))
