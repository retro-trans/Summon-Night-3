"""Materialize English night-talk drafts in 80-row slices; preview by default."""
import argparse, hashlib, json
from pathlib import Path
from chapter_source import chapter_source
from dialogue_encoding import control_tokens, encode_dialogue
from sn3_archive import ROOT

FOLDER = ROOT / 'work/translation/en/chapters_0.1.14'

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', default=str(FOLDER / 'night_drafts.json'))
    p.add_argument('--write', action='store_true')
    a = p.parse_args()
    drafts = json.loads(Path(a.input).read_text(encoding='utf-8'))
    for number, draft in drafts.items():
        number = int(number)
        resource, rows, data = chapter_source(number)
        start = draft['start']; texts = draft['texts']
        assert start == 11 and len(texts) == len(rows) - start, (number, len(texts), len(rows)-start)
        for base in range(start, len(rows), 80):
            translations = {}
            for n in range(base, min(base+80, len(rows))):
                r = rows[n]; text = texts[n-start]
                original = data[r['source_offset']:r['source_offset']+r['source_byte_length']].decode('cp932')
                assert control_tokens(text) == control_tokens(original), (number,n)
                if text: encode_dialogue(text,original)
                translations[r['id']] = dict(resource_row=n, **{k:r[k] for k in ('source_sha256','source_offset','source_byte_length','reference_instructions')}, text=text)
            doc = dict(resource_id=resource['id'], assigned_range=[base,min(base+79,len(rows)-1)], rows_in_slice=len(translations), rows_examined=draft['rows_examined'], context_range=draft['context_range'], status='translated_self_checked_pending_independent_review', uncertainties=draft.get('uncertainties',[]), translations=translations)
            dest = FOLDER / f'{number:04d}' / f'slice_{base:04d}.targets.json'
            print(json.dumps(dict(resource=number,rows=doc['assigned_range'],mode='write' if a.write else 'dry-run',sample=list(translations.values())[:2]),ensure_ascii=False))
            if a.write:
                dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__ == '__main__': main()
