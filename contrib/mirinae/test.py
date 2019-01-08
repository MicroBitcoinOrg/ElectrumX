# Copyright (c) 2018 iamstenman
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import mirinae
import struct
 
ver = "00000020"
prev_block = "0000acc34546b8285eafd0e6419e0fcf4c0577562eac23d632d123931e0fff72"
mrkl_root = "5e9846ebda6e8687582336d52e5a1b54974cc44c1156c267cf46d9c992bad96d"
time_ = 0x5BD3A212
bits = 0x1F00FFFF

exp = bits >> 24
mant = bits & 0xffffff
target_hexstr = '%064x' % (mant * (1 << (8 * (exp - 3))))
target_str = bytes.fromhex(target_hexstr)
nonce = 78679
height = 21

header = (bytes.fromhex(ver) + bytes.fromhex(prev_block)[::-1] + bytes.fromhex(mrkl_root)[::-1] + struct.pack("<LLL", time_, bits, nonce))

result = mirinae.get_hash(header, len(header), height)
assert result == b'\xc9\x19\xee\xcd\xf0Q\xdfqt\xac\xfa\xfd\x01\x98\xbbMq&i TR\xb7\x8f\xbf\x1f\x1d\x82\x94q\x00\x00'

print(result[::-1].hex())
