"""Scoped Level Up localization; preserve all previous loaded code/data."""
import json,struct,hashlib
from PIL import Image
import numpy as np
from sn3_archive import ROOT
from menu_code_020 import append
from dialogue_encoding import encode_dialogue
from stages_pupil_names import parse_elf,validate_loader_structure
from menu_art_015 import descend,replace_tree
from sn3_ui_textures import texture_records,decode_texture
from setup_ui_patch import encode_texture
BASE=ROOT/'work/output/0.1.59'
ART=ROOT/'work/ui/levelup_0.1.60'
TEXT=ROOT/'work/translation/en/levelup_0.1.60/strings.json'
sha=lambda b:hashlib.sha256(b).hexdigest()

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();entries=json.loads(TEXT.read_text())['entries'];blob=bytearray();offsets={}
 for e in entries:
  offsets[e['id']]=len(blob);blob.extend(encode_dialogue(e['english'],e['source'])[0]+b'\0\0')
  blob.extend(bytes(-len(blob)%4))
 patched,report=append(old,lambda a:a.ret(),{},bytes(blob));out=bytearray(patched)
 table=int(report['code_address'],16)+report['labels']['table']
 rel=parse_elf(old)['phdrs'][2];records=list(struct.iter_unpack('<II',old[rel[1]:rel[1]+rel[4]]))
 changes=[]
 for e in entries:
  hi,lo=[int(v,16) for v in e['sites']];before=int(e['old_address'],16);after=table+offsets[e['id']]
  for va,word,typ in [(hi,0x3c060000|((before+0x8000)>>16),5),(lo,0x24c60000|(before&65535),6)]:
   assert struct.unpack_from('<I',old,va+192)[0]==word,(e['id'],hex(va))
   assert (va,typ) in records,(hex(va),typ)
  struct.pack_into('<I',out,hi+192,0x3c060000|((after+0x8000)>>16));struct.pack_into('<I',out,lo+192,0x24c60000|(after&65535))
  changes.append(dict(id=e['id'],english=e['english'],sites=e['sites'],address=hex(after),cells=len(e['english'])))
 # Only audited LUI/ADDIU pairs may change outside the append helper's structure.
 allowed={i for e in entries for site in e['sites'] for i in range(int(site,16)+192,int(site,16)+196)}
 assert all(i in allowed for i,(a,b) in enumerate(zip(patched,out)) if a!=b)
 report.update(entries=changes,source_sha256=sha(old),output_sha256=sha(out),structure=validate_loader_structure(out))
 return bytes(out),report

def prior_audit_view(elf):
 expected,_=prepare_elf();assert elf==expected,'Unexpected Level Up executable changes'
 return (BASE/'EBOOT.elf').read_bytes()

def prepare_names(source,write_assets=False):
 generated=Image.open(ART/'levelup_generated.png').convert('RGBA').resize((896,480),Image.Resampling.LANCZOS)
 raw=source.resource('02.DAT',1346);replacements={};reports=[]
 for n,y in [(33,0),(34,288)]:
  path=(5,n);data=descend(raw,path);rows=texture_records(data);assert len(rows)==1
  old=decode_texture(data,rows[0]);assert old.size==(112,24)
  art=old.copy();box=(16,4,103,21)
  crop=generated.crop((box[0]*8,y+box[1]*8,box[2]*8,y+box[3]*8)).resize((87,17),Image.Resampling.LANCZOS)
  art.paste(crop,(16,4));art.putalpha(old.getchannel('A'))
  patched,native,changed=encode_texture(data,rows[0],art)
  mask=np.zeros((24,112),bool);mask[4:21,16:103]=True
  assert np.array_equal(np.asarray(native)[~mask],np.asarray(old)[~mask])
  replacements[path]=patched
  if write_assets:native.save(ART/f'levelup_{n}_native.png')
  reports.append(dict(path=list(path),source_sha256=sha(data),output_sha256=sha(patched),box=box,changed_pixels=changed,frame_preserved=True))
 return {1346:replace_tree(raw,replacements)},reports
