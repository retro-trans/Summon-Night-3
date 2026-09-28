"""Reflow already-relocated Battle Info strings for the native 27-cell draw limit."""
import hashlib,json,struct
from sn3_archive import ROOT
from stages_pupil_names import parse_elf
from menu_hotfix_017 import lines_at
from dialogue_encoding import encode_dialogue
BASE=ROOT/'work/output/0.1.29'
def sha(data):return hashlib.sha256(data).hexdigest()
TARGETS={
 'elf:ui:00217bf8':['View Party Abilities and','select them for battle.'],
 'elf:ui:00217c3c':['Check the victory and','defeat conditions.'],
}
def prepare():
 old=(BASE/'EBOOT.elf').read_bytes();out=bytearray(old)
 m=json.loads((BASE/'manifest.json').read_text());ph=parse_elf(old)['phdrs']
 def offset(va):return next(p[1]+va-p[2] for p in ph if p[0]==1 and p[2]<=va<p[2]+p[4])
 # slti a0,s3,27: displayed columns, distinct from 29-cell row stride.
 word=struct.unpack_from('<I',old,offset(0x64344))[0]
 assert word==0x2a64001b,hex(word)
 assert struct.unpack_from('<I',old,offset(0x63da4))[0]==0x34060036
 records={e['id']:e for k in ['menu_text','menu016_text'] for e in m[k]['entries']}
 def check(lines):
  counts=[len(x)//2 for x in lines]
  assert len(lines)<=2 and all(n<=27 for n in counts) and sum(counts)<=54,counts
  return counts
 changes=[]
 for identity,lines in TARGETS.items():
  e=records[identity];pos=offset(int(e['new_address'],16));before,end=lines_at(old,pos)
  assert max(len(x)//2 for x in before)==28
  encoded=[encode_dialogue(s,'')[0] for s in lines];counts=check(encoded)
  payload=b''.join(x+b'\0\0' for x in encoded)+b'\0\0'
  span=max(end-pos+2,len(payload));assert span<=e['bundle_bytes']
  assert not any(old[end:pos+span])
  out[pos:pos+span]=payload+bytes(span-len(payload))
  actual,last=lines_at(out,pos);assert actual==encoded and out[last:last+2]==b'\0\0'
  changes.append(dict(id=identity,address=e['new_address'],file_offset=pos,span=span,lines=lines,glyphs_per_line=counts,previous_glyphs_per_line=[len(x)//2 for x in before]))
 checked=[]
 for identity in [*TARGETS,'elf:ui:00217fe4','elf:ui:00218008']:
  e=records[identity];actual,end=lines_at(out,offset(int(e['new_address'],16)))
  checked.append(dict(id=identity,glyphs_per_line=check(actual)))
 assert ' '.join(TARGETS['elf:ui:00217c3c'])==records['elf:ui:00217c3c']['target_text']
 diffs=[i for i,(x,y) in enumerate(zip(old,out)) if x!=y]
 assert len(old)==len(out) and all(any(c['file_offset']<=i<c['file_offset']+c['span'] for c in changes) for i in diffs)
 return bytes(out),dict(changes=changes,checked_help_groups=checked,visible_cells_per_line=27,row_stride_cells=29,glyph_capacity=54,changed_bytes=len(diffs),meaning_review='battle_text_review approved Party wording; Win/Lose wording unchanged',allocation='Reflow existing relocated bundles in new ELF only; published base untouched.')
