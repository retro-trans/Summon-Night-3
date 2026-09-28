"""Localize tutorial notice and Shine Saber description; immutable 0.1.24 base."""
import json,struct,hashlib,argparse
import battle_elf_patch as patcher
from sn3_archive import ROOT,parse_index,child,GameSource
from sn3_repack import repack
from dialogue_encoding import encode_dialogue
from menu_hotfix_017 import glyph_check,lines_at
from font_metrics import collect
BASE=ROOT/'work/output/0.1.24'
FOLDER=ROOT/'work/translation/en/battle_ui_0.1.25'
sha=lambda b:hashlib.sha256(b).hexdigest()
LINES=['Chaos-rending light blade','Ancient hero dead; aglow.']
NOTICE='Tutorials: see Gallery.'

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();idx=patcher.indexed_rows();row=dict(idx['elf:ui:00214ddc'],target_full=NOTICE)
 previous=patcher.BASELINE;old_encoder=patcher.encoded_target
 def encoder(target,source):
  text,display,encoded,variant=old_encoder(target,source)
  return text,display,encoded+b'\0\0',variant
 try:
  patcher.encoded_target=encoder
  patcher.BASELINE=BASE/'EBOOT.elf';data,report=patcher.prepare(old,[row],idx)
 finally:patcher.BASELINE=previous;patcher.encoded_target=old_encoder
 assert not report['skipped']
 e=report['entries'][0];end=e['new_file_offset']+e['encoded_bytes'];assert data[end-4:end]==bytes(4)
 report['explicit_empty_line_sentinel']=True
 return data,report

def prepare_tables(source):
 idx=json.loads((ROOT/'work/translation/en/interface.index.json').read_text());t=next(t for t in idx['tables'] if t['resource_path']==[3,12])
 root=next(r for r in t['strings'] if any(f['record']==84 and f['slot']==12 for f in r['references']));n=t['strings'].index(root);rows=t['strings'][n:n+2]
 assert not rows[1]['references']
 static=source.resource('02.DAT',3);si=parse_index(static,len(static));before=child(static,si,12);out=bytearray(before)
 for r in rows:assert sha(before[r['source_offset']:r['source_offset']+r['source_byte_length']])==r['source_sha256']
 fields=[f['pointer_field_offset'] for f in root['references']]
 assert all(struct.unpack_from('<I',before,f)[0]==root['source_offset'] for f in fields)
 raw=[encode_dialogue(s,'')[0] for s in LINES];counts=glyph_check(raw);assert sum(counts)<=50
 metrics=collect()[0]['characters'];widths=[sum(metrics[c]['proposed_advance_pixels'] for c in line) for line in LINES]
 assert max(widths)<=230, widths # Conservative margin below observed 240px help clipping.
 out.extend(bytes(-len(out)%2));pos=len(out);out.extend(b''.join(s+b'\0\0' for s in raw)+b'\0\0')
 for f in fields:struct.pack_into('<I',out,f,pos)
 assert lines_at(out,pos)[0]==raw
 patched=repack(static,{12:bytes(out)});master=source.resource('00.DAT',44);mi=parse_index(master,len(master));assert child(master,mi,7)==static
 master=repack(master,{7:patched})
 report=dict(units=[],tables=[dict(child=12,changes=[dict(id=root['id'],record=84,rows=rows,lines=LINES,glyph_counts=counts,measured_advance_pixels=widths,pointer_fields=fields,new_offset=pos)])])
 return {3:patched},{},master,report

def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();_,er=prepare_elf()
 with GameSource(BASE/'Summon_Night_3_EN_0.1.24.iso') as s:_,_,_,tr=prepare_tables(s)
 record=dict(version='0.1.25',notice=NOTICE,description_full="A weapon wreathed in light that shatters chaos. Its radiance remains undimmed after the ancient hero's death.",description_lines=LINES,review='Independent meaning reviewer accepted blade from Shine Saber context, ancient hero death and enduring radiance. Compact display retains these within native 54-glyph budget.',elf=er,tables=tr)
 print(json.dumps(record,indent=2))
 if a.write:
  FOLDER.mkdir(exist_ok=True,parents=True);(FOLDER/'text.review.json').write_text(json.dumps(record,indent=2)+'\n')
if __name__=='__main__':main()


