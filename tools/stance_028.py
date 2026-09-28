"""Relocate stance help as bounded, explicitly terminated two-line records."""
import argparse,json,struct,hashlib
from sn3_archive import ROOT,GameSource,parse_index,child
from sn3_repack import repack
from dialogue_encoding import encode_dialogue
from menu_hotfix_017 import glyph_check,lines_at
from font_metrics import collect
BASE=ROOT/'work/output/0.1.27'
FOLDER=ROOT/'work/translation/en/stance_0.1.28'
sha=lambda b:hashlib.sha256(b).hexdigest()

def prepare_elf():
 data=(BASE/'EBOOT.elf').read_bytes()
 return data,dict(entries=[],skipped=[],unchanged_sha256=sha(data))

def prepare_tables(source):
 index=json.loads((ROOT/'work/translation/en/interface.index.json').read_text())
 table=next(t for t in index['tables'] if t['resource_path']==[3,31]);byid={r['id']:r for r in table['strings']}
 review=json.loads((FOLDER/'meaning_review.json').read_text())
 expected={r['id'] for r in table['strings'] if any(100<=f['record']<=176 and f['slot']==9 for f in r['references'])}
 assert {e['id'] for e in review['entries']}==expected, 'Review must cover every stance description, records 100..176'
 static=source.resource('02.DAT',3);si=parse_index(static,len(static));before=child(static,si,31);out=bytearray(before);changes=[]
 metrics=collect()[0]['characters']
 for entry in review['entries']:
  row=byid[entry['id']];refs=row['references'];assert any(r['record']==entry['record'] and r['slot']==9 for r in refs)
  assert all(r['slot']==9 for r in refs)
  start,n=row['source_offset'],row['source_byte_length'];assert sha(before[start:start+n])==row['source_sha256']
  fields=[r['pointer_field_offset'] for r in refs];prior=struct.unpack_from('<I',before,fields[0])[0]
  assert all(struct.unpack_from('<I',before,f)[0]==prior for f in fields)
  lines=entry.get('lines',entry.get('compact_lines'));assert len(lines)<=2
  raw=[encode_dialogue(line,'')[0] for line in lines];counts=glyph_check(raw)
  widths=[sum(metrics[c]['proposed_advance_pixels'] for c in line)*.875 for line in lines];assert max(widths)<=340,widths
  payload=b''.join(line+b'\0\0' for line in raw)+b'\0\0'
  out.extend(bytes(-len(out)%2));new=len(out);out.extend(payload)
  for f in fields:struct.pack_into('<I',out,f,new)
  assert lines_at(out,new)[0]==raw
  changes.append(dict(id=row['id'],record=entry['record'],lines=lines,full_translation=entry.get('full_translation',entry.get('full')),source_sha256=row['source_sha256'],previous_offset=prior,new_offset=new,pointer_fields=fields,glyph_counts=counts,total_glyphs=sum(counts),advance_pixels=widths,explicit_empty_line=True))
 patched=repack(static,{31:bytes(out)});master=source.resource('00.DAT',44);mi=parse_index(master,len(master));assert child(master,mi,7)==static
 master=repack(master,{7:patched})
 return {3:patched},{},master,dict(units=[],tables=[dict(child=31,changes=changes)],line_capacity=29,glyph_capacity=54,maximum_lines=2)

def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
 with GameSource(BASE/'Summon_Night_3_EN_0.1.27.iso') as s:_,_,_,report=prepare_tables(s)
 print(json.dumps(report,indent=2))
 if args.write:(FOLDER/'layout_report.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
