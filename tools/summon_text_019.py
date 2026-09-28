"""Complete base summon names, five affinity tiles, and the short cycle label."""
import json,struct,hashlib,unicodedata,argparse
from PIL import Image
from sn3_archive import ROOT,parse_index,child,GameSource
from sn3_repack import repack
from sn3_ui_textures import texture_records,decode_texture
from setup_ui_patch import encode_texture
from menu_art_015 import descend,replace_tree
from battle_table_patch import relocate_fullwidth
from dialogue_encoding import encode_dialogue
from menu_hotfix_017 import lines_at,glyph_check

BASE=ROOT/'work/output/0.1.18'
FOLDER=ROOT/'work/translation/en/summon_0.1.19'
ART=ROOT/'work/ui/summon_0.1.19'
sha=lambda b:hashlib.sha256(b).hexdigest()

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();out=bytearray(old);m=json.loads((BASE/'manifest.json').read_text())
 e=next(e for e in m['menu016_text']['entries'] if e['id']=='elf:ui:0021e22c')
 pos=e['new_file_offset'];span=e['encoded_bytes'];assert out[pos:pos+span]==e['display_text'].encode('cp932')+b'\0\0'
 encoded,display=encode_dialogue('Type','');assert len(encoded)+2<=span
 out[pos:pos+span]=encoded+bytes(span-len(encoded))
 for r in m['menu017_hotfix']['changes']:
  p=r['new_file_offset'];n=r['span'];assert out[p:p+n]==old[p:p+n];glyph_check(lines_at(out,p)[0])
 changes=[i for i,(a,b) in enumerate(zip(old,out)) if a!=b]
 assert len(old)==len(out) and all(pos<=i<pos+span for i in changes)
 return bytes(out),dict(entries=[dict(id=e['id'],target_text='Type',display_text=display,new_file_offset=pos,span=span)],changed_bytes=len(changes),retained_crash_fixes=5)

def prepare_art(source):
 locations=json.loads((ART/'affinity.locations.json').read_text());sheet=Image.open(ART/'affinity_generated.png').convert('RGBA')
 assert sheet.size==(2170,725)
 # ImageGen returned one five-tile strip with transparent letterboxing.
 # Crop only the strip, then resample/palette-convert to native geometry.
 strip=sheet.crop((0,143,2170,580));patches={};images=[];report=[]
 reference=descend(source.resource('02.DAT',2952),[2]);rr=texture_records(reference)
 for row in locations:
  k=row['kind'];n=row['number'];assert 0<=k<5 and n==17+k
  original=decode_texture(reference,rr[n]);art=strip.crop((434*k,0,434*(k+1),437)).resize((16,16),Image.Resampling.LANCZOS)
  art.putalpha(original.getchannel('A'))
  for occ in row['occurrences']:
   assert occ['bank']=='02.DAT';path=tuple(occ['path']);data=patches.get(path,descend(source.resource('02.DAT',path[0]),path[1:]))
   records=texture_records(data);old=decode_texture(data,records[n]);assert old.tobytes()==original.tobytes()
   after,native,_=encode_texture(data,records[n],art)
   # Other texture pixels and shared palette must remain identical.
   for q in records:
    if q['number']!=n:assert decode_texture(after,q).tobytes()==decode_texture(data,q).tobytes()
   assert len(after)==len(data);patches[path]=after
   report.append(dict(path=list(path),texture=n,letter='MOSBN'[k],native_sha256=sha(native.tobytes())))
  images.append(native)
 packs={n:replace_tree(source.resource('02.DAT',n),{p[1:]:v for p,v in patches.items() if p[0]==n}) for n in {p[0] for p in patches}}
 return packs,images,report

def prepare_tables(source):
 idx=json.loads((ROOT/'work/translation/en/interface.index.json').read_text());table=next(t for t in idx['tables'] if t['resource_path']==[3,12])
 targets=json.loads((FOLDER/'names.targets.json').read_text())['translations'];assert len(targets)==87
 rows={r['id']:r for r in table['strings']};starts={}
 for identity,t in targets.items():
  r=rows[identity];assert t['source_sha256']==r['source_sha256']
  assert any(ref['slot']==9 and ref['record']==t['record'] for ref in r['references'])
  text=t['compact'];assert text.isascii() and 0<len(text)<=15 and text.isprintable()
  starts[identity]=dict(text=text,source_sha256=t['source_sha256'])
 static=source.resource('02.DAT',3);si=parse_index(static,len(static));before=child(static,si,12)
 after,changes,skipped=relocate_fullwidth(before,table['strings'],starts,starts)
 for r in skipped:
  identity=r['id'];row=rows[identity];ref=next(ref for ref in row['references'] if ref['slot']==9)
  p=struct.unpack_from('<I',before,ref['pointer_field_offset'])[0]
  text=unicodedata.normalize('NFKC',before[p:before.index(b'\0',p)].decode('cp932'))
  assert text and text.isascii() and text.isprintable();r['retained_english']=text
 # Every base-name field now resolves to printable English, including old translations.
 checked=[]
 for identity,t in targets.items():
  ref=next(ref for ref in rows[identity]['references'] if ref['slot']==9);p=struct.unpack_from('<I',after,ref['pointer_field_offset'])[0]
  text=unicodedata.normalize('NFKC',after[p:after.index(b'\0',p)].decode('cp932'))
  assert text and text.isascii() and text.isprintable() and len(text)<=15
  checked.append(dict(record=t['record'],id=identity,text=text,pointer_field=ref['pointer_field_offset'],offset=p))
 assert next(x['text'] for x in checked if x['record']==6)=='Dritol'
 assert next(x['text'] for x in checked if x['record']==84)=='Shine Saber'
 patched=repack(static,{12:after});master=source.resource('00.DAT',44);mi=parse_index(master,len(master));assert child(master,mi,7)==static
 master=repack(master,{7:patched});art,images,ar=prepare_art(source)
 return {3:patched,**art},{},master,dict(tables=[dict(child=12,changes=changes,skipped=skipped)],units=[],base_names=checked,affinity_icons=ar)

def main():
 p=argparse.ArgumentParser();p.add_argument('--write-preview',action='store_true');a=p.parse_args()
 with GameSource(BASE/'Summon_Night_3_EN_0.1.18.iso') as source:_,images,r=prepare_art(source)
 print(json.dumps(dict(mode='write-preview' if a.write_preview else 'dry-run',icons=len(images),occurrences=len(r),labels=['Machine','Oni','Spirit','Beast','Neutral']),indent=2))
 if a.write_preview:
  out=Image.new('RGBA',(5*128,128))
  for n,im in enumerate(images):out.paste(im.resize((128,128),Image.Resampling.NEAREST),(n*128,0))
  out.save(ART/'native_icons_preview.png')
if __name__=='__main__':main()
