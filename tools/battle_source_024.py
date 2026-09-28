"""Read bounded battle dialogue slices, without saving source transcripts."""
import argparse,json,hashlib
from functools import lru_cache
from sn3_archive import ROOT,GameSource

def sha(data):return hashlib.sha256(data).hexdigest()

@lru_cache(None)
def catalog():
    return json.loads((ROOT/'work/translation/en/script_strings.index.json').read_text(encoding='utf8'))

def load(number):
    r=next(r for r in catalog()['resources'] if r['bank']=='01.DAT' and r['path']==[number,1])
    with GameSource() as source:data=source.read(r['bank'],r['offset'],r['size'])
    assert sha(data)==r['sha256'] and r['compression'] is None
    rows=sorted(r['strings'],key=lambda x:min(x['reference_instructions']))
    return r,rows,data

def ordered():
    result=[]
    for r in catalog()['resources']:
        if r['bank']=='01.DAT' and r['strings'] and r['path'][0]<175:
            for n,row in enumerate(sorted(r['strings'],key=lambda x:min(x['reference_instructions']))):
                result.append(dict(row,resource=r['path'][0],resource_row=n,ordered_index=len(result)))
    return result

def source_text(row,data):
    b=data[row['source_offset']:row['source_offset']+row['source_byte_length']]
    assert sha(b)==row['source_sha256']
    return b.decode('cp932')

def main():
    p=argparse.ArgumentParser();p.add_argument('--start',type=int,default=0);p.add_argument('--count',type=int,default=80);p.add_argument('--resource',type=int);a=p.parse_args()
    rows=ordered() if a.resource is None else load(a.resource)[1]
    for n in range(a.start,min(a.start+a.count,len(rows))):
        row=rows[n];number=a.resource if a.resource is not None else row['resource']
        print(n,row['id'],source_text(row,load(number)[2]))

if __name__=='__main__':main()
