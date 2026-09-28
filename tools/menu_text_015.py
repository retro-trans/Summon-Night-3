"""Relocate backlog, attack styles and full menu help groups; preview first."""
import argparse,hashlib,json
from pathlib import Path
import battle_elf_patch as patcher
from dialogue_encoding import encode_dialogue
from sn3_archive import ROOT

BASE=ROOT/'work/output/0.1.14/EBOOT.elf'
OUT=ROOT/'work/translation/en/menu_0.1.15'
TEXT={
 0x2176fc:'V. Slash',0x217704:'H. Slash',0x21770c:'Thrust',
 0x217714:'Strike',0x21771c:'Fire',0x217724:'Throw',0x21772c:'Special',
 0x217734:'V. Throw',0x21773c:'H. Throw',
 0x217bb8:'Select units to deploy.',0x217bd6:'Check status and change equipment.',
 0x217bf8:'View Party Abilities and change',0x217c1c:'which ones to use in battle.',
 0x217c3c:'Check the victory and defeat conditions.',
 0x217c60:'View your inventory.',0x217c7c:'View summon details and combination results.',
 0x217cb4:'Change game settings.',0x217cd4:'Save the game.',0x217cf4:'Load a saved game.',
 0x217e1c:'Start the battle.',0x21c6c0:'Replay',
}
HELP_LINES={
 0x217bd6:['Check status and change','equipment.'],
 0x217bf8:['View Party Abilities','and change'],
 0x217c3c:['Check the victory and defeat','conditions.'],
 0x217c7c:['View summon details and','combination results.'],
}

def prepare():
 index=patcher.indexed_rows();raw=(ROOT/'work/source/EBOOT.elf').read_bytes()
 # The old index begins three bytes before this actual string. Preserve those
 # binary bytes; only the relocation-backed start at module0x21c600 is text.
 off=0x21c6c0;end=raw.index(b'\0',off)
 index[f'elf:ui:{off:08x}']=dict(id=f'elf:ui:{off:08x}',source_offset=off,module_address=hex(off-0xc0),source_byte_length=end-off,source_sha256=hashlib.sha256(raw[off:end]).hexdigest(),source_control_tokens=[])
 targets=[dict(index[f'elf:ui:{off:08x}'],target_full=t,layout_lines=HELP_LINES.get(off,[t])) for off,t in TEXT.items()]
 old_base=patcher.BASELINE;old_roots=patcher.TRANSLATABLE_TAIL_ROOTS
 old_encoder=patcher.encoded_target
 def menu_encoder(target,source_raw):
  text,display,encoded,variant=old_encoder(target,source_raw)
  lines=target['layout_lines']
  assert ' '.join(lines)==text
  if len(lines)>1:
   encoded=b''.join(encode_dialogue(line,source_raw.decode('cp932'))[0]+b'\0\0' for line in lines)
  return text,display,encoded,variant
 try:
  patcher.BASELINE=BASE
  patcher.encoded_target=menu_encoder
  # Getter0x67da8 ->0x632a0 ->0x64820 consumes up to3 NUL-terminated
  # U16 lines, ending on an empty line. No fixed source byte stride.
  # Copy loop0x649dc..0x64a34 and0xae-byte staging buffer were inspected.
  patcher.TRANSLATABLE_TAIL_ROOTS={0x217af8,0x217b38}
  elf,report=patcher.prepare(BASE.read_bytes(),targets,index)
 finally:
  patcher.BASELINE=old_base;patcher.TRANSLATABLE_TAIL_ROOTS=old_roots
  patcher.encoded_target=old_encoder
 # Only explicit continuation rows have no independent reference.
 assert {r['id'] for r in report['skipped']}=={'elf:ui:00217bd6','elf:ui:00217c1c'},report['skipped']
 assert len(report['entries'])==19
 for row in report['entries']:
  if row['id']=='elf:ui:00217bb8':assert len(row['unreferenced_tails'])==1
  if row['id']=='elf:ui:00217bf8':assert len(row['unreferenced_tails'])==1
 report['profile']='menu_text_0.1.15';report['translated_strings']=21
 report['meaning_review']='Independent agent reviewed screenshot labels and exact source strings; compact Replay retains voice action context.'
 report['consumer_proof']={'help_getter':'0x67da8','help_setter':'0x632a0','copy_loop':'0x649dc..0x64a34','max_lines':3,'staging_bytes':174,'longest_help_group_bytes':max(sum((len(t)+1)*2 for o,t in TEXT.items() if o in offsets)+2 for offsets in [(0x217bb8,0x217bd6),(0x217bf8,0x217c1c)])}
 assert report['consumer_proof']['longest_help_group_bytes']<=174
 groups=[(0x217bb8,0x217bd6),(0x217bf8,0x217c1c)]+[(o,) for o in TEXT if 0x217c3c<=o<=0x217e1c]
 report['help_layout']=[]
 for offsets in groups:
  lines=[line for off in offsets for line in HELP_LINES.get(off,[TEXT[off]])]
  assert len(lines)<=3 and max(map(len,lines))<=30
  size=sum((len(line)+1)*2 for line in lines)+2
  assert size<=174
  report['help_layout'].append(dict(source_offsets=list(offsets),lines=lines,bytes_with_empty_terminator=size))
  entry=next(e for e in report['entries'] if e['source_offset']==offsets[0])
  pos=entry['new_file_offset'];actual=[]
  for _ in range(3):
   start=pos
   while elf[pos:pos+2]!=b'\0\0':
    pos+=2
    assert pos-start<=174
   if pos==start:break
   actual.append(elf[start:pos]);pos+=2
  assert actual==[encode_dialogue(line,'')[0] for line in lines]
 return elf,report,targets

def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 elf,report,targets=prepare()
 print(json.dumps(dict(mode='write' if a.write else 'dry-run',strings=report['translated_strings'],groups=len(report['entries']),samples=[r['target_text'] for r in report['entries']],consumer=report['consumer_proof']),indent=2))
 if a.write:
  OUT.mkdir(parents=True,exist_ok=True)
  for name,data in [('text.layout.targets.json',{'version':'0.1.15','entries':targets}),('text.layout.report.json',report)]:
   with (OUT/name).open('x') as stream:stream.write(json.dumps(data,indent=2)+'\n')
if __name__=='__main__':main()
