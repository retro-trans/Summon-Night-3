"""Accessory names/effect text and missing Deployment Learn Skills branches."""
import json,struct,hashlib,unicodedata
import battle_elf_patch as patcher
from sn3_archive import ROOT,parse_index,child
from sn3_repack import repack
from dialogue_encoding import encode_dialogue
from stat_spacing_026 import _file_offset_for_va
from menu_code_020 import append
from font_patch import REG

BASE=ROOT/'work/output/0.1.39'
FOLDER=ROOT/'work/translation/en/accessories_0.1.40'
sha=lambda b:hashlib.sha256(b).hexdigest()
TARGETS={0x2171ac:'Hit+',0x2171b8:'Evade+',0x2171c4:'Move:',
 0x2171ec:'Down:',0x2171f8:' On Hit',0x217204:' Attack',0x217210:'Range+',
 0x217218:'Res ',0x21721c:'Poss. Proof',0x217228:'Half Ailments',
 0x217234:' Half',0x21723c:'Ailment Proof',0x217248:' Proof',
 0x217250:'Female Only',0x21725c:'Male Only'}

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();idx=patcher.indexed_rows()
 previous=patcher.BASELINE
 try:
  patcher.BASELINE=BASE/'EBOOT.elf'
  data,report=patcher.prepare(old,[dict(idx[f'elf:ui:{o:08x}'],target_full=t) for o,t in TARGETS.items()],idx)
 finally:patcher.BASELINE=previous
 assert not report['skipped'],report['skipped']
 out=bytearray(data)
 # Two shared-HI movement literals are safely shortened inside their own slots.
 for off,text in {0x2171d0:'Up/Dn:',0x2171e0:'Up:'}.items():
  row=idx[f'elf:ui:{off:08x}'];n=row['source_byte_length']
  assert sha(old[off:off+n])==row['source_sha256']
  raw,display=encode_dialogue(text,'');assert len(raw)<=n
  out[off:off+n]=raw+bytes(n-len(raw))
  report['entries'].append(dict(id=row['id'],target_text=text,display_text=display,mode='in_place',new_file_offset=off))
 # The old translation patched two linear consumers, missing these two branch
 # entries. Each LUI is on the taken edge; its fallthrough is overwritten.
 addr=0x3389a0;p=_file_offset_for_va(out,addr)
 expected=encode_dialogue('Й Learn Skills','Й')[0]+b'\0\0'
 assert out[p:p+len(expected)]==expected
 branches=[]
 for hi,lo in [(0x6384c,0x63878),(0x639d0,0x639fc)]:
  assert struct.unpack_from('<I',old,hi+192)[0]==0x3c060021
  assert struct.unpack_from('<I',old,lo+192)[0]==0x24c66f00
  struct.pack_into('<I',out,hi+192,0x3c060000|((addr+0x8000)>>16))
  struct.pack_into('<I',out,lo+192,0x24c60000|(addr&65535))
  branches.append(dict(high=hex(hi),low=hex(lo),target=hex(addr)))
 report['learn_skills_branch_fixes']=branches
 # Key-item branch-entry HI paired with the already translated label's LO.
 assert struct.unpack_from('<I',old,0x65864+192)[0]==0x3c070021
 assert struct.unpack_from('<I',old,0x6589c+192)[0]==0x24e7fd98
 struct.pack_into('<I',out,0x65864+192,0x3c070034)
 report['key_item_branch_fix']='0x65864'
 # Preserve the native single-cell affinity slots.
 for off,jp,en in zip(range(0x218f6c,0x218f80,4),'機鬼霊獣無','MOSBN'):
  assert old[off:off+4]==jp.encode('cp932')+b'\0\0'
  out[off:off+4]=encode_dialogue(en,'')[0]+b'\0\0'
 report['affinity_labels']='M/O/S/B/N (Machine/Oni/Spirit/Beast/Null)'
 # Ailment group scratch buffers hold only 27 cells including NUL. For 3+
 # effects use short forms locally; other UI and single effects retain names.
 compact=['Stone','Chrm','Rge','Psn','Para','Bld','Seal','Sleep']
 table=b'';offsets=[]
 for text in compact:offsets.append(len(table));table+=encode_dialogue(text,'')[0]+b'\0\0'
 def emit(a):
  a.label('effect_name');a.i(9,'t0','zero',0);a.i(9,'t1','zero',0)
  a.label('count');a.emit(REG['s6']<<21|REG['t0']<<16|REG['t2']<<11|0x21)
  a.i(32,'t2','t2',0x10);a.branch(5,'t2','s3','next');a.i(9,'t1','t1',1)
  a.label('next');a.i(9,'t0','t0',1);a.i(11,'t2','t0',8);a.branch(5,'t2','zero','count')
  a.i(11,'t2','t1',3);a.branch(4,'t2','zero','compact');a.jump(0x67558,link=False)
  a.label('compact')
  for n,off in enumerate(offsets,1):
   a.i(9,'t0','zero',n);a.branch(5,'a0','t0',f'next_{n}')
   a.table_address('v0');a.i(9,'v0','v0',off);a.ret();a.label(f'next_{n}')
  a.jump(0x67558,link=False)
 out,helpers=append(bytes(out),emit,{site:('effect_name',3<<26|0x67558>>2) for site in [0x655d0,0x65708]},table)
 report['effect_name_helpers']=helpers
 report['retained_native_stat_spacing']=out[0x642c0+192:0x642c8+192]==old[0x642c0+192:0x642c8+192]
 assert report['retained_native_stat_spacing']
 return bytes(out),report

