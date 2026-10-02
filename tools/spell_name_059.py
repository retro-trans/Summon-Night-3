"""Fit Shine Saber's skill label before the MP cost; pure planning, preview first."""
import argparse,hashlib,json,struct,unicodedata
from sn3_archive import ROOT,GameSource,parse_index,child
from sn3_repack import repack
from dialogue_encoding import encode_dialogue

BASE=ROOT/'work/output/0.1.58'
TARGET=ROOT/'work/translation/en/spell_name_0.1.59/targets.json'
sha=lambda b:hashlib.sha256(b).hexdigest()

def label(table,field):
    p=struct.unpack_from('<I',table,field)[0]
    if not p:return ''
    end=p
    while table[end:end+2]!=b'\0\0':
        end+=2;assert end+2<=len(table)
    return unicodedata.normalize('NFKC',table[p:end].decode('cp932'))

def prepare_tables(source):
    spec=json.loads(TARGET.read_text(encoding='utf8'))
    assert spec['text']=='Crush! L.Gen.Sword' and spec['record']==233
    static=source.resource('02.DAT',3);si=parse_index(static,len(static))
    before=child(static,si,13);out=bytearray(before)
    assert struct.unpack_from('<I',before)[0]==237
    field=4+233*40+8*4
    assert label(before,field)==spec['prior_display']
    source_name=spec['source_label'].encode('cp932')
    assert before[0x34e0:0x34e0+len(source_name)]==source_name
    raw,display=encode_dialogue(spec['text'],spec['source_label']);assert len(raw)//2<=32
    metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters']
    width=lambda text:sum(metrics[c]['proposed_advance_pixels'] for c in text)*.875
    advance=width(spec['text']);assert advance<=spec['max_advance_pixels']
    out.extend(bytes(-len(out)%2));at=len(out);out.extend(raw+b'\0\0')
    struct.pack_into('<I',out,field,at)
    assert out[:field]==before[:field] and out[field+4:len(before)]==before[field+4:]
    assert label(out,field)==spec['text']
    audited=[]
    for n in range(237):
        text=label(out,4+n*40+8*4)
        if text and all(c in metrics for c in text):
            pixels=width(text);assert pixels<=140,(n,text,pixels)
            audited.append(dict(record=n,text=text,advance_pixels=pixels))
    after=repack(static,{13:bytes(out)});ai=parse_index(after,len(after))
    assert all(child(after,ai,e['id'])==child(static,si,e['id']) for e in si['entries'] if e['id']!=13)
    master=source.resource('00.DAT',44);mi=parse_index(master,len(master))
    assert child(master,mi,7)==static
    report=dict(version='0.1.59',text=spec['text'],full_translation=spec['full_translation'],
        child=13,record=233,slot=8,pointer_field=field,old_offset=struct.unpack_from('<I',before,field)[0],
        new_offset=at,source_sha256=sha(before),output_sha256=sha(out),
        old_advance_pixels=width(spec['prior_display']),new_advance_pixels=advance,max_advance_pixels=140,
        other_table_fields_unchanged=True,original_pool_preserved=True,other_children_unchanged=True,
        spell_name_audit=audited,runtime_verified=False)
    return {3:after},repack(master,{7:after}),report

def main():
    p=argparse.ArgumentParser();p.add_argument('--write-report',action='store_true');a=p.parse_args()
    with GameSource(BASE/'Summon_Night_3_EN_0.1.58.iso') as s:_,_,r=prepare_tables(s)
    sample={k:v for k,v in r.items() if k!='spell_name_audit'}
    sample['audited_spell_names']=len(r['spell_name_audit'])
    print(json.dumps(dict(mode='write report' if a.write_report else 'preview',report=sample),indent=2))
    if a.write_report:
        dest=ROOT/'work/ui/spell_name_0.1.59/import-validation.json';dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(r,indent=2)+'\n')

if __name__=='__main__':main()
