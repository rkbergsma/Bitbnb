from typing import List

CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
Bytes = List[int]

def convertbits(data, frombits, tobits, pad=True):
    """General power-of-2 base conversion."""
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    max_acc = (1 << (frombits + tobits - 1)) - 1
    for value in data:
        if value < 0 or (value >> frombits):
            return None
        acc = ((acc << frombits) | value) & max_acc
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad:
        if bits:
            ret.append((acc << (tobits - bits)) & maxv)
    elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
        return None
    return ret

def bech32_create_checksum(hrp, data):
    """Compute the checksum values given HRP and data."""
    values = bech32_hrp_expand(hrp) + data
    const = 1
    polymod = bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ const
    return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]

def bech32_hrp_expand(hrp):
    """Expand the HRP into values for checksum computation."""
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]

def bech32_polymod(values):
    """Internal function that computes the Bech32 checksum."""
    generator = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
    chk = 1
    for value in values:
        top = chk >> 25
        chk = (chk & 0x1ffffff) << 5 ^ value
        for i in range(5):
            chk ^= generator[i] if ((top >> i) & 1) else 0
    return chk

def bech32_decode(bech: str) -> Bytes:
    """Validate a Bech32 string, and determine HRP and data."""
    if any(ord(x) < 33 or ord(x) > 126 for x in bech):
        raise RuntimeError('Character outside the US-ASCII [33-126] range')

    if (bech.lower() != bech) and (bech.upper() != bech):
        raise RuntimeError('Mixed upper and lower case')

    bech = bech.lower()
    pos = bech.rfind('1')

    if pos == 0:
        raise RuntimeError('Empty human readable part')
    elif pos == -1:
        raise RuntimeError('No seperator character')
    elif pos + 7 > len(bech):
        raise RuntimeError('Checksum too short')

    if len(bech) > 90:
        raise RuntimeError('Max string length exceeded')

    if not all(x in CHARSET for x in bech[pos+1:]):
        raise RuntimeError('Character not in charset')

    hrp = bech[:pos]
    data = [CHARSET.find(x) for x in bech[pos+1:]]

    if not bech32_verify_checksum(hrp, data):
        raise RuntimeError('Invalid checksum')

    return data[1:-6]

def bech32_verify_checksum(hrp: str, data: Bytes) -> bool:
    """Verify a checksum given HRP and converted data characters."""
    return bech32_polymod(bech32_hrp_expand(hrp) + data) == 1

