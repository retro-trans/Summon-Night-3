"""Center recipe-title ink inside its unchanged native strip on immutable 0.1.51."""
import struct,hashlib
from sn3_archive import ROOT
BASE=ROOT/'work/output/0.1.51'
SITE=0x1227a0
OLD=3<<26|0x347b5c>>2
CENTER=0x348a7c
NEW=3<<26|CENTER>>2

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();out=bytearray(old)
 assert struct.unpack_from('<I',old,SITE+192)[0]==OLD
 assert struct.unpack_from('<I',old,0x193d80+192)[0]==NEW
 from stages_pupil_names import parse_elf
 rel=parse_elf(old)['phdrs'][2]
 assert (SITE,4) in list(struct.iter_unpack('<II',old[rel[1]:rel[1]+rel[4]]))
 struct.pack_into('<I',out,SITE+192,NEW)
 assert out[:SITE+192]==old[:SITE+192] and out[SITE+196:]==old[SITE+196:]
 return bytes(out),dict(entries=[],site=hex(SITE),old_target='0x347b5c',new_target=hex(CENTER),existing_relocation_reused=True,new_code_bytes=0,patched_elf_sha256=hashlib.sha256(out).hexdigest())

def prepare_tables(source):
 return {3:source.resource('02.DAT',3)},{},source.resource('00.DAT',44),dict(units=[],tables=[])

def prior_layout_view(elf):
 # Older audits assert the historical title call. Verify the sole candidate
 # change, then restore only that word for their unchanged-path checks.
 expected,_=prepare_elf();assert elf==expected
 out=bytearray(elf);struct.pack_into('<I',out,SITE+192,OLD)
 assert bytes(out)==(BASE/'EBOOT.elf').read_bytes()
 return bytes(out)

def verify(elf,static):
 from verify_cooking_title_052 import verify as run
 return run(elf,static)
