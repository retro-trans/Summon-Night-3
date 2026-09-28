"""Fix native help-renderer capacity overruns; preview before creating a release."""
import argparse,copy,json,struct,shutil,hashlib
from datetime import datetime,timezone
from sn3_archive import ROOT
from dialogue_encoding import encode_dialogue
from build_candidate import hash_file,extent_hash
from scan_source import inventory

BASE=ROOT/'work/output/0.1.16'
REVIEW=ROOT/'work/translation/en/menu_0.1.17/meaning_review.json'
CAPACITY=54

def lines_at(data,pos):
 lines=[]
 for _ in range(3):
  start=pos
  while data[pos:pos+2]!=b'\0\0':
   pos+=2
   assert pos-start<1024
  if start==pos:break
  lines.append(data[start:pos]);pos+=2
 return lines,pos

def glyph_check(lines):
 counts=[len(line)//2 for line in lines]
 assert len(counts)<=3 and all(n<=29 for n in counts),counts
 assert sum(counts)<=CAPACITY,(counts,sum(counts),CAPACITY)
 assert sum(len(line)+2 for line in lines)+2<=174
 return counts

def prepare():
 m=json.loads((BASE/'manifest.json').read_text());old=(BASE/'EBOOT.elf').read_bytes();out=bytearray(old)
 # Native bind call passes 0x36 glyph objects, each renderer object is 0xe0 bytes.
 assert struct.unpack_from('<I',old,0x63da4+0xc0)[0]==0x34060036
 assert struct.unpack_from('<I',old,0x64c00+0xc0)[0]==0x00063a00
 review=json.loads(REVIEW.read_text());targets={g['source_ids'][0]:g['lines'] for g in review['groups']}
 targets.update({'elf:ui:00216f74':['View status; change gear.'],
                 'elf:ui:00217d14':['View status;','change equipment.'],
                 'elf:ui:0021cac8':['Set battle cursor','directions.']})
 records={e['id']:e for k in ['menu_text','menu016_text'] for e in m[k]['entries']};changes=[]
 for identity,lines in targets.items():
  e=records[identity];pos=e['new_file_offset'];before,end=lines_at(old,pos)
  encoded=[encode_dialogue(line,'')[0] for line in lines];counts=glyph_check(encoded)
  if identity=='elf:ui:00216f74':
   assert lines==[review['groups'][0]['lines'][1]] # Same reviewed source wording, single-line consumer.
  elif identity not in {g['source_ids'][0] for g in review['groups']}:
   assert ' '.join(lines)==e['target_text']
  payload=b''.join(line+b'\0\0' for line in encoded)+b'\0\0'
  span=max(end-pos+2,len(payload))
  assert span<=e['bundle_bytes'],(identity,span,e['bundle_bytes'])
  assert not any(old[end:pos+span]),'Refuse to consume following nonempty text'
  out[pos:pos+span]=payload+bytes(span-len(payload))
  actual,_=lines_at(out,pos);assert actual==encoded
  changes.append(dict(id=identity,new_file_offset=pos,new_address=e['new_address'],span=span,
    lines=lines,glyphs_per_line=counts,total_glyphs=sum(counts),previous_glyphs=sum(len(x)//2 for x in before),
    before_sha256=hashlib.sha256(old[pos:pos+span]).hexdigest(),after_sha256=hashlib.sha256(out[pos:pos+span]).hexdigest()))
 checked=[]
 # These roots have the proven three-line help consumer. Other controls use different readers.
 roots=[e for e in m['menu_text']['entries'] if 0x217bb8<=e['source_offset']<=0x217e1c]
 roots += [e for e in m['menu016_text']['entries'] if e['source_offset'] in (0x217d14,0x217e7c,0x217fe4,0x218008,0x218050,0x21ca58,0x21ca7c,0x21caa0,0x21cac8,0x21caf0)]
 for e in roots:
  lines,_=lines_at(out,e['new_file_offset']);counts=glyph_check(lines)
  checked.append(dict(id=e['id'],glyphs_per_line=counts,total_glyphs=sum(counts)))
 diffs=[n for n,(x,y) in enumerate(zip(old,out)) if x!=y]
 assert len(old)==len(out) and all(any(c['new_file_offset']<=n<c['new_file_offset']+c['span'] for c in changes) for n in diffs)
 # Regression: both old descriptions must fail the real object-capacity check.
 for c in changes[:2]:
  try:glyph_check(lines_at(old,c['new_file_offset'])[0])
  except AssertionError:pass
  else:raise AssertionError('Old overrun no longer detected')
 return bytes(out),dict(changes=changes,checked_help_groups=checked,glyph_capacity=CAPACITY,line_cells=29,staging_bytes=174,
  constructor_address='0x63d94',glyph_loop_address='0x64bf0..0x64cc4',old_overruns_detected=2,changed_bytes=len(diffs))

def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 elf,report=prepare();dest=ROOT/'work/scratch/menu_candidate_0.1.17_final';assert not dest.exists()
 print(json.dumps(dict(mode='write' if a.write else 'dry-run',destination=str(dest),**report),indent=2),flush=True)
 if not a.write:return
 previous=json.loads((BASE/'manifest.json').read_text());prior=BASE/previous['output_iso']
 assert hash_file(prior)==previous['output_sha256']
 for n,h in previous['inputs_sha256'].items():assert hash_file(ROOT/n)==h,n
 dest.mkdir();iso=dest/'Summon_Night_3_EN_0.1.17.iso';shutil.copyfile(prior,iso)
 with iso.open('r+b') as f:
  _,files=inventory(f,iso.stat().st_size);entry=next(e for e in files if e['path']=='/PSP_GAME/SYSDIR/EBOOT.BIN')
  assert entry['size_bytes']==len(elf)
  f.seek(entry['sector']*2048);f.write(elf)
 verified=[]
 with iso.open('rb') as out,prior.open('rb') as original:
  for e in files:
   h=extent_hash(out,e['sector'],e['size_bytes']);changed=e['path']==entry['path']
   assert h==(hashlib.sha256(elf).hexdigest() if changed else extent_hash(original,e['sector'],e['size_bytes']))
   verified.append(dict(path=e['path'],changed=changed,sha256=h))
 m=copy.deepcopy(previous);m.update(version='0.1.17',built_at_utc=datetime.now(timezone.utc).isoformat(),output_iso=iso.name,
   output_sha256=hash_file(iso),output_size_bytes=iso.stat().st_size,previous_build_sha256=previous['output_sha256'],menu017_hotfix=report,
   static_validation=dict(comparison_build='0.1.16',per_file=verified,all_23_banks_byte_identical=True,runtime_verified=False))
 for path in [ROOT/'tools/menu_hotfix_017.py',REVIEW]:
  m['inputs_sha256'][path.relative_to(ROOT).as_posix()]=hash_file(path)
 for n,h in m['inputs_sha256'].items():assert hash_file(ROOT/n)==h,n
 (dest/'EBOOT.elf').write_bytes(elf);(dest/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 (dest/'hotfix.report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(dict(iso=str(iso),sha256=m['output_sha256'])),flush=True)
if __name__=='__main__':main()
