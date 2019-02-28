# Copyright (c) 2016-2017, Neil Booth
# Copyright (c) 2017, the ElectrumX authors
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

'''Module providing coin abstraction.

Anything coin-specific should go in this file and be subclassed where
necessary for appropriate handling.
'''

from collections import namedtuple
import re
import struct
from decimal import Decimal
from hashlib import sha256

import lib.util as util
from lib.hash import Base58, hash160, double_sha256, hash_to_str, groestl_hash, rainforest_hash, HASHX_LEN
from lib.script import ScriptPubKey, OpCodes
import lib.tx as lib_tx
from server.block_processor import BlockProcessor
import server.daemon as daemon
from server.session import ElectrumX


Block = namedtuple("Block", "raw header transactions")
OP_RETURN = OpCodes.OP_RETURN


class CoinError(Exception):
    '''Exception raised for coin-related errors.'''


class Coin(object):
    '''Base class of coin hierarchy.'''

    REORG_LIMIT = 200
    # Not sure if these are coin-specific
    RPC_URL_REGEX = re.compile('.+@(\\[[0-9a-fA-F:]+\\]|[^:]+)(:[0-9]+)?')
    VALUE_PER_COIN = 100000000
    CHUNK_SIZE = 2016
    BASIC_HEADER_SIZE = 80
    STATIC_BLOCK_HEADERS = True
    SESSIONCLS = ElectrumX
    DESERIALIZER = lib_tx.Deserializer
    DAEMON = daemon.Daemon
    BLOCK_PROCESSOR = BlockProcessor
    XPUB_VERBYTES = bytes('????', 'utf-8')
    XPRV_VERBYTES = bytes('????', 'utf-8')
    ENCODE_CHECK = Base58.encode_check
    DECODE_CHECK = Base58.decode_check
    # Peer discovery
    PEER_DEFAULT_PORTS = {'t': '50001', 's': '50002'}
    PEERS = []

    @classmethod
    def lookup_coin_class(cls, name, net):
        '''Return a coin class given name and network.

        Raise an exception if unrecognised.'''
        req_attrs = ['TX_COUNT', 'TX_COUNT_HEIGHT', 'TX_PER_BLOCK']
        for coin in util.subclasses(Coin):
            if (coin.NAME.lower() == name.lower() and
                    coin.NET.lower() == net.lower()):
                coin_req_attrs = req_attrs.copy()
                missing = [attr for attr in coin_req_attrs
                           if not hasattr(coin, attr)]
                if missing:
                    raise CoinError('coin {} missing {} attributes'
                                    .format(name, missing))
                return coin
        raise CoinError('unknown coin {} and network {} combination'
                        .format(name, net))

    @classmethod
    def sanitize_url(cls, url):
        # Remove surrounding ws and trailing /s
        url = url.strip().rstrip('/')
        match = cls.RPC_URL_REGEX.match(url)
        if not match:
            raise CoinError('invalid daemon URL: "{}"'.format(url))
        if match.groups()[1] is None:
            url += ':{:d}'.format(cls.RPC_PORT)
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'http://' + url
        return url + '/'

    @classmethod
    def daemon_urls(cls, urls):
        return [cls.sanitize_url(url) for url in urls.split(',')]

    @classmethod
    def genesis_block(cls, block):
        '''Check the Genesis block is the right one for this coin.

        Return the block less its unspendable coinbase.
        '''
        header = cls.block_header(block, 0)
        header_hex_hash = hash_to_str(cls.header_hash(header))
        if header_hex_hash != cls.GENESIS_HASH:
            raise CoinError('genesis block has hash {} expected {}'
                            .format(header_hex_hash, cls.GENESIS_HASH))

        return header + bytes(1)

    @classmethod
    def hashX_from_script(cls, script):
        '''Returns a hashX from a script, or None if the script is provably
        unspendable so the output can be dropped.
        '''
        if script and script[0] == OP_RETURN:
            return None
        return sha256(script).digest()[:HASHX_LEN]

    @util.cachedproperty
    def address_handlers(cls):
        return ScriptPubKey.PayToHandlers(
            address=cls.P2PKH_address_from_hash160,
            script_hash=cls.P2SH_address_from_hash160,
            pubkey=cls.P2PKH_address_from_pubkey,
            unspendable=lambda: None,
            strange=lambda script: None,
        )

    @classmethod
    def address_from_script(cls, script):
        '''Given a pk_script, return the adddress it pays to, or None.'''
        return ScriptPubKey.pay_to(cls.address_handlers, script)

    @staticmethod
    def lookup_xverbytes(verbytes):
        '''Return a (is_xpub, coin_class) pair given xpub/xprv verbytes.'''
        # Order means BTC testnet will override NMC testnet
        for coin in util.subclasses(Coin):
            if verbytes == coin.XPUB_VERBYTES:
                return True, coin
            if verbytes == coin.XPRV_VERBYTES:
                return False, coin
        raise CoinError('version bytes unrecognised')

    @classmethod
    def address_to_hashX(cls, address):
        '''Return a hashX given a coin address.'''
        return cls.hashX_from_script(cls.pay_to_address_script(address))

    @classmethod
    def P2PKH_address_from_hash160(cls, hash160):
        '''Return a P2PKH address given a public key.'''
        assert len(hash160) == 20
        return cls.ENCODE_CHECK(cls.P2PKH_VERBYTE + hash160)

    @classmethod
    def P2PKH_address_from_pubkey(cls, pubkey):
        '''Return a coin address given a public key.'''
        return cls.P2PKH_address_from_hash160(hash160(pubkey))

    @classmethod
    def P2SH_address_from_hash160(cls, hash160):
        '''Return a coin address given a hash160.'''
        assert len(hash160) == 20
        return cls.ENCODE_CHECK(cls.P2SH_VERBYTES[0] + hash160)

    @classmethod
    def multisig_address(cls, m, pubkeys):
        '''Return the P2SH address for an M of N multisig transaction.

        Pass the N pubkeys of which M are needed to sign it.  If
        generating an address for a wallet, it is the caller's
        responsibility to sort them to ensure order does not matter
        for, e.g., wallet recovery.
        '''
        script = cls.pay_to_multisig_script(m, pubkeys)
        return cls.P2SH_address_from_hash160(hash160(script))

    @classmethod
    def pay_to_multisig_script(cls, m, pubkeys):
        '''Return a P2SH script for an M of N multisig transaction.'''
        return ScriptPubKey.multisig_script(m, pubkeys)

    @classmethod
    def pay_to_pubkey_script(cls, pubkey):
        '''Return a pubkey script that pays to a pubkey.

        Pass the raw pubkey bytes (length 33 or 65).
        '''
        return ScriptPubKey.P2PK_script(pubkey)

    @classmethod
    def pay_to_address_script(cls, address):
        '''Return a pubkey script that pays to a pubkey hash.

        Pass the address (either P2PKH or P2SH) in base58 form.
        '''
        raw = cls.DECODE_CHECK(address)

        # Require version byte(s) plus hash160.
        verbyte = -1
        verlen = len(raw) - 20
        if verlen > 0:
            verbyte, hash_bytes = raw[:verlen], raw[verlen:]

        if verbyte == cls.P2PKH_VERBYTE:
            return ScriptPubKey.P2PKH_script(hash_bytes)
        if verbyte in cls.P2SH_VERBYTES:
            return ScriptPubKey.P2SH_script(hash_bytes)

        raise CoinError('invalid address: {}'.format(address))

    @classmethod
    def privkey_WIF(cls, privkey_bytes, compressed):
        '''Return the private key encoded in Wallet Import Format.'''
        payload = bytearray(cls.WIF_BYTE) + privkey_bytes
        if compressed:
            payload.append(0x01)
        return cls.ENCODE_CHECK(payload)

    @classmethod
    def header_hash(cls, header):
        '''Given a header return hash'''
        return double_sha256(header)

    @classmethod
    def header_prevhash(cls, header):
        '''Given a header return previous hash'''
        return header[4:36]

    @classmethod
    def static_header_offset(cls, height):
        '''Given a header height return its offset in the headers file.

        If header sizes change at some point, this is the only code
        that needs updating.'''
        assert cls.STATIC_BLOCK_HEADERS
        return height * cls.BASIC_HEADER_SIZE

    @classmethod
    def static_header_len(cls, height):
        '''Given a header height return its length.'''
        return (cls.static_header_offset(height + 1)
                - cls.static_header_offset(height))

    @classmethod
    def block_header(cls, block, height):
        '''Returns the block header given a block and its height.'''
        return block[:cls.static_header_len(height)]

    @classmethod
    def block(cls, raw_block, height):
        '''Return a Block namedtuple given a raw block and its height.'''
        header = cls.block_header(raw_block, height)
        txs = cls.DESERIALIZER(raw_block, start=len(header)).read_tx_block()
        return Block(raw_block, header, txs)

    @classmethod
    def decimal_value(cls, value):
        '''Return the number of standard coin units as a Decimal given a
        quantity of smallest units.

        For example 1 BTC is returned for 100 million satoshis.
        '''
        return Decimal(value) / cls.VALUE_PER_COIN

    @classmethod
    def satoshis_value(cls, value):
        return int(value * cls.VALUE_PER_COIN)

    @classmethod
    def electrum_header(cls, header, height):
        version, = struct.unpack('<I', header[:4])
        timestamp, bits, nonce = struct.unpack('<III', header[68:80])

        return {
            'block_height': height,
            'version': version,
            'prev_block_hash': hash_to_str(header[4:36]),
            'merkle_root': hash_to_str(header[36:68]),
            'timestamp': timestamp,
            'bits': bits,
            'nonce': nonce,
        }


