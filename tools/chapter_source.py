"""Resolve chapter source rows transiently; never persist Japanese transcripts."""
import argparse,hashlib,json
from functools import lru_cache
from sn3_archive import ROOT,GameSource
from sn3_codec import decompress
def sha(b):return hashlib.sha256(b).hexdigest()
@lru_cache(maxsize=1)
def index():return json.loads((ROOT/'work/translation/en/script_strings.index.json').read_text())
def chapter_source(number):
    resource=next(r for r in index()['resources'] if r['id']==f'00:{number:05d}')
    with GameSource() as source:raw=source.resource('00.DAT',number)
    assert sha(raw)==resource['sha256']
    data=decompress(raw,0xa695)[0] if resource['compression'] else raw
    if resource['compression']:assert sha(data)==resource['compression']['decoded_sha256']
    ordered=sorted(resource['strings'],key=lambda r:min(r['reference_instructions']))
    common=next(r for r in index()['resources'] if r['id']=='00:00065')
    prefix=sorted(common['strings'],key=lambda r:min(r['reference_instructions']))[:1808]
    skip=0
    for a,b in zip(ordered,prefix):
        if a['source_sha256']!=b['source_sha256'] or a['reference_instructions']!=b['reference_instructions']:break
        skip+=1
    # Main scripts carry the entire identical shared library. Smaller scripts
    # may carry none or a shorter library; uncertain partial matches stay visible.
    if skip!=1808:skip=0
    rows=ordered[skip:]
    for r in rows:assert sha(data[r['source_offset']:r['source_offset']+r['source_byte_length']])==r['source_sha256']
    return resource,rows,data
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('resource',type=int);p.add_argument('--start',type=int,default=0);p.add_argument('--count',type=int,default=100);a=p.parse_args()
    resource,rows,data=chapter_source(a.resource)
    print(json.dumps(dict(resource=resource['id'],row_count=len(rows),shared_prefix_skipped=len(resource['strings'])-len(rows))))
    for n in range(a.start,min(a.start+a.count,len(rows))):
        r=rows[n];print(n,r['id'],r['reference_instructions'],data[r['source_offset']:r['source_offset']+r['source_byte_length']].decode('cp932'))
if __name__=='__main__':main()
