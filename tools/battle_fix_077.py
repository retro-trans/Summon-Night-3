"""Scope centered spell text to banners, preserving list alignment and all prior code."""
import json,struct,hashlib
from sn3_archive import ROOT,GameSource
from menu_code_020 import append
from stat_spacing_026 import _file_offset_for_va
from menu_hotfix_017 import lines_at
from dialogue_encoding import encode_dialogue
from battle_elf_refs import references
BASE=ROOT/'work/output/0.1.76'
TEXT=ROOT/'work/translation/en/battle_0.1.77'
sha=lambda b:hashlib.sha256(b).hexdigest()

def emit(a):
 # s6 is the text owner at this exact native binder call site. The banner
 # owns one row, starts at row zero, and has the two banner contexts set.
 # Reuse the prior exact-name matcher only for that owner configuration.
 a.label('list_or_banner')
 a.branch(4,'s6','zero','list')
 a.i(35,'t0','s6',0x3c);a.i(9,'t1','zero',1);a.branch(5,'t0','t1','list')
 a.i(35,'t0','s6',0x20);a.branch(5,'t0','zero','list')
 a.i(35,'t0','s6',0x50);a.branch(4,'t0','zero','list')
 a.i(35,'t0','s6',0x4c);a.branch(4,'t0','zero','list')
 a.jump(0x35283c,link=False)
 a.label('list');a.jump(0x34a0c8,link=False)

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes()
 data,r=append(old,emit,{0x1b390:('list_or_banner',3<<26|0x35283c>>2)})
 assert data[0x1b394+192:0x1b398+192]==old[0x1b394+192:0x1b398+192]
 r.update(source_sha256=sha(old),output_sha256=sha(data),scope='Native strip binder: list left alignment, exact spell banners centered',preserves_prior_name_matcher=True)
 return data,r

def prepare_tables(source):
 # These messages were translated in 075. Verify the live references, including
 # a group with explicit empty-row termination, rather than rewriting snapshots.
 b=(BASE/'EBOOT.elf').read_bytes();refs=references(b)[0]
 wanted={0x21a3d0:['Equip the crafted stone?','Yes','No'],0x21a404:['Stone equipped.'],0x21a438:['Choose a Summonite Stone.'],0x21a45c:['Change equipment?','Yes','No']}
 cfg=json.loads((ROOT/'work/output/0.1.76/manifest.json').read_text())['menus075_fix']['elf']['entries']
 checked=[]
 for oldva,english in wanted.items():
  e=next(e for e in cfg if e['source_address']==oldva);va=e['new_address'];raw=lines_at(b,_file_offset_for_va(b,va))[0]
  assert raw==[encode_dialogue(t,'')[0] for t in english]
  assert refs.get(va)
  checked.append(dict(source_address=oldva,address=va,english=english,bindings=refs[va]))
 return {},{},source.resource('00.DAT',44),dict(entries=0,existing_crafting_prompts_verified=checked)
