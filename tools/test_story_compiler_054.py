"""Local-corpus regressions for consolidated 0.1.54 story fragments.

Requires the extracted source and accepted drafts; writes no game or translation.
"""
import copy, unittest
from unittest.mock import patch
import story_patch_054 as story


class ContinuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = story.read_inputs(299)

    def test_complete_merged_sentences_compile_once(self):
        for number in (299, 300):
            with self.subTest(resource=number):
                _, report, _, checks = story.prepare(number)
                expected = {
                    (19, 20): "Yeah. Maybe it's because the seal wasn't complete.",
                    (21, 22): "Yes. Perhaps it was because the seal wasn't complete.",
                }
                actual = {tuple(g['resource_rows']): g for g in report['layout_groups']}
                for rows, text in expected.items():
                    group = actual[rows]
                    self.assertEqual(group['text'], text)
                    emitted = [r['text'] for page in group['pages'] for r in page]
                    self.assertTrue(all(emitted))
                    self.assertEqual(' '.join(emitted), text)
                self.assertTrue(checks['all_group_calls_simulated'])
                self.assertTrue(checks['meaning_review_verified'])

    def test_blank_whole_dialogue_rejected(self):
        inputs = copy.deepcopy(self.inputs)
        for row in (19, 20):
            inputs[3][row]['text'] = ''
        with patch.object(story, 'read_inputs', return_value=inputs):
            with self.assertRaisesRegex(AssertionError, 'empty dialogue group'):
                story.prepare(299)

    def test_blank_menu_label_rejected(self):
        inputs = copy.deepcopy(self.inputs)
        inputs[3][19]['text'] = ''
        with patch.object(story, 'read_inputs', return_value=inputs), \
                patch.object(story, 'direct_rows', return_value={19}):
            with self.assertRaisesRegex(AssertionError, 'conditional/menu text'):
                story.prepare(299)


if __name__ == '__main__':
    unittest.main()
