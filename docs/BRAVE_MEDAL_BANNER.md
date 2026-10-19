# Unresolved Brave Medal award banner

The reported battle results screen retains the Japanese heading above ORDER.
The reviewed English caption is **Brave Medals awarded!**

This is a pending translation, not an implemented fix. No new ISO or patch was
produced for this report. Local test 0.1.87 is unchanged.

The caption's source binding remains unidentified. Searches of the executable,
indexed resources, decoded containers and existing graphics catalog did not
establish a reliable location. Do not infer from these searches that it must
be artwork: native text generation, animation data and uncatalogued graphics
remain possible. The ordinary reward heading changed in 0.1.84 is a separate
caption and must not be relabeled to hide this report.

The user has no matching state. A private copy of the earlier Berserk state was
recovered with the existing 0.1.83 recovery tool for diagnostic battle playback.
That playback did not reach the reported results screen. It does not validate
the latest build or demonstrate a medal-banner fix. Owned emulator instances
were closed after the investigation. Supplied saves and files remain unchanged.

Next verification needs to identify the actual result caption through its live
draw/setup path or a decoded source asset. Then translate remaining captions on
that same path, preserve the frame and medal artwork, and check native bounds
before producing a numbered test build.
