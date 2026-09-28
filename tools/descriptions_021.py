"""Spell-description translations on 0.1.20, with native formatter validation."""
import json,struct,hashlib
import battle_elf_patch as patcher
from sn3_archive import ROOT,parse_index,child
from sn3_repack import repack
from dialogue_encoding import encode_dialogue
from menu_hotfix_017 import lines_at,glyph_check
from verify_descriptions_021 import verify

BASE=ROOT/'work/output/0.1.20'
FOLDER=ROOT/'work/translation/en/descriptions_0.1.21'
sha=lambda b:hashlib.sha256(b).hexdigest()
TARGETS={0x21727c:'Deploy using Unit Summon.',0x2172b4:'ATK Pwr:',0x2172c8:'HP Heal Pwr:',
 0x2172dc:'+Cure?',0x2172e8:'+Cure',0x2172fc:'Poss.',0x21730c:'Single',
 0x217318:'Small',0x217324:'Med.',0x217330:'Lrg.',
 0x21733c:'Area: V5',0x217348:'Area: V3',0x217354:'Area: Cross H2',
 0x217364:'Area: H3',0x217370:'Area: V/H3',0x217380:'Favorites only',
 0x217390:'Assist only ВAssist members'}

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();idx=patcher.indexed_rows();targets=[]
 # The scanner split this controller glyph from its suffix. The native formatter
 # consumes the whole U16 string, verified through its terminator.
 r=idx['elf:ui:00217390'];raw=old[0x217390:0x2173b4]
 assert raw.decode('cp932')=='アシスト専用　Вアシストメンバー確認'
 r.update(source_byte_length=len(raw),source_sha256=sha(raw))
 for off,text in TARGETS.items():targets.append(dict(idx[f'elf:ui:{off:08x}'],target_full=text))
 previous=patcher.BASELINE
 try:
  patcher.BASELINE=BASE/'EBOOT.elf';data,report=patcher.prepare(old,targets,idx)
 finally:patcher.BASELINE=previous
 assert not report['skipped'],report['skipped']
 # This prefix uses a HI16 across a branch. Keep its proven five-cell slot;
 # no speculative relocation and no change to surrounding code or data.
 out=bytearray(data)
 # Alternate branch-entry HI16s share the relocated LO16s. The conservative
 # linear reference scan sees only the fall-through entry. Both edges are
 # exercised by the unchanged native formatter in verify_descriptions_021.
 aliases={0x21730c:[0x65d7c],0x217318:[0x65cdc],0x217324:[0x65db0],
          0x217330:[0x65d10,0x65dd8],0x217380:[0x65e80],0x217390:[0x65ed0]}
 alias_changes=[]
 for offset,addresses in aliases.items():
  e=next(e for e in report['entries'] if e['source_offset']==offset)
  high=(int(e['new_address'],16)+0x8000)>>16
  for addr in addresses:
   w=struct.unpack_from('<I',old,addr+192)[0];assert w==0x3c060021
   struct.pack_into('<I',out,addr+192,(w&0xffff0000)|high)
   alias_changes.append(dict(instruction=hex(addr),source_id=e['id'],before=hex(w),after=hex((w&0xffff0000)|high)))
 report['branch_entry_high_halves']=alias_changes
 row=idx['elf:ui:002172f0'];p=row['source_offset'];n=row['source_byte_length']
 assert sha(old[p:p+n])==row['source_sha256']
 encoded,display=encode_dialogue('Ail: ','');assert len(encoded)==n
 out[p:p+n]=encoded
 report['entries'].append(dict(id=row['id'],target_text='Ail: ',source_sha256=row['source_sha256'],mode='same_size_in_place',new_file_offset=p,display_text=display))
 manifest=json.loads((BASE/'manifest.json').read_text())
 for e in manifest['menu017_hotfix']['changes']:
  p,n=e['new_file_offset'],e['span'];assert out[p:p+n]==old[p:p+n];glyph_check(lines_at(out,p)[0])
 report['retained_crash_fixes']=5
 return bytes(out),report

def prepare_tables(source):
 index=json.loads((ROOT/'work/translation/en/interface.index.json').read_text());static=source.resource('02.DAT',3);si=parse_index(static,len(static))
 replacements={};reports=[]
 for number in (1,13):
  table=next(t for t in index['tables'] if t['resource_path']==[3,number]);rows={r['id']:r for r in table['strings']}
  before=child(static,si,number);out=bytearray(before);changes=[];pending=[]
  if number==1:
   reviews=json.loads((FOLDER/'possession.review.json').read_text())['entries']
   targets=[dict(root_id=k,rows=[dict(id=k,source_sha256=v['source_sha256'])],lines=[v['compact']]) for k,v in reviews.items() if v['slot']==7]
  else:
   reviews=json.loads((FOLDER/'special_spells.review.json').read_text())['entries']
   targets=[]
   for r in reviews:
    targets.append(dict(r,lines=r['proposed_display_lines']))
  for target in targets:
   r=rows[target['root_id']];old=r['source_offset'];fields=[f['pointer_field_offset'] for f in r['references']]
   assert all(struct.unpack_from('<I',before,f)[0]==old for f in fields),(number,r['id'],'already relocated')
   for rr in target['rows']:
    sr=rows[rr['id']];p,n=sr['source_offset'],sr['source_byte_length'];assert sha(before[p:p+n])==rr['source_sha256']
   texts=target['lines'];assert len(texts)<=2 and all(0<len(s)<=27 for s in texts),texts
   raw=[encode_dialogue(s,'')[0] for s in texts];glyph_check(raw)
   out.extend(bytes(-len(out)%2));new=len(out);out.extend(b''.join(b+b'\0\0' for b in raw)+b'\0\0')
   for f in fields:struct.pack_into('<I',out,f,new)
   changes.append(dict(id=r['id'],lines=texts,source_rows=target['rows'],old_offset=old,new_offset=new,pointer_fields=fields))
  replacements[number]=bytes(out);reports.append(dict(child=number,changes=changes,pending=pending))
 patched=repack(static,replacements);master=source.resource('00.DAT',44);mi=parse_index(master,len(master));assert child(master,mi,7)==static
 master=repack(master,{7:patched})
 elf,_=prepare_elf();cases=verify(elf,patched)
 for c in cases:
  assert len(c['lines'])<=2 and max(c['lengths'],default=0)<=27 and c['total']<=54,c
  assert all(not any('\u3040'<=ch<='\u9fff' for ch in s) for s in c['lines']),c
 return {3:patched},{},master,dict(units=[],tables=reports,native_formatter_cases=cases)
