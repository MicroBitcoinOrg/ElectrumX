# Copyright (c) 2016-2017, Neil Booth
# Copyright (c) 2017 Pieter Wuille
#
# All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''Cryptograph hash functions and related classes.'''


import hashlib
import hmac
import groestlcoin_hash
import mirinae

from lib.util import bytes_to_int, int_to_bytes, hex_to_bytes

_sha256 = hashlib.sha256
_sha512 = hashlib.sha512
_new_hash = hashlib.new
_new_hmac = hmac.new
HASHX_LEN = 11


def sha256(x):
    '''Simple wrapper of hashlib sha256.'''
    return _sha256(x).digest()


def groestl_hash(x):
    '''Simple wrapper of groestl hash.'''
    return groestlcoin_hash.getHash(x, len(x))


def mirinae_hash(x, height):
    '''Simple wrapper of mirinae hash.'''
    return mirinae.get_hash(x, len(x), height)


def ripemd160(x):
    '''Simple wrapper of hashlib ripemd160.'''
    h = _new_hash('ripemd160')
    h.update(x)
    return h.digest()


def double_sha256(x):
    '''SHA-256 of SHA-256, as used extensively in bitcoin.'''
    return sha256(sha256(x))


def hmac_sha512(key, msg):
    '''Use SHA-512 to provide an HMAC.'''
    return _new_hmac(key, msg, _sha512).digest()


def hash160(x):
    '''RIPEMD-160 of SHA-256.

    Used to make bitcoin addresses from pubkeys.'''
    return ripemd160(sha256(x))


def hash_to_hex_str(x):
    '''Convert a big-endian binary hash to displayed hex string.

    Display form of a binary hash is reversed and converted to hex.
    '''
    return bytes(reversed(x)).hex()


hash_to_str = hash_to_hex_str   # Temporary


def hex_str_to_hash(x):
    '''Convert a displayed hex string to a binary hash.'''
    return bytes(reversed(hex_to_bytes(x)))


class Base58Error(Exception):
    '''Exception used for Base58 errors.'''


class Base58(object):
    '''Class providing Base58 functionality.'''

    chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    assert len(chars) == 58
    cmap = {c: n for n, c in enumerate(chars)}

    @staticmethod
    def char_value(c):
        val = Base58.cmap.get(c)
        if val is None:
            raise Base58Error('invalid base 58 character "{}"'.format(c))
        return val

    @staticmethod
    def decode(txt):
        """Decodes txt into a big-endian bytearray."""
        if not isinstance(txt, str):
            raise TypeError('a string is required')

        if not txt:
            raise Base58Error('string cannot be empty')

        value = 0
        for c in txt:
            value = value * 58 + Base58.char_value(c)

        result = int_to_bytes(value)

        # Prepend leading zero bytes if necessary
        count = 0
        for c in txt:
            if c != '1':
                break
            count += 1
        if count:
            result = bytes(count) + result

        return result

    @staticmethod
    def encode(be_bytes):
        """Converts a big-endian bytearray into a base58 string."""
        value = bytes_to_int(be_bytes)

        txt = ''
        while value:
            value, mod = divmod(value, 58)
            txt += Base58.chars[mod]

        for byte in be_bytes:
            if byte != 0:
                break
            txt += '1'

        return txt[::-1]

    @staticmethod
    def decode_check(txt, *, hash_fn=double_sha256):
        '''Decodes a Base58Check-encoded string to a payload.  The version
        prefixes it.'''
        be_bytes = Base58.decode(txt)
        result, check = be_bytes[:-4], be_bytes[-4:]
        if check != hash_fn(result)[:4]:
            raise Base58Error('invalid base 58 checksum for {}'.format(txt))
        return result

    @staticmethod
    def encode_check(payload, *, hash_fn=double_sha256):
        """Encodes a payload bytearray (which includes the version byte(s))
        into a Base58Check string."""
        be_bytes = payload + hash_fn(payload)[:4]
        return Base58.encode(be_bytes)

class Bech32(object):
    '''Class providing Bech32 functionality.'''

    CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"

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

    def bech32_hrp_expand(hrp):
        """Expand the HRP into values for checksum computation."""
        return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]

    def bech32_verify_checksum(hrp, data):
        """Verify a checksum given HRP and converted data characters."""
        return bech32_polymod(bech32_hrp_expand(hrp) + data) == 1

    def bech32_create_checksum(hrp, data):
        """Compute the checksum values given HRP and data."""
        values = bech32_hrp_expand(hrp) + data
        polymod = bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ 1
        return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]

    def bech32_encode(hrp, data):
        """Compute a Bech32 string given HRP and data values."""
        combined = data + bech32_create_checksum(hrp, data)
        return hrp + '1' + ''.join([CHARSET[d] for d in combined])

    def bech32_decode(bech):
        """Validate a Bech32 string, and determine HRP and data."""
        if ((any(ord(x) < 33 or ord(x) > 126 for x in bech)) or
                (bech.lower() != bech and bech.upper() != bech)):
            return (None, None)
        bech = bech.lower()
        pos = bech.rfind('1')
        if pos < 1 or pos + 7 > len(bech) or len(bech) > 90:
            return (None, None)
        if not all(x in CHARSET for x in bech[pos+1:]):
            return (None, None)
        hrp = bech[:pos]
        data = [CHARSET.find(x) for x in bech[pos+1:]]
        if not bech32_verify_checksum(hrp, data):
            return (None, None)
        return (hrp, data[:-6])

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

    def decode(hrp, addr):
        """Decode a segwit address."""
        hrpgot, data = bech32_decode(addr)
        if hrpgot != hrp:
            return (None, None)
        decoded = convertbits(data[1:], 5, 8, False)
        if decoded is None or len(decoded) < 2 or len(decoded) > 40:
            return (None, None)
        if data[0] > 16:
            return (None, None)
        if data[0] == 0 and len(decoded) != 20 and len(decoded) != 32:
            return (None, None)
        return (data[0], decoded)

    def encode(hrp, witver, witprog):
        """Encode a segwit address."""
        ret = bech32_encode(hrp, [witver] + convertbits(witprog, 8, 5))
        if decode(hrp, ret) == (None, None):
            return None
        return ret
