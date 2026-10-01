"""Read-only guards for the resource 393 conditional dialogue exception."""
import copy
import struct
import sys
import unittest

sys.path.insert(0,'tools')

from conditional_layout_054 import COMMON_PREFIX, FALSE_JUMP, RETURN, detect, simulate
from font_metrics_014 import collect
from sn3_vm import instructions
from story_patch_054 import read_inputs


class ConditionalLayout054Tests(unittest.TestCase):
    def fixture(self):
        _,rows,data,translated,_=read_inputs(393,False)
        metrics=copy.deepcopy(collect()[0]['characters'])
        for character,advance in [('▲',128),('●',96),('■',128),('♪',16),('　',6)]:
            metrics[character]={'proposed_advance_pixels':advance}
        at={row['offset']:row for row in instructions(data)}
        destinations={row['target_word']*2 for row in at.values() if 'target_word' in row}|{struct.unpack_from('<I',data,16)[0]*2}
        return rows,data,translated,at,destinations,metrics

    def test_original_paths_match_their_source_rows(self):
        rows,data,translated,at,destinations,metrics=self.fixture()
        plan=detect(393,rows,translated,data,at,destinations,metrics)
        self.assertEqual([(b['condition'],b['resource_rows']) for b in plan['branches']],[(True,[112,114]),(False,[113,114])])
        for condition,source_rows in ((True,(112,114)),(False,(113,114))):
            old=simulate(data,at,FALSE_JUMP,RETURN,condition)
            expected=[data[rows[n]['source_offset']:rows[n]['source_offset']+rows[n]['source_byte_length']].decode('cp932') for n in source_rows]
            self.assertEqual(old[0]['lines'],expected)

    def test_external_branch_into_common_continuation_is_rejected(self):
        rows,data,translated,at,destinations,metrics=self.fixture()
        forged=copy.deepcopy(at)
        forged[9000]=dict(offset=9000,opcode=10,mode=0,target_word=COMMON_PREFIX//2)
        with self.assertRaisesRegex(AssertionError,'conditional branch origin'):
            detect(393,rows,translated,data,forged,destinations,metrics)


if __name__=='__main__':
    unittest.main()
