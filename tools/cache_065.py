"""Give the chapter-common VM script a private, loader-owned 32 KiB arena.

The native arena at main+0x240000 overlaps the expanded resident tables.
Only its three base-getter calls change; every other main-memory partition
and the native decoder/binder remain unchanged. The ELF loader owns the new
arena for the process lifetime, including chapter switches and game loads.
"""
import struct,hashlib
from sn3_archive import ROOT,GameSource
from sn3_codec import decompress
from menu_code_020 import append
from stages_pupil_names import parse_elf,validate_loader_structure
BASE=ROOT/'work/output/0.1.64'
CAPACITY=0x8000
HOOKS=(0x209a4,0x209e0,0x20b24)
sha=lambda b:hashlib.sha256(b).hexdigest()

def emit(a):
 a.label('common_script_base')
 a.table_address('v0')
 a.i(15,'t0','zero',0x24)
 a.emit(2<<21|8<<16|2<<11|0x23) # subu v0,v0,t0
 a.ret()

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes()
 out,r=append(old,emit,{p:('common_script_base',3<<26|0x13ee4>>2) for p in HOOKS},bytes(CAPACITY))
 out=bytearray(out);parsed=parse_elf(out);seg=parsed['phdrs'][3]
 # This segment now contains executable helpers and a writable VM arena.
 struct.pack_into('<I',out,parsed['phoff']+3*32+24,7)
 # Keep the corresponding ELF section writable as well.
 shoff=struct.unpack_from('<I',out,32)[0]
 for i,s in enumerate(parsed['sections']):
  if s[3]==seg[2] and s[4]==seg[1]:struct.pack_into('<I',out,shoff+i*40+8,s[2]|1)
 out=bytes(out)
 ids=struct.unpack_from('<21h',old,0x226790+0xc0)
 scripts=[]
 with GameSource(BASE/'Summon_Night_3_EN_0.1.64.iso') as src:
  for n in sorted(set(x+1 for x in ids if x)):
   raw=src.resource('00.DAT',n);d=decompress(raw,0xa695)[0]
   assert len(d)<=CAPACITY,(n,len(d))
   scripts.append(dict(resource=n,decoded_bytes=len(d)))
 r.update(source_sha256=sha(old),output_sha256=sha(out),arena_capacity=CAPACITY,
          arena_va=int(r['code_address'],16)+r['labels']['table'],
          chapter_scripts=scripts,other_main_partitions_unchanged=True,
          structure=validate_loader_structure(out))
 return out,r

def prepare_names(source,write_assets=False):
 return {3:source.resource('02.DAT',3)},[]
