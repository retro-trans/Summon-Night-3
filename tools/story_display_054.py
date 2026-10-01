"""Source-bound display profiles for newly encountered story helpers."""
from stages_patch import sha

HELPER_2154_SHA256 = '428e49866bb288d29b974303cd09b2064cd63e81dd95e7e004fd27e0cac623d9'
HELPER_2219_SHA256 = '232b8cb08bc0a7e258029107d194cda50bbf9d75646ef1530ddc533f966e424d'
HELPER_2246_SHA256 = '1cee3bb39e2cfd29d8c7202fd8bff25ae362c2c6db06aaf27a1936e45767e638'


def profiles_for(number, data, base):
    profiles = dict(base)
    if number in (410, 433, 485):
        # Zero-argument wrapper: eight constant pushes, native 0x3052, return.
        # Use the conservative 208px dialogue width until runtime measurement.
        assert sha(data[4308:4332]) == HELPER_2154_SHA256, 'Display helper 2154 signature changed'
        profiles[2154] = (208, 0)
    if number == 433:
        # Same native display call with eight constants; the second is 15.
        # Preserve the wrapper and its arguments on every relocated page.
        assert sha(data[4438:4464]) == HELPER_2219_SHA256, 'Display helper 2219 signature changed'
        profiles[2219] = (208, 0)
    if number in (482, 485):
        # Zero-argument wrapper: eight constants, native 0x3052, return.
        # Its second constant is 12. Keep its original call on each page.
        assert sha(data[4492:4518]) == HELPER_2246_SHA256, 'Display helper 2246 signature changed'
        profiles[2246] = (208, 0)
    return profiles
