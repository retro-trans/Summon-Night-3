"""Execute banner dispatch, free-strip merging and actual centered pixel packing."""
import json,struct
from banner_vwf_086 import ROOT,BASE,prepare_elf
from verify_guards_050 import GuardCPU
from verify_menu_vwf_020 import CPU
from dialogue_encoding import encode_dialogue
from font_patch import CODE_VA
from font_metrics import collect

class BannerCPU(GuardCPU):
 def until(self,pc,stop):
  for _ in range(100000):
   if pc==stop:return
   pc=self.step(pc)
  raise AssertionError('Banner instruction budget')

def text(t):return (encode_dialogue(t,'')[0] if t else b'')+bytes(2)

def pixels(elf,r,base,sample):
 metrics,font=collect();chars=metrics['characters'];glyphs=[];expected=[];advance=0
 for ch in sample:
  m=next((v for v in chars.values() if bytes.fromhex(v['cp932_hex'])==encode_dialogue(ch,'')[0]),None);g=font[m['font_byte_offset']:m['font_byte_offset']+128] if m else bytes(range(128));bounds=m['ink_bounds_inclusive'] if m else [0,0,15,15];left=bounds[0] if bounds else 0;width=bounds[2]-left+1 if bounds else 0
  expected.append((advance,left,width,g));glyphs.append(g);advance+=m['proposed_advance_pixels'] if m else 16
 count=len(sample);shift=(count*16-expected[-1][0]-expected[-1][2])//2;expected=[(x+shift,left,width,g) for x,left,width,g in expected]
 c=CPU(elf,r,base);stack=0x09f00000;obj=0x09000000;entry=obj+0x1000;src=obj+0x2000;manager=0x09100000;wrapper=manager+0xcac;bitmap=0x09200000;cache=0x09300000
 c.store(stack-4600,b'G'*4800);c.store(obj,bytes(0xe0));c.store(src,text(sample));c.store(entry,struct.pack('<4H',0,16,16,1));c.store(base+0x22a340,struct.pack('<I',manager));c.store(wrapper,bytes(64));c.store(wrapper+4,struct.pack('<H',512));c.store(wrapper+8,struct.pack('<H',32));c.store(wrapper+0x24,struct.pack('<II',cache,bitmap));c.store(cache,b'\xaa'*2048);c.store(bitmap,b'\xb6'*(256*64))
 def bind(m):
  assert m.reg[4:8]==[obj,src,count,1];m.store(obj+0xc0,struct.pack('<I',entry));return {'v0':123}
 def populate(m):
  assert m.reg[4:8]==[wrapper,entry,src,count]
  for j,g in enumerate(glyphs):
   for y in range(16):m.store(bitmap+(16+y)*256+j*8,g[y*8:y*8+8])
  m.store(cache+64,text(sample)[:-2]);return {}
 c.native_handlers={base+0x1cbe48:bind,base+0x1d8e34:populate};c.set('sp',stack)
 for reg,value in [('a0',obj),('a1',src),('a2',count),('a3',1)]:c.set(reg,value)
 manifest=json.loads((BASE/'manifest.json').read_text('utf8'));old=manifest['menu020_text']['list_vwf'];c.run(int(old['code_address'],16)-CODE_VA+old['labels']['center_bind'])
 wanted=bytearray(b'\xb6'*(256*64))
 for y in range(16):wanted[(16+y)*256:(16+y)*256+count*8]=bytes(count*8)
 for x,left,width,g in expected:
  for y in range(16):
   for p in range(width):wanted[(16+y)*256+(x+p)//2]|=(g[y*8+(left+p)//2]>>(4*((left+p)%2))&15)<<(4*((x+p)%2))
 assert c.bytes(bitmap,len(wanted))==wanted and c.bytes(stack-4600,160)==b'G'*160 and c.bytes(stack,200)==b'G'*200
 return dict(text=sample,cells=count,advance_pixels=advance,full_pixels_and_transparent_tail=True)

def verify():
 elf,r=prepare_elf();old=(BASE/'EBOOT.elf').read_bytes();stop=0x08801234;matches=draws=merges=0;pixel_checks=[];owner=0x09400000;rows=0x09500000;src=0x09600000
 samples=r['banner_names']+['Deadly S','Deadly Strike extra','Custom','', 'W'*33]
 for base in (0x08804000,0x0890c000):
  m=BannerCPU(elf,r,base);code=base+int(r['code_address'],16)
  for t in samples:
   m.store(src,text(t));m.r=[0]*32;m.r[4]=src;m.r[31]=stop;m.until(base+r['prior_match'],stop)
   assert m.r[2]==(len(t) if t in r['banner_names'] else 0);matches+=1
   for valid in (True,False):
    m.store(owner,bytes(128));m.store(rows,bytes(16));m.write(rows,src);m.write(owner,3);m.write(owner+0x30,rows);m.write(owner+0x34,0x09700000);m.write(owner+0x64,8,1);m.write(owner+0x3c,1 if valid else 2);m.write(owner+0x50,8);m.write(owner+0x4c,0x09800000)
    before=m.bytes(owner,128);m.r=[0x12500000+i for i in range(32)];m.r[0]=0;m.r[4:8]=[owner,11,22,33];m.r[29]=0x09f00000;m.r[31]=stop;saved=m.r.copy();convert=valid and t in r['banner_names'];m.until(base+r['prior_draw'],base+0x1b100)
    assert m.read(owner+0x34)==(0 if convert else 0x09700000) and m.read(owner+0x64,1)==(255 if convert else 8)
    m.write(owner,m.read(owner)&~0x400);m.r[22]=m.read(m.r[29]+252);m.r[29]+=272;m.until(m.r[31],stop)
    assert m.bytes(owner,128)==before and m.r[16:24]==saved[16:24] and m.r[29:32]==saved[29:32];draws+=1
  # The old matcher rejected the exact reported name. This reproduces the
  # exclusion that left the native eight-font-object banner in character mode.
  old_report=dict(r);p=__import__('stages_pupil_names').parse_elf(old)['phdrs'][3];old_report.update(added_segment_file_offset=p[1],added_segment_bytes=p[4]);old_report['extra_relocation_records']=[x for x in r['extra_relocation_records'] if x not in r['new_relocations']]
  prior=BannerCPU(old,old_report,base);prior.store(src,text('Deadly Strike'));prior.r[4]=src;prior.r[31]=stop;prior.until(base+r['prior_match'],stop);assert prior.r[2]==0
  for count,descs,merged in [(13,[(0,128,8,0),(128,128,8,0)],True),(13,[(0,128,16,0),(256,128,8,0)],False),(13,[(0,128,8,1),(128,128,8,0)],False),(13,[(384,128,8,0),(0,144,8,0)],False),(8,[(0,128,8,0),(128,128,8,0)],False)]:
   font=0x09100000;pool=0x09200000;original=b''.join(struct.pack('<4H',*d) for d in descs);m.store(pool,original);m.store(src,text('A'*count));m.write(base+0x22a340,font);m.write(font+0xcac+0x1c,pool);m.write(font+0xcac+0x20,len(descs));m.write(owner+0xc0,0)
   m.r=[0]*32;m.r[4:7]=[owner,src,1];m.r[29]=0x09f00000;m.r[31]=stop;pc=code+r['labels']['center_bind'];calls=0
   for _ in range(10000):
    if pc==stop:break
    if pc==base+0x1e4ac8:m.r[2]=count;pc=m.r[31];continue
    if pc==base+0x348a7c:assert m.r[4:7]==[owner,src,1];calls+=1;pc=m.r[31];continue
    pc=m.step(pc)
   assert pc==stop and calls==1
   got=m.bytes(pool,len(original));assert got==(struct.pack('<8H',0,128,16,0,128,128,0,1) if merged else original);merges+=1
  for t in ('Deadly Strike','Deadly Gaze',max(r['attack_names'],key=len),'W'*16):pixel_checks.append(pixels(elf,r,base,t))
 return dict(passed=True,reported_name='Deadly Strike',prior_banner_match_failed=True,exact_name_cases=matches,widget_cases=draws,free_strip_cases=merges,centered_pixel_cases=pixel_checks,load_bases=2,attack_names=r['attack_name_count'],loaded_bytes_added=r['code_bytes'],loaded_page_growth=r['loaded_page_growth'],no_new_texture_pool_memory=True,original_ui_tables_unchanged=True,save_bytes_unchanged=True)

if __name__=='__main__':
 result=verify();dest=ROOT/'work/ui/ui_0.1.86';dest.mkdir(parents=True,exist_ok=True);(dest/'validation.json').write_text(json.dumps(result,indent=2)+'\n','utf8');print(json.dumps(result),flush=True)
