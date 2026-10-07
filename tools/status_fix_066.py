"""Localize the reported summon labels and scope proportional SELECT placement."""
import argparse,json,struct,hashlib
from sn3_archive import ROOT,GameSource,parse_index,child
from sn3_repack import repack
from character_labels import collect
from dialogue_encoding import encode_dialogue
from menu_code_020 import append
from font_patch import REG
from stages_pupil_names import validate_loader_structure
BASE=ROOT/'work/output/0.1.65'
TEXT=ROOT/'work/translation/en/status_0.1.66/targets.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
LOOKUP=0x32e380

def emit(a,fallback):
    def r(fn,rd,rs,rt):a.emit(REG[rs]<<21|REG[rt]<<16|REG[rd]<<11|fn)
    def shift(rd,rt,n):a.emit(REG[rt]<<16|REG[rd]<<11|n<<6)
    a.label('food_icon')
    # Descriptor row/index are internal native values. Compare only nine cells
    # within the existing 29-cell second-row buffer, immediately after the icon.
    a.i(36,'t0','s3',0x101);a.i(9,'t1','zero',1);a.branch(5,'t0','t1','fallback')
    a.i(36,'t0','s3',0x100);a.i(11,'t1','t0',17);a.branch(4,'t1','zero','fallback')
    shift('t0','t0',1);r(0x21,'t0','s2','t0');a.i(9,'t0','t0',0x4c+58+4)
    a.table_address('t1');a.i(9,'t2','zero',9)
    a.label('compare');a.i(37,'t3','t0',0);a.i(37,'t4','t1',0)
    a.branch(5,'t3','t4','fallback');a.i(9,'t0','t0',2);a.i(9,'t1','t1',2)
    a.i(9,'t2','t2',-1);a.branch(5,'t2','zero','compare')
    a.i(9,'sp','sp',-64)
    for reg,off in [('ra',60),('a0',48),('a2',52),('s0',32),('s1',36),('s2',40),('s3',44)]:a.i(43,reg,'sp',off)
    a.i(9,'s0','s2',0x4c+58);a.i(36,'s1','s3',0x100);a.move('s3','s1');a.move('s2','zero')
    a.label('sum');a.branch(4,'s1','zero','done');a.i(37,'a0','s0',0);a.jump(LOOKUP)
    a.i(9,'t3','zero',16);a.branch(4,'a0','t3','unknown')
    shift('t3','v0',3);r(0x23,'t3','t3','v0');a.branch(4,'zero','zero','add')
    a.label('unknown');a.i(9,'t3','zero',104)
    a.label('add');r(0x21,'s2','s2','t3');a.i(9,'s0','s0',2);a.i(9,'s1','s1',-1);a.branch(4,'zero','zero','sum')
    a.label('done');shift('t0','s3',6);shift('t1','s3',5);r(0x21,'t0','t0','t1');shift('t1','s3',3);r(0x21,'t0','t0','t1');r(0x23,'s2','s2','t0')
    a.int_to_float('s2',4);a.i(15,'t3','zero',0x3e00);a.emit(17<<26|4<<21|REG['t3']<<16|2<<11)
    a.emit(17<<26|16<<21|2<<16|4<<11|4<<6|2);a.add_float(12,12,4)
    a.i(35,'a0','sp',48);a.i(35,'t9','sp',52);a.emit(REG['t9']<<21|REG['ra']<<11|9);a.emit(0)
    for reg,off in [('ra',60),('s0',32),('s1',36),('s2',40),('s3',44)]:a.i(35,reg,'sp',off)
    a.i(9,'sp','sp',64);a.ret()
    a.label('fallback');a.jump(fallback,link=False)

def prepare_elf():
    old=(BASE/'EBOOT.elf').read_bytes();word=struct.unpack_from('<I',old,0x64490+192)[0];assert word>>26==3
    prior=(word&0x3ffffff)<<2
    out,r=append(old,lambda a:emit(a,prior),{0x64490:('food_icon',word)},encode_dialogue('Give Food','')[0]+b'\0\0')
    r.update(source_sha256=sha(old),output_sha256=sha(out),fallback=hex(prior),scope='Second-row icon followed by Give Food only; nine bounded cells; all other icons retain the previous handler.',structure=validate_loader_structure(out))
    return out,r

def prepare_tables(source):
    old,count,rows=collect(source);out=bytearray(old);targets=json.loads(TEXT.read_text(encoding='utf8'))['entries'];changes=[];allowed=set()
    metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters']
    for t in targets:
        row=next(r for r in rows if old[r['source_offset']:r['source_offset']+r['source_byte_length']].decode('cp932')==t['source'])
        assert row['source_sha256']==t['source_sha256'];text=t['english'];assert text.isascii() and len(text)<=16
        width=sum(metrics[c]['proposed_advance_pixels'] for c in text)*.875;assert width<=133
        out.extend(bytes(-len(out)%2));pos=len(out);raw,_=encode_dialogue(text,'');out.extend(raw+b'\0\0')
        for ref in row['references']:
            f=ref['pointer_field_offset'];assert struct.unpack_from('<I',old,f)[0]==row['source_offset'];struct.pack_into('<I',out,f,pos);allowed.update(range(f,f+4))
        changes.append(dict(english=text,width_pixels=width,source_sha256=t['source_sha256'],new_offset=pos,references=row['references']))
    assert len(changes[0]['references'])==1 and len(changes[1]['references'])==16
    assert all(a==b for i,(a,b) in enumerate(zip(old,out)) if i not in allowed)
    bank=source.resource('01.DAT',1);bank=repack(bank,{0:bytes(out)})
    master=source.resource('00.DAT',44);mi=parse_index(master,len(master));cached=child(master,mi,6)
    master=repack(master,{6:repack(cached,{0:bytes(out)})})
    return {3:source.resource('02.DAT',3)},{1:bank},master,dict(units=changes,tables=[],label_count=count,all_other_original_label_bytes_unchanged=True)

def main():
    elf,r=prepare_elf()
    with GameSource(BASE/'Summon_Night_3_EN_0.1.65.iso') as src:_,_,_,labels=prepare_tables(src)
    print(json.dumps(dict(mode='preview',labels=labels,helper={k:r[k] for k in ('code_address','code_bytes','labels','hooks','scope','fallback','output_sha256')}),indent=2))
if __name__=='__main__':main()
