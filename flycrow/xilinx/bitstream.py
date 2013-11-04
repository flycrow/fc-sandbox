'''
Copyright 2012 Digshadow <digshadow2064@gmail.com>
'''

import struct
import binascii
import sys
import os

def xbit(num, amax, amin = None):
	if amin is None:
		amin = amax
	return (num & (0xFFFFFFFF >> (31 - amax))) >> amin

'''
XAPP452: Spartan-3 FPGA Family Advanced Configuration Architecture application note



My test bitstream
AND gate from two of the switches to an LED
Second LED hard coded on

Run 0
	[localhost andg]$ ls -lh andg.bit 
	-rw-rw-r-- 1 XXX XXX 128K Apr  8 00:38 andg.bit


	00000000  00 09 0f f0 0f f0 0f f0  0f f0 00 00 01 61 00 1b  |.............a..|
	00000010  61 6e 64 67 2e 6e 63 64  3b 55 73 65 72 49 44 3d  |andg.ncd;UserID=|
	00000020  30 78 46 46 46 46 46 46  46 46 00 62 00 0b 33 73  |0xFFFFFFFF.b..3s|
	00000030  32 30 30 66 74 32 35 36  00 63 00 0b 32 30 31 32  |200ft256.c..2012|
	00000040  2f 30 34 2f 30 38 00 64  00 09 30 30 3a 33 38 3a  |/04/08.d..00:38:|
	00000050  33 39 00 65 00 01 ff 88  ff ff ff ff aa 99 55 66  |39.e..........Uf|
	00000060  30 00 80 01 00 00 00 07  30 01 60 01 00 00 00 34  |0.......0.`....4|
	00000070  30 01 20 01 40 00 3f e5  30 01 c0 01 01 41 40 93  |0. .@.?.0....A@.|
	00000080  30 00 c0 01 00 00 00 00  30 00 80 01 00 00 00 09  |0.......0.......|
	00000090  30 00 20 01 00 00 00 00  30 00 80 01 00 00 00 01  |0. .....0.......|
	000000a0  30 00 40 00 50 00 7f 88  00 00 00 00 00 00 00 00  |0.@.P...........|
	000000b0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
	*
	
Confirmed that a second run didn't generate the same bitstream

	00000000  00 09 0f f0 0f f0 0f f0  0f f0 00 00 01 61 00 1b  |.............a..|
	00000010  61 6e 64 67 2e 6e 63 64  3b 55 73 65 72 49 44 3d  |andg.ncd;UserID=|
	00000020  30 78 46 46 46 46 46 46  46 46 00 62 00 0b 33 73  |0xFFFFFFFF.b..3s|
	00000030  32 30 30 66 74 32 35 36  00 63 00 0b 32 30 31 32  |200ft256.c..2012|
	00000040  2f 30 34 2f 30 38 00 64  00 09 30 30 3a 35 33 3a  |/04/08.d..00:53:|
	00000050  31 35 00 65 00 01 ff 88  ff ff ff ff aa 99 55 66  |15.e..........Uf|
	00000060  30 00 80 01 00 00 00 07  30 01 60 01 00 00 00 34  |0.......0.`....4|
	00000070  30 01 20 01 40 00 3f e5  30 01 c0 01 01 41 40 93  |0. .@.?.0....A@.|
	00000080  30 00 c0 01 00 00 00 00  30 00 80 01 00 00 00 09  |0.......0.......|
	00000090  30 00 20 01 00 00 00 00  30 00 80 01 00 00 00 01  |0. .....0.......|
	000000a0  30 00 40 00 50 00 7f 88  00 00 00 00 00 00 00 00  |0.@.P...........|
	000000b0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|

[localhost bitstreams]$ diff andg_0.hex andg_1.hex 
	5,6c5,6
	< 00000040  2f 30 34 2f 30 38 00 64  00 09 30 30 3a 33 38 3a  |/04/08.d..00:38:|
	< 00000050  33 39 00 65 00 01 ff 88  ff ff ff ff aa 99 55 66  |39.e..........Uf|
	---
	> 00000040  2f 30 34 2f 30 38 00 64  00 09 30 30 3a 35 33 3a  |/04/08.d..00:53:|
	> 00000050  31 35 00 65 00 01 ff 88  ff ff ff ff aa 99 55 66  |15.e..........Uf|

Second generated ~12:55 AM Sun Apr 8 2012 which matches up with the local timestamp in the header


Change from an and to an or function
[localhost bitstreams]$ diff andg_0.hex org_0.hex 
	5,6c5,6
	< 00000040  2f 30 34 2f 30 38 00 64  00 09 30 30 3a 33 38 3a  |/04/08.d..00:38:|
	< 00000050  33 39 00 65 00 01 ff 88  ff ff ff ff aa 99 55 66  |39.e..........Uf|
	---
	> 00000040  2f 30 34 2f 30 38 00 64  00 09 30 30 3a 35 39 3a  |/04/08.d..00:59:|
	> 00000050  32 31 00 65 00 01 ff 88  ff ff ff ff aa 99 55 66  |21.e..........Uf|
	77c77
	< 00014000  00 00 ff cc ff ff 00 00  00 00 00 00 00 00 00 00  |................|
	---
	> 00014000  00 00 cc 00 ff ff 00 00  00 00 00 00 00 00 00 00  |................|
	111c111
	< 0001fec0  00 00 00 00 00 00 00 00  00 00 6f e1 30 00 80 01  |..........o.0...|
	---
	> 0001fec0  00 00 00 00 00 00 00 00  00 00 52 e0 30 00 80 01  |..........R.0...|

'''

