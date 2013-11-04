#!/usr/bin/env python
'''
first run "./gen_rbt.sh  |bash"

$ python fdiff.py 0x0000/SBAPR.FCRBT 0xFFFF/SBAPR.FCRBT 
0x008D: 000000000000000000000000000000000000000000000000000000010000000000000000000
0x0090: 000000000000000000000000000000000000000000000000000000010000000000000000000
0x009B: 000000000000000000000000000000000000000000000000000000010000000000000000000
0x008B: 000000000000000000000000000000000000000000000000000000010000000000000000000
0x008C: 000000000000000000000000000000000000000000000000000000010000000000000000000
'''
from bitarray import bitarray
import sys
import subprocess
import os
import argparse
from flycrow.xilinx.xc2000_dumper import *

def runProcess(exe):
    ret = ''
    p = subprocess.Popen(exe, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while(True):
        #returns None while subprocess is running
        retcode = p.poll() 
        ret += p.stdout.read()
        if retcode is not None:
            break
    return ret

parser = argparse.ArgumentParser(description='Intelligently differentiate two raw bitstreams')
parser.add_argument('left')
parser.add_argument('right')
parser.add_argument('--verbose', '-v', action='count', default=0)
parser.add_argument('--base')
args = parser.parse_args()

ltmp = '/tmp/fdiffl'
rtmp = '/tmp/fdiffr'

def gen_rbt(in_file, out_file):
    global args
    
    options = Options()
    options.verbose = args.verbose
    options.prefix = True
    options.core = True
    dumper = BitstreamDumper(open(in_file).read(), options=options, handler=StringHandler(options))
    out = dumper.dump()
    open(out_file, 'w').write(out)
    
l = args.left
if l.find('.') < 0:
    lt = os.path.join(l, 'SBAPR.FCRBT')
    if os.path.exists(lt):
        l = lt
    else:
        i = os.path.join(l, 'SBAPR.BIT')
        if not os.path.exists(i):
            raise Exception('Could not source left from left (%s)' % l)
        l = ltmp
        gen_rbt(i, l)

r = args.right
if r.find('.') < 0:
    rt = os.path.join(r, 'SBAPR.FCRBT')
    if os.path.exists(rt):
        r = rt
    else:
        i = os.path.join(r, 'SBAPR.BIT')
        if not os.path.exists(i):
            raise Exception('Could not source left from right (%s)' % r)
        r = rtmp
        gen_rbt(i, r)

verbose = args.verbose

if verbose >= 2:
    print 'Selected L: %s' % l
    print 'Selected R: %s' % r

if not os.path.exists(l):
    raise Exception('%s does not exist' % l)
if not os.path.exists(r):
    raise Exception('%s does not exist' % r)
'''
141,143c141,143
< 008B: 011111111111111111111111111111111111111111111111110111110111111111111111111
< 008C: 011111111111111111111111111111111111111111111111111111111101111111111111111
< 008D: 011111111111111111111111111111111111111111111111111101111101111111111111111
---
> 008B: 011111111111111111111111111111111111111111111111110111100111111111111111111
> 008C: 011111111111111111111111111111111111111111111111111111101101111111111111111
> 008D: 011111111111111111111111111111111111111111111111111101101101111111111111111
146c146
< 0090: 011111111111111111111111111111111111111111111111111111111111111111111111111
---
> 0090: 011111111111111111111111111111111111111111111111111111101111111111111111111
157c157
< 009B: 011111111111111111111111111111111111111111111111111111111111111111111111111
---
> 009B: 011111111111111111111111111111111111111111111111111111101111111111111111111
'''
out = runProcess('diff %s %s' % (l, r))
left = dict()
right = dict()
for line in out.split('\n'):
    line = line.strip()
    if len(line) == 0:
        continue
    if line[0] == '<':
        d = left
    elif line[0] == '>':
        d = right
    else:
        continue
    try:
        (lr, addr, bits) = line.split()
    except:
        print line
        raise
    addr = addr.replace(':', '')
    d[addr] = bits

if len(left) != len(right):
    raise Exception('Bad')

for addr in sorted(list(left)):
    lb = bitarray(left[addr])
    rb = bitarray(right[addr])
    addr = int(addr, 16)
    if args.base:
        addr -= int(args.base, 0)
    mask = (lb ^ rb)
    print '0x%04X: %s' % (addr, mask.to01())
    if verbose:
        print '     L: %s' % (lb & mask).to01()
        print '     R: %s' % (rb & mask).to01()
    
