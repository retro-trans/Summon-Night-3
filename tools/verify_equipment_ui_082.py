"""Execute both caption consumers and test adjacent-row isolation at two bases."""
import json,struct
from equipment_ui_082 import BASE,TARGET,SITES,captions,encoded,prepare_elf
from sn3_archive import ROOT
from verify_guards_050 import GuardCPU
from dialogue_encoding import encode_dialogue
from stat_spacing_026 import _file_offset_for_va as off
from stages_pupil_names import parse_elf

def verify():
 elf,r=prepare_elf();old=(BASE/'EBOOT.elf').read_bytes();rows=captions();cases=0
 for base in (0x08804000,0x0890c000):
  c=GuardCPU(elf,r,base);dst=0x09400000;stack=0x09f00000;stop=0x08801234
  for site,name in SITES.items():
   for mode,weapon in [(m,w) for m in range(10) for w in range(15)]+[(-1,2),(10,2),(1,-1),(1,15)]:
    c.store(dst,b'G'*256);c.store(stack-64,b'S'*128)
    c.r=[0x12500000+i for i in range(32)];c.r[0]=0;c.r[4:7]=[dst+20,mode&0xffffffff,weapon&0xffffffff];c.r[29]=stack;c.r[31]=stop;saved=c.r.copy()
    c.until(base+int(r['code_address'],16)+r['labels'][name],stop)
    text=rows[mode*15+weapon] if 0<=mode<10 and 0<=weapon<15 else ''
    expected=encoded(text);p=c.r[2]
    assert bytes(c.read(p+i,1) for i in range(len(expected)))==expected
    changed=16 if name=='equipment_list' else 17
    assert c.r[changed]==p and all(c.r[i]==saved[i] for i in range(16,32) if i!=changed)
    assert bytes(c.read(dst+i,1) for i in range(256))==b'G'*256,'Native row buffer overwritten'
    assert bytes(c.read(stack-64+i,1) for i in range(48))==b'S'*48
    assert bytes(c.read(stack+i,1) for i in range(64))==b'S'*64
    cases+=1
   assert struct.unpack_from('<I',elf,off(elf,site))[0]==3<<26|(int(r['code_address'],16)+r['labels'][name])>>2
  # Three adjacent captions remain independent after another character rebuild.
  pointers=[]
  for mode,weapon in [(1,2),(1,3),(2,5),(3,7),(1,2)]:
   c.r=[0]*32;c.r[4:7]=[dst,mode,weapon];c.r[29]=stack;c.r[31]=stop
   c.until(base+int(r['code_address'],16)+r['labels']['equipment_status'],stop);pointers.append(c.r[2])
  assert pointers[0]==pointers[-1] and len(set(pointers[:3]))==3
 os=parse_elf(old)['phdrs'][3];ns=parse_elf(elf)['phdrs'][3]
 assert old[os[1]:os[1]+os[4]]==elf[ns[1]:ns[1]+os[4]]
 return dict(passed=True,version='0.1.82',relocated_consumer_cases=cases,load_bases=2,caption_count=150,max_caption_cells=max(map(len,rows)),adjacent_row_guards=True,character_rebuild_isolation=True,invalid_id_guards=True,inherited_code_data_preserved=True,output_elf_sha256=r['output_sha256'])

if __name__=='__main__':
 result=verify();d=ROOT/'work/ui/ui_0.1.82';d.mkdir(parents=True,exist_ok=True);(d/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
