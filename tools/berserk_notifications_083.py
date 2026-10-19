"""Fit battle notifications in the native 31-entry character-row list."""
import hashlib,json
from sn3_archive import ROOT
from dialogue_encoding import encode_dialogue
from stat_spacing_026 import _file_offset_for_va as off

BASE=ROOT/'work/output/0.1.82'
TARGET=ROOT/'work/translation/en/battle_0.1.83/notifications.json'

def encoded(text):return encode_dialogue(text,'')[0]+bytes(2)

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();out=bytearray(old);spec=json.loads(TARGET.read_text('utf8'));changed=[];allowed=set()
 assert spec['max_cells']==31
 for row in spec['entries']:
  before=encoded(row['prior_english']);after=encoded(row['english']);at=off(old,row['current_address'])
  assert old[at:at+len(before)]==before,(hex(row['current_address']),row['prior_english'])
  assert len(row['english'])<=31 and len(after)<=len(before)
  if before==after:continue
  replacement=after+bytes(len(before)-len(after));out[at:at+len(before)]=replacement
  allowed.update(range(at,at+len(before)))
  changed.append(dict(address=hex(row['current_address']),prior_cells=len(before)//2-1,cells=len(after)//2-1,english=row['english']))
 assert len(changed)==9 and all(i in allowed for i,(a,b) in enumerate(zip(old,out)) if a!=b)
 r=dict(version='0.1.83',baseline_sha256=hashlib.sha256(old).hexdigest(),output_sha256=hashlib.sha256(out).hexdigest(),changed_notifications=changed,audited_notifications=len(spec['entries']),max_cells=31,executable_size_unchanged=True,code_and_relocations_unchanged=True,scope='Battle notification text only. Retains 0.1.82 equipment fix; combat logic and save formats unchanged.')
 return bytes(out),r
