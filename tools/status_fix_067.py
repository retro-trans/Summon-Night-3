"""Keep Status help within two visible rows; align its SELECT icon."""
import json,struct
from sn3_archive import ROOT
from dialogue_encoding import encode_dialogue
from menu_code_020 import append
from status_fix_066 import emit as emit_food,sha
from stat_spacing_026 import _file_offset_for_va
from stages_pupil_names import validate_loader_structure
BASE=ROOT/'work/output/0.1.66'
TEXT=ROOT/'work/translation/en/status_0.1.67/targets.json'
def emit(a,fallback):
 # Reuse the measured prefix calculation; compare a bounded 12-cell label
 # after SELECT and five spaces rather than Give Food and one space.
 emit_food(a,fallback)
 a.labels['skills_icon']=a.labels.pop('food_icon')
 words=a.words
 old=36<<26|19<<21|8<<16|0x101
 assert words[0]==old
 changes={11<<26|8<<21|9<<16|17:11<<26|8<<21|9<<16|12,
          9<<26|8<<21|8<<16|0x8a:9<<26|8<<21|8<<16|0x92,
          9<<26|10<<16|9:9<<26|10<<16|12}
 for before,after in changes.items():
  assert words.count(before)==1,hex(before);words[words.index(before)]=after
def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();out=bytearray(old);entries=[]
 targets=json.loads(TEXT.read_text(encoding='utf8'))['entries'];skill_raw=None
 for e in targets:
  va=int(e['address'],16);pos=_file_offset_for_va(old,va)
  before=encode_dialogue(e['before'],e['before'])[0]+b'\0\0'
  after=encode_dialogue(e['english'],e['english'])[0]+b'\0\0'
  capacity=e['capacity_bytes']
  assert old[pos:pos+len(before)]==before and not any(old[pos+len(before):pos+capacity])
  if e.get('relocate'):skill_raw=after
  else:
   assert len(after)<=capacity;out[pos:pos+capacity]=after.ljust(capacity,b'\0')
  entries.append(dict(address=e['address'],english=e['english'],capacity_bytes=capacity,cells=len(e['english'])))
 word=struct.unpack_from('<I',old,0x64490+192)[0];assert word>>26==3;prior=(word&0x3ffffff)<<2
 payload=encode_dialogue('Learn Skills','')[0]+b'\0\0';payload+=bytes(-len(payload)%4)
 skill_offset=len(payload);payload+=skill_raw;payload+=bytes(-len(payload)%4)
 result,r=append(bytes(out),lambda a:emit(a,prior),{0x64490:('skills_icon',word)},payload)
 result=bytearray(result);address=int(r['code_address'],16)+r['labels']['table']+skill_offset;bindings=[]
 for hi,lo in ((0x6384c,0x63878),(0x639d0,0x639fc),(0x63b14,0x63b24)):
  assert struct.unpack_from('<I',old,hi+192)[0]==0x3c060034
  assert struct.unpack_from('<I',old,lo+192)[0]==0x24c689a0
  struct.pack_into('<I',result,hi+192,0x3c060000|((address+0x8000)>>16))
  struct.pack_into('<I',result,lo+192,0x24c60000|(address&65535));bindings.append([hex(hi),hex(lo)])
 r.update(learn_skills_address=hex(address),bindings=bindings)
 r.update(entries=entries,source_sha256=sha(old),output_sha256=sha(result),fallback=hex(prior),scope='Bounded second-row SELECT followed by five spaces and Learn Skills; earlier Give Food/icon handlers remain fallback.',structure=validate_loader_structure(result))
 return bytes(result),r
def prepare_tables(source):
 return {3:source.resource('02.DAT',3)},{},source.resource('00.DAT',44),dict(units=[],tables=[],player_entered_names_unchanged=True,default_protagonist_names_already_translated=True)
if __name__=='__main__':
 _,r=prepare_elf();print(json.dumps(dict(mode='preview',entries=r['entries'],scope=r['scope'],helper=r['code_address']),indent=2))
