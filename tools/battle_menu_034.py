"""Battle menu sprites and reviewed system-saving notice on immutable 0.1.33."""
import json,hashlib
import battle_elf_patch as patcher
from sn3_archive import ROOT
from popup_rows_034 import prepare as popup_prepare
from battle_menu_art_034 import prepare as art_prepare
BASE=ROOT/'work/output/0.1.33'
LINES=['Saving system data.','Do not remove the Memory Stick.']
def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();idx=patcher.indexed_rows()
 rows=[dict(idx[f'elf:ui:{p:08x}'],target_full=text) for p,text in zip([0x21d22c,0x21d250],LINES)]
 prior,roots=patcher.BASELINE,patcher.TRANSLATABLE_TAIL_ROOTS
 try:
  patcher.BASELINE=BASE/'EBOOT.elf';patcher.TRANSLATABLE_TAIL_ROOTS=set(roots)|{0x21d16c}
  data,r=patcher.prepare(old,rows,idx)
 finally:patcher.BASELINE=prior;patcher.TRANSLATABLE_TAIL_ROOTS=roots
 assert len(r['entries'])==1 and r['entries'][0]['unreferenced_tails'][0]['text']==LINES[1],r
 e=r['entries'][0];address=int(e['new_address'],16)
 data,vr=popup_prepare(data,[(address,LINES[0]),(address+e['encoded_bytes'],LINES[1])]);r['popup_vwf']=vr
 r['meaning_review']='battle_text_review approved the twelve menu labels and both saving lines.'
 r['patched_elf_sha256']=hashlib.sha256(data).hexdigest()
 return data,r
def prepare_tables(source):
 p01,_,ar=art_prepare(source)
 return {},p01,source.resource('00.DAT',44),dict(units=[],tables=[],graphics=ar)
if __name__=='__main__':
 _,r=prepare_elf();print(json.dumps(dict(entries=r['entries'],popup_rows=r['popup_vwf']['rows']),indent=2))
