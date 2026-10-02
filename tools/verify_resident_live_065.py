"""Read the live Extra Brave table and compare every relocated text pointer."""
import argparse,base64,struct,json
from release_runtime_065 import request
from sn3_archive import ROOT,GameSource,parse_index,child
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 assert request('game.status')['game']['id']=='NPJH50380'
 def read(ptr,n):return base64.b64decode(request('memory.read',address=ptr,size=n)['base64'])
 owner=read(0x08ad65f8,16);count,pool=struct.unpack_from('<II',owner,8);base=pool-4
 with GameSource(ROOT/'work/output/0.1.65/Summon_Night_3_EN_0.1.65.iso') as src:
  static=src.resource('02.DAT',3);table=child(static,parse_index(static,len(static)),46)
 expected=struct.unpack_from('<I',table)[0];assert count==expected==62
 live=read(base,len(table));assert live[:4]==table[:4]
 pointers=0
 for rec in range(count):
  for slot in range(7,17):
   offset=4+rec*68+slot*4;want=struct.unpack_from('<I',table,offset)[0];actual=struct.unpack_from('<I',live,offset)[0]
   fallback_slot=7 if slot<=12 else 8
   fallback=struct.unpack_from('<I',table,4+rec*68+fallback_slot*4)[0]
   resolved=want or fallback
   assert actual==base+resolved if resolved else actual in (0,base),(rec,slot,hex(actual),hex(want))
   pointers+=1
 r=dict(passed=True,extra_brave_records=count,text_pointers_checked=pointers,
        table_header_intact=True,all_text_pointers_match_disk_table=True,
        scope='Read-only inspection after Chapter 15 Continue and Brave Goals navigation')
 print(json.dumps(dict(mode='write' if a.write else 'preview',**r),indent=2))
 if a.write:(ROOT/'work/ui/release_0.1.65/resident-table-validation.json').write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
