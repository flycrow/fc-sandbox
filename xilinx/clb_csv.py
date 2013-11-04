#!/usr/bin/env python
import string

def gen_clb_names():
    # "The format for CLB locations is two letters. The first letter indicates the row, the second letter indicates the column
    for row in [chr(ord('A') + i) for i in xrange(8)]:
        for col in [chr(ord('A') + i) for i in xrange(8)]:
            yield row + col






def row(clb_name, bit, address):
	print '%s, %s, %s' % (clb_name, bit, address)

row('CLB', 'LUT bit #', 'Frame address')
for clb_name in gen_clb_names():
    for biti in xrange(16):
        row(clb_name, biti, '')

