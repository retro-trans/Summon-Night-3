"""Read-only structural checks across available new chapter drafts."""
import argparse,json
from chapter_patch_014 import prepare,FOLDER

def main():
    p=argparse.ArgumentParser();p.add_argument('resources',type=int,nargs='*');p.add_argument('--partial',action='store_true');a=p.parse_args()
    numbers=a.resources or [int(p.name) for p in FOLDER.iterdir() if p.is_dir() and p.name.isdigit() and int(p.name) not in (134,157,180,203,226)]
    failed=[];rows=0
    for n in sorted(numbers):
        try:
            _,r,_,c=prepare(n,False,a.partial);rows+=c['covered_source_rows']
            print(json.dumps(dict(resource=n,rows=c['covered_source_rows'],bytes=r['decoded_size'],pages=c['pages'],saved=c['pool_compaction']['saved_bytes'])),flush=True)
        except Exception as e:failed.append((n,str(e)));print(json.dumps(dict(resource=n,error=str(e))),flush=True)
    print(json.dumps(dict(resources=len(numbers),covered_rows=rows,failures=failed)),flush=True)
    if failed:raise SystemExit(1)
if __name__=='__main__':main()
