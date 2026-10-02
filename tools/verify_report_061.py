"""Execute the scoped renderer helpers and original binding loop on guarded memory."""
import argparse,json,struct
from sn3_archive import ROOT,GameSource,parse_index,child
from stages_pupil_names import parse_elf
from report_ui_061 import prepare_elf,prepare_names,BASE,TEXT
from dialogue_encoding import encode_dialogue
from font_patch import CODE_VA
from verify_guards_060 import GuardCPU,AliasCPU,stage
from verify_descriptions_021 import CPU as NativeCPU
from verify_menu_vwf_020 import CPU as BinderCPU

def current_report(elf):
 p=parse_elf(elf)['phdrs'];seg,rel=p[3],p[2];records=list(struct.iter_unpack('<II',elf[rel[1]:rel[1]+rel[4]]))
 return dict(added_segment_file_offset=seg[1],added_segment_bytes=seg[4],extra_relocation_records=[r for r in records if r[1]>>8&255==3])
def verify(elf,static):
 expected,r=prepare_elf();assert elf==expected
 report=current_report(elf);entry=int(r['code_address'],16);spec=json.loads(TEXT.read_text(encoding='utf8'))
 cases=0;binding=0;names=spec['banner_names'];samples=names+['Zip Toas','Zip Toast extra','Custom','', 'ジップトースト','W'*33]
 for base in (0x08804000,0x0890c000):
  for text in samples:
   for shape in ('normal','multirow','no_index','offset','no_pool'):
    m=GuardCPU(elf,report,base);owner=0x09400000;rows=owner+0x1000;src=owner+0x2000;stack=0x09f00000
    m.store(owner,bytes(128));m.store(rows,bytes(16));m.store(src,(encode_dialogue(text,'')[0] if text else b'')+b'\0\0')
    m.write(owner,3);m.write(owner+0x34,0 if shape=='no_index' else owner+0x3000)
    m.write(owner+0x64,8,1);m.write(owner+0x3c,2 if shape=='multirow' else 1)
    m.write(owner+0x20,1 if shape=='offset' else 0);m.write(owner+0x50,0 if shape=='no_pool' else 8)
    m.write(owner+0x4c,owner+0x4000);m.write(owner+0x30,rows);m.write(rows,src)
    before=m.bytes(owner,128);m.store(stack-500,b'G'*700)
    m.r=[0x12500000+i for i in range(32)];m.r[0]=0;m.r[4:8]=[owner,11,22,33];m.r[29]=stack;m.r[31]=0x08801234;saved=m.r.copy()
    m.until(base+entry+r['labels']['draw'],base+0x1b100)
    convert=shape=='normal' and text in names
    assert m.read(owner+0x34)==(0 if convert else int.from_bytes(before[0x34:0x38],'little'))
    assert m.read(owner+0x64,1)==(255 if convert else 8)
    assert m.read(owner)==(0x403 if convert else 3)
    assert m.r[4:8]==saved[4:8] and m.r[29]==stack-80-272
    # Graphics body boundary: emulate native restoration and cache-dirty clear.
    m.write(owner,m.read(owner)&~0x400);m.r[22]=m.read(m.r[29]+252);m.r[29]+=272
    pc=m.r[31];m.until(pc,0x08801234)
    assert m.bytes(owner,128)==before
    assert m.r[16:24]==saved[16:24] and m.r[29]==stack and m.r[31]==saved[31]
    assert m.bytes(stack-500,140)==b'G'*140 and m.bytes(stack,200)==b'G'*200
    cases+=1
  # The actual new binder selects centered VWF only for exact known names.
  for text in samples:
   c=BinderCPU(elf,report,base);src=0x09400000;obj=src+0x1000;stack=0x09f00000
   c.store(src,(encode_dialogue(text,'')[0] if text else b'')+b'\0\0');c.store(stack-128,b'G'*328)
   c.set('sp',stack);c.set('a0',obj);c.set('a1',src);c.set('a2',1);calls=[]
   def called(m):calls.append(tuple(m.reg[4:7]));return {'v0':77}
   target=base+(0x348a7c if text in names else 0x34a0c8)
   c.native_handlers={target:called};c.run(entry-CODE_VA+r['labels']['bind'])
   assert calls==[(obj,src,1)] and c.reg[2]==77
   assert c.bytes(stack-128,80)==b'G'*80 and c.bytes(stack,200)==b'G'*200;binding+=1
 # Execute the unchanged native whole-row binding loop, including its delay slots.
 c=NativeCPU(elf,static);owner=0x500000;rows=0x510000;src=0x520000;pool=0x530000;stack=0x700000
 c.write(owner+0x64,255,1);c.write(owner+0x30,rows);c.write(owner,0x403);c.write(rows,src)
 c.mem[src:src+20]=encode_dialogue('Zip Toast','')[0]+b'\0\0';c.write(stack+184,1);c.write(stack+196,rows)
 c.r[4]=rows;c.r[17]=pool;c.r[22]=owner;c.r[29]=stack;pc=0x1b354;calls=[]
 for _ in range(10000):
  if pc==0x1b3d8:break
  if pc==0x348a7c:
   assert c.r[4:7]==[pool,src,1];calls.append('full centered strip');pc=c.r[31]
  else:pc=c.step(pc)
 else:raise AssertionError('Original widget bind loop budget')
 assert calls==['full centered strip'] and c.read(owner)==3 and c.r[17]==pool+224
 # Run the existing centered pixel packer against this actual candidate's code.
 import verify_list_vwf_020 as pixels
 manifest=json.loads((BASE/'manifest.json').read_text());pr=dict(manifest['menu020_text']['list_vwf']);pr.update(report);pr['patched_elf_sha256']=r['output_sha256']
 saved=pixels.prepare_elf;pixels.prepare_elf=lambda:(elf,{'list_vwf':pr})
 try:packed=pixels.verify(True)
 finally:pixels.prepare_elf=saved
 # Newly appended help blocks through the actual guarded native staging path.
 t=child(static,parse_index(static,len(static)),25);renderer=AliasCPU(elf,static);helps=[]
 for e in spec['attacks']:
  ptr=struct.unpack_from('<I',t,4+e['record']*48+36)[0];payload=t[ptr:ptr+sum((len(x)+1)*2 for x in e['help'])+2]
  staged=stage(renderer,payload);assert staged['glyphs']==sum(map(len,e['help'])) and staged['rows']==1
  helps.append(dict(record=e['record'],lines=e['help'],staging=staged))
 return dict(passed=True,wrapper_cases=cases,binder_cases=binding,load_bases=2,native_whole_row_binding=True,
  centered_pixels=packed,indirect_attack_help=helps,limits=['Graphics body uses an ABI boundary stub; native binding loop and emitted helpers execute actual candidate instructions.','Exact reported screens require PPSSPP visual verification.'])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--build');p.add_argument('--report');a=p.parse_args()
 if a.build:
  folder=ROOT/a.build;m=json.loads((folder/'manifest.json').read_text());elf=(folder/'EBOOT.elf').read_bytes()
  with GameSource(folder/m['output_iso']) as s:r=verify(elf,s.resource('02.DAT',3))
 else:
  elf,_=prepare_elf()
  with GameSource(BASE/'Summon_Night_3_EN_0.1.60.iso') as s:packs,_=prepare_names(s);r=verify(elf,packs[3])
 print(json.dumps(r,indent=2),flush=True)
 if a.report:(ROOT/a.report).write_text(json.dumps(r,indent=2)+'\n')
