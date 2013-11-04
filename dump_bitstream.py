#!/usr/bin/env python

'''
Copyright 2012 Digshadow <digshadow2064@gmail.com>
'''

from flycrow.xilinx.bitstream import *
import sys

print 'Flying Crowbar bitstream parser'
print

bitstream = Bitstream.from_file(sys.argv[1])
bitstream.dump()


