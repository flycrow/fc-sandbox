import bitstream
from dumper import DumperBase

class Bitstream:
	def __init__(self, data):
		self.data = data
	
	@staticmethod
	def from_file(fn):
		return Bitstream(open(fn).read())

	def dump(self):
		class Handler(DumperHandler):
			def __init__(self):
				DumperHandler.__init__(self)
				self.emit_pos = False
			
			def parse_begin(self, length):
				print 'Parsing %d (%x) byte file' % (length, length)			
			
			def on_first_header(self, header):
				print 'Unknown header (hex): %s' % binascii.hexlify(header)
			
			def on_header_section(self, section_type, section_len):
				print 'Section %s (len %d):' % (section_type, section_len)
			
			def on_header_a_kv(self, k, v):
				print '  %s: %s' % (k, v)
			
			def on_header_a_NCD(self, fn):
				print '  NCD file name: %s' % fn
			
			def on_header_b_device_name(self, name):
				print '  Device name: %s' % name
			
			def on_header_c_date(self, date):
				print '  Date: %s' % date

			def on_header_d_time(self, time):
				print '  Time: %s' % time
			
			def on_header_e(self, val):
				print '  data (hex): %s' % binascii.hexlify(val)
		
			def on_header_end(self, header_end):
				print 'Header end (hex): %s' % binascii.hexlify(header_end)
		
		
		
			def on_sync_word(self, sync_word):
				print 'Sync word: 0x%08X' % sync_word
		
		
			def on_type1_header(self, reg_addr, reserved, word_count):
				print '  Register address: %s (%d)' % (REG.id2str(reg_addr), reg_addr)
				print '  Reserved: %d' % reserved
				print '  Word count: %d' % word_count
		
			def on_type1_payload_raw(self, payload):
				print 'Payload: %d (0x%08X) bytes / %u bits' % (len(payload), len(payload), len(payload) * 8)
				if len(payload) <= 16:
					print '  Raw: %s' % binascii.hexlify(payload)
				else:
					print '  Raw: %s...' % binascii.hexlify(payload[0:16])
		
			def on_REG_CMD(self, cmd):
				print '  Command: %s (%d)' % (CMD.id2str(cmd), cmd)
			
			def on_REG_FAR(self, far):
				print '  Execute last command in CMD register'
				print '  top: %u' % far.top
				print '  Column adddress: %u' % far.col_addr
				print '  Major address: %u' % far.major_addr
				print '  Minor address: %u' % far.minor_addr
				print '  FRM_BYTE: %u' % far.FRM_BYTE
				
			def pstat(self, stat, prefix):
		
				if stat.ID_ERROR:
					print "%s%s" % (prefix, "ID_ERROR")
				if stat.DONE:
					print "%s%s" % (prefix, "DONE")
				if stat.INIT:
					print "%s%s" % (prefix, "INIT")
		
				# TODO: print this out
				print "%smode %u" % (prefix, stat.MODE)
		
				if stat.GHIGH_B:
					print "%s%s" % (prefix, "GHIGH_B")
				if stat.GWE:
					print "%s%s" % (prefix, "GWE")
				if stat.GTS_CFG:
					print "%s%s" % (prefix, "GTS_CFG")
				if stat.IN_ERROR:
					print "%s%s" % (prefix, "IN_ERROR")
				if stat.DCI_MATCH:
					print "%s%s" % (prefix, "DCI_MATCH")
				if stat.DCM_LOCK:
					print "%s%s" % (prefix, "DCM_LOCK")
				if stat.RES1:
					print "%s%s" % (prefix, "RES1")
				if stat.CRC_ERROR:
					print "%s%s" % (prefix, "CRC_ERROR")
			
			def on_REG_MASK(self, stat):
				print '  Bit set when allowed to write STAT position'
				self.pstat(stat, '  ')
		
			def on_REG_STAT(self, stat):
				self.pstat(stat, '  ')

			def on_REG_FLR_raw(self, fl):
				# I don't really get why this is off by 1 but the app note is pretty clear
				# and read bit length matches the X3S200 table after adjustment
				print '  Frame length: %d words / %d bits (raw %d)' % (fl + 1, (fl + 1) * 32, fl)
				
			def on_REG_FLR(self, fl):
				pass
		
			def packet_begin_header(self, header, begin_pos):
				print
				pos = ''
				if self.emit_pos:
					pos = ' @ 0x%08X' % begin_pos
				print 'Packet header (0x%08X)%s' % (header, pos)
			
			def header_type_str(self, t):
				if t == Header.TYPE_1:
					return 'type 1'
				elif t == Header.TYPE_2:
					return 'type 2'
				else:
					return 'unknown'
				
			def OSCFSEL2str(self, i):
				'''
				Table 6: OSCFSEL-Specified Master CCLK Settings
					  CCLK (MHz)              OSCFSEL
				 3                    X10x
				 6                    X000
				 12                   X001
				 25                   X010
				 50                   X011
				 100                  X11x
				'''
				if i & 0x06 == 0x04:
					return '3 MHz'
				elif i & 0x07 == 0x00:
					return '6 MHz'
				elif i & 0x07 == 0x01:
					return '12 MHz'
				elif i & 0x07 == 0x02:
					return '25 MHz'
				elif i & 0x07 == 0x03:
					return '50 MHz'
				elif i & 0x06 == 0x06:
					return '100 MHz'
				else:
					raise ValueError('Uknown OSCFSEL value')
			
			def on_REG_COR(self, cor):
			 	print '  CRC_BYPASS %d: ' % cor.CRC_BYPASS,
				if cor.CRC_BYPASS:
				 	print 'do not check CRC'
	 			else:
				 	print 'check CRC'

			 	print '  DONE_PIPE %d: ' % cor.DONE_PIPE,
				if cor.DONE_PIPE:
				 	print 'add pipeline stage for DONEIN'
	 			else:
				 	print 'no pipeline stage for DONEIN'
				 
				print '  DRIVE_DONE %d: ' % cor.DRIVE_DONE,
				if cor.DRIVE_DONE:
				 	print 'actively driven high' 
	 			else:
				 	print 'open drain'
				 	
				print '  SINGLE %d: ' % cor.SINGLE,
				if cor.SINGLE:
				 	print 'readback is one-shot, use RCAP for multiple reads'
	 			else:
				 	print 'readback is not one shot'
				
				print '  OSCFSEL %d: %s' % (cor.OSCFSEL, self.OSCFSEL2str(cor.OSCFSEL))
			
			def on_REG_IDCODE(self, code):
				print '  Part: %s (%d)' % (IDCODE.id2str(code), code)
			
			def begin_header2(self, word_count):
				print '  Word count: %d' % word_count
				bytes = word_count * 4
				# datasheet lists 1,043,040, 1,047,616 including overhead
				# 1,044,736 bits
				print 'Payload: %d (0x%08X) bytes / %u bits' % (bytes, bytes, bytes * 8)
			
			def end_header2(self, crc):
				print '  Pad (/ CRC?) 0x%08X' % crc
			
			def packet_begin(self, t, op):
				print '  Type: %s (%d)' % (self.header_type_str(t), t)
				print '  Operation: %d' % op
				# What is the other bit?
				# no doc on what this field is but I think I got the R/W part
				print '    Unknown bit: %d' % ((op >> 0) & 0x01)
				if op & 0x02:
					print '    Write'
				else:
					print '    Read'
			
			def begin_FDRI(self, frame_size, start_addr):
				print 'FDRI @ (col %u, major %u, minor %u) and size 0x%08X' % (
						start_addr.col_addr, start_addr.major_addr, start_addr.minor_addr,
						frame_size)
				#sys.exit(1)
			
		BitstreamDumper(self, Handler()).dump()

