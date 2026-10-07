"""Verify actual two-row formatter and SELECT coordinates at both load bases."""
import argparse,json,struct
from status_fix_067 import ROOT,BASE,prepare_elf
from probe_status_067 import run
from sn3_archive import GameSource
from stages_pupil_names import parse_elf
from verify_menu_vwf_020 import CPU
from font_patch import CODE_VA
from dialogue_encoding import encode_dialogue
def verify():
 elf,r=prepare_elf();old=(BASE/'EBOOT.elf').read_bytes()
 os=parse_elf(old)['phdrs'][3];ns=parse_elf(elf)['phdrs'][3]
 assert ns[6]==7
 allowed=set()
 for e in r['entries']:
  if e['address']=='0x338964':allowed.update(range(0x338964-os[2],0x338984-os[2]))
 assert all(i in allowed for i,(a,b) in enumerate(zip(old[os[1]:os[1]+os[4]],elf[ns[1]:ns[1]+os[4]])) if a!=b)
 for va in (0x209a4,0x209e0,0x20b24):assert elf[va+192:va+196]==old[va+192:va+196]
 formatter=[]
 with GameSource(BASE/'Summon_Night_3_EN_0.1.66.iso') as src:
  static=src.resource('02.DAT',3)
  for entry in (0x63774,0x638f8):
   for food in (0,1):
    for switch in (0,1):
     for skills in (0,1):
      flags=(food,switch,0,skills,0);lines=run(elf,static,entry,flags)
      assert len(lines)<=2 and max(map(len,lines))<=27
      assert ('Learn Skills' in lines[-1])==(not food and bool(skills))
      if food and skills:assert 'Give Food' in lines[-1]
      if switch:assert 'ЕЁSwitch' in lines[-1]
      formatter.append(dict(entry=hex(entry),flags=flags,lines=lines))
 metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters']
 advances={int.from_bytes(bytes.fromhex(v['cp932_hex']),'little'):v['proposed_advance_pixels']*.875 for v in metrics.values()}
 def width(raw,n):return sum(advances.get(int.from_bytes(raw[i:i+2],'little'),13) for i in range(0,n*2,2))
 cases=[]
 for base in (0x08804000,0x0890c000):
  for row,index,match in [(1,n,True) for n in (0,1,9,10,11)]+[(0,9,True),(1,9,False),(1,12,True),(2,9,True)]:
   c=CPU(elf,r,base);ctx=0x09000000;desc=0x09002000;cb=base+0x1000
   raw=bytearray(58);prefix=encode_dialogue('ЕЁSwitch ','ЕЁ')[0][:index*2].ljust(index*2,b'\0');raw[:len(prefix)]=prefix
   label=encode_dialogue('Learn Skills' if match else 'Learn SkillX','')[0];start=index*2+12
   if start+len(label)<=58:raw[start:start+len(label)]=label
   c.store(ctx,bytes(0x200));c.store(ctx+0x4c+58,raw);c.store(desc,bytes(0x110));c.store(desc+0x100,bytes([index,row]));c.store(0x09effe00,b'G'*1024)
   for i in range(16,31):c.reg[i]=0x55500000+i
   c.set('sp',0x09f00000);c.set('s2',ctx);c.set('s3',desc);c.set('a0',desc);c.set('a2',cb)
   for n in range(32):c.fp[n]=int.from_bytes(struct.pack('<f',n+.25),'little')
   c.fp[12]=int.from_bytes(struct.pack('<f',118+index*13),'little');saved=c.reg[16:31].copy();fs=c.fp.copy();seen=[]
   def record(tag,m):seen.append((tag,m.reg[4],struct.unpack('<f',struct.pack('<I',m.fp[12]))[0]));return {}
   c.native_handlers={cb:lambda m:record('callback',m),base+int(r['fallback'],16):lambda m:record('fallback',m)}
   c.run(int(r['code_address'],16)-CODE_VA+r['labels']['skills_icon'])
   corrected=row==1 and index<=11 and match;expected=118+(width(raw,index) if corrected else index*13)
   assert seen==[('callback' if corrected else 'fallback',desc,expected)],seen
   assert c.reg[16:24]+c.reg[26:31]==saved[:8]+saved[10:] and c.fp[13:]==fs[13:]
   assert c.bytes(0x09effe00,0x1c0)==b'G'*0x1c0 and c.bytes(0x09f00000,0x200)==b'G'*0x200
   cases.append(dict(base=hex(base),row=row,index=index,matched=corrected,x=expected))
 space=metrics[' ']['proposed_advance_pixels']*.875;assert 13+space*5>=30
 return dict(passed=True,formatter_cases=formatter,position_cases=cases,select_to_text_gap_pixels=13+space*5,buffer_guards=True,private_chapter_arena_retained=True,custom_player_names_preserved=True,exact_screen_runtime_verified=False)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--report');a=p.parse_args();r=verify();print(json.dumps(r,indent=2))
 if a.report:
  path=(ROOT/a.report).resolve();assert ROOT in path.parents and not path.exists();path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(r,indent=2)+'\n')
