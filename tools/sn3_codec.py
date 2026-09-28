"""Bounded codec for the game's obfuscated LZ stream (ELF VA 0x1e56d0)."""


def decoded_size(data, key=0x9831):
    key = key or 0x9831
    if not 0 <= key <= 0xffff:
        raise ValueError('Compression key must fit in 16 bits')
    if len(data) < 5:
        raise ValueError('Compressed header is too short')
    high, low = key >> 8, key & 255
    seed = data[0] ^ high ^ low
    return ((data[2] ^ seed ^ low) | ((data[4] ^ seed ^ low) << 8) |
            ((data[1] ^ seed ^ high) << 16) | ((data[3] ^ seed ^ high) << 24))


def decompress(data, key=0x9831, max_output=64 * 1024 * 1024):
    key = key or 0x9831
    size = decoded_size(data, key)
    if not 0 < size <= max_output:
        raise ValueError('Decoded length exceeds the configured bound')
    high, low = key >> 8, key & 255
    mask = high ^ low
    out = bytearray()
    position = 5
    flags = 0
    tokens = 0
    high_nibble = False
    lengths = 0

    def take():
        nonlocal position
        if position >= len(data):
            raise ValueError('Truncated compressed stream')
        value = data[position]
        position += 1
        return value

    while len(out) < size:
        if tokens % 8 == 0:
            flags = take() ^ mask
        else:
            flags >>= 1
        tokens += 1
        if flags & 1:
            if high_nibble:
                lengths >>= 4
            else:
                lengths = take() ^ low
            high_nibble = not high_nibble
            length = (lengths & 15) + 2
            distance = ((take() ^ mask) ^ (len(out) & 255)) + 1
            if distance > len(out) or len(out) + length > size:
                raise ValueError('Invalid back-reference bounds')
            for _ in range(length):
                out.append(out[-distance])
        else:
            out.append(take() ^ high ^ ((~len(out)) & 255))
    return bytes(out), position


def compress(data, key=0x9831, max_input=64 * 1024 * 1024):
    """Encode with a deterministic greedy 256-byte window and 2..17-byte matches.

    Length nibbles are paired globally, including across flag groups. A second
    reference updates the reserved high nibble in the earlier length byte.
    """
    key = key or 0x9831
    if not 0 <= key <= 0xffff:
        raise ValueError('Compression key must fit in 16 bits')
    data = bytes(data)
    size = len(data)
    if not 0 < size <= min(max_input, 0xffffffff):
        raise ValueError('Input length exceeds the configured bound')
    high, low = key >> 8, key & 255
    mask = high ^ low
    out = bytearray((mask, ((size >> 16) & 255) ^ high, (size & 255) ^ low,
                     ((size >> 24) & 255) ^ high, ((size >> 8) & 255) ^ low))
    position, token = 0, 0
    length_byte = None
    while position < size:
        if token % 8 == 0:
            flag_byte = len(out)
            out.append(mask)
        length, distance = 0, 0
        if position + 1 < size:
            minimum = max(0, position - 256)
            prefix = data[position:position + 2]
            # The end permits a distance-one overlapping match.
            match = data.rfind(prefix, minimum, position + 1)
            limit = min(17, size - position)
            while match >= minimum:
                count = 2
                while count < limit and data[match + count] == data[position + count]:
                    count += 1
                if count > length:
                    length, distance = count, position - match
                if length == limit:
                    break
                match = data.rfind(prefix, minimum, match + 1)
        if length >= 2:
            out[flag_byte] ^= 1 << (token % 8)
            if length_byte is None:
                length_byte = len(out)
                out.append((length - 2) ^ low)
            else:
                out[length_byte] ^= (length - 2) << 4
                length_byte = None
            out.append((distance - 1) ^ mask ^ (position & 255))
            position += length
        else:
            out.append(data[position] ^ high ^ ((~position) & 255))
            position += 1
        token += 1
    return bytes(out)
