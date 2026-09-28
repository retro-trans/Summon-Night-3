"""Add the independently checked island-cast spelling; preview by default."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args()
root=Path(__file__).resolve().parents[1]
path=root/'work/glossary/chapter_terms_0.1.12.json'
doc=json.loads(path.read_text(encoding='utf-8'))
entry=dict(source_name='フレイズ',target_name='Phlaiz',category='character',status='wiki_verified',
 gender=None,gender_status='Not established in the checked roster; do not infer from the name.',
 nickname=None,personality='Not established in the checked roster.',
 role="Falzen's advisor in the Realm of In Between; introduced in Chapter 3.",
 evidence=[dict(url='https://summonnight.fandom.com/wiki/Summon_Night_3/PSP_Gallery',supports=['English roster spelling']),
 dict(url='https://summonnight.fandom.com/wiki/Summon_Night_3',supports=['Realm of In Between affiliation'])],
 notes='Replaces the draft Freize spelling after independent meaning review.',checked_on='2026-09-27')
assert not any(e['source_name']==entry['source_name'] for e in doc['entries'])
print(json.dumps(dict(mode='write' if a.write else 'dry run',addition=entry),indent=2))
if a.write:
 doc['entries'].append(entry);path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
