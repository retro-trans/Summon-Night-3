"""Check the built executable and translated tables against verified inputs."""
import json,hashlib
from sn3_archive import ROOT,GameSource
from ui_fix_080 import BASE,prepare_tables,prepare_elf
from build_candidate import hash_file
from replay_art_080 import prepare as prepare_art

def main():
 dest=ROOT/'work/output/0.1.80';m=json.loads((dest/'manifest.json').read_text());iso=dest/m['output_iso'];assert hash_file(iso)==m['output_sha256']
 with GameSource(BASE/'Summon_Night_3_EN_0.1.79.iso') as source:
  tables,_,_,tr=prepare_tables(source);art,artreport=prepare_art(source)
 elf,report=prepare_elf(tables[3]);assert (dest/'EBOOT.elf').read_bytes()==elf
 with GameSource(iso) as candidate:
  built=candidate.resource('02.DAT',3);assert built[:len(tables[3])]==tables[3] and not any(built[len(tables[3]):])
  for n,expected in art.items():
   built=candidate.resource('02.DAT',n);assert built[:len(expected)]==expected and not any(built[len(expected):])
 result=json.loads((ROOT/'work/ui/ui_0.1.80/validation.json').read_text());assert result['passed']
 result.update(version='0.1.80',iso_sha256=m['output_sha256'],built_table_fields_verified=tr['entries'],built_executable_sha256=hashlib.sha256(elf).hexdigest(),native_translation_groups=len(report['entries']),replay_marker_sprites=artreport,inherited_category_changes='0.1.79; unchanged resources compared during build')
 (dest/'asset-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':main()
