"""Focused invariants for 0.1.54 suffix storage, independent of story text."""
import struct,unittest
from story_storage_054 import compact,parse_pool
from script_strings import SCRIPT_PREFIX
from dialogue_layout import operand_instruction
from sn3_vm import instructions

def fixture(texts):
    raw=[t.encode('cp932') for t in texts];pool=32+4+4*len(raw)+2
    strings=bytearray(b'\0\0');words=[]
    for b in raw:
        words.append(len(strings)//2);strings.extend(b+b'\0\0');strings.extend(bytes(len(strings)%2))
    header=SCRIPT_PREFIX+struct.pack('<5I',0x1010,16,pool//2,0,0)
    code=operand_instruction(10,0,18)+b''.join(operand_instruction(5,4,w) for w in words)+struct.pack('<H',9)
    return header+code+strings

def referenced(data):
    pool=struct.unpack_from('<I',data,20)[0]*2
    return [data[pool+i['string_word']*2:data.index(b'\0',pool+i['string_word']*2)] for i in instructions(data) if 'string_word' in i]

class StorageTests(unittest.TestCase):
    def test_suffix_and_duplicate_bytes_and_code(self):
        before=fixture(['ＡＢＣ','ＢＣ','Ｃ','ＢＣ','abc','bc','c'])
        after,report=compact(before,[],[])
        self.assertEqual(referenced(before),referenced(after));self.assertGreater(report['suffix_saved_bytes'],0)
        self.assertEqual(instructions(before)[0],instructions(after)[0]);self.assertEqual(before[:32],after[:32])
        for a,b in zip(instructions(before),instructions(after)):
            if 'string_word' not in a:self.assertEqual(a,b)
        again,_=compact(bytes(after),[],[]);self.assertEqual(after,again)
    def test_reject_inside_multibyte_character(self):
        before=fixture(['A漢Z']);pool=struct.unpack_from('<I',before,20)[0]*2
        mutated=bytearray(before);mutated[36:40]=operand_instruction(5,4,2)
        with self.assertRaises((UnicodeDecodeError,ValueError)):parse_pool(mutated)
    def test_reject_pointer_to_terminator(self):
        before=fixture(['ＡＢ']);mutated=bytearray(before);mutated[36:40]=operand_instruction(5,4,3)
        with self.assertRaises(ValueError):parse_pool(mutated)
    def test_no_change_without_shareable_suffix(self):
        before=fixture(['abc','def']);after,r=compact(before,[],[])
        self.assertEqual(referenced(before),referenced(after));self.assertEqual(r['suffix_saved_bytes'],0)

if __name__=='__main__':unittest.main()
