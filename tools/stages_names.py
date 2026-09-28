"""Relocate the newly encountered cast's backlog labels; keep other labels intact."""
import struct
from sn3_archive import parse_index,child
from sn3_repack import repack
from sn3_codec import decompress,compress
from dialogue_encoding import encode_dialogue
from stages_patch import sha
NAMES={'カイル':'Kyle','ソノラ':'Sonolar','スカーレル':'Scarrel','ヤード':'Yard','アズリア':'Azlier','ギャレオ':'Galleor','ビジュ':'Vijue'}
def prepare_names(source):
    replacements={};reports=[]
    for resource in (85,86,87):
        data=decompress(source.resource('02.DAT',resource),0x9831)[0];idx=parse_index(data,len(data));table=child(data,idx,22)
        out=bytearray(table);changes=[];seen=set();count=struct.unpack_from('<I',table)[0];assert count==255
        # Both fields are optional string pointers. Preserve alternate labels.
        for field in range(4,4+count*8,4):
            old=struct.unpack_from('<I',table,field)[0]
            if not old:continue
            assert 4+count*8<=old<len(table)
            end=old
            while table[end:end+2]!=b'\0\0':end+=2
            raw=table[old:end];name=raw.decode('cp932')
            if name not in NAMES:continue
            encoded,display=encode_dialogue(NAMES[name],name);new=len(out);out.extend(encoded+b'\0\0');struct.pack_into('<I',out,field,new)
            seen.add(name);changes.append(dict(pointer_field=field,old_offset=old,new_offset=new,source_sha256=sha(raw),text=NAMES[name],display_text=display))
        assert seen==set(NAMES),(seen,set(NAMES)-seen)
        updated=repack(data,{22:bytes(out)});ix=parse_index(updated,len(updated))
        for n in range(idx['count']):
            if n!=22:assert child(data,idx,n)==child(updated,ix,n)
        packed=compress(updated,0x9831);assert decompress(packed,0x9831)[0]==updated
        replacements[resource]=packed;reports.append(dict(resource='02:%05d/00022'%resource,changes=changes,table_sha256=sha(child(updated,ix,22)),table_size=len(child(updated,ix,22)),decoded_sha256=sha(updated)))
    return replacements,dict(names=list(NAMES.values()),packs=reports,glossary='work/glossary/ship_0.1.12.json')
