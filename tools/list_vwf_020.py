"""Native list VWF and display-only translation of saved default summon names."""
import json,struct,hashlib,unicodedata
import font_patch
from font_patch import REG
from menu_code_020 import append
from menu_packer_020 import compile_code
from sn3_archive import ROOT,GameSource,parse_index,child

BASE=ROOT/'work/output/0.1.19'
def name_pairs():
    idx=json.loads((ROOT/'work/translation/en/interface.index.json').read_text())
    table=next(t for t in idx['tables'] if t['resource_path']==[3,12])
    with GameSource(BASE/'Summon_Night_3_EN_0.1.19.iso') as s:
        st=s.resource('02.DAT',3);tb=child(st,parse_index(st,len(st)),12)
    found={};audit=[]
    for row in table['strings']:
        refs=[r for r in row['references'] if r['slot'] in (9,10,11)]
        if not refs:continue
        p=struct.unpack_from('<I',tb,refs[0]['pointer_field_offset'])[0]
        end=next(q for q in range(p,len(tb),2) if tb[q:q+2]==b'\0\0');target=tb[p:end]
        norm=unicodedata.normalize('NFKC',target.decode('cp932'))
        if not norm or not norm.isascii():continue
        start=row['source_offset'];length=row['source_byte_length'];source=tb[start:start+length]
        assert hashlib.sha256(source).hexdigest()==row['source_sha256']
        assert len(target)//2<=16
        if source in found:assert found[source]==target
        found[source]=target
        audit.append(dict(id=row['id'],source_sha256=row['source_sha256'],target=norm))
    pairs=sorted(found.items());payload=bytearray(len(pairs)*8)
    for i,(src,dst) in enumerate(pairs):
        so=len(payload);payload.extend(src+b'\0\0');do=len(payload);payload.extend(dst+b'\0\0')
        struct.pack_into('<II',payload,i*8,so,do)
    return pairs,bytes(payload),audit

def emitter(count):
    def emit(a):
        code,labels,relocs=compile_code(font_patch.CODE_VA)
        a.words=list(struct.unpack('<%dI'%(len(code)//4),code))
        a.labels={k:v for k,v in labels.items() if k!='table'};a.relocs=list(relocs)
        offset=len(code);center,clabels,crelocs=compile_code(font_patch.CODE_VA+offset,center=True)
        a.words+=list(struct.unpack('<%dI'%(len(center)//4),center))
        a.labels.update({'center_'+k:offset+v for k,v in clabels.items() if k!='table'})
        a.relocs += [(offset+o,info) for o,info in crelocs]
        def r(fn,rd,rs,rt='zero'):a.emit(REG[rs]<<21|REG[rt]<<16|REG[rd]<<11|fn)
        a.label('saved_name');a.move('v0','a0');a.table_address('t0');a.move('t2','t0');a.i(9,'t1','zero',count)
        a.label('name_next');a.i(35,'t3','t2',0);r(0x21,'t3','t3','t0');a.move('t4','a0')
        a.label('name_compare');a.i(37,'t5','t3',0);a.i(37,'t6','t4',0)
        a.branch(5,'t5','t6','name_miss');a.branch(4,'t5','zero','name_found')
        a.i(9,'t3','t3',2);a.i(9,'t4','t4',2);a.branch(4,'zero','zero','name_compare')
        a.label('name_miss');a.i(9,'t1','t1',-1);a.i(9,'t2','t2',8);a.branch(5,'t1','zero','name_next');a.ret()
        a.label('name_found');a.i(35,'v0','t2',4);r(0x21,'v0','v0','t0');a.ret()
        for label,bind in [('list','bind'),('center_list','center_bind')]:
            a.label(label);a.i(9,'sp','sp',-48)
            for reg,off in [('ra',44),('a0',16),('a2',20)]:a.i(43,reg,'sp',off)
            a.move('a0','a1');a.jump('saved_name');a.i(43,'v0','sp',24)
            a.move('a0','v0');a.jump(0x1e4ac8)
            a.i(35,'a0','sp',16);a.i(35,'a1','sp',24);a.move('a2','v0');a.i(35,'a3','sp',20)
            a.jump(bind);a.i(35,'ra','sp',44);a.i(9,'sp','sp',48);a.ret()
    return emit

def prepare(data):
    pairs,table,audit=name_pairs()
    out,report=append(data,emitter(len(pairs)),{0x1b390:('list',3<<26|0x1cbdec>>2),0x1b37c:('bind',3<<26|0x1cbe48>>2),0x14ecf8:('list',3<<26|0x1cbdec>>2),0x193d80:('center_list',3<<26|0x1cbdec>>2)},table)
    report.update(profile='native_list_vwf_saved_names_020',max_packed_cells=32,display_name_pairs=len(pairs),names=audit,save_files_unchanged=True)
    return out,report
