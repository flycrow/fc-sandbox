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
import math

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

def diff(l, r):
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
    to_exec = 'diff %s %s' % (l, r)
    print to_exec
    out = runProcess(to_exec)
    print out
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
    #print left
    #print right
    
    ret = []
    for addr in sorted(list(left)):
        lb = left[addr]
        rb = right[addr]
        ret.append((addr, (bitarray(lb) ^ bitarray(rb)).to01()))
    #print 'ret', ret
    return ret


def gen_clb_names():
    # "The format for CLB locations is two letters. The first letter indicates the row, the second letter indicates the column
    for row in [chr(ord('A') + i) for i in xrange(8)]:
        for col in [chr(ord('A') + i) for i in xrange(8)]:
            yield row + col

def row(clb_name, bit, address, mask):
	global csv
	csv.write('%s, %s, %s, %s\n' % (clb_name, bit, address, mask))

csv = open('fsweep.csv', 'w')
row('CLB', 'LUT bit #', 'Frame address', 'Mask')

for clb_name in gen_clb_names():
    if clb_name == 'IM':
        print 'Out of CLBs'
        break
    print
    print
    print
    print '*' * 80
    print clb_name
    reference = None
    diffs = {}
    '''
    Assuming things go smoothly...
    If I diff against a single bit (say 0x0001) all should contain two diffs
    and every diff should contain one value that is the reference bit
    Also assume that no group has more than one bit set
    '''
    # Calculate address frequencies
    # Everything should be 1 except for the reference
    # which should be 15
    # (16 bits, no diff against reference)
    # keys are (addr, bit) where bit is single
    fs = dict()
    for clb_configi in xrange(16):
        clb_config = 1 << clb_configi
        f = 'sweep_clb/CLB_%s_0x%04X/SBAPR.FCRBT' % (clb_name, clb_config)
        if reference is None:
            reference = f
            continue
        res = diff(reference, f)
        diffs[clb_config] = res
        # Should be two bit difference (assuming not sharing same frame)
        if len(res) != 2:
            print 'ERROR: wrong number of diffs (%d)' % len(res)
            for a_diff in res:
                print '  %s' % a_diff
            raise Exception('Unexpected number of different frames')
        '''
        nope...this was for A*
        # So far all bits have been at this position
        # lets make sure
        for (addr, bits) in res:
            if bits != '000000000000000000000000000000000000000000000000000000000000000100000000000':
                print 'Unexpected bits: %s' % str(res)
                raise Exception('Not as simple as I thought')
        '''
        for k in res:
            (addr, bits) = k
            if bitarray(bits).count() != 1:
                # Will need to break up if this occurs
                raise Exception('Its never as simple as we hope')
            #print
            #print 'Existing', fs
            #print 'Adding: %s' % str(k)
            #print 'Exists: %s' % str(k in fs)
            fs[k] = fs.get(k, 0) + 1

    print 'Frequencies:'
    reference_ks = set()
    fail = False
    for k in fs:
        (addr, bits) = k
        n = fs[k]
        print '  %s:%s = %u' % (addr, bits, n)
        if n == 15:
            reference_ks.add(k)
        elif n != 1:
            print 'ERROR: bad number of values'
            fail = True
    if len(reference_ks) != 1:
        raise Exception('Expect exactly one to share all others')
    if fail:
        raise Exception('See previous errors')

    reference = list(reference_ks)[0]

    '''
    Oh boy
    By here we know that there is as reference and all other bits are uniqe
    We can now cancel the bits out of the otherssweep_clb
    '''
    bit_positions = dict()
    # Reference at 0
    print 'Extracting CLB configs...'
    bit_positions[0] = reference
    for clb_config in diffs:
        a_diff = diffs[clb_config]
        bit_index = int(math.log(clb_config, 2))
        print '  %s (%d)' % (clb_config, bit_index)
        for k in a_diff:
            if k == reference:
                continue
            if bit_index in bit_positions:
                raise Exception('Overconstrained bit')
            bit_positions[bit_index] = k

    print 'Final output:'
    for i in xrange(16):
        (addr, bits) = bit_positions[i]
        print '  %u: %s:%s' % (i, addr, bits)
        # row('CLB', 'LUT bit #', 'Frame address')
        row(clb_name, i, '0x' + addr, '0b' + bits)

