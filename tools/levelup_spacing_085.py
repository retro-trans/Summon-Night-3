"""Fit Level Up controller hints in existing English literal allocations."""
import hashlib,json,struct
from sn3_archive import ROOT
from stat_spacing_026 import _file_offset_for_va as off
from dialogue_encoding import encode_dialogue
from stages_pupil_names import parse_elf,validate_loader_structure

BASE=ROOT/'work/output/0.1.84'
TEXT=ROOT/'work/translation/en/ui_0.1.85/targets.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
def encoded(t):return encode_dialogue(t,t)[0]+bytes(2)

def pointer(b,hi,lo):
 h,l=struct.unpack_from('<I',b,hi+192)[0],struct.unpack_from('<I',b,lo+192)[0]
 assert h>>26==15 and l>>26==9
 return ((h&65535)<<16)+(l&65535)-(65536 if l&32768 else 0)

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();cfg=json.loads(TEXT.read_text('utf8'));out=bytearray(old)
 confirm=pointer(old,0x63be8,0x63bf8);controls=pointer(old,0x63c48,0x63c58);skills=pointer(old,0x63c60,0x63c70)
 assert (confirm,controls,skills)==(0x3525e4,0x352660,0x352674)
 for p,t in [(confirm,'АConfirm'),(controls,'АOK БEnd'),(skills,'Й     Learn Skills')]:assert old[off(old,p):off(old,p)+len(encoded(t))]==encoded(t)
 # 20 bytes for confirmation, followed elsewhere by the contiguous 20+40
 # byte controls/skills allocation. Reuse it without growing PSP memory.
 cb=encoded(cfg['confirm']);first=encoded(cfg['controls']);second=encoded(cfg['skills']);assert len(cb)<=20
 second_offset=(len(first)+3)//4*4;assert second_offset+len(second)<=60
 allowed=set();segments=[]
 for p,span,raw in [(confirm,20,cb),(controls,60,first+bytes(second_offset-len(first))+second)]:
  f=off(old,p);out[f:f+span]=raw+bytes(span-len(raw));allowed.update(range(f,f+span));segments.append(dict(address=p,bytes=span))
 new_skills=controls+second_offset;assert (new_skills+0x8000)>>16==(skills+0x8000)>>16
 low=0x63c70+192;word=struct.unpack_from('<I',old,low)[0];struct.pack_into('<I',out,low,(word&0xffff0000)|(new_skills&65535));allowed.update(range(low,low+4))
 assert len(out)==len(old) and all(i in allowed for i,(a,b) in enumerate(zip(old,out)) if a!=b)
 assert parse_elf(old)['phdrs']==parse_elf(out)['phdrs'];assert validate_loader_structure(out)
 r=dict(version='0.1.85',source_sha256=sha(old),output_sha256=sha(out),confirm_address=confirm,controls_address=controls,skills_address=new_skills,changed_allocations=segments,changed_pointer_low=hex(0x63c70),loaded_bytes_added=0,iso_growth_bytes=0,button_tokens_preserved=True,relocations_unchanged=True,save_bytes_unchanged=True)
 return bytes(out),r
