"""Execute actual candidate banner, help-staging and native Set anchor instructions."""
import argparse,json,struct
from sn3_archive import ROOT,GameSource,parse_index,child
from report_ui_062 import prepare_elf,prepare_names,BASE,TEXT
from dialogue_encoding import encode_dialogue
from menu_hotfix_017 import lines_at
from verify_guards_060 import AliasCPU,stage
from verify_descriptions_021 import CPU
class AnchorCPU(CPU):
 def __init__(self,*args):super().__init__(*args);self.f=[0]*32
 def step(self,pc,delay=False):
  w=self.read(pc);op=w>>26;rs=w>>21&31;rt=w>>16&31;imm=w&65535;imm=imm-65536 if imm&32768 else imm
  if op==17 and rs==4:self.f[w>>11&31]=self.r[rt];return pc+4
  if op==57:self.write((self.r[rs]+imm)&0xffffffff,self.f[rt]);return pc+4
  return super().step(pc,delay)
def verify(elf,static):
 expected,r=prepare_elf();assert elf==expected;s=json.loads(TEXT.read_text(encoding='utf8'))
 import verify_report_061 as prior
 saved=prior.prepare_elf,prior.TEXT,prior.BASE;prior.prepare_elf=prepare_elf;prior.TEXT=TEXT;prior.BASE=BASE
 try:banner=prior.verify(elf,static)
 finally:prior.prepare_elf,prior.TEXT,prior.BASE=saved
 checks=[];renderer=AliasCPU(elf,static)
 for n,stride,slot,records in [(12,52,12,[23]),(28,48,9,[0,1,2,3])]:
  b=child(static,parse_index(static,len(static)),n)
  for rec in records:
   ptr=struct.unpack_from('<I',b,4+rec*stride+slot*4)[0];rows,end=lines_at(b,ptr);blob=b[ptr:end+2];got=stage(renderer,blob)
   assert got['rows']==2 and got['glyphs']==sum(len(x)//2 for x in rows) and got['max_slot']<54
   checks.append(dict(table=n,record=rec,staging=got))
 anchors=[];old=(BASE/'EBOOT.elf').read_bytes()
 def native(candidate,mode):
  c=AnchorCPU(candidate,static);c.r[4]=mode;c.r[29]=0x700000;pc=0x154660
  for _ in range(100):
   if pc==0x15472c:return [struct.unpack('<f',struct.pack('<I',c.read(0x700000+x)))[0]+240 for x in (0,8)]
   pc=c.step(pc)
  raise AssertionError('Native anchor budget')
 for mode in range(6):
  got=native(elf,mode);previous=native(old,mode)
  assert got==([424.0,440.0] if mode==3 else previous);anchors.append(dict(mode=mode,icon_x=got[0],text_x=got[1]))
 metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters'];width=lambda t:3+sum(metrics[ch]['proposed_advance_pixels'] for ch in t)
 assert 440+width('Set')<=480
 for row in s['skills']+s['spells']:assert width(row['english'])*.875<=140,(row['english'],width(row['english']))
 return dict(passed=True,banner=banner,native_help=checks,native_hint_modes=anchors,set_ink_right=440+width('Set'),placeholder_behavior='No discovery checks or placeholder fields patched')
def main():
 p=argparse.ArgumentParser();p.add_argument('--build');p.add_argument('--report');a=p.parse_args()
 if a.build:
  folder=ROOT/a.build;m=json.loads((folder/'manifest.json').read_text());elf=(folder/'EBOOT.elf').read_bytes()
  with GameSource(folder/m['output_iso']) as source:result=verify(elf,source.resource('02.DAT',3))
 else:
  elf,_=prepare_elf()
  with GameSource(BASE/'Summon_Night_3_EN_0.1.61.iso') as source:replacements,_=prepare_names(source);result=verify(elf,replacements[3])
 print(json.dumps(result,indent=2),flush=True)
 if a.report:(ROOT/a.report).write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()