def prepare_tables(source):
 index=json.loads((ROOT/'work/translation/en/interface.index.json').read_text())
 table=next(t for t in index['tables'] if t['resource_path']==[3,17])
 rows={r['id']:r for r in table['strings']}
 targets=json.loads((FOLDER/'targets.json').read_text())['entries']
 static=source.resource('02.DAT',3);si=parse_index(static,len(static));before=child(static,si,17);out=bytearray(before);changes=[];fields=set()
 for target in targets:
  row=rows[target['id']];p=row['source_offset'];n=row['source_byte_length'];text=target['text']
  assert sha(before[p:p+n])==row['source_sha256']==target['source_sha256']
  assert text.isascii() and 0<len(text)<=15
  assert row['references'] and all(r['slot']==19 for r in row['references'])
  raw,display=encode_dialogue(text,'');out.extend(bytes(-len(out)%2));pos=len(out);out.extend(raw+b'\0\0')
  for ref in row['references']:
   f=ref['pointer_field_offset'];assert struct.unpack_from('<I',before,f)[0]==p
   struct.pack_into('<I',out,f,pos);fields.update(range(f,f+4))
  changes.append(dict(id=row['id'],text=text,new_offset=pos,references=row['references']))
 # Numeric stats, recipe relationships and all other table bytes stay exact.
 assert all(a==b for i,(a,b) in enumerate(zip(before,out)) if i not in fields)
 for rec in range(table['record_count']):
  f=4+rec*table['record_stride']+19*4;p=struct.unpack_from('<I',out,f)[0]
  if not p:continue
  end=p
  while out[end:end+2]!=b'\0\0':end+=2
  text=unicodedata.normalize('NFKC',out[p:end].decode('cp932'))
  assert not any('\u3040'<=c<='\u9fff' for c in text),(rec,text)
 patched=repack(static,{17:bytes(out)});master=source.resource('00.DAT',44);mi=parse_index(master,len(master))
 assert child(master,mi,7)==static
 return {3:patched},{},repack(master,{7:patched}),dict(units=[],tables=[dict(child=17,changes=changes)],all_accessory_names_english=True,stats_and_recipes_unchanged=True)
