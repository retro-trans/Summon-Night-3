"""Map Chapter 2/3 script-scope candidates without exporting dialogue text.

Run without --write to preview the compact metadata document.  The document
contains identifiers, counts, hashes, reference ranges, and structural hints;
it deliberately contains no source dialogue.
"""
import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from sn3_archive import GameSource, ROOT
from sn3_codec import decompress
from script_repack import instructions


INDEX = ROOT / 'work/translation/en/script_strings.index.json'
OUTPUT = ROOT / 'docs/chapter23_scope_draft.json'
PREFIX_ROWS = 1808


def digest(value):
    return hashlib.sha256(value).hexdigest()


def ordered_rows(resource):
    return sorted(resource['strings'], key=lambda row: min(row['reference_instructions']))


def compact_ranges(values):
    if not values:
        return []
    output = []
    start = previous = values[0]
    for value in values[1:]:
        if value == previous + 1:
            previous = value
        else:
            output.append([start, previous])
            start = previous = value
    output.append([start, previous])
    return output


def resource_runtime_profile(source, resource):
    """Return control-flow metadata only; decoded source text is never stored."""
    raw = source.resource(resource['bank'], resource['path'][0])
    decoded = decompress(raw, int(resource['compression']['key'], 16))[0]
    code = {item['offset']: item for item in instructions(decoded)}
    immediate_next_calls = Counter()
    queue_pushes = 0
    string_references = 0
    for row in resource['strings']:
        for reference in row['reference_instructions']:
            string_references += 1
            following = code.get(reference + 4)
            if following and following['opcode'] == 7:
                helper = following.get('target_word')
                if helper is not None:
                    immediate_next_calls[str(helper)] += 1
                    if helper == 2003:
                        queue_pushes += 1
    return {
        'decoded_sha256': digest(decoded),
        'string_reference_count': string_references,
        'immediate_call_after_string_reference': dict(sorted(immediate_next_calls.items(), key=lambda pair: int(pair[0]))),
        'queue_push_2003_references': queue_pushes,
    }


def main_scope(label, resource):
    rows = ordered_rows(resource)
    prefix = rows[:PREFIX_ROWS]
    tail = rows[PREFIX_ROWS:]
    return {
        'chapter': label,
        'source_id': resource['id'],
        'archive_index': resource['path'][0],
        'row_count': len(rows),
        'row_ranges': {'shared_prefix': [0, PREFIX_ROWS - 1], 'chapter_unique_tail': [PREFIX_ROWS, len(rows) - 1]},
        'shared_prefix_row_count': len(prefix),
        'chapter_unique_tail_row_count': len(tail),
        'source_id_ranges': {
            'shared_prefix': [prefix[0]['id'], prefix[-1]['id']],
            'chapter_unique_tail': [tail[0]['id'], tail[-1]['id']],
        },
        'shared_prefix_sequence_sha256': digest(('\n'.join(row['source_sha256'] for row in prefix)).encode()),
        'unique_tail_sequence_sha256': digest(('\n'.join(row['source_sha256'] for row in tail)).encode()),
        'source_offsets': {
            'shared_prefix': [min(row['source_offset'] for row in prefix), max(row['source_offset'] for row in prefix)],
            'chapter_unique_tail': [min(row['source_offset'] for row in tail), max(row['source_offset'] for row in tail)],
        },
        'reference_instruction_offsets': {
            'shared_prefix': [min(min(row['reference_instructions']) for row in prefix), max(max(row['reference_instructions']) for row in prefix)],
            'chapter_unique_tail': [min(min(row['reference_instructions']) for row in tail), max(max(row['reference_instructions']) for row in tail)],
        },
    }


def support_scope(source, resource, prefix_hashes, tail2_hashes, tail3_hashes):
    rows = ordered_rows(resource)
    hashes = {row['source_sha256'] for row in rows}
    number = resource['path'][0]
    profile = resource_runtime_profile(source, resource)
    return {
        'source_id': resource['id'],
        'archive_index': number,
        'archive_offset': resource['offset'],
        'compressed_size': resource['size'],
        'row_count': len(rows),
        'row_range': [0, len(rows) - 1] if rows else None,
        'source_id_range': [rows[0]['id'], rows[-1]['id']] if rows else None,
        'japanese_row_count': sum(row['contains_japanese'] for row in rows),
        'unique_source_hash_count': len(hashes),
        'reference_instruction_offsets': [min(min(row['reference_instructions']) for row in rows), max(max(row['reference_instructions']) for row in rows)] if rows else None,
        'exact_source_hash_overlap': {
            'shared_main_prefix': len(hashes & prefix_hashes),
            'chapter2_unique_tail': len(hashes & tail2_hashes),
            'chapter3_unique_tail': len(hashes & tail3_hashes),
            'exclusive_to_this_scope_comparison': len(hashes - prefix_hashes - tail2_hashes - tail3_hashes),
        },
        'runtime_text_usage': profile,
        'classification_hint': (
            'candidate companion story/event script: indexed Japanese strings and 2003 dialogue-queue references present'
            if profile['queue_push_2003_references'] else
            'candidate companion script: indexed strings present, but no immediate 2003 dialogue-queue reference'
        ),
    }


