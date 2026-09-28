"""Translate the locked-feature popup and center its proportional glyphs."""
import json,struct,hashlib
import battle_elf_patch as patcher
import notice_vwf_027 as notice
from sn3_archive import ROOT
from menu_code_020 import append
BASE=ROOT/'work/output/0.1.30'
TEXT='Not available yet.'

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();idx=patcher.indexed_rows();row=dict(idx['elf:ui:0021e5ac'],target_full=TEXT)
 prior=patcher.BASELINE
 try:
  patcher.BASELINE=BASE/'EBOOT.elf';data,r=patcher.prepare(old,[row],idx)
 finally:patcher.BASELINE=prior
 assert len(r['entries'])==1 and not r['skipped'],r
 address=int(r['entries'][0]['new_address'],16)
 hookword=struct.unpack_from('<I',data,notice.HOOK+192)[0];assert hookword>>26==3
 fallback=(hookword&0x3ffffff)<<2
 original_text,original_notice=notice.TEXT,notice.NOTICE
 try:
  notice.TEXT=TEXT;notice.NOTICE=address;values,width=notice.positions()
  def emit(a):
   notice.emit(a)
   # Preserve the existing tutorial-notice handler for all unmatched text.
   del a.words[-2:];a.jump(fallback,link=False)
  data,nr=append(data,emit,{notice.HOOK:('notice_position',hookword)},struct.pack('<%df'%len(values),*values))
 finally:notice.TEXT=original_text;notice.NOTICE=original_notice
 nr.update(text=TEXT,source_address=hex(address),fallback=hex(fallback),positions=values,ink_width_pixels=width*.875)
 r['full_translation']='This feature is not available yet.'
 r['notice_vwf']=nr;r['meaning_review']='battle_text_review approved full translation and compact popup: Not available yet.'
 r['patched_elf_sha256']=hashlib.sha256(data).hexdigest()
 return data,r

def prepare_tables(source):return {},{},source.resource('00.DAT',44),dict(units=[],tables=[])
if __name__=='__main__':print(json.dumps(prepare_elf()[1],indent=2))
