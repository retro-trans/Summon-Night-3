"""Remaining pictured summon text and Kyle portrait label on immutable 0.1.25."""
import argparse,json,struct,hashlib
import numpy as np
from PIL import Image
import battle_elf_patch as patcher
from sn3_archive import ROOT,GameSource,parse_index,child
from sn3_repack import repack
from sn3_codec import decompress,compress
from dialogue_encoding import encode_dialogue
from sn3_ui_textures import texture_records,decode_texture
from setup_ui_patch import encode_texture
from stat_spacing_026 import prepare as prepare_spacing
from long_list_026 import prepare as prepare_long_list
from stages_pupil_names import parse_elf

BASE=ROOT/'work/output/0.1.25';ART=ROOT/'work/ui/ui_fixes_0.1.26'
FOLDER=ROOT/'work/translation/en/ui_fixes_0.1.26'
SPELL="Crush! Light Gen. Sword"
SPELL_FULL="Shatter! Light General's Sword!"
sha=lambda b:hashlib.sha256(b).hexdigest()

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();idx=patcher.indexed_rows()
 # The locked spell's two-line record begins at the question marks, eight
 # bytes before the restriction. The scanner omits this non-Japanese root.
 off=0x216428;raw=old[off:off+6];assert raw.decode('cp932')=='？？？'
 root=dict(id=f'elf:ui:{off:08x}',source_offset=off,module_address=hex(off-192),source_byte_length=6,source_sha256=sha(raw),source_control_tokens=[])
 idx[root['id']]=root
 rows=[dict(root,target_full='???'),dict(idx['elf:ui:00216430'],target_full='Favorites Only')]
 previous=patcher.BASELINE;prior_roots=patcher.TRANSLATABLE_TAIL_ROOTS
 try:
  patcher.TRANSLATABLE_TAIL_ROOTS=set(prior_roots)|{off-192}
  patcher.BASELINE=BASE/'EBOOT.elf';data,r=patcher.prepare(old,rows,idx)
 finally:patcher.BASELINE=previous;patcher.TRANSLATABLE_TAIL_ROOTS=prior_roots
 assert len(r['entries'])==1
 assert all(e['id']=='elf:ui:00216430' for e in r['skipped'])
 assert r['entries'][0]['unreferenced_tails'][0]['text']=='Favorites Only'
 r['locked_record_proof']='Root reference 0x5d658/0x5d65c points to question marks followed by restriction line; original line boundaries retained.'
 data,sr=prepare_spacing(data);r['stat_spacing']=sr
 data,lr=prepare_long_list(data);r['long_list']=lr;r['patched_elf_sha256']=sha(data)
 for e in r['entries']:
  va=int(e['new_address'],16);ph=next(h for h in parse_elf(data)['phdrs'] if h[0]==1 and h[2]<=va<h[2]+h[4])
  e['new_file_offset']=ph[1]+va-ph[2]
 return data,r

def prepare_text(source):
 ix=json.loads((ROOT/'work/translation/en/interface.index.json').read_text())
 table=next(t for t in ix['tables'] if t['resource_path']==[3,13])
 row=next(r for r in table['strings'] if r['id']=='02:00003/00013:ui:000034e0')
 static=source.resource('02.DAT',3);si=parse_index(static,len(static));before=child(static,si,13);out=bytearray(before)
 p,n=row['source_offset'],row['source_byte_length'];assert sha(before[p:p+n])==row['source_sha256']
 fields=[r['pointer_field_offset'] for r in row['references']];assert all(struct.unpack_from('<I',before,f)[0]==p for f in fields)
 raw,display=encode_dialogue(SPELL,'');assert len(raw)//2<=32
 out.extend(bytes(-len(out)%2));new=len(out);out.extend(raw+b'\0\0')
 for f in fields:struct.pack_into('<I',out,f,new)
 patched=repack(static,{13:bytes(out)});master=source.resource('00.DAT',44);mi=parse_index(master,len(master));assert child(master,mi,7)==static
 master=repack(master,{7:patched})
 metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters'];width=sum(metrics[c]['proposed_advance_pixels'] for c in SPELL)*.875
 assert width<=185,width
 return patched,master,dict(child=13,changes=[dict(id=row['id'],record=233,slot=8,text=SPELL,full_translation=SPELL_FULL,advance_pixels=width,source_sha256=row['source_sha256'],new_offset=new,pointer_fields=fields)])

