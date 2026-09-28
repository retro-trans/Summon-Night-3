"""Validate resource 134 slice metadata and source-token preservation."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5];sys.path.insert(0,str(ROOT/'tools'))
from chapter_source import chapter_source
from dialogue_encoding import control_tokens,encode_dialogue
_,rows,data=chapter_source(134);folder=Path(__file__).parent;seen=set()
for start in range(160,960,80):
 doc=json.loads((folder/f'slice_{start:04d}.targets.json').read_text(encoding='utf-8'))
 assert doc['assigned_range']==[start,start+79]
 assert len(doc['translations'])==80
 for t in doc['translations'].values():
  n=t['resource_row'];r=rows[n];s=data[r['source_offset']:r['source_offset']+r['source_byte_length']].decode('cp932')
  assert start<=n<=start+79 and n not in seen
  assert all(t[k]==r[k] for k in ('id','source_sha256','source_offset','source_byte_length','reference_instructions'))
  assert control_tokens(t['text'])==control_tokens(s);encode_dialogue(t['text'],s)
  assert not any(old in t['text'] for old in ('Sonora','Belfrau','Cunnon','Galleor','Ardyllia','Salome'))
  seen.add(n)
assert seen==set(range(160,960))
print(json.dumps({'validated_rows':len(seen),'slices':10,'range':[min(seen),max(seen)]}))
