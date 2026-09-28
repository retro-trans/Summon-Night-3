"""Reviewed remaining inventory labels; relocation-backed sources only."""
import json
import battle_elf_patch as patcher
from sn3_archive import ROOT

BASE=ROOT/'work/output/0.1.19'
TARGETS={0x21726c:'Key Item',0x218aa8:'None',0x218abc:'No equippable items.',
         0x218ae0:'No equippable goods.',0x21a4e8:'None',0x21e1d4:'None',0x21ef68:'None'}

def prepare():
    index=patcher.indexed_rows(); targets=[]
    for offset,text in TARGETS.items():
        row=dict(index[f'elf:ui:{offset:08x}']);row['target_full']=text;targets.append(row)
    old=patcher.BASELINE
    try:
        patcher.BASELINE=BASE/'EBOOT.elf'
        data,report=patcher.prepare(patcher.BASELINE.read_bytes(),targets,index)
    finally:patcher.BASELINE=old
    assert not report['skipped'],report['skipped']
    report['profile']='inventory_labels_020'
    return data,report

if __name__=='__main__':
    _,r=prepare();print(json.dumps({'mode':'dry-run','entries':r['entries']},indent=2))
