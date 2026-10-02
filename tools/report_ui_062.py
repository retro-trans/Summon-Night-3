"""Append small UI translations and scope the Set hint on immutable 0.1.61."""
import json,struct,hashlib,unicodedata
from sn3_archive import ROOT,parse_index,child
from sn3_repack import repack
from dialogue_encoding import encode_dialogue
from menu_code_020 import append
from stages_pupil_names import validate_loader_structure
from stat_spacing_026 import _file_offset_for_va
from menu_hotfix_017 import lines_at
from spell_name_059 import label
BASE=ROOT/'work/output/0.1.61'
TEXT=ROOT/'work/translation/en/report_0.1.62/strings.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();s=json.loads(TEXT.read_text(encoding='utf8'));names=s['banner_names']
 payload=bytearray(4+8*len(names));struct.pack_into('<I',payload,0,len(names))
 for i,text in enumerate(names):
  b=encode_dialogue(text,'')[0];assert 0<len(b)//2<=32
  struct.pack_into('<II',payload,4+8*i,len(payload),len(b)//2);payload.extend(b+b'\0\0')
 payload.extend(bytes(-len(payload)%4));hint_offset=len(payload);payload.extend(encode_dialogue('Set','')[0]+b'\0\0')
 patched,r=append(old,lambda a:a.ret(),{},bytes(payload));out=bytearray(patched);table=int(r['code_address'],16)+r['labels']['table']
 def pair(hi,lo,va):
  # Existing PRX HI16/LO16 pairs continue to relocate the appended segment.
  h=struct.unpack_from('<I',out,hi+192)[0];l=struct.unpack_from('<I',out,lo+192)[0]
  assert h>>26==15 and l>>26==9
  struct.pack_into('<I',out,hi+192,(h&0xffff0000)|((va+0x8000)>>16));struct.pack_into('<I',out,lo+192,(l&0xffff0000)|(va&65535))
 # Added code is not at the main segment's file offset.
 for va,imm in [(0x3526a4,(table+0x8000)>>16),(0x3526a8,table&65535)]:
  p=_file_offset_for_va(out,va);w=struct.unpack_from('<I',out,p)[0];assert w>>26 in (15,9);struct.pack_into('<I',out,p,(w&0xffff0000)|imm)
 pair(0x154b38,0x154b48,table+hint_offset)
 coordinates=[]
 for va,before,after in [(0x1546d8,135,184),(0x1546e0,151,200)]:
  def word(x):return (15<<26)|(4<<16)|(struct.unpack('<I',struct.pack('<f',x))[0]>>16)
  assert struct.unpack_from('<I',old,va+192)[0]==word(before);struct.pack_into('<I',out,va+192,word(after));coordinates.append(dict(va=hex(va),before=before,after=after,screen_x=240+after))
 allowed={i for va in [0x3526a4,0x3526a8,0x154b38,0x154b48,0x1546d8,0x1546e0] for i in range(_file_offset_for_va(out,va),_file_offset_for_va(out,va)+4)}
 assert all(i in allowed for i,(x,y) in enumerate(zip(patched,out)) if x!=y)
 # Metadata retains the original wrapper entries for execution-based audits.
 prior=json.loads((BASE/'manifest.json').read_text())['report061_ui']['elf'];report=dict(prior)
 report.update(source_sha256=sha(old),output_sha256=sha(out),names=names,extended_match_table=hex(table),set_hint_address=hex(table+hint_offset),set_coordinates=coordinates,structure=validate_loader_structure(out),append=r)
 return bytes(out),report
def prior_audit_view(elf):
 expected,_=prepare_elf();assert elf==expected,'Unexpected 0.1.62 executable changes';return (BASE/'EBOOT.elf').read_bytes()
def prepare_names(source,write_assets=False):
 s=json.loads(TEXT.read_text(encoding='utf8'));static=source.resource('02.DAT',3);ix=parse_index(static,len(static));changed={};reports=[]
 groups={12:[],13:[],28:[]}
 for row in s['summon']['alternates']:groups[12].append(dict(record=23,**row))
 groups[12].append(dict(record=23,slot=12,source=s['summon']['source'],english=s['summon']['help']))
 groups[13]=s['spells']
 for row in s['skills']:
  groups[28].append(row);groups[28].append(dict(record=row['record'],slot=9,source=['剣の力を解放し覚醒状態になる','全異常・憑依無効　暴走召喚使用可'],english=s['awakening']['help']))
 for n,rows in groups.items():
  stride={12:52,13:40,28:48}[n];old=child(static,ix,n);out=bytearray(old);allowed=set();entries=[]
  for row in rows:
   field=4+row['record']*stride+row['slot']*4;ptr=struct.unpack_from('<I',old,field)[0];before,_=lines_at(old,ptr)
   actual=[unicodedata.normalize('NFKC',b.decode('cp932')) for b in before]
   wanted=row['source'] if isinstance(row['source'],list) else [row['source']]
   if not isinstance(row['source'],list):actual=actual[:1]
   # The source uses fullwidth spaces; compare normalized spacing only.
   norm=lambda x:' '.join(unicodedata.normalize('NFKC',x).split())
   assert list(map(norm,actual))==list(map(norm,wanted)),(n,row['record'],row['slot'],actual,wanted)
   texts=row['english'] if isinstance(row['english'],list) else [row['english']]
   if len(texts)>1:assert len(texts)==2 and max(map(len,texts))<=27 and sum(map(len,texts))<=54
   else:assert len(texts[0])<=16
   encoded=[encode_dialogue(x,'')[0] for x in texts];blob=b''.join(b+b'\0\0' for b in encoded)+(b'\0\0' if len(texts)>1 else b'')
   out.extend(bytes(-len(out)%2));new=len(out);out.extend(blob);struct.pack_into('<I',out,field,new);allowed.update(range(field,field+4))
   assert lines_at(out,new)[0]==encoded if len(texts)>1 else label(out,field)==texts[0]
   entries.append(dict(record=row['record'],slot=row['slot'],before=actual,english=texts,pointer_field=field,offset=new,cells=list(map(len,texts))))
  out.extend(bytes(-len(out)%ix['unit_bytes']))
  assert all(i in allowed for i,(a,b) in enumerate(zip(old,out)) if a!=b);changed[n]=bytes(out);reports.append(dict(table=n,source_sha256=sha(old),output_sha256=sha(out),entries=entries))
 patched=repack(static,changed);ni=parse_index(patched,len(patched));assert all(child(patched,ni,e['id'])==changed.get(e['id'],child(static,ix,e['id'])) for e in ix['entries'])
 return {3:patched},reports
