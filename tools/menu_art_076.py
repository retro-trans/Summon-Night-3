"""Import scoped generated art with native palette and geometry assertions."""
import json,hashlib
from collections import defaultdict
from PIL import Image
from sn3_archive import ROOT
from menu_art_075 import descend,replace_tree
from sn3_ui_textures import texture_records,decode_texture
from setup_ui_patch import encode_texture
from dialogue_encoding import encode_dialogue
from menu_hotfix_017 import lines_at
import struct
F=ROOT/'work/ui/menus_0.1.76'
def prepare(source,write=False):
 cfg=json.loads((ROOT/'work/translation/en/menus_0.1.76/graphics.json').read_text());groups=defaultdict(list);replacements=defaultdict(dict);report=[]
 for e in cfg['entries']:groups[tuple(e['path'])].append(e)
 if write:(F/'native').mkdir(exist_ok=True)
 for path,items in groups.items():
  before=descend(source.resource('02.DAT',path[0]),path[1:]);data=before;rows=texture_records(data);changed={e['sprite'] for e in items}
  for e in items:
   row=next(r for r in rows if r['number']==e['sprite']);old=decode_texture(data,row);native=Image.open(F/'generated'/e['image']).convert('RGBA');assert native.size==old.size,(e['path'],e['sprite'],native.size,old.size)
   # Button contours and all unrelated frame pixels remain untouched.
   if native.size==(112,24):native.putalpha(old.getchannel('A'))
   data,out,pixels=encode_texture(data,row,native);assert len(data)==len(before) and texture_records(data)==rows
   if 'changed_box' in e:
    box=e['changed_box']
    for y in range(old.height):
     for x in range(old.width):
      if not(box[0]<=x<box[2] and box[1]<=y<box[3]):assert out.getpixel((x,y))==old.getpixel((x,y))
   if write:out.save(F/'native'/e['image'])
   report.append(dict(e,changed_pixels=pixels,source_sha256=hashlib.sha256(before).hexdigest(),native_size=list(old.size)))
  for r in rows:
   if r['number'] not in changed:assert decode_texture(before,r).tobytes()==decode_texture(data,r).tobytes()
  replacements[path[0]][path[1:]]=data
 captions=json.loads((ROOT/'work/translation/en/menus_0.1.76/gallery_captions.json').read_text());cgroups=defaultdict(list);creports=[]
 for e in captions['entries']:cgroups[tuple(e['path'])].append(e)
 for path,entries in cgroups.items():
  before=descend(source.resource('02.DAT',path[0]),path[1:]);data=bytearray(before);allowed=set();dedup={}
  for e in entries:
   raw=lines_at(before,e['source_offset'])[0][0];assert hashlib.sha256(raw).hexdigest()==e['source_sha256']
   # This gallery loader reads rows until an empty row, not a single C string.
   # Keep a separate empty-row terminator so adjacent captions cannot join.
   text=encode_dialogue(e['english'][0],'')[0]+bytes(4);assert len(text)//2<=34
   if text not in dedup:dedup[text]=len(data);data.extend(text)
   for f in e['pointer_fields']:
    assert struct.unpack_from('<I',before,f)[0]==e['source_offset'];struct.pack_into('<I',data,f,dedup[text]);allowed.update(range(f,f+4))
   creports.append(dict(e,new_offset=dedup[text]))
  assert all(i in allowed for i,(a,b) in enumerate(zip(before,data)) if a!=b)
  replacements[path[0]][path[1:]]=bytes(data)
 packs={root:replace_tree(source.resource('02.DAT',root),items) for root,items in replacements.items()}
 result=dict(entries=report,translated_sprites=len(report),leaf_occurrences=len(groups),gallery_captions=creports,night_talk_titles=captions['night_talk_titles'],ending_titles=captions['ending_titles'],codec_palette_geometry_preserved=True)
 if write:(F/'native/report.json').write_text(json.dumps(result,indent=2)+'\n')
 return {'02.DAT':packs},result
