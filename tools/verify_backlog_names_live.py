"""Check the entire relocated name table in the isolated final ISO session."""
import argparse,json,hashlib,struct
from setup_qa import ROOT,request
from harbor_gap_qa import memory

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
    session=json.loads((ROOT/'work/scratch/setup_qa_0.1.11_final/session.json').read_text(encoding='utf-8-sig'))
    manifest=json.loads((ROOT/'work/output/0.1.11/manifest.json').read_text());expected=manifest['backlog_names']['packs'][0]
    assert session['game']==str(ROOT/'work/output/0.1.11/Summon_Night_3_EN_0.1.11.iso')
    paused=request('cpu.status')['stepping']
    if not paused:request('cpu.stepping')
    try:
        base=0x08f25800;data=bytearray(memory(base,expected['table_size']));count=struct.unpack_from('<I',data)[0];assert count==255
        refs=0
        for slot in range(count*2):
            field=4+slot*4;ptr=struct.unpack_from('<I',data,field)[0]
            if ptr:
                assert base+2044<=ptr<base+len(data)
                struct.pack_into('<I',data,field,ptr-base);refs+=1
        digest=hashlib.sha256(data).hexdigest();assert digest==expected['table_sha256']
        for c in expected['changes']:
            ptr=struct.unpack_from('<I',data,c['pointer_field'])[0];assert ptr==c['new_offset']
            assert data[ptr:ptr+len(c['display_text'])*2].decode('cp932')==c['display_text']
    finally:
        if not paused:request('cpu.resume')
    report=dict(version='0.1.11',candidate_sha256=manifest['output_sha256'],table_base=hex(base),
        bytes=len(data),records=count,rebased_pointers_checked=refs,translated_references_checked=len(expected['changes']),
        normalized_table_sha256=digest,all_bytes_match=True,method='Normalize the game\'s pointer rebasing, then compare the entire table, including strings and padding.')
    print(json.dumps(dict(mode='write' if a.write else 'dry run',**report),indent=2))
    if a.write:
        dest=ROOT/'work/ui/harbor_complete_0.1.11/runtime/name_table_validation.json';assert not dest.exists()
        dest.write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
