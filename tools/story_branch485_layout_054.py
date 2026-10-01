"""Source-validated two-slot layout for resource 485's shared dialogue tail."""
import copy

from dialogue_layout import latin_width
from sn3_vm import instructions
from stages_patch import sha, units, wrap

RESOURCE = 485
PAIRS = ((1956, 1957), (1959, 1960), (1961, 1962))
REGION_START = 79890
REGION_END = 80130
REGION_SHA256 = 'd8f93db41cda7f9d6440e0f281afadab521a969c853f47dd305b3261e266156b'


def expand_direct_pairs(number, rows, data, translated, metrics):
    """Split only the three verified shared-tail messages across their source slots.

    The original branch instructions and common style/helper tail remain in place;
    only existing text-pool operands are relocated by the regular compiler.
    """
    if number != RESOURCE:
        return translated
    assert sha(data[REGION_START:REGION_END]) == REGION_SHA256, 'Resource 485 shared-tail signature changed'
    at = {item['offset']: item for item in instructions(data)}
    expected_refs = ((79914, 79922), (79998, 80006), (80044, 80052))
    for (first, second), (a, b) in zip(PAIRS, expected_refs):
        assert rows[first]['reference_instructions'] == [a]
        assert rows[second]['reference_instructions'] == [b]
        assert at[a]['opcode'] == at[b]['opcode'] == 5 and at[a]['mode'] == at[b]['mode'] == 4
        assert at[a + 4].get('target_word') == at[b + 4].get('target_word') == 2003
        assert at[b + 8]['opcode'] == 10 and at[b + 8].get('target_word') == 40034
    # The shared tail's style decisions and 2030 calls are source-locked by the
    # region hash; these explicit checks document the call preservation contract.
    assert at[80114].get('target_word') == at[80126].get('target_word') == 2030
    out = copy.deepcopy(translated)
    for first, second in PAIRS:
        assert out[second]['text'] == '', ('expected internal continuation', second)
        text = out[first]['text']
        lines = wrap(text, 208, metrics)
        assert len(lines) == 2 and ' '.join(lines) == text
        for line in lines:
            assert line and units(line) <= 31 and latin_width(line, metrics) <= 208
        out[first]['text'], out[second]['text'] = lines
    return out