class DumperHandler:
	def __init__(self):
		pass

	def on_REG_CMD(self, cmd):
		'''Called every time a command request is made'''


class BitstreamDumper(DumperBase):
	def __init__(self, bitstream, handler):
		self.bitstream = bitstream
		self.data = self.bitstream.data
		self.pos = 0
		self.expecting_type_2 = False
		self.handler = handler
		self.strict = True
		self.FL = None
		self.frame_start = None
		
	def parse_stat(self, val):
		class STAT:
			pass
		stat = STAT()
		
		high = xbit(val, 31, 14)
		if high:
			raise ValueError("High bits should all be 0")
		
		'''
		ID_ERROR   13  IDCODE not validated while trying to write the FDRI
					   register
		DONE       12  Input from the DONE pin
		INIT       11  Input from the INIT pin
		MODE      10:8 Input from the MODE pins (M2:M0)
		GHIGH_B     7  Status of GHIGH_B (0 = asserted)
		GWE         6  Status of GWE (0 = all FFs and Block RAMs are write-
					   disabled)
		GTS_CFG     5  Status of GTS_CFG_B (0 = all I/Os are 3-stated)
		IN_ERROR   4   Legacy input error. This error occurs when serial data
					   is loaded too fast.
		DCI_MATCH  3   DCI is matched. This bit is a logical AND function of all
					   the MATCH signals (one per bank). If no DCI I/Os are
					   in a particular bank, then a 1 is used.
		DCM_LOCK    2  DCMs are locked. This bit is a logical AND function of
					   all the LOCKED signals. If DCM is not used, then a 1
					   is used.
		CRC_ERROR   0  CRC error
		'''
		stat.ID_ERROR = xbit(val, 13)
		stat.DONE = xbit(val, 12)
		stat.INIT = xbit(val, 11)
		stat.MODE = xbit(val, 10, 8)
		stat.GHIGH_B = xbit(val, 7)
		stat.GWE = xbit(val, 6)
		stat.GTS_CFG = xbit(val, 5)
		stat.IN_ERROR = xbit(val, 4)
		stat.DCI_MATCH = xbit(val, 3)
		stat.DCM_LOCK = xbit(val, 2)
		stat.RES1 = xbit(val, 1)
		stat.CRC_ERROR = xbit(val, 0)
		
		return stat
		
	def parse_packet(self):
		'''
		Table 9: Bitstream Start and Configuration Options for XC3S400
		Data Description                             	  Data Field
		Dummy Word										  0xFFFFFFFF(1)
		Synchronization Word                              0xAA995566
		CMD Write Packet Header                           0x30008001
		CMD Write Packet Data (Reset CRC)                 0x00000007
		FLR Write Packet Header                           0x30016001
		FLR Write Packet Data							  0x00000044(2)
		COR Write Packet Header                           0x30012001
		COR Write Packet Data							  0x00003FE5(2)
		IDCODE Write Packet Header                        0x3001C001
		IDCODE Write Packet Data (3S400)				  0x0141C093(2)
		MASK Write Packet Header                          0x3000C001
		MASK Write Packet Data							  0x00000000(2)
		CMD Write Packet Header                           0x30008001
		CMD Write Packet Data (Switch CCLK)               0x00000009
		FAR Write Packet Header                           0x30002001
		FAR Write Packet Data                             0x00000000
		CMD Write Packet Header                           0x30008001
		CMD Write Packet Data (WCFG)                      0x00000001
		
		(1): varies between releases
		(2): This value may be different based on device/design options.
		'''
	
	
		'''
		32 bit header
			31:29: type
			28:27: op
			26:13: reg addr
			12:11: reserved
			10:0: word count
		'''
		begin_pos = self.pos
		header = self.uint32()
		self.handler.packet_begin_header(header, begin_pos)
		t = (header >> 29) & 0x7
		op = (header >> 27) & 0x3
		self.handler.packet_begin(t, op)
		
		if t == Header.TYPE_1:
			reg_addr = (header >> 13) & 0x3FFF
			reserved = (header >> 11) & 0x3
			word_count = (header >> 0) & 0x7FF
			
			if reserved != 0:
				raise ValueError('WARNING: reserved not 0')
			
			self.handler.on_type1_header(reg_addr, reserved, word_count)
			
			# Actual payload in 4 byte word length
			payload = self.consume(word_count * 4)
			# Must be padded to 32 bit boundries
			#padding = self.consume((4 - word_count) % 4)
			self.handler.on_type1_payload_raw(payload)
				
			if reg_addr == REG.CRC:
				pass
			elif reg_addr == REG.FAR:
				code = self.str2u32(payload)
				far = FrameAddress.from_word(code)
				self.frame_start = far
				self.handler.on_REG_FAR(far)
			elif reg_addr == REG.FDRI:
				pass
			elif reg_addr == REG.FDRO:
				pass
			elif reg_addr == REG.CMD:
				code = self.str2u32(payload)
				self.handler.on_REG_CMD(code)
			elif reg_addr == REG.CTL:
				pass
			elif reg_addr == REG.MASK:
				code = self.str2u32(payload)
				self.handler.on_REG_MASK(self.parse_stat(code))
			elif reg_addr == REG.STAT:
				code = self.str2u32(payload)
				self.handler.on_REG_STAT(self.parse_stat(code))
			elif reg_addr == REG.LOUT:
				pass
			elif reg_addr == REG.COR:
				'''
				Table 5: COR Values
					   Name        Bit Indices                         Description
				 CRC_BYPASS             29     0: CRC used (Default)
								               1: Does not check against updated CRC value
				 DONE_PIPE              25     0: No pipeline stage for DONEIN (Default)
								               1: Add pipeline stage for DONEIN. The FPGA waits for
								               DONE, which is delayed by one StartupClk cycle. Use
								               this option when StartupClk is running at high speeds
				 DRIVE_DONE             24     0: DONE pin is open drain (Default)
								               1: DONE is actively driven High
				 SINGLE                 23     0: Readback is not one-shot. Newly captured values are
								               loaded on each successive CAP assertion on the
								               CAPTURE_SPARTAN3 primitive. Capture can also be
								               performed with the GCAPTURE instruction in the CMD
								               register. (Default)
								               1: Readback is one-shot. The RCAP instruction must be
								               loaded into the CMD register between successive
								               readbacks.
				 OSCFSEL              22:19    Select CCLK frequency in Master configuration modes
								               (see Table 6)
				 SSCLKSRC             16:15    Startup sequence clock source:
								               00: CCLK (Default)
								               01: UserClk (connection on the STARTUP_SPARTAN3
								               block)
								               1x: JTAGClk
				 DONE_CYCLE           14:12    Startup phase in which the DONE pin is released
				 MATCH_CYCLE           11:9    Stall in this startup phase until the DCI is matched
				 LOCK_CYCLE             8:6    Stall in this startup phase until DCMs are locked
				 GTS_CYCLE              5:3    Startup phase in which the Global 3-State (GTS) is
								               deasserted
				 GWE_CYCLE              2:0    Startup phase in which the Global Write Enable (GWE)
								               is asserted
				'''

				code = self.str2u32(payload)
				
				class COR:
					pass
				cor = COR()
				cor.CRC_BYPASS = xbit(code, 29)
				cor.DONE_PIPE = xbit(code, 25)
				cor.DRIVE_DONE = xbit(code, 24)
				cor.SINGLE = xbit(code,  23)
				cor.OSCFSEL = xbit(code, 22, 19)
				cor.SSCLKSRC = xbit(code, 16, 15)
				cor.DONE_CYCLE = xbit(code, 14, 12)
				cor.MATCH_CYCLE = xbit(code, 11, 9)
				cor.LOCK_CYCLE = xbit(code, 8, 6)
				cor.GTS_CYCLE = xbit(code, 5, 3)
				cor.GWE_CYCLE = xbit(code, 2, 0)
 
 				self.handler.on_REG_COR(cor)

			elif reg_addr == REG.MFWR:
				pass
			elif reg_addr == REG.FLR:
				fl = self.str2u32(payload)
				self.handler.on_REG_FLR_raw(fl)
				self.FL = fl
				self.handler.on_REG_FLR(fl + 1)
			elif reg_addr == REG.RES1:
				raise Exception('Reserved instruction')
			elif reg_addr == REG.RES2:
				raise Exception('Reserved instruction')
			elif reg_addr == REG.IDCODE:
				code = self.str2u32(payload)
				self.handler.on_REG_IDCODE(code)
			else:
				raise Exception('Unknown reg')
			
			'''
			"A Type 2 header must immediately follow a Type 1 header with Word Count = 0."
			'''
			self.expecting_type_2 = word_count == 0
		elif t == Header.TYPE_2:
			if not self.expecting_type_2:
				raise Exception('Type 1 header with word count 0 must precede type 2 header')
			
			word_count = (header >> 0) & 0x7FFFFFF
			
			self.handler.begin_header2(word_count)
			
			if self.FL is None:
				raise Exception("Can't parse packets without frame length")
			if self.frame_start is None:
				raise Exception("Can't parse packets without an address")
			
			
			# Actual payload
			payload = self.consume(word_count * 4)
			# Must be padded to 32 bit boundries
			#padding = self.consume((4 - word_count) % 4)
			# TODO: check that the payload is a multiple of the frame length
			FDRI_parser(payload, self.handler, self.FL, self.frame_start).run()
			
			
			# Pad frame that gets eaten so that the last frame can load to let the pipeline sufficiently finish
			# However other doc says the last word is automatically treated as CRC
			# note no-CRC should be written 0xDEFC
			pad = self.uint32()
			self.handler.end_header2(pad)
		else:
			raise Exception('Unknown header type %d @ %d (0x%04X)' % (t, self.pos, self.pos))
		
	def parse_header(self):
		header = self.consume(13)
		
		self.handler.on_first_header(header)
		
		#if data[14] != 0x00:
		#	raise ValueError('Missing table start marker')
		section_type = None
		so_far = set()
		# Break on getting section e since thats the last clear area
		while True:
			# Parse token
			# Really this is intended to be a string I guess but in practice its a single char
			token = self.token()
			
			# New section type?
			if len(token) != 1:
				raise Exception('Expecting single char section type')
			
			if not section_type is None and token != chr(ord(section_type) + 1):
				print 'Section type: %s' % section_type
				print 'Token: %s' % token
				raise Exception("Expect section types to be increasing")
			section_type = token
			if self.strict and section_type in so_far:
				raise Exception('Already found section of type %s' % section_type)
			so_far.add(section_type)
			
			# I was half expecting a null terminated base 10 string giving the record length
			# 00000040  XX XX XX XX XX XX XX 64  00 09 30 30 3a 35 33 3a  |XXXXXXXd..00:53:|

			section_len = self.byte()
			'''
			if data[pos] != chr(0):
				raise Exception('Expect 0 after record len')
			'''

			self.handler.on_header_section(section_type, section_len)
			payload = self.consume(section_len)
			
			# Last known section
			if section_type == 'a':
				'''
				00000000  00 09 0f f0 0f f0 0f f0  0f f0 00 00 01 61 00 1b  |.............a..|
				00000010  61 6e 64 67 2e 6e 63 64  3b 55 73 65 72 49 44 3d  |andg.ncd;UserID=|
				00000020  30 78 46 46 46 46 46 46  46 46 00 62 00 0b 33 73  |0xFFFFFFFF.b..3s|
				'''
				payload = clean_null(payload)
				for part in payload.split(';'):
					if part.find('=') >= 0:
						parts = part.split('=')
						k = parts[0]
						v = parts[1]
						self.handler.on_header_a_kv(k, v)
					else:
						self.handler.on_header_a_NCD(part)
			elif section_type == 'b':
				'''
				00000020  30 78 46 46 46 46 46 46  46 46 00 62 00 0b 33 73  |0xFFFFFFFF.b..3s|
				00000030  32 30 30 66 74 32 35 36  00 63 00 0b 32 30 31 32  |200ft256.c..2012|
				
				0x0b => vertical tab
				Must be the chars + the null
				'''
				payload = clean_null(payload)
				self.handler.on_header_b_device_name(payload)
			elif section_type == 'c':
				'''
				00000030  32 30 30 66 74 32 35 36  00 63 00 0b 32 30 31 32  |200ft256.c..2012|
				00000040  2f 30 34 2f 30 38 00 64  00 09 30 30 3a 35 33 3a  |/04/08.d..00:53:|
				
				0x0b => vertical tab
				almost number of chars
				2012/04/09 => 10 chars but 0b is 11...hmm.  Includes null?
				'''
				payload = clean_null(payload)
				self.handler.on_header_c_date(payload)
			elif section_type == 'd':
				'''
				00000040  2f 30 34 2f 30 38 00 64  00 09 30 30 3a 35 33 3a  |/04/08.d..00:53:|
				00000050  31 35 00 65 00 01 ff 88  ff ff ff ff aa 99 55 66  |15.e..........Uf|
				'''
				payload = clean_null(payload)
				self.handler.on_header_d_time(payload)
			elif section_type == 'e':
				'''
				01 ff
				02 25 fc
				if len(payload) != 1:
					raise Exception('Different data than expected')
				'''
				payload = clean_null(payload)
				self.handler.on_header_e(payload)
				# e is the last record
				break
			else:
				raise Exception('Unknown section type %s' % section_type)
		
	def dump(self):
		# First 14 bytes unknown function, always the same for my simple tests
		# 	00000000  00 09 0f f0 0f f0 0f f0  0f f0 00 00 01 61 00 1b  |.............a..|

		'''
		Next header has some info
		00000000  00 09 0f f0 0f f0 0f f0  0f f0 00 00 01 61 00 1b  |.............a..|
		00000010  61 6e 64 67 2e 6e 63 64  3b 55 73 65 72 49 44 3d  |andg.ncd;UserID=|
		00000020  30 78 46 46 46 46 46 46  46 46 00 62 00 0b 33 73  |0xFFFFFFFF.b..3s|
		00000030  32 30 30 66 74 32 35 36  00 63 00 0b 32 30 31 32  |200ft256.c..2012|
		00000040  2f 30 34 2f 30 38 00 64  00 09 30 30 3a 35 33 3a  |/04/08.d..00:53:|
		00000050  31 35 00 65 00 01 ff 88  ff ff ff ff aa 99 55 66  |15.e..........Uf|
		
		NCD: native circuit description
			http://www.xilinx.com/support/documentation/sw_manuals/xilinx11/ise_c_implement_fpga_design.htm
			Containers a description of how the device is structured at a low level
			Differs from bitstream in that it says the what but not how to get the FPGA into that state
		
		Ah I get it now
		there are record sections
		starts in the first 16 bytes
		null code null
		a - e
		
		format is
		Single printable letter indicating the record type, a - e
		Next byte is record length in bytes
		Strings actually have the null character in the file and must be included in the length
		
		'''
		
		
		'''
		14 byte initial header
		00 09 0f f0 0f f0 0f f0  0f f0 00 00 01
		
		does the 09 have anything to do with the length following?  There are a few more
		'''
		data = self.data
		self.handler.parse_begin(len(data))
		
		self.parse_header()
			
		'''
		Part after but before commands begin
		How do I know how long this is suppose to be? 
		Based on the sync word comment below I'm guessing you are suppose to parse until that magic value
		Has a dummy word before it
		but what the heck is the 88?
		
		00000050  XX XX XX XX XX XX XX 88  ff ff ff ff aa 99 55 66  |XXXXXXX.......Uf|
		
		Using debug flag e entry has two bytes and the next byte is consumed
		but the overall file position where the sync word starts remains constant
		'''
		sync_pos = self.find('\xaa\x99\x55\x66')
		if sync_pos < 0:
			raise ValueError("Couldn't find sync word")
		header_end = self.consume_to(sync_pos)
		self.handler.on_header_end(header_end)
	
		'''
		"Synchronization Word": 0xAA995566
		XAPP452 page 10
		
		"The Spartan-3 FPGA configuration logic processes everything 
		on 32-bit boundaries, and the Sync Word effectively indicates 
		where those boundaries lie.
		'''
		sync_word = self.uint32()
		SYNC_WORD = 0xAA995566
		if sync_word != SYNC_WORD:
			raise ValueError('Incorrect sync word')
		self.handler.on_sync_word(sync_word)
	
		'''
		Fun time
		We are now at the FPGA command section
		'''
		while not self.end():
			'''
			The following four operations must be performed successfully in order for the device to enter
			the startup sequence:
			1. Write to the COR register to program the desired startup sequence.
			2. Write the START command to the CMD register.
			3. Write a CRC checksum to the CRC register.
			4. Write the DESYNCH command to the CMD register.
			'''
			self.parse_packet()