def prepare_art(source):
 original_image=Image.open(ART/'kyle_generated.png').convert('RGBA');alpha=original_image.getchannel('A')
 assert alpha.getextrema()==(0,255)
 box=alpha.point(lambda v:255 if v>=12 else 0).getbbox();cut=original_image.crop(box)
 scale=min(20/cut.height,122/cut.width);size=(round(cut.width*scale),round(cut.height*scale))
 native=Image.new('RGBA',(144,32));native.paste(cut.resize(size,Image.Resampling.LANCZOS),((144-size[0])//2,6))
 catalog=json.loads((ROOT/'work/ui/nameplates_0.1.10/packs_870-1080_names/index.json').read_text())
 raw=source.resource('02.DAT',914);data,used=decompress(raw,0x1731);assert not any(raw[used:]);idx=parse_index(data,len(data))
 replacements={};images=[];records=[]
 for ci in (3,4):
  record=next(r for r in catalog['textures'] if r['id']==f'02:00914/{ci:05d}:0');assert len(record['occurrences'])==1
  old=child(data,idx,ci);assert sha(old)==record['occurrences'][0]['source_sha256'];row=texture_records(old)[0]
  wanted=native
  if ci==4:
   pixels=np.asarray(decode_texture(old,row));colors,counts=np.unique(pixels[pixels[:,:,3]>200,:3],axis=0,return_counts=True)
   color=tuple(int(x) for x in colors[counts.argmax()]);wanted=Image.new('RGBA',native.size,color+(0,));wanted.putalpha(native.getchannel('A'))
  packed,preview,changed=encode_texture(old,row,wanted);replacements[ci]=packed;images.append((f'kyle_native_{ci}.png',preview))
  records.append(dict(name='Kyle',pack=914,child=ci,source_sha256=sha(old),output_sha256=sha(packed),changed_pixels=changed))
 new=repack(data,replacements);ni=parse_index(new,len(new))
 for ci in range(idx['count']):assert child(new,ni,ci)==replacements.get(ci,child(data,idx,ci))
 packed=compress(new,0x1731);assert decompress(packed,0x1731)[0]==new
 return packed,images,dict(records=records,other_portrait_layers_unchanged=True)

def prepare_tables(source):
 static,master,tr=prepare_text(source);art,images,ar=prepare_art(source)
 battle,_,br=prepare_battle_art(source);ar['records'].extend(br['records'])
 return {3:static,914:art,1098:battle},{},master,dict(units=[],tables=[tr],graphics=ar)

def prepare_battle_art(source):
 original=Image.open(ART/'kyle_generated.png').convert('RGBA');box=original.getchannel('A').point(lambda v:255 if v>=12 else 0).getbbox();cut=original.crop(box)
 scale=min(16/cut.height,76/cut.width);size=(round(cut.width*scale),round(cut.height*scale))
 native=Image.new('RGBA',(88,24));native.paste(cut.resize(size,Image.Resampling.LANCZOS),((88-size[0])//2,3))
 raw=source.resource('02.DAT',1098);data,used=decompress(raw,0x9831);assert not any(raw[used:]);idx=parse_index(data,len(data))
 expected={1:'cc72a271a7dc0d79438a4cfdebec4530c5968b8a0d664331836771918ef14e5b',2:'20d6b0455e00a5126e68568206c9cbcfbe8c95760c12a142378969dc478e3341'}
 replacements={};images=[];records=[]
 for ci in (1,2):
  old=child(data,idx,ci);assert sha(old)==expected[ci];row=texture_records(old)[0];wanted=native
  if ci==2:
   pixels=np.asarray(decode_texture(old,row));colors,counts=np.unique(pixels[pixels[:,:,3]>200,:3],axis=0,return_counts=True)
   color=tuple(int(x) for x in colors[counts.argmax()]);wanted=Image.new('RGBA',native.size,color+(0,));wanted.putalpha(native.getchannel('A'))
  packed,preview,changed=encode_texture(old,row,wanted);replacements[ci]=packed;images.append((f'kyle_battle_native_{ci}.png',preview))
  records.append(dict(name='Kyle',pack=1098,child=ci,source_sha256=sha(old),output_sha256=sha(packed),changed_pixels=changed))
 new=repack(data,replacements);ni=parse_index(new,len(new))
 for ci in range(idx['count']):assert child(new,ni,ci)==replacements.get(ci,child(data,idx,ci))
 packed=compress(new,0x9831);assert decompress(packed,0x9831)[0]==new
 return packed,images,dict(records=records,other_portrait_layers_unchanged=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--text-only',action='store_true');a=p.parse_args()
 _,er=prepare_elf()
 with GameSource(BASE/'Summon_Night_3_EN_0.1.25.iso') as source:
  _,_,tr=prepare_text(source)
  if a.text_only:images=[];ar={}
  else:
   _,images,ar=prepare_art(source);_,bi,br=prepare_battle_art(source);images+=bi;ar['records'].extend(br['records'])
 report=dict(version='0.1.26',elf=er,table=tr,graphics=ar,meaning_review='Independent reviewer accepted Crush! Light Gen. Sword as a compact skill-title compound: Crush retains the imperative, Gen. abbreviates General, and omitted possessive is grammatical compression. Favorites Only preserves the restriction. Kyle spelling locked to selected glossary.',locked_question_marks_preserved=True)
 print(json.dumps(report,indent=2))
 if a.write:
  FOLDER.mkdir(parents=True,exist_ok=True);(FOLDER/'review.json').write_text(json.dumps(report,indent=2)+'\n')
  for name,im in images:im.save(ART/name)
if __name__=='__main__':main()
