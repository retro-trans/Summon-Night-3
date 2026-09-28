"""Append relocatable menu helpers without changing prior loaded code/data."""
import struct,hashlib
from stages_pupil_names import parse_elf,validate_loader_structure
import font_patch
from font_patch import Assembler

def append(data,emit,hooks,table=b''):
    parsed=parse_elf(data); ph=[x[:] for x in parsed['phdrs']];sh=[x[:] for x in parsed['sections']]
    seg,rel=ph[3],ph[2];old=data[seg[1]:seg[1]+seg[4]];base=seg[2]+len(old)
    assert base%4==0
    prior=font_patch.CODE_VA
    try:
        font_patch.CODE_VA=base;a=Assembler();emit(a);code=a.finish(table)
    finally:font_patch.CODE_VA=prior
    oldrel=data[rel[1]:rel[1]+rel[4]];records=list(struct.iter_unpack('<II',oldrel));new=[];out=bytearray(data)
    for va,(target,expected) in hooks.items():
        actual=struct.unpack_from('<I',data,va+0xc0)[0]
        assert actual==expected,(hex(va),hex(actual),hex(expected))
        address=base+a.labels[target] if isinstance(target,str) else target
        struct.pack_into('<I',out,va+0xc0,3<<26|address>>2)
        if (va,4) not in records:new.append((va,4))
    new += [(len(old)+offset,info) for offset,info in a.relocs]
    def pad(n):out.extend(bytes(-len(out)%n))
    pad(64);sf=len(out);out.extend(old+code)
    pad(16);rf=len(out);out.extend(oldrel);out.extend(b''.join(struct.pack('<II',*r) for r in new))
    for s in sh:
        if s[1]==0x700000a0:s[4]+=rf-rel[1]
        if s[3]==seg[2] and s[4]==seg[1]:s[4]=sf;s[5]=len(old)+len(code)
    code_section=next(i for i,s in enumerate(sh) if s[3]==seg[2] and s[4]==sf)
    sh.append([0,0x700000a0,0,0,rf+len(oldrel),len(new)*8,52,code_section,4,8])
    seg[1]=sf;seg[4]=seg[5]=len(old)+len(code);rel[1]=rf;rel[4]=len(oldrel)+len(new)*8
    pad(16);newsh=len(out);out.extend(b''.join(struct.pack('<10I',*s) for s in sh))
    for i,p in enumerate(ph):struct.pack_into('<8I',out,parsed['phoff']+i*32,*p)
    struct.pack_into('<I',out,32,newsh);struct.pack_into('<H',out,48,len(sh))
    assert out[sf:sf+len(old)]==old
    report=dict(code_address=hex(base),code_bytes=len(code),labels=a.labels,hooks={hex(k):v[0] for k,v in hooks.items()},
                new_relocations=new,extra_relocation_records=[r for r in records+new if r[1]>>8&255==3],
                added_segment_file_offset=sf,added_segment_bytes=seg[4],
                patched_elf_sha256=hashlib.sha256(out).hexdigest(),structure=validate_loader_structure(out))
    return bytes(out),report