def build():
    catalog = json.loads(INDEX.read_text(encoding='utf-8'))
    resources = {item['id']: item for item in catalog['resources']}
    chapter2 = resources['00:00088']
    chapter3 = resources['00:00111']
    c2_rows = ordered_rows(chapter2)
    c3_rows = ordered_rows(chapter3)
    assert len(c2_rows) == 3519 and len(c3_rows) == 4127
    assert [row['source_sha256'] for row in c2_rows[:PREFIX_ROWS]] == [row['source_sha256'] for row in c3_rows[:PREFIX_ROWS]]
    assert len(c2_rows) - PREFIX_ROWS == 1711 and len(c3_rows) - PREFIX_ROWS == 2319
    prefix_hashes = {row['source_sha256'] for row in c2_rows[:PREFIX_ROWS]}
    tail2_hashes = {row['source_sha256'] for row in c2_rows[PREFIX_ROWS:]}
    tail3_hashes = {row['source_sha256'] for row in c3_rows[PREFIX_ROWS:]}
    by_number = {item['path'][0]: item for item in catalog['resources'] if item['id'].startswith('00:') and len(item['path']) == 1}
    chapter2_numbers = list(range(66, 111))
    chapter3_numbers = list(range(112, 134))
    with GameSource() as source:
        chapter2_support = [support_scope(source, by_number[number], prefix_hashes, tail2_hashes, tail3_hashes) for number in chapter2_numbers if number in by_number and number != 88]
        chapter3_support = [support_scope(source, by_number[number], prefix_hashes, tail2_hashes, tail3_hashes) for number in chapter3_numbers if number in by_number and number != 111]
    document = {
        'schema_version': 1,
        'purpose': 'Read-only chapter 2/3 scope map. Metadata only; no dialogue text.',
        'source_catalog': str(INDEX.relative_to(ROOT)).replace('\\', '/'),
        'shared_prefix_definition': {
            'row_count': PREFIX_ROWS,
            'proof': 'The ordered source-hash sequence for rows 0..1807 is identical in 00:00088 and 00:00111.',
            'chapter_specific_definition': 'Rows after the shared-prefix range in each main resource; this is a structural distinction, not a reachability claim.',
        },
        'main_resources': [main_scope('chapter2', chapter2), main_scope('chapter3', chapter3)],
        'candidate_support_regions': {
            'chapter2_archive_index_window': [66, 110],
            'chapter2_main_archive_index': 88,
            'chapter2_all_present_indexes': [number for number in chapter2_numbers if number in by_number],
            'chapter2_support_present_indexes': [item['archive_index'] for item in chapter2_support],
            'chapter2_absent_indexes': [number for number in chapter2_numbers if number not in by_number],
            'chapter2_support_resources': chapter2_support,
            'chapter3_archive_index_window': [112, 133],
            'chapter3_main_archive_index': 111,
            'chapter3_all_present_indexes': [number for number in chapter3_numbers if number in by_number],
            'chapter3_support_present_indexes': [item['archive_index'] for item in chapter3_support],
            'chapter3_absent_indexes': [number for number in chapter3_numbers if number not in by_number],
            'chapter3_support_resources': chapter3_support,
        },
        'reachable_transition_hints': {
            'archive_order': '00:00088 follows the chapter-2 companion window and 00:00111 begins after it; 00:00134 is the next observed large main-script boundary.',
            'dialogue_signal': 'Support resources with immediate call target 2003 after a string reference are candidates for dialogue-bearing optional scenes, night talks, or battle events. The VM evidence does not identify the game-state loader condition.',
            'scope_rule_for_future_slices': 'Translate main unique tails by ordered row range. Treat every companion resource with Japanese rows and dialogue-queue references as a separate required coverage queue until runtime route evidence assigns it to a chapter.',
        },
        'coverage_accounting': {
            'chapter2_main_unique_rows': 1711,
            'chapter3_main_unique_rows': 2319,
            'chapter2_support_japanese_rows': sum(item['japanese_row_count'] for item in chapter2_support),
            'chapter3_support_japanese_rows': sum(item['japanese_row_count'] for item in chapter3_support),
            'unassigned_dialogue_bearing_support_source_ids': [item['source_id'] for item in chapter2_support + chapter3_support if item['runtime_text_usage']['queue_push_2003_references']],
        },
        'unknowns': [
            'Static string references prove text presence and immediate dialogue queue use, but do not prove which game-state flags load each companion resource.',
            'The archive-number windows are a bounded candidate map. They do not prove that no chapter 2/3 optional story lives outside those windows.',
            'Night-talk and battle-event labels require runtime route tracing or loader-function research; this document deliberately does not infer those labels from dialogue text.',
        ],
    }
    return document


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    document = build()
    summary = {
        'mode': 'write' if args.write else 'dry-run',
        'main_unique_rows': {item['chapter']: item['chapter_unique_tail_row_count'] for item in document['main_resources']},
        'support_source_ids': document['coverage_accounting']['unassigned_dialogue_bearing_support_source_ids'],
        'support_japanese_rows': {
            'chapter2': document['coverage_accounting']['chapter2_support_japanese_rows'],
            'chapter3': document['coverage_accounting']['chapter3_support_japanese_rows'],
        },
    }
    print(json.dumps(summary, indent=2))
    if args.write:
        OUTPUT.write_text(json.dumps(document, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
