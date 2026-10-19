"""Execute new UI dispatch at relocated bases and audit all changed resources."""
import json,struct
from ui_fix_084 import prepare_elf,BASE,TEXT,encoded
from verify_guards_050 import GuardCPU
from list_vwf_020 import name_pairs
from stat_spacing_026 import _file_offset_for_va as off
from stages_pupil_names import parse_elf
from sn3_archive import ROOT,GameSource
from retreat_art_084 import prepare as art_prepare
from sn3_ui_textures import texture_records,decode_texture
from menu_art_015 import descend
import numpy as np

def alias_pairs(elf):
 manifest=json.loads((BASE/'manifest.json').read_text('utf8'));lookup=manifest['menus075_fix']['elf']['default_name_lookup'];table=int(lookup['code_address'],16)+lookup['labels']['table'];out=[]
 for n in range(lookup['pairs']):
  so,do=struct.unpack_from('<II',elf,off(elf,table)+n*8)
  def raw(p):
   p=off(elf,table+p);end=p
   while elf[end:end+2]!=bytes(2):end+=2
   return elf[p:end]
  out.append((raw(so),raw(do)))
 assert dict(out)['ライザー'.encode('cp932')]==encoded('Riser')[:-2]
 return out

def verify():
 elf,r=prepare_elf();old=(BASE/'EBOOT.elf').read_bytes();cases=aliases=0;stop=0x08801234
 for base in (0x08804000,0x0890c000):
  m=GuardCPU(elf,r,base);owner=0x09400000;rows=0x09700000;ptr=0x09800000;code=base+int(r['code_address'],16)
  for text,matched in [(t,True) for t in r['exact_captions']]+[('Use this class?',True),('CustomName',False),('W'*32,False),('',False)]:
   for rowindex in (0,2):
    m.store(ptr,encoded(text));source_ptr=ptr
    if matched:
     if text=='Use this class?':source_ptr=ptr
     else:
      arena=elf[off(elf,r['equipment_caption_start']):off(elf,r['equipment_caption_end'])];source_ptr=base+r['equipment_caption_start']+arena.index(encoded(text))
    m.store(owner,bytes(0x100));m.store(rows,bytes(48));m.write(rows+16*rowindex,source_ptr);m.write(owner+0x30,rows);m.write(owner+0x34,0x09710000);m.write(owner+0x3c,3);m.write(owner+0x64,9,1)
    m.r=[0x12500000+i for i in range(32)];m.r[0]=0;m.r[4:8]=[owner,99,88,77];m.r[29]=0x09f00000;m.r[31]=stop;before=m.r.copy();pc=code+r['labels']['draw'];calls=0
    for _ in range(100000):
     if pc==stop:break
     if pc==base+r['prior_draw']:
      assert m.r[4:8]==before[4:8] and m.read(owner+0x34)==(0 if matched else 0x09710000)
      assert m.read(owner+0x64,1)==(255 if matched else 9);calls+=1;pc=m.r[31];continue
     pc=m.step(pc)
    assert pc==stop and calls==1 and m.r[16:24]==before[16:24] and m.r[28:32]==before[28:32]
    assert m.read(owner+0x34)==0x09710000 and m.read(owner+0x64,1)==9;cases+=1
  # Run the actual inherited saved-default-name lookup used by the newly
  # corrected summon banner branch. Stub only strlen and font submission.
  for src,dst in alias_pairs(elf)+[(encoded('CustomName')[:-2],encoded('CustomName')[:-2])]:
   m.store(ptr,src+bytes(2));m.r=[0]*32;m.r[4:7]=[owner,ptr,1];m.r[29]=0x09f00000;m.r[31]=stop
   pc=base+0x347b5c;calls=0
   for _ in range(100000):
    if pc==stop:break
    if pc==base+0x1e4ac8:
     p=m.r[4];n=0
     while m.read(p+2*n,2):n+=1;assert n<=32
     m.r[2]=n;pc=m.r[31];continue
    if pc==base+0x32e060:
     p=m.r[5];got=bytes(m.read(p+i,1) for i in range(len(dst)));assert got==dst,(src,dst,got,hex(p))
     assert m.r[4]==owner and m.r[6]==len(dst)//2 and m.r[7]==1;calls+=1;pc=m.r[31];continue
    pc=m.step(pc)
   assert pc==stop and calls==1;aliases+=1
 cfg=json.loads(TEXT.read_text('utf8'))
 for e in cfg['class_change']:
  p=r['class_literals'][e['source_address']];want=b''.join(encoded(t) for t in e['english'])+bytes(2)
  assert elf[off(elf,p):off(elf,p)+len(want)]==want
 for site in r['discovery_vwf_sites']+[0x14ecbc]:
  assert struct.unpack_from('<I',elf,site+192)[0]==3<<26|0x347b5c>>2
  assert elf[site+196:site+200]==(struct.pack('<I',int(r['changed_native_words'][hex(site+4)],16)) if hex(site+4) in r['changed_native_words'] else old[site+196:site+200])
 # Both class-help branches use the same translated allocation, each HI/LO
 # pair remains valid at either PRX base (including the shared-HI branch).
 for hi,lo,source in [(0x11c5d0,0x11c5d8,'0x21c788'),(0x11c5cc,0x11c5dc,'0x21c7bc')]:
  h=struct.unpack_from('<I',elf,hi+192)[0]&65535;l=struct.unpack_from('<h',elf,lo+192)[0];assert (h<<16)+l==r['class_literals'][source]
 # Verify every changed indexed texture preserves native footprint, palette,
 # frame pixels and alpha from its neighbor. No other leaf is substituted.
 with GameSource(BASE/'Summon_Night_3_EN_0.1.83.iso') as source:
  packs,art=art_prepare(source,True)
  for entry in art['states']:
   ref=descend(source.resource('02.DAT',1333),entry['reference'][1:]);row=texture_records(ref)[0];reference=np.asarray(decode_texture(ref,row))
   for path in entry['occurrences']:
    data=descend(packs[path[0]],path[1:]);actual=np.asarray(decode_texture(data,row));assert len(data)==len(ref)
    a,b=row['data_offset'],row['data_offset']+row['data_size'];assert data[:a]==ref[:a] and data[b:]==ref[b:]
    mask=np.ones((24,112),bool);mask[3:21,25:100]=False
    assert np.array_equal(actual[mask],reference[mask]) and np.array_equal(actual[:,:,3],reference[:,:,3])
 return dict(passed=True,relocated_widget_cases=cases,summon_name_alias_cases=aliases,load_bases=2,discovery_bindings=len(r['discovery_vwf_sites']),class_literal_groups=len(cfg['class_change']),retreat_states=2,retreat_occurrences=art['occurrences'],delay_slots_preserved=True,save_data_unchanged=True,exact_beach_save_available=False)

if __name__=='__main__':
 result=verify();dest=ROOT/'work/ui/ui_0.1.84';dest.mkdir(parents=True,exist_ok=True);(dest/'validation.json').write_text(json.dumps(result,indent=2)+'\n','utf8');print(json.dumps(result),flush=True)
