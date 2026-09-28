"""Append-only battle/help translation on immutable 0.1.34."""
import json,struct,hashlib
from sn3_archive import ROOT,parse_index,child
from sn3_repack import repack
from character_labels import collect
from battle_elf_refs import references
from battle_elf_patch import indexed_rows
from menu_code_020 import append
from dialogue_encoding import encode_dialogue
from menu_hotfix_017 import lines_at
from stages_pupil_names import parse_elf
from menu_enemy_targets_035 import HELP,ENEMIES
BASE=ROOT/'work/output/0.1.34'
sha=lambda x:hashlib.sha256(x).hexdigest()

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();refs,_,_=references(old);idx=indexed_rows()
 original=(ROOT/'work/source/EBOOT.elf').read_bytes();payload=bytearray();entries=[]
 for off,lines in HELP.items():
  row=idx[f'elf:ui:{off:08x}'];va=off-192;n=row['source_byte_length']
  assert old[off:off+n]==original[off:off+n] and sha(old[off:off+n])==row['source_sha256']
  assert len(lines)<=2 and all(len(s)<=27 for s in lines) and sum(map(len,lines))<=54
  rr=refs[va];assert rr and all(r['kind']=='pointer' for r in rr)
  payload.extend(bytes(-len(payload)%4));pos=len(payload)
  payload.extend(b''.join(encode_dialogue(s,'')[0]+b'\0\0' for s in lines)+b'\0\0')
  entries.append(dict(id=row['id'],source_offset=off,source_sha256=row['source_sha256'],target_text=' '.join(lines),lines=lines,table_offset=pos,references=rr))
 def emit(a):a.ret()
 data,ar=append(old,emit,{},bytes(payload));out=bytearray(data)
 table=int(ar['code_address'],16)+ar['labels']['table']
 ph=parse_elf(out)['phdrs']
 for e in entries:
  address=table+e['table_offset'];e['new_address']=hex(address)
  for r in e['references']:
   p=r['address']+192;assert struct.unpack_from('<I',out,p)[0]==e['source_offset']-192
   struct.pack_into('<I',out,p,address)
  p=next(h[1]+address-h[2] for h in ph if h[0]==1 and h[2]<=address<h[2]+h[4])
  actual,end=lines_at(out,p);assert actual==[encode_dialogue(s,'')[0] for s in e['lines']]
  assert out[end:end+2]==b'\0\0'
 return bytes(out),dict(entries=entries,append=ar,help_capacity=dict(lines=2,cells_per_line=27,total_cells=54),patched_elf_sha256=sha(out))

def prepare_tables(source):
 labels,_,rows=collect(source);out=bytearray(labels);bypos={r['source_offset']:r for r in rows};changes=[]
 metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters']
 for pos,(full,text) in ENEMIES.items():
  row=bypos[pos];assert row['contains_japanese'] and any(r['slot']==1 for r in row['references'])
  assert text.isascii() and len(text)<=10
  width=sum(metrics[c]['proposed_advance_pixels'] for c in text)*.875;assert width<=115
  encoded,display=encode_dialogue(text,'');out.extend(bytes(-len(out)%2));new=len(out);out.extend(encoded+b'\0\0')
  for r in row['references']:
   p=r['pointer_field_offset'];assert struct.unpack_from('<I',out,p)[0]==pos;struct.pack_into('<I',out,p,new)
  changes.append(dict(id=row['id'],source_sha256=row['source_sha256'],full_translation=full,text=text,display_text=display,new_offset=new,advance_pixels=width,references=row['references']))
 # Shared strings can also appear as class labels: update every reference.
 for e in changes:
  for r in e['references']:
   p=struct.unpack_from('<I',out,r['pointer_field_offset'])[0]
   assert out[p:p+len(e['display_text'].encode('cp932'))+2]==e['display_text'].encode('cp932')+b'\0\0'
 bank=source.resource('01.DAT',1);bi=parse_index(bank,len(bank));assert child(bank,bi,0)==labels
 master=source.resource('00.DAT',44);mi=parse_index(master,len(master));cached=child(master,mi,6);ci=parse_index(cached,len(cached));assert child(cached,ci,0)==labels
 return {},{1:repack(bank,{0:bytes(out)})},repack(master,{6:repack(cached,{0:bytes(out)})}),dict(tables=[],units=changes,scope='Generic enemy unit names; named cast and named creature species are separate categories.',source_table_sha256=sha(labels),patched_table_sha256=sha(out))

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--write-targets',action='store_true');args=ap.parse_args()
 from sn3_archive import GameSource
 _,r=prepare_elf()
 with GameSource(BASE/'Summon_Night_3_EN_0.1.34.iso') as s:_,_,_,t=prepare_tables(s)
 print(json.dumps(dict(help_groups=len(r['entries']),enemy_labels=len(t['units']),help=[e['lines'] for e in r['entries']],enemies=[e['text'] for e in t['units']]),indent=2))
 if args.write_targets:
  folder=ROOT/'work/translation/en/menu_enemy_0.1.35';folder.mkdir(parents=True,exist_ok=False)
  report=dict(version='0.1.35',help=r['entries'],enemies=t['units'],meaning_review=dict(reviewer='meaning_review035',help_groups=24,source_literals=28,enemy_mappings=39,status='approved after Endless Halls glossary correction',notes='Compact labels preserve identifying distinctions where space allows; full translations retained. Named cast and creature species outside this generic-label scope.'))
  (folder/'targets.reviewed.json').write_text(json.dumps(report,indent=2)+'\n')