def clean_null(s):
	if len(s) == 0 or s[-1] != chr(0):
		return s
	else:
		return s[0:-1]

class FrameAddress:
	def __init__(self, top, col_addr, major_addr, minor_addr, FRM_BYTE):
		# Core data
		self.col_addr = col_addr
		self.major_addr = major_addr
		self.minor_addr = minor_addr
		
		# Constant
		self.top = top
		self.FRM_BYTE = FRM_BYTE
	
	@staticmethod
	def from_word(code):
		top = xbit(code, 31, 28)
		if top != 0:
			raise ValueError("expect top to be 0")
		col_addr = xbit(code, 27, 25)
		major_addr = xbit(code, 24, 17)
		minor_addr = xbit(code, 16, 9)
		FRM_BYTE = xbit(8, 0)
		if FRM_BYTE != 0:
			raise ValueError('Expect FRM_BYTE to be 0')
		return FrameAddress(top, col_addr, major_addr, minor_addr, FRM_BYTE)

class IDCODE:
	# Device       IDCODE
	# XC3S50     0x0140D093
	XC3S50 = 0x0140D093
	# XC3S200    0x01414093
	XC3S200 = 0x01414093
	# XC3S400    0x0141C093
	XC3S400 = 0x0141C093
	# XC3S1000   0x11428093
	XC3S1000 = 0x11428093
	# XC3S1500   0x01434093
	XC3S1500 = 0x01434093
	# XC3S2000   0x01440093
	XC3S2000 = 0x01440093
	# XC3S4000   0x01448093
	XC3S4000 = 0x01448093
	# XC3S5000   0x01450093
	XC3S5000 = 0x01450093

	@staticmethod
	def id2str(i):
		m = {
			IDCODE.XC3S50: "XC3S50",
			IDCODE.XC3S200: "XC3S200",
			IDCODE.XC3S400: "XC3S400",
			IDCODE.XC3S1000: "XC3S1000",
			IDCODE.XC3S1500: "XC3S1500",
			IDCODE.XC3S2000: "XC3S2000",
			IDCODE.XC3S4000: "XC3S4000",
			IDCODE.XC3S5000: "XC3S5000",
		}
		if not i in m:
			raise ValueError('Unknown part ID %d' % i)
		
		return m[i]

class REG:
	# XAPP452:
	# Cyclic Redundancy Check          CRC  R/W 00000
	CRC = 0
	# Frame Address Register           FAR  R/W 00001
	FAR = 1
	# Frame Data Input Register        FDRI  W  00010
	FDRI = 2
	# Frame Data Output Register      FDRO   R  00011
	FDRO = 3
	# Command Register                 CMD  R/W 00100
	CMD = 4
	# Control Register                 CTL  R/W 00101
	CTL = 5
	# Mask Register                   MASK  R/W 00110
	MASK = 6
	# Status Register                  STAT  R  00111elif reg == 7:
	STAT = 7
	# Legacy Output Register          LOUT   W  01000
	LOUT = 8
	# Configuration Options Register   COR  R/W 01001
	COR = 9
	# Multiple Frame Write Register   MFWR   W  01010
	MFWR = 10
	# Frame Length Register            FLR  R/W 01011
	FLR = 11
	# (Reserved)                        -    -  01100
	RES1 = 12
	# (Reserved)                        -    -  01101
	RES2 = 13
	# Product IDCODE Register        IDCODE R/W 01110
	IDCODE = 14

	@staticmethod
	def id2str(reg):
		m = {
			REG.CRC: 'CRC',
			REG.FAR: 'FAR',
			REG.FDRI: 'FDRI',
			REG.FDRO: 'FDRO',
			REG.CMD: 'CMD',
			REG.CTL: 'CTL',
			REG.MASK: 'MASK',
			REG.STAT: 'STAT',
			REG.LOUT: 'LOUT',
			REG.COR: 'COR',
			REG.MFWR: 'MFWR',
			REG.FLR: 'FLR',
			REG.RES1: 'RES1',
			REG.RES2: 'RES2',
			REG.IDCODE: 'IDCODE',
		}
		if not reg in m:
			raise Exception('Unknown reg %d' % reg)
		
		return m[reg]
		


