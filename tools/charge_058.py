"""Translate the separate Charge command label; pure preparation, preview first."""
import argparse, hashlib, json, struct
from pathlib import Path
from sn3_archive import ROOT, GameSource, parse_index, child
from sn3_repack import repack
from dialogue_encoding import encode_dialogue

BASE=ROOT/'work/output/0.1.57'
TARGET=ROOT/'work/translation/en/charge_0.1.58/targets.json'
sha=lambda b:hashlib.sha256(b).hexdigest()

def prepare_tables(source):
    spec=json.loads(TARGET.read_text(encoding='utf8'))
    assert spec['text']=='Charge' and spec['record']==50 and spec['child']==28
    static=source.resource('02.DAT',3); si=parse_index(static,len(static))
    before=child(static,si,28); out=bytearray(before)
    assert struct.unpack_from('<I',before)[0]==74
    field=4+50*48+8*4
    old=struct.unpack_from('<I',before,field)[0]
    assert old==0x14a0 and before[old:old+10]=='チャージ'.encode('cp932')+b'\0\0'
    raw,display=encode_dialogue(spec['text'],'チャージ')
    assert len(raw)==12 and all(raw[i]>=0x80 for i in range(0,len(raw),2))
    assert len(display)*16<=480-276, 'Charge exceeds reported 204-pixel banner'
    out.extend(bytes(-len(out)%2)); at=len(out); out.extend(raw+b'\0\0')
    struct.pack_into('<I',out,field,at)
    assert out[:field]==before[:field] and out[field+4:len(before)]==before[field+4:]
    assert out[at:at+len(raw)].decode('cp932')==display
    after=repack(static,{28:bytes(out)}); ai=parse_index(after,len(after))
    assert all(child(after,ai,e['id'])==child(static,si,e['id']) for e in si['entries'] if e['id']!=28)
    master=source.resource('00.DAT',44); mi=parse_index(master,len(master))
    assert child(master,mi,7)==static
    report=dict(version='0.1.58',text=spec['text'],display_text=display,bank='02.DAT',
        resource=3,child=28,record=50,slot=8,pointer_field=field,old_offset=old,new_offset=at,
        encoded_bytes=len(raw),source_sha256=sha(before),output_sha256=sha(out),
        original_pool_preserved=True,other_children_unchanged=True,
        fixed_cell_width_bound=96,reported_banner_width=204,
        runtime_verified=False)
    return {3:after}, repack(master,{7:after}), report

def main():
    p=argparse.ArgumentParser();p.add_argument('--write-report',action='store_true');a=p.parse_args()
    with GameSource(BASE/'Summon_Night_3_EN_0.1.57.iso') as s: _,_,r=prepare_tables(s)
    print(json.dumps(dict(mode='write report' if a.write_report else 'preview',report=r),indent=2,ensure_ascii=False))
    if a.write_report:
        dest=ROOT/'work/ui/charge_0.1.58/import-validation.json';dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n',encoding='utf8')

if __name__=='__main__': main()
