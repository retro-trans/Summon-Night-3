"""Relocate glossary-locked opening names in all three backlog data packs."""
import hashlib,struct
from sn3_archive import ROOT,parse_index,child
from sn3_repack import repack
from sn3_codec import decompress,compress
from dialogue_encoding import encode_dialogue

NAMES={'レックス':'Rexx','アティ':'Aty','ナップ':'Nup','ベルフラウ':'Belfrau',
       'アリーゼ':'Alieze','ウィル':'Will','サローネ':'Salome'}
def sha(b):return hashlib.sha256(b).hexdigest()

def prepare_names(source):
    replacements={};reports=[];reference_table=None
    for resource in (85,86,87):
        original=source.resource('02.DAT',resource);data,used=decompress(original,0x9831)
        assert not any(original[used:]);idx=parse_index(data,len(data));table=child(data,idx,22)
        if reference_table is None:reference_table=table
        assert table==reference_table
        count=struct.unpack_from('<I',table)[0];assert count==255
        out=bytearray(table);changes=[];seen=set()
        for row in range(count):
            field=4+row*8;old,flags=struct.unpack_from('<2I',table,field)
            if not old:continue
            assert 4+count*8<=old<len(table) and old%2==0
            end=old
            while table[end:end+2]!=b'\0\0':end+=2
            raw=table[old:end];name=raw.decode('cp932')
            if name not in NAMES:continue
            target=NAMES[name];encoded,display=encode_dialogue(target,name)
            new=len(out);out.extend(encoded+b'\0\0');struct.pack_into('<I',out,field,new)
            changes.append(dict(row=row,pointer_field=field,old_offset=old,new_offset=new,
                source_sha256=sha(raw),text=target,display_text=display))
            seen.add(name)
        assert seen==set(NAMES) and len(changes)==21,(seen,len(changes))
        patched=repack(data,{22:bytes(out)});newidx=parse_index(patched,len(patched))
        for n in range(idx['count']):
            if n!=22:assert child(data,idx,n)==child(patched,newidx,n)
        updated=child(patched,newidx,22)
        for c in changes:
            ptr=struct.unpack_from('<I',updated,c['pointer_field'])[0]
            assert updated[ptr:ptr+len(c['display_text'])*2].decode('cp932')==c['display_text']
        packed=compress(patched,0x9831);assert decompress(packed,0x9831)[0]==patched
        replacements[resource]=packed
        reports.append(dict(resource='02:%05d/00022'%resource,source_decoded_sha256=sha(data),
            decoded_sha256=sha(patched),decoded_size=len(patched),table_sha256=sha(updated),
            table_size=len(updated),changes=changes))
    return replacements,dict(glossary='work/glossary/opening_harbor.json',packs=reports,
        names=list(NAMES.values()),note='Exact name labels only; suffixed and alternate labels retained.')
