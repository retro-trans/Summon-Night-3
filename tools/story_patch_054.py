"""Source-bound 0.1.54 story integration, read-only preview by default.

Meaning approval is a separate, hash-bound gate. Draft previews cannot produce
an accepted compilation or game image. No historical build input is modified.
"""
import argparse,copy,json,re
from pathlib import Path
import story_compiler_054 as compiler
from chapter_source_014 import load
from chapter_patch_014 import direct_rows,PROFILES as BASE_PROFILES
from story_display_054 import profiles_for
from conditional_layout_054 import rows_for as conditional_rows_for
from story_branch485_layout_054 import expand_direct_pairs
from story_source_054 import FOLDER,target_text
from dialogue_encoding import control_tokens,encode_dialogue
from font_metrics_014 import collect
from dialogue_layout import latin_width
from stages_patch import sha,units
from sn3_archive import ROOT


def read_inputs(number, reviewed=True):
    resource,rows,data=load(number)
    scope_path=FOLDER/'scope.json';scope=json.loads(scope_path.read_text('utf8'))
    entry=next(r for r in scope['resources'] if r['resource']==number)
    assert entry['source_sha256']==resource['sha256']
    inputs={str(scope_path.relative_to(ROOT)).replace('\\','/'):sha(scope_path.read_bytes())}
    shared_path=FOLDER/'shared_library.targets.json';shared=json.loads(shared_path.read_text('utf8'))
    inputs[str(shared_path.relative_to(ROOT)).replace('\\','/')]=sha(shared_path.read_bytes())
    result={}
    for segment in entry['shared_segments']:
        for n in range(segment['start'],segment['end']):
            t=shared['translations'][str(segment['library_start']+n-segment['start'])]
            assert rows[n]['source_sha256']==t['source_sha256'],(number,n,'shared source identity')
            result[n]=dict(rows[n],text=t['text'],resource_row=n)
    draft_inputs={};new_rows=set()
    for path in sorted((FOLDER/f'{number:04d}').glob('slice_*.targets.json')):
        doc=json.loads(path.read_text('utf8'));assert doc['source_sha256']==resource['sha256']
        draft_inputs[str(path.relative_to(ROOT)).replace('\\','/')]=sha(path.read_bytes())
        for identity,t in doc['translations'].items():
            n=t['resource_row'];assert n not in result,(number,n,'overlap')
            assert identity==rows[n]['id']
            for k in ('source_sha256','source_offset','source_byte_length','reference_instructions'):
                assert t[k]==rows[n][k],(number,n,k)
            result[n]=copy.deepcopy(t);new_rows.add(n)
    inputs.update(draft_inputs)
    expected=set(range(len(rows)))-set(entry['preserved_internal_ascii_rows'])
    assert set(result)==expected,('incomplete coverage',number,len(result),len(expected),sorted(expected-set(result))[:12])
    if reviewed and new_rows:
        review_path=FOLDER/f'{number:04d}'/'accepted_review.json'
        review=json.loads(review_path.read_text('utf8'))
        assert review['semantic_complete'] is True
        assert review['reviewed_new_rows']==sorted(new_rows)
        assert review['draft_inputs_sha256']==draft_inputs
        assert not review['unresolved_blockers']
        for name,h in review['review_inputs_sha256'].items():
            assert sha((ROOT/name).read_bytes())==h
            inputs[name]=h
        for fix in review['corrections']:
            n=fix['resource_row'];assert n in new_rows and fix['source_sha256']==rows[n]['source_sha256']
            result[n]['text']=fix['text']
        inputs[str(review_path.relative_to(ROOT)).replace('\\','/')]=sha(review_path.read_bytes())
    # Naming normalization follows any meaning-review corrections.
    for n,t in result.items():
        r=rows[n];original=data[r['source_offset']:r['source_offset']+r['source_byte_length']].decode('cp932')
        t['text']=target_text(t['text'])
        assert control_tokens(t['text'])==control_tokens(original),(number,n,'controls')
        assert not re.search('[\u3040-\u30ff\u3400-\u9fff]',t['text']),(number,n,'Japanese target')
        if t['text']:encode_dialogue(t['text'],original)
    for filename in ('tools/story_patch_054.py','tools/story_compiler_054.py','tools/conditional_layout_054.py','tools/story_branch485_layout_054.py','tools/story_source_054.py','tools/chapter_patch_014.py','tools/chapter_source_014.py','tools/script_compact_014.py','tools/story_storage_054.py','tools/font_metrics_014.py','tools/night_talk_037.py','work/glossary/character_reference_sn6_vita.json','work/glossary/terminology_preferences.json'):
        inputs[filename]=sha((ROOT/filename).read_bytes())
    inputs['tools/story_display_054.py']=sha((ROOT/'tools/story_display_054.py').read_bytes())
    return resource,rows,data,result,inputs


def prepare(number,reviewed=True):
    resource,rows,data,translated,inputs=read_inputs(number,reviewed)
    metrics=copy.deepcopy(collect()[0]['characters'])
    for c,advance in [('▲',128),('●',96),('■',128),('♪',16),('　',6)]:metrics[c]={'proposed_advance_pixels':advance}
    translated=expand_direct_pairs(number,rows,data,translated,metrics)
    profiles=profiles_for(number,data,BASE_PROFILES)
    direct=direct_rows(rows,data,translated,profiles)
    direct-=conditional_rows_for(number)
    for n in direct:
        text=translated[n]['text']
        assert text and units(text)<=31 and latin_width(text,metrics)<=208,('conditional/menu text too wide',number,n,text,units(text),latin_width(text,metrics))
    saved={k:getattr(compiler,k) for k in ('chapter_source','load_targets','DIRECT','PROFILES')}
    try:
        compiler.chapter_source=lambda _:(resource,rows,data)
        compiler.load_targets=lambda *args:(translated,inputs)
        compiler.DIRECT={number:direct};compiler.PROFILES=profiles
        packed,report,selection,checks=compiler.prepare(number,reviewed)
    finally:
        for k,v in saved.items():setattr(compiler,k,v)
    checks.update(meaning_review_verified=reviewed,conditional_or_menu_rows=len(direct),night_talk_groups=sum(g['max_lines_per_page']==2 for g in report['layout_groups']))
    return packed,report,selection,checks


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('resources',type=int,nargs='+')
    parser.add_argument('--draft-preview',action='store_true')
    args=parser.parse_args()
    for n in args.resources:
        _,_,_,checks=prepare(n,not args.draft_preview)
        print(json.dumps(dict(mode='read-only draft preview' if args.draft_preview else 'read-only accepted preview',**checks),ensure_ascii=False,indent=2),flush=True)
