"""Proportional name, attack and defense text in the compact battle unit card."""
import json,struct,hashlib
from sn3_archive import ROOT
from stages_pupil_names import parse_elf

BASE=ROOT/'work/output/0.1.22'
sha=lambda b:hashlib.sha256(b).hexdigest()

def prepare():
 m=json.loads((BASE/'manifest.json').read_text());old=(BASE/'EBOOT.elf').read_bytes();out=bytearray(old)
 wrapper=0x347b5c;r=m['menu020_text']['strip_vwf'];assert int(r['code_address'],16)+r['labels']['type']==wrapper
 ph=parse_elf(old)['phdrs'];rel=ph[2];records=list(struct.iter_unpack('<II',old[rel[1]:rel[1]+rel[4]]));patches=[]
 for field,site in [('name',0xe10a8),('attack',0xe1268),('defense',0xe1448)]:
  before=struct.unpack_from('<I',old,site+192)[0];assert before==3<<26|0x1cbe48>>2
  assert struct.unpack_from('<I',old,site+188)[0]==0x34060008 # old a2=8 fixed cells
  assert struct.unpack_from('<I',old,site+196)[0]==0x34070001 # old a3=1 style
  assert records.count((site,4))==1
  # The reused whole-string wrapper takes (object,text,style), computes actual
  # source length, then dispatches to the tested <=16-cell proportional packer.
  struct.pack_into('<I',out,site+188,0x34060001)
  struct.pack_into('<I',out,site+192,3<<26|wrapper>>2)
  patches.append(dict(field=field,call=hex(site),argument=hex(site-4),wrapper=hex(wrapper)))
 changes=[i for i,(a,b) in enumerate(zip(old,out)) if a!=b]
 assert len(old)==len(out) and all(any(int(p['call'],16)+188<=i<int(p['call'],16)+196 for p in patches) for i in changes)
 metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters']
 widths=[dict(text=r['text'],width_pixels=sum(metrics[c]['proposed_advance_pixels'] for c in r['text'])*.875) for r in m['status018_tables']['units']]
 assert all(len(r['text'])<=16 and r['width_pixels']<=115 for r in widths)
 return bytes(out),dict(profile='compact_unit_card_vwf',patches=patches,changed_bytes=len(changes),
  max_packed_cells=16,source_length_instead_of_fixed_eight=True,all_other_elf_bytes_identical=True,
  font_code_unchanged=True,name_labels_checked=len(widths),widest_catalog_label=max(widths,key=lambda r:r['width_pixels']),
  sample_widths={s:sum(metrics[c]['proposed_advance_pixels'] for c in s)*.875 for s in ['Aty','HSlash','VSlash','Guard','Cntr','Soldier']})

if __name__=='__main__':print(json.dumps(prepare()[1],indent=2))
