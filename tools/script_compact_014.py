"""Compact only VM string storage; prove every live operand retains its bytes."""
from copy import deepcopy
from script_strings import parse_pool
from sn3_vm import instructions
from dialogue_layout import operand_instruction


def compact(data, changes, groups):
    parsed = parse_pool(data)
    pool = parsed['pool_offset']
    by_word = {r['pool_word_offset']:r for r in parsed['strings']}
    out = bytearray(data[:pool] + b'\0\0')
    unique = {b'': 0}; remap = {0:0}; offsets = {}
    before = instructions(data)
    for inst in before:
        if 'string_word' not in inst: continue
        word = inst['string_word']
        if word not in remap:
            r=by_word[word]
            raw=data[r['source_offset']:r['source_offset']+r['source_byte_length']]
            if raw not in unique:
                unique[raw]=(len(out)-pool)//2
                out.extend(raw+b'\0\0')
                out.extend(bytes(len(out)%2))
            remap[word]=unique[raw]
            offsets[r['source_offset']]=pool+remap[word]*2
        p=inst['offset']
        out[p:p+4]=operand_instruction(5,4,remap[word])
    after=instructions(out)
    assert len(before)==len(after)
    new_parsed=parse_pool(out)
    new_words={r['pool_word_offset']:r for r in new_parsed['strings']}
    def raw_at(blob, rows, word):
        if word==0:return b''
        r=rows[word]
        return blob[r['source_offset']:r['source_offset']+r['source_byte_length']]
    for a,b in zip(before,after):
        if 'string_word' not in a: assert a==b
        else:
            assert (a['offset'],a['size'],a['opcode'],a['mode'])==(b['offset'],b['size'],b['opcode'],b['mode'])
            assert raw_at(data,by_word,a['string_word'])==raw_at(out,new_words,b['string_word'])
    assert data[:32]==out[:32]
    archived=[];live=[]
    for record in changes:
        if not record['reference_instructions']:
            archived.append(deepcopy(record))
            continue
        live.append(record)
    changes[:]=live
    new_by_offset={r['source_offset']:r for r in new_parsed['strings']}
    records=changes+[r for g in groups for p in g['pages'] for r in p]
    for r in records:
        old=r['new_offset'];new=offsets[old]
        r['new_offset']=new;r['pool_word_offset']=(new-pool)//2
        # Multiple display fragments may now share one immutable byte string.
        r['owned_reference_instructions']=r['reference_instructions']
        r['reference_instructions']=new_by_offset[new]['reference_instructions']
    return out,dict(before_bytes=len(data),after_bytes=len(out),saved_bytes=len(data)-len(out),live_string_references=sum('string_word' in i for i in before),unique_live_strings=len(unique),all_live_string_bytes_preserved=True,all_non_string_instructions_preserved=True,archived_logical_changes=archived)
