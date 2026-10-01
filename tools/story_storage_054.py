"""0.1.54-only pool packing: share identical, aligned CP932 suffixes.

The VM reads a pointer at pool + word*2 (docs/SCRIPT_FORMAT.md).
No code addresses, glyph bytes, terminators, or display sequences are changed.
Historical compilers and their strict physical-string index remain unchanged.
"""
from bisect import bisect_right
from copy import deepcopy
import hashlib,struct
from script_strings import SCRIPT_PREFIX,JAPANESE
from sn3_vm import instructions,verify_script
from dialogue_layout import operand_instruction


def parse_pool(data):
    if len(data)<32 or data[:12]!=SCRIPT_PREFIX:raise ValueError('Unrecognized script header')
    variant,entry,pool_word,r1,r2=struct.unpack_from('<5I',data,12);pool=pool_word*2
    if variant not in (0x1010,0x1020) or r1 or r2 or not 32<=pool<len(data) or data[pool:pool+2]!=b'\0\0':raise ValueError('Invalid header or pool')
    physical=[];cursor=pool
    while cursor<len(data):
        if not data[cursor]:cursor+=1;continue
        if cursor%2:raise ValueError('Unaligned physical string')
        end=data.index(b'\0',cursor);raw=data[cursor:end];raw.decode('cp932','strict')
        if any(b<32 for b in raw):raise ValueError('Raw control byte')
        physical.append((cursor,end));cursor=end+1
    starts=[a for a,b in physical];ends=dict(physical);offsets=set(starts)
    for inst in instructions(data):
        if 'string_word' not in inst or not inst['string_word']:continue
        offset=pool+inst['string_word']*2;i=bisect_right(starts,offset)-1
        if i<0 or offset>=physical[i][1]:raise ValueError('String pointer outside physical text')
        start,end=physical[i]
        # A CP932 character must not be entered at its second byte.
        data[start:offset].decode('cp932','strict');data[offset:end].decode('cp932','strict')
        ends[offset]=end;offsets.add(offset)
    rows=[]
    for offset in sorted(offsets):
        end=ends[offset];raw=data[offset:end];text=raw.decode('cp932')
        rows.append(dict(source_offset=offset,pool_word_offset=(offset-pool)//2,source_byte_length=len(raw),source_sha256=hashlib.sha256(raw).hexdigest(),contains_japanese=bool(JAPANESE.search(text))))
    verified=verify_script(data,rows)
    for row in rows:row['reference_instructions']=verified['references'][row['pool_word_offset']]
    return dict(pool_offset=pool,strings=rows,vm_statistics={k:v for k,v in verified.items() if k!='references'})


def compact(data,changes,groups):
    parsed=parse_pool(data);pool=parsed['pool_offset'];by_word={r['pool_word_offset']:r for r in parsed['strings']};before=instructions(data)
    used={i['string_word'] for i in before if 'string_word' in i and i['string_word']}
    raw_by_word={w:bytes(data[by_word[w]['source_offset']:by_word[w]['source_offset']+by_word[w]['source_byte_length']]) for w in used}
    out=bytearray(data[:pool]+b'\0\0');suffixes={};locations={b'':0};suffix_count=0
    unique=sorted(set(raw_by_word.values()),key=lambda b:(-len(b),b))
    standard_size=pool+2+sum(len(raw)+2+len(raw)%2 for raw in unique)
    for raw in unique:
        if raw in suffixes:locations[raw]=suffixes[raw];suffix_count+=1;continue
        word=(len(out)-pool)//2;locations[raw]=word
        out.extend(raw+b'\0\0');out.extend(bytes(len(out)%2))
        for offset in range(0,len(raw),2):
            try:raw[:offset].decode('cp932','strict');raw[offset:].decode('cp932','strict')
            except UnicodeDecodeError:continue
            suffixes.setdefault(raw[offset:],word+offset//2)
    remap={0:0,**{w:locations[raw] for w,raw in raw_by_word.items()}}
    offsets={by_word[w]['source_offset']:pool+remap[w]*2 for w in used}
    for inst in before:
        if 'string_word' in inst:out[inst['offset']:inst['offset']+4]=operand_instruction(5,4,remap[inst['string_word']])
    after=instructions(out);new_parsed=parse_pool(out);new_words={r['pool_word_offset']:r for r in new_parsed['strings']}
    assert len(before)==len(after) and data[:32]==out[:32]
    for a,b in zip(before,after):
        if 'string_word' not in a:assert a==b
        else:
            assert (a['offset'],a['size'],a['opcode'],a['mode'])==(b['offset'],b['size'],b['opcode'],b['mode'])
            old=raw_by_word.get(a['string_word'],b'');offset=pool+b['string_word']*2
            assert out[offset:offset+len(old)]==old and out[offset+len(old):offset+len(old)+2]==b'\0\0'
    archived=[];live=[]
    for r in changes:
        (live if r['reference_instructions'] else archived).append(r if r['reference_instructions'] else deepcopy(r))
    changes[:]=live;new_offsets={r['source_offset']:r for r in new_parsed['strings']}
    for r in changes+[r for g in groups for page in g['pages'] for r in page]:
        new=offsets[r['new_offset']];r['new_offset']=new;r['pool_word_offset']=(new-pool)//2
        r['owned_reference_instructions']=r['reference_instructions'];r['reference_instructions']=new_offsets[new]['reference_instructions']
    return out,dict(before_bytes=len(data),after_bytes=len(out),saved_bytes=len(data)-len(out),exact_dedup_bytes=standard_size,suffix_saved_bytes=standard_size-len(out),suffix_shared_strings=suffix_count,live_string_references=sum('string_word' in i for i in before),unique_live_strings=len(unique)+1,all_live_string_bytes_preserved=True,all_non_string_instructions_preserved=True,archived_logical_changes=archived)


def verify_layout(data,changes,groups):
    parsed=parse_pool(data);by_offset={r['source_offset']:r for r in parsed['strings']}
    for r in changes+[r for g in groups for page in g['pages'] for r in page]:
        row=by_offset[r['new_offset']];end=r['new_offset']+r['new_byte_length']
        assert row['reference_instructions']==r['reference_instructions']
        assert data[r['new_offset']:end].decode('cp932')==r['display_text'] and data[end:end+2]==b'\0\0'
    for g in groups:
        assert g['layout_profile'] in ('story_expanded_tokens_054','story_conditional_expanded_054')
        if g['layout_profile']=='story_conditional_expanded_054':
            assert len(g['branches'])==2
            for branch in g['branches']:
                assert ' '.join(r['text'] for page in branch['pages'] for r in page)==branch['text']
        else:
            assert ' '.join(r['text'] for page in g['pages'] for r in page)==g['text']
        assert all(1<=len(page)<=g['max_lines_per_page'] for page in g['pages'])
        assert all(len(r['display_text'])<=g['max_display_units'] for page in g['pages'] for r in page)
