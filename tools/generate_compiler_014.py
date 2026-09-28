"""Create a versioned compiler snapshot; preview exact modifications first."""
import argparse, inspect
from pathlib import Path
import chapter_patch
from sn3_archive import ROOT

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    src=inspect.getsource(chapter_patch.prepare)
    src=src.replace("    destinations={i['target_word']*2 for i in code if 'target_word' in i}","    assert code[-1]['opcode']==9, 'Original code must terminate before appended continuations'\n    destinations={i['target_word']*2 for i in code if 'target_word' in i}|{struct.unpack_from('<I',before,16)[0]*2}")
    old="    assert len(out)<0x78000,(number,len(out),'allocation')"
    new="    out, compaction = compact(bytes(out),changes,groups)\n    verify_layout(bytes(out),changes,groups)\n"+old
    assert src.count(old)==1;src=src.replace(old,new)
    src=src.replace("helper=inst.get('target_word');assert inst['opcode']==7 and helper in PROFILES", "helper=inst.get('target_word',-0x3052 if inst['opcode']==8 and inst['operands']==[0x3052] else None);assert (inst['opcode']==7 or helper==-0x3052) and helper in PROFILES")
    start=src.index('        hp=helper*2;')
    stop=src.index("        end+=inst['size'];",start)
    block=src[start:stop]
    src=src[:start]+"        if helper>0:\n"+''.join('    '+line+'\n' for line in block.splitlines())+"        else:\n            assert helper==-0x3052 and inst['mode']==8\n"+src[stop:]
    src=src.replace("inputs['tools/chapter_patch.py']", "inputs['tools/chapter_compiler_014.py']")
    src=src.replace("source_pool_preserved=True", "source_pool_preserved=False,live_pool_text_preserved=True")
    src=src.replace("    return packed,report,selection,checks", "    report['pool_compaction']=compaction\n    checks['pool_compaction']={k:v for k,v in compaction.items() if k!='archived_logical_changes'}\n    return packed,report,selection,checks")
    # Reuse the original instruction span before appending any overflow.
    # Each split is an instruction boundary; branches into the span were
    # already rejected by the inherited compiler's control-flow check.
    marker="        plans.append(dict(id="
    pos=src.index(marker)
    sizing="""        payload_size=sum(8*len(p)+end-tail_start for p in pages)
        if payload_size<=end-pos:
            inline_prefix=payload_size;extra_size=0
        else:
            sizes=[]
            tail_sizes=[i['size'] for i in code if tail_start<=i['offset']<end]
            for page in pages:sizes.extend([4,4]*len(page)+tail_sizes)
            boundaries=[0]
            for size in sizes:boundaries.append(boundaries[-1]+size)
            assert boundaries[-1]==payload_size
            inline_prefix=max(x for x in boundaries if x<=end-pos-4)
            extra_size=payload_size-inline_prefix+4
"""
    src=src[:pos]+sizing+src[pos:]
    src=src.replace("code_size=sum(8*len(p)+end-tail_start for p in pages)+4", "code_size=extra_size,inline_prefix_size=inline_prefix")
    src=src.replace("ref=cursor+len(emitted)", "ref=(plan['original_span'][0]+len(emitted) if len(emitted)<plan['inline_prefix_size'] else cursor+len(emitted)-plan['inline_prefix_size'])")
    old_emit="""        start,end=plan['original_span'];emitted.extend(operand_instruction(10,0,end//2));assert len(emitted)==plan['code_size']
        out[cursor:cursor+len(emitted)]=emitted;out[start:end]=operand_instruction(10,0,cursor//2)+bytes(end-start-4)"""
    new_emit="""        start,end=plan['original_span'];cut=plan['inline_prefix_size']
        if not plan['code_size']:
            assert len(emitted)==cut<=end-start
            out[start:end]=emitted+bytes(end-start-len(emitted))
        else:
            extra=emitted[cut:]+operand_instruction(10,0,end//2)
            assert len(extra)==plan['code_size']
            out[cursor:cursor+len(extra)]=extra
            out[start:end]=emitted[:cut]+operand_instruction(10,0,cursor//2)+bytes(end-start-cut-4)"""
    assert old_emit in src;src=src.replace(old_emit,new_emit)
    src=src.replace("trampoline_offset=cursor", "trampoline_offset=cursor if plan['code_size'] else None")
    src=src.replace("groups.append(group);cursor+=len(emitted)", "groups.append(group);cursor+=plan['code_size']")
    sim=inspect.getsource(chapter_patch.simulate)
    sim=sim.replace('        elif op==7:', '        elif op==7 or (op==8 and row[\'operands\']==[0x3052]):')
    sim=sim.replace("row['target_word']==2003", "row.get('target_word')==2003")
    sim=sim.replace("helper=row['target_word']", "helper=row.get('target_word',-0x3052)")
    sim=sim.replace("        if op==10:", "        if op==0:pass\n        elif op==10:")
    output='"""Version 0.1.14 compiler with verified live string compaction."""\nfrom chapter_patch import *\nfrom script_compact_014 import compact\nfrom font_metrics_014 import collect\n\n'+sim+'\n'+src
    path=ROOT/'tools/chapter_compiler_014.py'
    print(dict(mode='write' if a.write else 'dry-run',destination=str(path),changes=['Compact live string storage before allocation gate','Verify layout after compaction','Keep frozen original compiler unchanged'],sample=new))
    if a.write:path.write_text(output,encoding='utf-8')
if __name__=='__main__':main()
