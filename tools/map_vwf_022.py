"""Use the existing bounded VWF binder for battle-map shortcut labels."""
import json,struct,hashlib
from sn3_archive import ROOT
from stages_pupil_names import parse_elf

BASE=ROOT/'work/output/0.1.21'
sha=lambda b:hashlib.sha256(b).hexdigest()

def prepare():
 m=json.loads((BASE/'manifest.json').read_text());old=(BASE/'EBOOT.elf').read_bytes()
 r=m['menu020_text']['strip_vwf'];entry=int(r['code_address'],16)+r['labels']['type']
 assert entry==0x347b5c
 site=0xb1d94;before=struct.unpack_from('<I',old,site+192)[0]
 assert before==(3<<26|0x1cbdec>>2)
 assert struct.unpack_from('<I',old,site+196)[0]==0x34060001 # style argument in native delay slot
 ph=parse_elf(old)['phdrs'];rel=ph[2];records=list(struct.iter_unpack('<II',old[rel[1]:rel[1]+rel[4]]))
 assert records.count((site,4))==1 # Existing R_MIPS_26 already covers this JAL.
 out=bytearray(old);after=3<<26|entry>>2;struct.pack_into('<I',out,site+192,after)
 changes=[i for i,(a,b) in enumerate(zip(old,out)) if a!=b]
 assert len(old)==len(out) and all(site+192<=i<site+196 for i in changes)
 # Reuse the exact released 16-cell VWF wrapper/packer/metrics, not a new copy.
 prior=(ROOT/'work/output/0.1.20/EBOOT.elf').read_bytes();pp=parse_elf(prior)['phdrs'][3];cp=ph[3]
 assert old[cp[1]:cp[1]+pp[4]]==prior[pp[1]:pp[1]+pp[4]]
 metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters']
 samples=[]
 for text in ['Prepare','Unit List','Battle Status','Start','Position','Status','Face']:
  width=sum(metrics[c]['proposed_advance_pixels'] for c in text)*.75
  assert len(text)<=16 and 50+width<=149
  samples.append(dict(text=text,cells=len(text),native_scale=.75,width_pixels=width,right_edge_pixels=50+width))
 return bytes(out),dict(profile='battle_map_shortcut_vwf',hook=hex(site),wrapper=hex(entry),
  original_instruction=hex(before),patched_instruction=hex(after),changed_bytes=len(changes),
  max_packed_cells=16,long_text_native_fallback=True,all_other_elf_bytes_identical=True,
  font_code_byte_identical_to_020=True,samples=samples)

if __name__=='__main__':print(json.dumps(prepare()[1],indent=2))
