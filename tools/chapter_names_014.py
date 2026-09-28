"""Translate remaining backlog cast labels using the selected name reference."""
import json,struct,unicodedata
from chapter_names import NAMES as PRIOR_NAMES
from chapter_patch_014 import normalize
from sn3_archive import ROOT,parse_index,child
from sn3_repack import repack
from sn3_codec import decompress,compress
from dialogue_encoding import encode_dialogue
from stages_patch import sha

NAMES={**PRIOR_NAMES,'イスラ':'Ishlar','ファリエル':'Fariel','ハイネル':'Hainel','メイメイ':'Meimei','ジャキーニ':'Jakini','オウキーニ':'Ohkini','オルドレイク':'Ordreik','ツェリーヌ':'Zeline','ウィゼル':'Vizel','ベルフラウ':'Belfraw','サローネ':'Salone','パナシェ':'Panashe','ゲンジ':'Genji'}

def prepare_names(source):
    replacements={};reports=[]
    for number in (85,86,87):
        data=decompress(source.resource('02.DAT',number),0x9831)[0]
        idx=parse_index(data,len(data));table=child(data,idx,22);out=bytearray(table)
        count=struct.unpack_from('<I',table)[0];assert count==255
        changes=[]
        for field in range(4,4+count*8,4):
            old=struct.unpack_from('<I',table,field)[0]
            if not old:continue
            assert 4+count*8<=old<len(table)
            end=old
            while table[end:end+2]!=b'\0\0':end+=2
            name=table[old:end].decode('cp932');plain=unicodedata.normalize('NFKC',name)
            target=normalize(NAMES.get(plain,plain))
            if target==plain:continue
            encoded,display=encode_dialogue(target,name);new=len(out)
            out.extend(encoded+b'\0\0');struct.pack_into('<I',out,field,new)
            changes.append(dict(pointer_field=field,source_sha256=sha(table[old:end]),old_offset=old,new_offset=new,text=target,display_text=display))
        updated=repack(data,{22:bytes(out)});ix=parse_index(updated,len(updated))
        for n in range(idx['count']):
            if n!=22:assert child(data,idx,n)==child(updated,ix,n)
        packed=compress(updated,0x9831);assert decompress(packed,0x9831)[0]==updated
        replacements[number]=packed
        reports.append(dict(resource=number,changes=changes,decoded_sha256=sha(updated)))
    return replacements,dict(packs=reports,reference='work/glossary/character_reference_sn6_vita.json',player_name_storage_unchanged=True)
