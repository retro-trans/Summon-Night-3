"""Validate the new source-bound wrapper without changing historical profiles."""
import unittest

from chapter_source_014 import load
from chapter_patch_014 import PROFILES, direct_rows
from story_display_054 import profiles_for


class DisplayProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.rows, cls.data = load(410)

    def test_dialogue_routed_but_choices_stay_direct(self):
        selected = set(range(3758, 3762)) | set(range(4703, 4706)) | set(range(4778, 4781)) | set(range(4906, 4922))
        old = direct_rows(self.rows, self.data, selected)
        new = direct_rows(self.rows, self.data, selected, profiles_for(410, self.data, PROFILES))
        self.assertEqual(old, selected)
        self.assertEqual(new, set(range(3758, 3762)))
        self.assertNotIn(2154, PROFILES)

    def test_unknown_wrapper_rejected_and_other_resources_unchanged(self):
        altered = bytearray(self.data)
        altered[4312] ^= 1
        with self.assertRaisesRegex(AssertionError, 'signature changed'):
            profiles_for(410, altered, PROFILES)
        self.assertEqual(profiles_for(387, self.data, PROFILES), PROFILES)

    def test_chapter17_wrappers_and_signature_guard(self):
        _, rows, data = load(433)
        selected = set(range(2764, 2767)) | set(range(3448, 3451)) | {3708, 3709}
        self.assertEqual(direct_rows(rows, data, selected), selected)
        self.assertEqual(direct_rows(rows, data, selected, profiles_for(433, data, PROFILES)), set())
        altered = bytearray(data)
        altered[4444] ^= 1
        with self.assertRaisesRegex(AssertionError, '2219 signature changed'):
            profiles_for(433, altered, PROFILES)
        self.assertNotIn(2219, PROFILES)

    def test_branch482_prayer_wrapper_preserves_conditional_names(self):
        _, rows, data = load(482)
        prayer = set(range(3002, 3032))
        conditional_names = {2264, 2265}
        selected = prayer | conditional_names
        self.assertEqual(direct_rows(rows, data, selected), selected)
        profile = profiles_for(482, data, PROFILES)
        self.assertEqual(direct_rows(rows, data, selected, profile), conditional_names)
        altered = bytearray(data)
        altered[4496] ^= 1
        with self.assertRaisesRegex(AssertionError, '2246 signature changed'):
            profiles_for(482, altered, PROFILES)
        self.assertNotIn(2246, PROFILES)


if __name__ == '__main__':
    unittest.main()
