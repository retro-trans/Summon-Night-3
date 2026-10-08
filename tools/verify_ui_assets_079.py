"""Verify the built image's active text, sprite metadata and help staging."""
import json,struct
from sn3_archive import ROOT,GameSource,parse_index,child
from ui_fix_079 import prepare_elf,sha,TEXT
from menu_art_075 import descend
from sn3_ui_textures import texture_records,decode_texture
from menu_hotfix_017 import lines_at
from dialogue_encoding import encode_dialogue
from check_ui_079 import check
from build_candidate import hash_file
from verify_guards_049 import AliasCPU,stage

def main():
 dest=ROOT/'work/output/0.1.79';m=json.loads((dest/'manifest.json').read_text());iso=dest/m['output_iso'];assert hash_file(iso)==m['output_sha256'];elf=(dest/'EBOOT.elf').read_bytes()
 fields=help_cases=sprites=0
 with GameSource(iso) as source,GameSource(ROOT/'work/output/0.1.78/Summon_Night_3_EN_0.1.78.iso') as prior:
  static=source.resource('02.DAT',3);assert prepare_elf(static)[0]==elf
  b=child(static,parse_index(static,len(static)),25)
  for e in m['ui079_fix']['labels']['changes']:
   expected=[encode_dialogue(t,'')[0] for t in e['english']];assert lines_at(b,e['new_offset'])[0]==expected
   for f in e['pointer_fields']:assert struct.unpack_from('<I',b,f)[0]==e['new_offset'];fields+=1
  c=AliasCPU(elf,static)
  for row in check(static,json.loads(TEXT.read_text()))['rows']:
   lines=row['help'];payload=b''.join(encode_dialogue(t,'')[0]+bytes(2) for t in lines)+bytes(2);r=stage(c,payload)
   assert r['glyphs']==sum(map(len,lines)) and r['rows']==len(lines) and r['max_slot']<54;help_cases+=1
  for e in m['ui079_fix']['labels']['gallery']:
   b=descend(source.resource('02.DAT',e['path'][0]),e['path'][1:]);assert lines_at(b,e['new_offset'])[0]==[encode_dialogue(e['english'][0],'')[0]]
  for e in m['ui079_fix']['art']['entries']:
   p=e['path'];old=descend(prior.resource(e['bank'],p[0]),p[1:]);new=descend(source.resource(e['bank'],p[0]),p[1:]);assert sha(old)==e['source_sha256'];rows=texture_records(old);assert texture_records(new)==rows and len(new)==len(old)
   r=rows[e['sprite']];pal=r['palette_base'];o,n,_,_=struct.unpack_from('<4I',old,pal+4);assert old[pal+o:pal+o+n]==new[pal+o:pal+o+n]
   assert decode_texture(new,r).getchannel('A').getbbox();sprites+=1
 r=dict(passed=True,iso_sha256=m['output_sha256'],active_text_pointers=fields,actual_help_staging_cases=help_cases,translated_sprites=sprites,translated_leaf_occurrences=m['ui079_fix']['art']['leaf_occurrences'],geometry_palette_codecs_preserved=True,numeric_fields_and_original_pools_preserved=True,executable_matches_verified_emission=True)
 (dest/'asset-validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
if __name__=='__main__':main()
