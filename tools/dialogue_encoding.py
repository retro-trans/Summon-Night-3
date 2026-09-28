"""Encode English for the original dialogue reader's two-byte CP932 units."""

# Characters selected by ELF 0x68070 from rodata 0x2193a8..0x2193f4.
# Preserve their order: several represent style changes or runtime substitutions.
CONTROL_CHARACTERS = frozenset('\u3014\u3015\uff3b\uff3d\u2460\u2461\u2462\u2463\u25cf\u25b2\u25a0'
                               '\u0410\u0411\u0413\u0412\u0414\u0415\u0401\u0417\u0419')


def control_tokens(text):
    return [character for character in text if character in CONTROL_CHARACTERS]


def encode_dialogue(text, source_text):
    """Use existing wide Latin glyphs; no shortening or line-width guess occurs.

    Ordinary target English remains in translation files. Converted display text
    is a build artifact. More general Latin rendering/wrapping is a separate task.
    """
    if control_tokens(text) != control_tokens(source_text):
        raise ValueError('Dialogue control tokens changed or moved')
    punctuation = {'"': '\u201d', "'": '\u2019'}
    display = ''.join('\u3000' if char == ' ' else punctuation.get(char, chr(ord(char) + 0xfee0))
                      if 0x21 <= ord(char) <= 0x7e else char for char in text)
    encoded = display.encode('cp932', 'strict')
    if control_tokens(display) != control_tokens(text):
        raise ValueError('Converted punctuation collides with a reserved game control token')
    if not encoded or any(len(char.encode('cp932')) != 2 for char in display):
        raise ValueError('Original dialogue renderer requires two-byte CP932 units')
    if '\0' in text or any(ord(char) < 32 for char in text):
        raise ValueError('Raw control bytes are not supported dialogue tokens')
    if encoded.decode('cp932') != display:
        raise ValueError('Display text does not round-trip through CP932')
    return encoded, display
