"""Read source transiently and bind new English story slices to exact identities."""
import argparse,json,re
from pathlib import Path
from chapter_source_014 import load,ROOT
from chapter_patch_014 import normalize
from dialogue_encoding import control_tokens,encode_dialogue
from stages_patch import sha
FOLDER=ROOT/'work/translation/en/story_0.1.54'

def target_text(text):
    text=normalize(text)
    return re.sub(r'\b[Pp]rofessor\b',lambda m:'Teacher' if m[0][0].isupper() else 'teacher',text)

def save(number,start,lines,examined,notes='', *, write=False, uncertainties=None, omissions=None):
    resource,rows,data=load(number)
    assert 0<=start<start+len(lines)<=len(rows)
    assert len(lines)==80 or start+len(lines)==len(rows), 'Use 80 consecutive rows except at resource end'
    assert uncertainties is not None and omissions is not None, 'Explicit uncertainty and omission lists required'
    examined_rows={n for lo,hi in examined for n in range(lo,hi+1)}
    assert set(range(start,start+len(lines)))<=examined_rows
    assert start==0 or start-1 in examined_rows, 'Read preceding context'
    assert start+len(lines)==len(rows) or start+len(lines) in examined_rows, 'Read following context'
    targets={}
    for n,text in enumerate(lines,start):
        row=rows[n];source=data[row['source_offset']:row['source_offset']+row['source_byte_length']].decode('cp932')
        text=target_text(text)
        assert not re.search('[\u3040-\u30ff\u3400-\u9fff]',text),(number,n,text)
        assert control_tokens(text)==control_tokens(source),(number,n,control_tokens(source),text)
        if '♪' in source and '♪' not in text:text+=' ♪'
        if text:encode_dialogue(text,source)
        targets[row['id']]=dict(row,resource_row=n,text=text,status='translated_author_self_check')
    path=FOLDER/f'{number:04d}'/f'slice_{start:04d}.targets.json'
    assert not path.exists(),path
    doc=dict(resource_id=resource['id'],range_inclusive=[start,start+len(lines)-1],source_sha256=resource['sha256'],review_status='author self-check; no independent meaning review',source_ranges_examined=examined,rows_examined=len(examined_rows),rows_in_slice=len(lines),uncertainties=uncertainties,preserved_source_omissions=omissions,notes=notes,translations=targets)
    print(json.dumps(dict(mode='write' if write else 'dry-run',destination=str(path),range=doc['range_inclusive'],rows_examined=len(examined_rows),rows_in_slice=len(lines),samples={str(n):targets[rows[n]['id']]['text'] for n in sorted({start,start+len(lines)//2,start+len(lines)-1})},uncertainties=uncertainties,preserved_source_omissions=omissions),ensure_ascii=False,indent=2))
    if not write:return doc
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(f'Saved {number}: {start}-{start+len(lines)-1} ({len(lines)} fragments)')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('resource',type=int);p.add_argument('--start',type=int,default=0);p.add_argument('--count',type=int,default=100);a=p.parse_args()
    resource,rows,data=load(a.resource)
    print(resource['id'],len(rows),'fragments')
    for n in range(a.start,min(len(rows),a.start+a.count)):
        row=rows[n];print(n,data[row['source_offset']:row['source_offset']+row['source_byte_length']].decode('cp932'))
