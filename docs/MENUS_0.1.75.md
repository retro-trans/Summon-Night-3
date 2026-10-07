# Summon Night 3 English test build 0.1.75

This local test build extends the screenshot reports to other text in the same categories, including earlier reports.

- Translate the remaining unit names and class labels, including Hazel, and display translated default names from existing saves. Player-entered names remain intact.
- Translate equipment removal, item rewards, shop confirmations, summon choices, training and related native notices.
- Translate ship, island and village location labels, including Warehouse and Meimei's Shop.
- Translate Meimei's menu buttons and their selected/unselected copies.
- Translate all seven minigame help pages, their results, bait choices, quit confirmations and slot-machine prompts.
- Translate character nameplates and the conversation-partner prompt across matching resource copies.
- Preserve the earlier Cooking, Party Abilities, summon-index spacing and All-Purpose Pot fixes.

Graphics retain native sprite dimensions and palettes; compressed containers retain their original codec. New text is appended without changing source pools or numeric gameplay fields. The default-name lookup matches complete original default names; unmatched custom names pass through.

Testing uses one PPSSPP instance and a fresh boot with a normal in-game save. The packaged upgrade is verified with Retro Trans Tools. This is a test build, not a claim that every story or menu has been translated or tested.

The new inputs cover 365 unit/class fields, 176 native messages and 306 sprite targets propagated across 492 matching resource occurrences. Bounded CPU checks run the default-name lookup, its status/gear wrapper and reward-width helper at two load addresses; all 14 inherited regression groups pass. Native sprite imports verify geometry, palette and compression round trips. Live checks use normal saves with audio enabled; this is not a complete playthrough.

Apply `SN3-English-test-v0.1.75.zip` with Retro Trans Tools to the published 0.1.73 ISO. The upgrade includes the intervening 0.1.74 fixes. Its manifest and checksums identify the required source and resulting ISO.
