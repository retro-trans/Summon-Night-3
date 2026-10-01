"""The one verified expanded-layout exception for story resource 393.

This is deliberately data-shaped: it accepts only the known two-way branch and
does not make conditional dialogue generally pageable.
"""
import struct

from dialogue_encoding import control_tokens, encode_dialogue
from dialogue_layout import latin_width, operand_instruction
from stages_patch import sha, units, wrap


RESOURCE = 393
ROWS = frozenset((112, 113, 114))
FALSE_JUMP = 12628
TRUE_PREFIX = 12632
TRUE_APPEND = 12636
TRUE_COMMON_JUMP = 12640
FALSE_PREFIX = 12644
FALSE_APPEND = 12648
COMMON_PREFIX = 12652
COMMON_APPEND = 12656
ARGUMENT = 12660
HELPER = 12664
RETURN = 12668


def rows_for(number):
    return ROWS if number == RESOURCE else frozenset()


def _same(row, *, opcode, mode, target=None):
    return row['opcode'] == opcode and row['mode'] == mode and (target is None or row.get('target_word') == target)


def detect(number, rows, translated, before, at, destinations, metrics):
    """Validate the source branch and return its two independent page plans."""
    if number != RESOURCE:
        return None
    assert ROWS <= set(translated), ('conditional rows missing', number, sorted(ROWS-set(translated)))
    assert [rows[n]['reference_instructions'] for n in sorted(ROWS)] == [[TRUE_PREFIX], [FALSE_PREFIX], [COMMON_PREFIX]]
    assert _same(at[FALSE_JUMP], opcode=12, mode=0, target=FALSE_PREFIX//2)
    assert _same(at[TRUE_PREFIX], opcode=5, mode=4)
    assert _same(at[TRUE_APPEND], opcode=7, mode=1, target=2003)
    assert _same(at[TRUE_COMMON_JUMP], opcode=10, mode=0, target=COMMON_PREFIX//2)
    assert _same(at[FALSE_PREFIX], opcode=5, mode=4)
    assert _same(at[FALSE_APPEND], opcode=7, mode=1, target=2003)
    assert _same(at[COMMON_PREFIX], opcode=5, mode=4)
    assert _same(at[COMMON_APPEND], opcode=7, mode=1, target=2003)
    assert _same(at[ARGUMENT], opcode=5, mode=9)
    assert _same(at[HELPER], opcode=7, mode=1, target=2100)
    entrances={d for d in destinations if TRUE_PREFIX <= d < RETURN}
    assert entrances == {FALSE_PREFIX, COMMON_PREFIX}, ('unexpected conditional branch entrance', sorted(entrances))
    incoming=[(row['offset'],row['opcode'],row['mode'],row['target_word']*2) for row in at.values()
              if 'target_word' in row and TRUE_PREFIX <= row['target_word']*2 < RETURN]
    assert incoming == [(FALSE_JUMP,12,0,FALSE_PREFIX),(TRUE_COMMON_JUMP,10,0,COMMON_PREFIX)], ('unexpected conditional branch origin',incoming)
    entrypoint=struct.unpack_from('<I',before,16)[0]*2
    assert not TRUE_PREFIX <= entrypoint < RETURN, ('conditional branch is script entrypoint',entrypoint)
    # The displayed common continuation is intentionally copied into each path.
    paths=((True, (112, 114)), (False, (113, 114)))
    branches=[]
    for selected, resource_rows in paths:
        for n in resource_rows:
            source=before[rows[n]['source_offset']:rows[n]['source_offset']+rows[n]['source_byte_length']]
            assert sha(source)==rows[n]['source_sha256'], ('conditional source identity',number,n)
        original=simulate(before,at,FALSE_JUMP,RETURN,selected)
        expected=[before[rows[n]['source_offset']:rows[n]['source_offset']+rows[n]['source_byte_length']].decode('cp932') for n in resource_rows]
        assert len(original)==1 and original[0]['helper']==2100 and original[0]['args']==[200]
        assert original[0]['lines']==expected, ('conditional path/source mismatch',selected,original[0]['lines'],expected)
        text=' '.join(translated[n]['text'] for n in resource_rows if translated[n]['text'])
        assert text.strip(), ('empty conditional dialogue', number, resource_rows)
        lines=wrap(text,280,metrics)
        pages=[lines[i:i+3] for i in range(0,len(lines),3)]
        for page in pages:
            assert sum(units(line) for line in page)<=192
            assert all(units(line)<=31 and latin_width(line,metrics)<=280 for line in page)
        branches.append(dict(condition=selected,resource_rows=list(resource_rows),text=text,page_texts=pages))
    return dict(id='story_393_conditional_112_113_114',resource_rows=sorted(ROWS),source_offsets=[rows[n]['source_offset'] for n in sorted(ROWS)],original_span=[FALSE_JUMP,RETURN],original_span_sha256=sha(before[FALSE_JUMP:RETURN]),prefix_entries=[TRUE_PREFIX,FALSE_PREFIX],tail=before[ARGUMENT:RETURN],display_helper_word=2100,original_helper_arguments=before[ARGUMENT:HELPER],branches=branches,measured_pixel_limit=280,max_lines=3)


def emit(plan, out, new_pool, cursor):
    """Append the true and false page sequences and return report page records."""
    block=bytearray();branch_reports=[]
    for branch in plan['branches']:
        start=cursor+len(block);pages=[]
        for pi,texts in enumerate(branch['page_texts']):
            fragments=[]
            for li,text in enumerate(texts):
                encoded,display=encode_dialogue(text,''.join(control_tokens(text)))
                offset=len(out);word=(offset-new_pool)//2;out.extend(encoded+b'\0\0')
                ref=cursor+len(block)
                block.extend(operand_instruction(5,4,word)+operand_instruction(7,1,2003))
                fragments.append(dict(id=f"{plan['id']}:{str(branch['condition']).lower()}:page:{pi}:line:{li}",text=text,display_text=display,new_offset=offset,new_byte_length=len(encoded),pool_word_offset=word,reference_instructions=[ref],expanded_units=units(text)))
            block.extend(plan['tail']);pages.append(fragments)
        block.extend(operand_instruction(10,0,RETURN//2))
        branch_reports.append(dict(condition=branch['condition'],text=branch['text'],entry_instruction=start,pages=pages))
    assert len(branch_reports)==2
    return bytes(block),branch_reports


def simulate(data, at, start, stop, condition):
    """Execute one original or rewritten path, retaining only helper calls."""
    pool=struct.unpack_from('<I',data,20)[0]*2
    pc=start;stack=['sentinel'];pending=[];pages=[];steps=0
    while pc != stop:
        steps+=1;assert steps<2000
        row=at[pc];pc+=row['size'];op=row['opcode'];mode=row['mode']
        if op == 12:
            if not condition: pc=row['target_word']*2
        elif op == 10: pc=row['target_word']*2
        elif op == 5:
            if mode == 4:
                offset=pool+row['string_word']*2;end=offset
                while data[end:end+2] != b'\0\0':end+=2
                stack.append(data[offset:end].decode('cp932'))
            elif mode in (5,9):
                value=(row['high']<<16)|row['operands'][0];stack.append(value-65536 if mode==9 and value>=32768 else value)
            elif mode == 10: stack.append(row['high']-1)
            elif mode == 2: stack.append(('local',row['high'],tuple(row['operands'])))
            else: raise AssertionError(('push',row))
        elif op == 7:
            args=stack[-mode:] if mode else []
            if mode: del stack[-mode:]
            if row.get('target_word') == 2003:
                assert len(args)==1 and isinstance(args[0],str);pending.append(args[0])
            else:
                assert pending;pages.append(dict(helper=row['target_word'],args=args,lines=pending));pending=[]
        else: raise AssertionError(('opcode',row))
    assert stack == ['sentinel'] and not pending
    return pages


def verify(plan, before, old_at, out, new_at, report_branches):
    """Prove each branch still calls the same helper with the same arguments."""
    for branch in report_branches:
        condition=branch['condition']
        old=simulate(before,old_at,FALSE_JUMP,RETURN,condition)
        new=simulate(out,new_at,FALSE_JUMP,RETURN,condition)
        assert len(old)==1 and len(new)==len(branch['pages'])
        for page,expected in zip(new,branch['pages']):
            assert page['helper']==old[0]['helper']==plan['display_helper_word']
            assert page['args']==old[0]['args']
            assert page['lines']==[line['display_text'] for line in expected]