class MicroBitcoin(Coin):
    NAME = "MicroBitcoin"
    SHORTNAME = "MBC"
    NET = "mainnet"
    VALUE_PER_COIN = 10000
    MBC_HEIGHT = 525000
    RAINFOREST_HEIGHT = 830000
    P2PKH_VERBYTE = bytes.fromhex("1A")
    P2SH_VERBYTES = [bytes.fromhex("33")]
    GENESIS_HASH = ("000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f")
    DESERIALIZER = lib_tx.DeserializerSegWit
    TX_COUNT = 265026255
    TX_COUNT_HEIGHT = 499923
    TX_PER_BLOCK = 50
    RPC_PORT = 6402

    @classmethod
    def electrum_header(cls, header, height):
        version, = struct.unpack('<I', header[:4])
        timestamp, bits, nonce = struct.unpack('<III', header[68:80])
        block_hash = bytes(reversed(cls.header_hash(header, height))).hex()

        return {
            'block_height': height,
            'version': version,
            'block_hash': block_hash,
            'prev_block_hash': hash_to_str(header[4:36]),
            'merkle_root': hash_to_str(header[36:68]),
            'timestamp': timestamp,
            'bits': bits,
            'nonce': nonce,
        }

    @classmethod
    def header_hash(cls, header, height=0):
        if height > cls.MBC_HEIGHT and height < cls.RAINFOREST_HEIGHT:
            return groestl_hash(header)
        elif height >= cls.RAINFOREST_HEIGHT:
            return rainforest_hash(header)
        else:
            return double_sha256(header)