class CMD:
	# NULL        0000 No Operation
	NULL = 0
	
	# WCFG        0001 Write Configuration Data - Used prior to writing configuration data to the FDRI register.
	WCFG = 1
	
	# MFWR        0010 Multiple Frame Write - Performs a write of a single frame data to multiple frame addresses.
	MFWR = 2
	
	# DGHIGH/LFRM 0011 Last Frame Write - GHIGH_B is deasserted during this time. This command also can be used
	# 	             for shutdown reconfiguration.
	DHIGH = 3
	LFRM = 3
	
	# RCFG        0100 Read Configuration Data - Used prior to reading configuration data from the FDRO register.
	RCFG = 4
	
	# START       0101 Begin Startup Sequence - Starts the startup sequence, which completes configuration when
	# 	             finished. The startup sequence begins after a successful CRC check and a DESYNC
	# 	             command is performed.
	START = 5
	
	# RCAP        0110 Reset Capture - Used when performing capture in single-shot mode. This command must be
	# 	             used to reset the capture signal if signal-shot capture has been selected.
	RCAP = 6
	
	# RCRC        0111 Reset CRC - Used to reset the CRC register.
	RCRC = 7
	
	# AGHIGH      1000 Assert GHIGH_B Signal - Used prior to reconfiguration to prevent contention while writing new
	# 	             configuration data. This command is only used in non-active reconfiguration.
	AGHIGH = 8
	
	# SWITCH      1001 Switch CCLK Frequency - Changes the frequency of the master CCLK. The frequencies are
	# 	             listed in Table 6.
	SWITCH = 9
	
	# GRESTORE    1010 Pulse the GRESTORE Signal - Used to set/reset the internal IOB and CLB flip-flops.
	GRESTORE = 10
	
	# SHUTDOWN    1011 Begin Shutdown Sequence - Starts the shutdown sequence and disables the device when
	# 	             finished. Shutdown is performed on the next successful CRC check or RCRC instruction.
	SHUTDOWN = 11
	
	# GCAPTURE    1100 Pulse GCAPTURE - Causes the capture cells within the device to be loaded.
	GCAPTURE = 12
	
	# DESYNCH     1101 Reset DALIGN Signal - Used at the end of configuration to desynchronize the device.
	DESYNCH = 13
	
	@staticmethod
	def id2str(i):
		m = {
			CMD.NULL: "NULL",
			CMD.WCFG: "WCFG",
			CMD.MFWR: "MFWR",
			CMD.DHIGH: "DHIGH",
			CMD.LFRM: "LFRM",
			CMD.RCFG: "RCFG",
			CMD.START: "START",
			CMD.RCAP: "RCAP",
			CMD.RCRC: "RCRC",
			CMD.AGHIGH: "AGHIGH",
			CMD.SWITCH: "SWITCH",
			CMD.GRESTORE: "GRESTORE",
			CMD.SHUTDOWN: "SHUTDOWN",
			CMD.GCAPTURE: "GCAPTURE",
			CMD.DESYNCH: "DESYNCH",
		}
		if not i in m:
			raise ValueError('Unknown CMD ID %d' % i)
		
		return m[i]

class Header:
	# General frame
	TYPE_1 = 1
	# Used for bulk data writes
	TYPE_2 = 2


CURSE_RED = "\x1b[0;31m"
CURSE_GREEN = "\x1b[0;32m"
CURSE_BLUE = "\x1b[0;34m"
CURSE_END = "\x1b[0;39m"

def curse():
	return os.isatty(1)

def red(s):
	if not curse():
		return s
	return '%s%s%s' % (CURSE_RED, s, CURSE_END)
def green(s):
	if not curse():
		return s
	return CURSE_GREEN + s + CURSE_END
def blue(s):
	if not curse():
		return s
	return CURSE_BLUE + s + CURSE_END



