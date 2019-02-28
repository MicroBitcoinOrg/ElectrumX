# Copyright (c) 2019 iamstenman
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import rainforest

header = bytes.fromhex("000000203925e0a940a13beaadba13c8a94c93f1b020a966867bc1334a8f5fdc8c000000b41136b86741ba61ade8e73f3740ffb012564c045c9ee2f2dcd418f29ce47b11e1c36f5cffff001e00124b98")
result = rainforest.get_hash(header, 80)
assert(result == b'\x15|N\xb3\x89!\xc1Ab\xf0\x14\x04\xad\xf0aJ\xd4\x8d\xdfu\xab}^\xc1\xa8I]f%\x00\x00\x00')

print(result[::-1].hex())
