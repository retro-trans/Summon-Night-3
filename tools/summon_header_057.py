"""Localize summon creation art and fix proportional top-right control hints."""
import argparse,hashlib,json,struct
from PIL import Image
import numpy as np
from sn3_archive import ROOT,GameSource
from menu_art_015 import descend,replace_tree
from sn3_ui_textures import texture_records,decode_texture
from setup_ui_patch import encode_texture
from dialogue_encoding import encode_dialogue
from stages_pupil_names import validate_loader_structure,parse_elf
BASE=ROOT/'work/output/0.1.56'
ART=ROOT/'work/ui/summon_0.1.57'
sha=lambda b:hashlib.sha256(b).hexdigest()

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();out=bytearray(old)
 manifest=json.loads((BASE/'manifest.json').read_text())
 entry=next(e for e in manifest['menu016_text']['entries'] if e['id']=='elf:ui:0021e24c')
 # Later builds moved the added segment. Historical file offsets point to an
 # unused old copy; resolve the stable module address through current headers.
 text_va=int(entry['new_address'],16);span=entry['encoded_bytes']
 segments=[p for p in parse_elf(old)['phdrs'] if p[0]==1 and p[2]<=text_va< p[2]+p[4]]
 assert len(segments)==1
 segment=segments[0];pos=segment[1]+text_va-segment[2]
 assert old[pos:pos+span]=='Ｃａｓｔ　Ｍａｇｉｃ'.encode('cp932')+b'\0\0'
 encoded,display=encode_dialogue('Cast','')
 out[pos:pos+span]=encoded+bytes(span-len(encoded))
 # Reuse the already shipped, length-checked Type binding wrapper.
 wrapper_word=struct.unpack_from('<I',old,0x1549f8+0xc0)[0]
 assert wrapper_word==3<<26|0x347b5c>>2
 hooks=[0x154aa8,0x154b44,0x154c1c,0x154c84]
 for va in hooks:
  assert struct.unpack_from('<I',old,va+0xc0)[0]==3<<26|0x1cbdec>>2
  struct.pack_into('<I',out,va+0xc0,wrapper_word)
 # These exact per-mode anchors are screen-center offsets, not shared constants.
 coordinates={0x154678:(190,130),0x1546bc:(190,130),0x1546c4:(206,146),
  0x1546d8:(163,135),0x1546e0:(179,151),
  0x1546b0:(111,74),0x1546f8:(191,148),0x154708:(127,90),0x154710:(207,164)}
 changes=[]
 for va,(before,after) in coordinates.items():
  def word(value):
   bits=struct.unpack('<I',struct.pack('<f',value))[0];assert bits&65535==0
   return 15<<26|4<<16|bits>>16
  assert struct.unpack_from('<I',old,va+0xc0)[0]==word(before),(hex(va),before)
  struct.pack_into('<I',out,va+0xc0,word(after))
  changes.append(dict(va=hex(va),before=before,after=after,screen_x=240+after))
 allowed=set(range(pos,pos+span))|{i for va in hooks+list(coordinates) for i in range(va+0xc0,va+0xc0+4)}
 assert len(out)==len(old) and all(i in allowed for i,(a,b) in enumerate(zip(old,out)) if a!=b)
 structure=validate_loader_structure(out)
 report=dict(text='Cast',display_text=display,text_file_offset=pos,text_module_address=hex(text_va),historical_unused_file_offset=entry['new_file_offset'],retained_text_span=span,
  vwf_wrapper='0x347b5c',bind_calls=list(map(hex,hooks)),coordinates=changes,
  source_sha256=sha(old),output_sha256=sha(out),structure=structure)
 return bytes(out),report

def prepare_names(source,write_assets=False):
 generated=Image.open(ART/'create_summons_generated.png').convert('RGBA').resize((480,272),Image.Resampling.LANCZOS)
 # Import only the localized text regions; retain the original frame and artwork.
 title_box=(39,7,128,30);title_src=(40,8,145,29);affinity_src=(119,41,171,56);affinity_dst=(112,41)
 packs={};reports=[]
 for n in [2953,2954,2955]:
  raw=source.resource('02.DAT',n);data=descend(raw,[0]);rows=texture_records(data);assert len(rows)==1
  old=decode_texture(data,rows[0]);assert old.size==(480,272)
  art=old.copy();boxes=[]
  if n==2953:
   title=generated.crop(title_src).resize((title_box[2]-title_box[0],title_box[3]-title_box[1]),Image.Resampling.LANCZOS)
   art.paste(title,(title_box[0],title_box[1]));boxes.append(title_box)
  patch=generated.crop(affinity_src);art.paste(patch,affinity_dst)
  boxes.append((affinity_dst[0],affinity_dst[1],affinity_dst[0]+patch.width,affinity_dst[1]+patch.height))
  art.putalpha(old.getchannel('A'))
  patched,native,changed=encode_texture(data,rows[0],art)
  mask=np.zeros((272,480),dtype=bool)
  for x0,y0,x1,y1 in boxes:mask[y0:y1,x0:x1]=True
  assert np.array_equal(np.asarray(native)[~mask],np.asarray(old)[~mask])
  r=rows[0];assert data[:r['data_offset']]==patched[:r['data_offset']]
  assert data[r['data_offset']+r['data_size']:]==patched[r['data_offset']+r['data_size']:]
  result=replace_tree(raw,{(0,):patched});packs[n]=result
  assert all(descend(result,[c])==descend(raw,[c]) for c in [1,2])
  reports.append(dict(resource=n,source_sha256=sha(raw),output_sha256=sha(result),
   title='Create Summons' if n==2953 else 'unchanged',label='Affinity:',boxes=boxes,
   changed_pixels=changed,original_frame_and_art_unchanged=True))
  if write_assets:native.save(ART/f'{n}_native.png')
 return packs,reports

def prior_audit_view(elf):
 # Three legacy audits require a byte-exact historical executable. Verify that
 # every candidate difference is the scoped hint patch before giving them the
 # unchanged original view. Other groups and the new hint audit use actual ELF.
 expected,_=prepare_elf();assert elf==expected,'Unexpected candidate executable'
 return (BASE/'EBOOT.elf').read_bytes()

def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 elf,er=prepare_elf()
 with GameSource(BASE/'Summon_Night_3_EN_0.1.56.iso') as s:_,ar=prepare_names(s,a.write)
 report=dict(mode='write previews' if a.write else 'dry-run',elf=er,art=ar)
 print(json.dumps(report,indent=2),flush=True)
 if a.write:(ART/'import-validation.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
