#!/usr/bin/env python

'''
Some sort of multi-file base-64 container
Need to check if the text also needs to be unzipped...
'''

from flycrow.xilinx.crypto import *
import sys
import argparse		
import base64

parser = argparse.ArgumentParser(description='Extract Xilinx base64 files')
parser.add_argument('files', metavar='files', type=str, nargs='*',
               help='input [output] or not required depending on options')
parser.add_argument('--verbose', action="store_true", dest="verbose", default=False, help='Print stuff')
args = parser.parse_args()

def dbg(s):
	if 0:
		print '%s' % s

fn_in = args.files[0]
if len(args.files) > 1:
	fn_out = args.files[1]
else:
	fn_out = None

def extract64(fn):
	'''
	First two lines:
		XILINX-XDB 0.1 STUB 0.1 ASCII
		XILINX-XDM V1.6
	After that:
		###3568:XlxV32DM    3ff8     dd8eNrNW0tv4zgS/isZYE8DbI9I...
	'''
	line = open(fn).read().split('\n')[2]
	while len(line):
		print
		pos = line.find(':')
		b64_header = line[0:pos]
		line = line[pos + 1:]
		zip_header = line[0:24]
		print zip_header
		lstr = zip_header[18:]
		print lstr
		l = int(lstr, 16)
		print 'Item of length %u' % l
		line = line[l:]

dbg('Extracting to %s...' % fn_out)
i = 0
for part in extract64(fn_in):
	if fn_out:
		open('%s.%d' % (fn_out, i), 'w').write()
	else:
		if i != 0:
			print
		print '***%d:***' % i
		print part
	i += 1

