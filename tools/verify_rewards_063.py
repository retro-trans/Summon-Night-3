"""Execute the native notification selector, relocated wrapper and inherited VWF."""
import argparse,json,struct,unicodedata
from sn3_archive import ROOT,GameSource,parse_index,child
from rewards_063 import BASE,TEXT,prepare_elf,prepare_names
from dialogue_encoding import encode_dialogue
from verify_descriptions_021 import CPU
from verify_menu_vwf_020 import CPU as BindCPU
from verify_report_061 import current_report
from font_patch import CODE_VA
def text(c,p):
 n=c.strlen(p);return unicodedata.normalize('NFKC',c.mem[p:p+n*2].decode('cp932'))
def verify(elf,static):
 expected,r=prepare_elf();assert elf==expected;spec=json.loads(TEXT.read_text(encoding='utf8'));old=(BASE/'EBOOT.elf').read_bytes();selections=[]
 wanted={0x2199bc:'materialized!',0x2199cc:'joined battle!',0x2199e0:'joined the party!',0x2199f4:'joined support!',0x219a0c:'left battle!',0x219a20:'rejoined battle!'}
 def select(data,mode,puppet,uid,flag):
  c=CPU(data,static);c.r[29]=0x700000;c.r[18]=0x580000;c.write(0x580008,mode);c.r[19]=puppet;c.r[20]=uid;pc=0x6f684
  for _ in range(100):
   if pc==0x6f740:return c.r[5],text(c,c.r[5])
   if pc==0x52814:c.r[2]=flag;pc=c.r[31]
   else:pc=c.step(pc)
  raise AssertionError('Native notification selector budget')
 for mode in range(4,8):
  for puppet in (0,1):
   for uid in (101,13):
    for flag in (0,1):
     before,_=select(old,mode,puppet,uid,flag);after,en=select(elf,mode,puppet,uid,flag);assert en==wanted[before]
     selections.append(dict(mode=mode,puppet=puppet,unit=uid,flag=flag,english=en))
 wrapper=int(r['popup_wrapper_address'],16);current=current_report(elf);cases=0
 for base in (0x08804000,0x0890c000):
  for value in ['Rewards obtained!','joined the party!','Puppet "','"','Kyle','Custom Name','アティ','', 'W'*32,'W'*33]:
   c=BindCPU(elf,current,base);src=0x09400000;obj=src+0x1000;stack=0x09f00000;c.store(src,(encode_dialogue(value,'')[0] if value else b'')+b'\0\0');c.store(stack-128,b'G'*328)
   c.set('sp',stack);c.set('a0',obj);c.set('a1',src);c.set('a2',1);seen=[]
   def strlen(m):assert m.reg[4]==src;return {'v0':len(value)}
   def bind(m):seen.append(tuple(m.reg[4:7]));return {'v0':73}
   target=base+(0x34a0c8 if len(value)<=32 else 0x1cbdec);c.native_handlers={base+0x1e4ac8:strlen,target:bind};c.run(wrapper-CODE_VA)
   assert seen==[(obj,src,1)] and c.reg[2]==73;assert c.bytes(stack-128,80)==b'G'*80 and c.bytes(stack,200)==b'G'*200;cases+=1
 metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters'];width=lambda s:sum(metrics[ch]['proposed_advance_pixels'] for ch in s)
 assert width('joined the party!')*.75+3<116
 for row in spec['items']:assert width(row['english'])*.875+3<145
 # Run all inherited banner and pixel cases against actual new code, using the
 # proven 0.1.62 metadata for the unchanged wrapper addresses.
 import verify_report_062 as inherited
 original=inherited.prepare_elf
 def inherited_metadata():
  m=json.loads((BASE/'manifest.json').read_text())['report062_ui']['elf'];m['output_sha256']=r['output_sha256'];return elf,m
 inherited.prepare_elf=inherited_metadata
 try:regression=inherited.verify(elf,static)
 finally:inherited.prepare_elf=original
 table=child(static,parse_index(static,len(static)),19);itemchecks=[]
 for row in spec['items']:
  field=4+row['record']*24;ptr=struct.unpack_from('<I',table,field)[0];end=ptr
  while table[end:end+2]!=b'\0\0':end+=2
  actual=unicodedata.normalize('NFKC',table[ptr:end].decode('cp932'));assert actual==row['english'];itemchecks.append(actual)
 return dict(passed=True,native_selector_cases=len(selections),selection_examples=selections[::8],wrapper_cases=cases,load_bases=2,item_labels=itemchecks,party_text_pixels=width('joined the party!')*.75+3,unchanged_vwf_regression=regression,limits=['Native graphics calls use ABI stubs; exact reward and joining screens require matching runtime saves.'])
def main():
 p=argparse.ArgumentParser();p.add_argument('--build');p.add_argument('--report');a=p.parse_args()
 if a.build:
  folder=ROOT/a.build;m=json.loads((folder/'manifest.json').read_text());elf=(folder/'EBOOT.elf').read_bytes()
  with GameSource(folder/m['output_iso']) as source:result=verify(elf,source.resource('02.DAT',3))
 else:
  elf,_=prepare_elf()
  with GameSource(BASE/'Summon_Night_3_EN_0.1.62.iso') as source:replacements,_=prepare_names(source);result=verify(elf,replacements[3])
 print(json.dumps(result,indent=2),flush=True)
 if a.report:(ROOT/a.report).write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()
