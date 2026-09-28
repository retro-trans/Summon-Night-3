"""Decode compressed portrait-pack candidates using validated obfuscated-LZ headers."""
import argparse,json,hashlib
from sn3_archive import ROOT,GameSource,parse_index,child
from sn3_codec import decompress
from sn3_ui_textures import texture_records,decode_texture,export

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packs',default='900,1000,1100');p.add_argument('--write',action='store_true');p.add_argument('--names-only',action='store_true');a=p.parse_args()
    records=[];images=[];resources=[]
    with GameSource() as s:
        numbers=range(*[int(x) for x in a.packs.split('-')]) if '-' in a.packs else map(int,a.packs.split(','))
        seen={}
        for n in numbers:
            raw=s.resource('02.DAT',n);matches=[]
            if len(raw)<5:continue
            for high in ([0x17] if a.names_only else range(256)):
                key=high*256+(raw[0]^raw[3])
                try:
                    d,used=decompress(raw,key,4000000)
                    if any(raw[used:]):continue
                    ix=parse_index(d,len(d));matches.append((key,d,ix))
                except ValueError:continue
            if not matches and a.names_only:continue
            assert len(matches)==1,(n,len(matches));key,d,ix=matches[0]
            resources.append(dict(pack=n,key=hex(key),decoded_bytes=len(d),children=ix['count'],source_sha256=hashlib.sha256(raw).hexdigest()))
            for e in ix['entries']:
                if a.names_only and e['id'] not in (3,4):continue
                data=child(d,ix,e['id'])
                try:rows=texture_records(data)
                except ValueError:continue
                for row in rows:
                    if a.names_only and (row['width'],row['height'])!=(144,32):continue
                    try:im=decode_texture(data,row)
                    except ValueError:continue
                    name=f"02_{n:05d}_{e['id']:05d}_{row['number']:03d}.png"
                    rec=dict(id=f"02:{n:05d}/{e['id']:05d}:{row['number']}",image_file=name,**row)
                    if a.names_only:
                        digest=hashlib.sha256(data).hexdigest();occ=dict(pack=n,child=e['id'],sprite=row['number'],key=hex(key),source_sha256=digest)
                        if digest in seen:seen[digest]['occurrences'].append(occ);continue
                        rec['occurrences']=[occ];seen[digest]=rec
                    records.append(rec);images.append((rec,im))
    dest=ROOT/'work/ui/nameplates_0.1.10'/('packs_'+a.packs.replace(',','_')+('_names' if a.names_only else ''))
    report=dict(resources=resources,textures=records,skipped=[])
    print(json.dumps(dict(mode='write' if a.write else 'dry run',destination=str(dest),resources=resources,
        images=[dict(id=r['id'],size=im.size) for r,im in images]),indent=2))
    if a.write:export(dest,report,images)

if __name__=='__main__':main()
