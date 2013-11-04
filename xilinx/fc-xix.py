#!/usr/bin/env python

from flycrow.xilinx.crypto import *
import sys
import argparse		

parser = argparse.ArgumentParser(description='Extract Xilinx files')
parser.add_argument('files', metavar='files', type=str, nargs='*',
               help='input [output] or not required depending on options')
parser.add_argument('--inspect', action="store_true", dest="inspect", default=False, help='Inspect file and print and return true/false')
parser.add_argument('--verbose', action="store_true", dest="verbose", default=False, help='Print stuff')
parser.add_argument('--extract', action="store_true", dest="extract", default=False, help='Extract file in to file out')
parser.add_argument('--extract-inspected', action="store_true", dest="extract_inspected", default=False, help='Extract file in to file out if encrypted')
args = parser.parse_args()

def dbg(s):
	if 0:
		print '%s' % s

fn_in = args.files[0]
if len(args.files) > 1:
	fn_out = args.files[1]
else:
	fn_out = "/dev/stdout"

if args.inspect:
	for fn in args.files:
		print '%s: %s' %(fn, is_encrypted(fn))

if args.extract:
	dbg('Extracting to %s...' % fn_out)
	open(fn_out, 'w').write(extract(fn_in))

if args.extract_inspected:
	if is_encrypted(fn_in):
		if args.verbose:
			print 'Encrypted, extracting %s to %s...' % (fn_in, fn_out)
		try:
			extracted = extract(fn_in)
			open(fn_out, 'w').write(extracted)
		except:
			print 'Failed to extract %s to %s' % (fn_in, fn_out)
			raise
