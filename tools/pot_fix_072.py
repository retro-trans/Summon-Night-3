"""Bound default initialization as well as summon renaming."""
import struct,hashlib
from sn3_archive import ROOT
from pot_fix_071 import prepare_elf as prior_prepare,prepare_names
from stages_pupil_names import validate_loader_structure
BASE=ROOT/'work/output/0.1.71'

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();expected,report=prior_prepare();assert old==expected
 out=bytearray(old);site=0x54900
 assert struct.unpack_from('<I',old,site+192)[0]==(3<<26|0x1e4b20>>2)
 target=int(report['code_address'],16)+report['labels']['copy_name']
 struct.pack_into('<I',out,site+192,3<<26|target>>2)
 # The native JAL already has a loader relocation; its target remains module-relative.
 from stages_pupil_names import parse_elf
 rel=parse_elf(out)['phdrs'][2]
 assert (site,4) in list(struct.iter_unpack('<II',out[rel[1]:rel[1]+rel[4]]))
 out=bytes(out)
 report=dict(report,default_initialization_site=hex(site),default_slots=96,
  source_sha256=hashlib.sha256(old).hexdigest(),output_sha256=hashlib.sha256(out).hexdigest(),
  structure=validate_loader_structure(out))
 return out,report
