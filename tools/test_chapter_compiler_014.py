"""Read-only compiler regressions using in-memory mutations of real scripts.

Run after regenerating chapter_compiler_014.py. No target, source, or build
artifacts are written. These checks establish static behavior, not runtime QA.
"""
import copy
import struct
import unittest
from unittest.mock import patch

import chapter_patch_014 as adapter
from chapter_source_014 import load
from sn3_codec import decompress
from sn3_vm import instructions


class CompilerRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = {}
        cls.baselines = {}
        for number in (204, 235):
            resource, rows, data = load(number)
            targets, inputs = adapter.targets(number, rows, data, False, False)
            cls.fixtures[number] = resource, rows, data, targets, inputs
            cls.baselines[number] = cls.compile_snapshot(number)

    @classmethod
    def compile_snapshot(cls, number, data=None):
        resource, rows, original, targets, inputs = cls.fixtures[number]
        source = resource, rows, original if data is None else data
        with patch.object(adapter, 'source', return_value=source), patch.object(
                adapter, 'targets',
                side_effect=lambda *args: (copy.deepcopy(targets), dict(inputs))):
            return adapter.prepare(number, reviewed=False, partial=False)

    def entry_mutation(self):
        """Enter at an original text-queue call, inside a normally reflowed span."""
        number = 235
        targets = self.fixtures[number][3]
        metrics = adapter.collect()[0]['characters']
        group = next(g for g in self.baselines[number][1]['layout_groups']
                     if len(g['resource_rows']) >= 2
                     and g['resource_rows'][0] >= 11
                     and all(not adapter.control_tokens(targets[n]['text'])
                             and adapter.units(targets[n]['text']) <= 31
                             and adapter.latin_width(targets[n]['text'], metrics) <= 208
                             for n in g['resource_rows']))
        data = bytearray(self.fixtures[number][2])
        entry = group['original_span'][0] + 4
        at = {i['offset']: i for i in instructions(data)}
        self.assertEqual(at[entry]['target_word'], 2003)
        self.assertLess(entry, group['original_span'][1])
        struct.pack_into('<I', data, 16, entry // 2)
        return number, bytes(data), entry, group

    def test_complete_baselines_and_post_compaction_execution(self):
        shared_fragments = 0
        overflow_groups = 0
        inline_groups = 0
        for number, (packed, report, selection, checks) in self.baselines.items():
            with self.subTest(resource=number):
                _, rows, original, _, _ = self.fixtures[number]
                self.assertEqual(checks['remaining_in_scope'], 0)
                self.assertFalse(checks['partial_preview'])
                self.assertFalse(checks['meaning_review_verified'])
                self.assertEqual(len(selection['translations']), len(rows))
                data = decompress(packed, 0xa695)[0]
                before = {i['offset']: i for i in instructions(original)}
                after = {i['offset']: i for i in instructions(data)}
                for group in report['layout_groups']:
                    start, stop = group['original_span']
                    old = adapter.compiler.simulate(original, before, start, stop)
                    new = adapter.compiler.simulate(data, after, start, stop)
                    self.assertEqual(len(old), 1)
                    self.assertEqual(len(new), len(group['pages']))
                    overflow_groups += bool(group['code_size'])
                    inline_groups += not group['code_size']
                    for actual, expected in zip(new, group['pages']):
                        self.assertEqual(actual['helper'], old[0]['helper'])
                        self.assertEqual(actual['args'], old[0]['args'])
                        self.assertEqual(actual['lines'],
                                         [r['display_text'] for r in expected])
                        for fragment in expected:
                            owned = fragment['owned_reference_instructions']
                            self.assertTrue(owned)
                            for reference in owned:
                                self.assertEqual(after[reference]['string_word'],
                                                 fragment['pool_word_offset'])
                            shared_fragments += len(fragment['reference_instructions']) > len(owned)
        self.assertGreater(shared_fragments, 0, 'Must exercise deduplicated fragments')
        self.assertGreater(overflow_groups, 0, 'Must exercise appended continuations')
        self.assertGreater(inline_groups, 0, 'Must exercise wholly inline reuse')

    def test_rejects_original_code_fallthrough(self):
        data = bytearray(self.fixtures[235][2])
        terminal = instructions(data)[-1]
        self.assertEqual(terminal['opcode'], 9)
        self.assertEqual(terminal['size'], 2)
        struct.pack_into('<H', data, terminal['offset'], 0)  # NOP, then pool.
        self.assertEqual(instructions(data)[-1]['opcode'], 0)
        with self.assertRaisesRegex(AssertionError, 'Original code must terminate'):
            self.compile_snapshot(235, bytes(data))

    def test_compiler_rejects_entry_inside_forced_reflow(self):
        number, data, _, _ = self.entry_mutation()
        resource, rows, _, targets, inputs = self.fixtures[number]
        original_direct = {r['row'] for r in self.baselines[number][3]['direct_rows']}
        # Bypass the adapter's fallback to exercise the compiler's own guard.
        with patch.multiple(adapter.compiler,
                            chapter_source=lambda _: (resource, rows, data),
                            load_targets=lambda *args: (copy.deepcopy(targets), dict(inputs)),
                            DIRECT={number: original_direct}, PROFILES=adapter.PROFILES):
            with self.assertRaisesRegex(AssertionError, 'branch into group'):
                adapter.BASE_PREPARE(number, reviewed=False)

    def test_adapter_preserves_entry_with_direct_fallback(self):
        number, data, entry, affected = self.entry_mutation()
        packed, report, _, checks = self.compile_snapshot(number, data)
        result = decompress(packed, 0xa695)[0]
        self.assertEqual(struct.unpack_from('<I', result, 16)[0] * 2, entry)
        before = {i['offset']: i for i in instructions(data)}
        after = {i['offset']: i for i in instructions(result)}
        self.assertEqual(after[entry], before[entry])
        direct = {r['row'] for r in checks['direct_rows']}
        self.assertTrue(set(affected['resource_rows']) <= direct)
        for group in report['layout_groups']:
            start, stop = group['original_span']
            self.assertFalse(start < entry < stop)
        self.assertEqual(checks['remaining_in_scope'], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