'''
Frame Data Input Register (FDRI)
Specifies FPGA main configuration to configure LUTs and such

FDRI can come from either type1 or type2 packets
since type2 can do everything a type1 can do except bigger not sure how common type1 is

Should this be a low level parser that doesn't track FAR?
For common usage will want to know addr and not care how we got there
If need a lower level parser simplify later

This will all be XC3S200 specific for now
'''
class FDRI_parser(DumperBase):
	def __init__(self, payload, handler, frame_size, start_addr):
		DumperBase.__init__(self)
		
		self.handler = handler
		self.data = payload
		# in words
		self.frame_size = frame_size
		self.start_addr = start_addr
	
	def run(self):
		self.handler.begin_FDRI(self.frame_size, self.start_addr)
		
		print
		all_frames = 0
		processed_frames = 0
		'''
		Frames of all 0's are NOPs
		
		31 non-boring frames for my simple 2-and and 1-high example
		Maybe I should route something that requires less interconnect?
		1 high would be a good start
		
		
		andg_0.bit
		Found 628 frames
		  processed: 31
		  boring: 597
		
		high_0.bit
			output P12 (LD6) tied high
		
			Found 628 frames
			  processed: 8
			  boring: 620
			  
			  
			Frame 5 @ 0x000004E0
			Raw: 00000000000000000000000000000000180000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

			Frame 335 @ 0x00011100
			Raw: 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000880000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

			Frame 336 @ 0x000111D0
			Raw: 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

			Frame 340 @ 0x00011510
			Raw: 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

			Frame 341 @ 0x000115E0
			Raw: 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

			Frame 342 @ 0x000116B0
			Raw: 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

			Frame 346 @ 0x000119F0
			Raw: 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

			Frame 348 @ 0x00011B90
			Raw: 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
			  
		high_1.bit
			output P13 (LD4) tied high
			
			Frame 5 @ 0x000004E0
			Raw: 00000000000000000000000000000000180000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

			Frame 335 @ 0x00011100
			Raw: 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000880000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

			Frame 336 @ 0x000111D0
			Raw: 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

			Frame 340 @ 0x00011510
			Raw: 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

			Frame 341 @ 0x000115E0
			Raw: 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

			Frame 342 @ 0x000116B0
			Raw: 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

			Frame 346 @ 0x000119F0
			Raw: 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

			Frame 348 @ 0x00011B90
			Raw: 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
		
		
		[localhost bitstreams]$ diff high_0.hex high_1.hex 
			Compile time expected to differ
				5,6c5,6
				< 00000040  2f 30 34 2f 30 38 00 64  00 09 32 33 3a 33 32 3a  |/04/08.d..23:32:|
				< 00000050  31 31 00 65 00 01 ff 88  ff ff ff ff aa 99 55 66  |11.e..........Uf|
				---
				> 00000040  2f 30 34 2f 30 38 00 64  00 09 32 33 3a 35 36 3a  |/04/08.d..23:56:|
				> 00000050  34 33 00 65 00 01 ff 88  ff ff ff ff aa 99 55 66  |43.e..........Uf|
			
			17,18c17,18
			< 00011110  00 00 00 00 00 00 08 80  00 00 00 00 00 00 00 00  |................|
			< 00011120  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
			---
			> 00014040  00 00 00 00 00 00 01 10  00 00 00 00 00 00 00 00  |................|
			> 00014050  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
			20,21c20,22
			< 000111e0  00 00 00 00 00 00 00 00  00 00 00 80 00 00 00 00  |................|
			< 000111f0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
			---
			> 00014110  00 00 00 00 00 00 00 00  00 00 01 00 00 00 00 00  |................|
			> 00014120  00 00 02 80 00 00 00 00  00 00 00 00 00 00 00 00  |................|
			> 00014130  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
			23,24c24,25
			< 00011530  00 00 00 00 00 00 00 00  00 00 00 00 00 00 03 00  |................|
			< 00011540  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
			---
			> 00014470  00 00 0a 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
			> 00014480  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
			26,27c27,28
			< 00011610  00 00 08 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
			< 00011620  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
			---
			> 00014610  00 00 00 00 00 00 00 00  00 00 03 00 00 00 00 00  |................|
			> 00014620  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
			29,38c30
			< 000116e0  00 00 00 00 00 00 01 00  00 00 00 00 00 00 00 00  |................|
			< 000116f0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
			< *
			< 00011a30  00 00 00 00 00 00 08 00  00 00 00 00 00 00 00 00  |................|
			< 00011a40  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
			< *
			< 00011bd0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 80  |................|
			< 00011be0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
			< *
			
			Checksum expected to differ
				< 0001fec0  00 00 00 00 00 00 00 00  00 00 e1 98 30 00 80 01  |............0...|
				---
				> 0001fec0  00 00 00 00 00 00 00 00  00 00 40 50 30 00 80 01  |..........@P0...|
		
		
		
		
		'''
		
		'''
Table 13: frame address scheme

Column	TERM_L	IOI_L	CLB		BRAM_INIT	BRAM	CLB		GCLK_L	CLB   CENTER	CLB GCLK_R	CLB		BRAM_INIT BRAM	CLB		IOR_R	TERM_R
Block	0		0		0		2			1		0		0		0	  0			0	0		0		2		  1		0		0		0
Major	1		2		3		0			0		4		0		5	  0	 		6   0		7		1		  1		8		9		10
Minor	0-1		0-18	0-18	0-18		0-75	0-18	0		0-18	2		0-18 1		0-18	0-18	  0-75	0-18	0-18	0-1
		
		
		For large frame writes, internal counters automatically increment the frame address
		starting with the Minor address, the Major address, and lastly the Block address.
		'''
		
		# all 0's / don't configure anything
		boring_frames = 0
		while not self.end():
			frame = self.consume(self.frame_size * 4)
			# Is it a nop frame?
			boring = True
			for byte in frame:
				boring = ord(byte) == 0
				if not boring:
					break
			if boring:		
				boring_frames += 1
				all_frames += 1
				continue
				
			print
			
			frame_n = all_frames
			print 'Frame %u @ 0x%08X' % (frame_n, self.pos)
			if 0:
				print 'Raw: %s' % binascii.hexlify(frame)
			else:
				row_w = 1
				print 'Raw:'
				for i in range(0, len(frame), row_w):
					this_bin = frame[i:i+row_w]
					print '  %04X:%04X: ' % (frame_n, i),
					for j in range(len(this_bin)):
						if j == row_w / 2 and j != 0:
							print '' ,
						h = binascii.hexlify(this_bin[j]).upper()
						if h == '00':
							print h ,
						else:
							print blue(h) ,
					print
		
			processed_frames += 1
			all_frames += 1
			#break
		print
		# Suppose to be 615 but I'm getting 628...hmm
		print 'Found %u frames' % all_frames
		print '  processed: %u' % processed_frames
		print '  boring: %u' % boring_frames
		if 1:
			print 'Debug break'
			sys.exit(0)
		


	
