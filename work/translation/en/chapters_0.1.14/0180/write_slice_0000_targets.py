"""Draft Chapter 6 main-tail rows 0--79; run without --write first."""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[5] / 'tools'))
from chapter_source_014 import load

OUT = Path(__file__).with_name('slice_0000.targets.json')
TEXT = [
"So imagine there are five Nauba fruits", "and the two of you have to", "split them between yourselves, okay?",
"So, imagine there are five Nauba fruits", "and the two of you", "have to split them between yourselves, okay?",
"Umm...", "One, two, th...", "Th-threeee?!", "Teacher, I don't understand", "this part!", "Me neither!",
"Ah, could you", "wait just a moment?", "Sure.", "Could you", "wait just a moment?", "I'll take a look.",
"Huh? Big Bro's", "going to teach us?", "Leave a simple sum", "like this to me!", "Will you show me?", "Big Bro Will...",
"Honestly...", "Come on, show me.", "O-okay...", "Can you tell me", "what part you don't understand?",
"Huh? Big Sis is", "going to teach us?", "Mm...", "It's fine, right, Teacher?", "Teacher, I'll look after", "these children.",
"Better than making them wait,", "right?", "Teacher, I'll make", "a special exception", "and look after them.", "You should be grateful, okay?", "That's fine, isn't it, Teacher?",
"Yes, ▲", "I'm counting on you.", "▲,", "could you help me?", "▲", "could you help me?",
"Well, leave it", "to the class representative!", "It's only natural", "as class representative.", "Well, I am everyone's", "class representative, after all.",
"Yes...", "I'm class representative, so", "at least this much...", "Making ▲", "class representative", "was the right choice, it seems.",
"Making ▲", "class representative", "was the right choice...", "Making ▲", "class representative", "was the right choice...",
"See you!", "Goodbye, Teacher.", "Phew...", "Goodbye.", "Get home safely.", "Good work.", "Good work, Teacher.", "Good work.", "Good work, Teacher.",
"It really has...", "Ardylia?!", "It looks like a proper school", "now, doesn't it?", "Why are you here?"
]

def build():
    resource, rows, _ = load(180)
    assert len(TEXT) == 80
    start = 3957
    out = {}
    for relative, text in enumerate(TEXT):
        physical = start + relative; row = rows[physical]
        out[row['id']] = {'id': row['id'], 'source_sha256': row['source_sha256'], 'source_offset': row['source_offset'], 'source_byte_length': row['source_byte_length'], 'reference_instructions': row['reference_instructions'], 'resource_row': relative, 'physical_ordered_index': physical, 'text': text, 'status': 'draft', 'notes': 'Self-checked draft; physical rows 3957-4038 examined for immediate context. Pending independent meaning review.'}
    return {'resource_id': resource['id'], 'section': 'main-tail', 'assigned_range': [0, 79], 'physical_ordered_index_range': [3957, 4036], 'rows_examined': {'ranges_inclusive': [[3957, 4038]], 'count': 82}, 'translations': out}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--write', action='store_true'); args = parser.parse_args()
    doc = build(); print(json.dumps({'mode': 'write' if args.write else 'dry-run', 'resource_id': doc['resource_id'], 'rows': len(doc['translations']), 'sample': list(doc['translations'].values())[:3]}, ensure_ascii=False, indent=2))
    if args.write: OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
