"""Relocate reviewed menu text and correct compact native labels. Preview first."""
import argparse,json,struct
from pathlib import Path
import battle_elf_patch as patcher
from battle_table_patch import relocate_fullwidth
from dialogue_encoding import encode_dialogue
from sn3_archive import ROOT,parse_index,child,GameSource
from sn3_repack import repack
from character_labels import collect

BASE=ROOT/'work/output/0.1.15'
FOLDER=ROOT/'work/translation/en/menu_0.1.16'
COMPACT={0x21e22c:'Affinity',0x216f74:'View status; change equipment.',0x217d14:'View status; change equipment.',
 0x21700c:'АDeploy ВStatus/Gear БMap',0x21ca58:'Adjust music volume.',
 0x21ca7c:'Turn event voices on or off.',0x21caa0:'Turn damage forecast on/off.',
 0x21cac8:'Set battle cursor directions.',0x21caf0:'Set L/R controls in battle.'}

def prepare_elf():
 review=json.loads((FOLDER/'meaning_review.json').read_text());idx=patcher.indexed_rows()
 prev=json.loads((BASE/'manifest.json').read_text())
 done={e['id'] for name in ['battle_elf','menu_text'] for e in prev[name]['entries']}
 done|={e['id'] for name in ['battle_elf','menu_text'] for r in prev[name]['entries'] for e in r.get('unreferenced_tails',[])}
 targets=[]
 for r in review['entries']:
  if not r['id'].startswith('elf:') or r['id'] in done:continue
  e=dict(idx[r['id']]);assert r['source_sha256']==e['source_sha256']
  e.update(target_full=COMPACT.get(e['source_offset'],r['target_full']))
  targets.append(e)
 old=patcher.BASELINE
 try:
  patcher.BASELINE=BASE/'EBOOT.elf'
  elf,report=patcher.prepare(patcher.BASELINE.read_bytes(),targets,idx)
 finally:patcher.BASELINE=old
 assert not report['skipped'],report['skipped']
 out=bytearray(elf);fixed=[]
 for identity,text in [('elf:ui:00218750','Protagonist KO'),('elf:ui:00218764','All allies KO')]:
  e=next(e for e in prev['battle_elf']['entries'] if e['id']==identity)
  start=e['new_file_offset'];count=e['encoded_bytes'];data,display=encode_dialogue(text,'')
  assert len(data)+2<=count and out[start:start+count]==e['display_text'].encode('cp932')+b'\0\0'
  out[start:start+count]=data+b'\0'*(count-len(data))
  fixed.append(dict(id=identity,text=text,new_file_offset=start,new_address=e['new_address'],bundle_bytes=count,display_text=display))
 report.update(profile='menu_0.1.16',compact_conditions=fixed)
 return bytes(out),report

def prepare_tables(source):
 review=json.loads((FOLDER/'meaning_review.json').read_text())
 idx=json.loads((ROOT/'work/translation/en/interface.index.json').read_text())
 wanted={e['id']:dict(e) for e in review['entries'] if e['id'].startswith('02:')}
 for e in wanted.values():
  if e['id'].startswith('02:00003/00032:'):e['target_full']='Search for ingredients.'
 wanted['02:00003/00012:ui:0000147e']['target_full']='Large-drill land developer.'
 wanted['02:00003/00012:ui:000014b4']['target_full']='Built for long polar work.'
 static=source.resource('02.DAT',3);si=parse_index(static,len(static));replacements={};reports=[]
 for table in idx['tables']:
  choices={r['id']:dict(text=wanted[r['id']]['target_full'],source_sha256=wanted[r['id']]['source_sha256']) for r in table['strings'] if r['id'] in wanted}
  if not choices:continue
  starts={r['id']:choices[r['id']] for r in table['strings'] if r['id'] in choices and r['references']}
  n=table['resource_path'][1];before=child(static,si,n)
  after,changes,skipped=relocate_fullwidth(before,table['strings'],starts,choices)
  replacements[n]=after;reports.append(dict(child=n,changes=changes,skipped=skipped))
 patched_static=repack(static,replacements)
 # The class label inserted by the first build is ASCII, while status reads U16.
 labels,_,entries=collect(source);out=bytearray(labels)
 row=next(r for r in entries if labels[r['source_offset']:r['source_offset']+r['source_byte_length']]==b'Family Teacher')
 assert all(r['slot']==2 for r in row['references']) and len(row['references'])==6
 out.extend(bytes(-len(out)%2));pos=len(out);encoded,_=encode_dialogue('Tutor','');out.extend(encoded+b'\0\0')
 for r in row['references']:struct.pack_into('<I',out,r['pointer_field_offset'],pos)
 bank01=repack(source.resource('01.DAT',1),{0:bytes(out)})
 master=source.resource('00.DAT',44);mi=parse_index(master,len(master))
 assert child(master,mi,7)==static
 cached=child(master,mi,6);ci=parse_index(cached,len(cached));assert child(cached,ci,0)==labels
 master=repack(master,{6:repack(cached,{0:bytes(out)}),7:patched_static})
 return {3:patched_static},{1:bank01},master,dict(tables=reports,class_label=dict(full='Family Teacher',compact='Tutor',old_offset=row['source_offset'],new_offset=pos,references=row['references'],encoding='two_byte_cp932'))

def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 elf,er=prepare_elf()
 with GameSource(BASE/'Summon_Night_3_EN_0.1.15.iso') as s:_,_,_,tr=prepare_tables(s)
 report=dict(elf=er,tables=tr)
 print(json.dumps(dict(mode='write' if a.write else 'dry-run',elf=[e['target_text'] for e in er['entries']],conditions=er['compact_conditions'],tables=[dict(child=r['child'],count=len(r['changes']),skipped=r['skipped']) for r in tr['tables']],class_label=tr['class_label']),indent=2))
 if a.write:
  with (FOLDER/'insertion.final.report.json').open('x') as f:f.write(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
