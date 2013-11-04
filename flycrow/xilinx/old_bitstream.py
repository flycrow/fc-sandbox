'''
Raw bit file
	ASCII encoded 0/1'
	75 bits / main line
		Datasheet lists 71 bits / frame
		
	All begin with 0
	168 - 9 + 1 = 160 main lines
	40 bit header
	16 bit footer
	Net bits: 40 + 160 * 75 + 16 = 12056 bits
	Datasheet lists 12038
		18 bit difference...hmm


Comparing raw bit to .BIT
	.BIT
		00000070  00 00 00 00 00 30 ff 20  02 f1 1f 75 fd fe ff fe  |.....0. ...u....|
	.RBT first data line
		1111111100100000000000101111000100011111
		1111 F
		1111 F
		0010 2
		0000 0
		0000 0
		0010 0
		1111 F
		0001 1
		0001 1
		1111 F
		FF 20 00 F1 1F
		
		00 00 00 00 00 30 some sort of header then?

dsuer.pdf has some interesting info in 6-5: "Configuration, Length Count, and Debugging: Data Format"
	The 40-bit header of a single device bitstream 
	begins with a minimum of eight ones (dummy bits) 
	followed by a 0010 preamble. 
	A 24-bit length count follows the preamble. 
	The header ends with a 4-bit separator field of ones.

	XC2000
		Tail bits are 1111
		Each frame begins with 0 start bit
		3 1's as stop bits
		4 1's as tail bits
		End bits includes tail and pad bits
		So 8 bits total
			1 start
			3 stop
			4 tail
		Swapping
			All its really saying is that the LSB is transmitted first on each byte
		Length count
			DONE method
				Init LC and then ad 40 for 40 bit header
				Add (bits per frame) * (number of frames) to LC using the values given for the particular device
				Add number of tailbits to LC, where the number of tail bits is 4 for XC2000 and XC3000 parts, and 5 for XC4000 and XC5200 parts
				Add K
					3: XC2000
					Something related to daisy chaining
				Add byte alignment pad value P to LC
					P = 0: LC evenly divisible by 8
					P = n: where n is number of bits to make divisible by 8
				Subtract K
				Ex:
					XC2018: 17885
						(40) + [((91)*(196)) + (4)] + (0) + (K=3) + (P=5) - (K=3)
					Config bits reported as 17878
						17885 - 17878 = 7
					Padding and not important
					Something to do with K and tail bits
			Length count alignment
				XC2018: 17881
Summary
	Device		Non-data bits
	XC2018		826		
	XC2064		678		

XC2000.pdf
	Device		Logic (gates)	CLBs	Max IOBs	Config bits
	XC2018		1000-1500		100		74			17878
	XC2064		600-1000		64		58			12038

XC2000FM.pdf
	Agrees on config bits
				Config frames		Data bits / frame 	Net data bits
	XC2018		196					87					17052
	XC2064		160					71					11360

	Header
		11111111					Dummy Bits (4 Bits Minimum), XACT 2.10 Generates 8 Bits
		0010                       	Preamble Code                                                        
		<24-Bit Length Count>		Configuration Program Length
		1111						Dummy Bits (4 Bits Minimum)
	Program data
		0 <Data Frame # 001> 111
		0 <Data Frame # 002> 111
		0 <Data Frame # 003> 111...
		...		                                             
		0 <Data Frame # 159> 111
		0 <Data Frame # 160> 111
		1111                              Postamble Code (4 Bits Minimum)

Start-Up Requires Three Configuration Clocks Beyond Length Count

ff 20 02 f1 1f
	ff: 8 dummy 1's
	20: preamble
	02 f1 1f: length => 192799, but XC2064 only has 12038
		Should be 00 2F 06 (012038)?

Human pattern matching says the array goes
	First: 0x0079
	Last: 0x0674
	Net bits: (0x0674 - 0x0079 + 1) * 8 = 12256
		Suppose to have only 11360...hmmm
		896 extra bits
		Possibly doesn't include the 

XC2064 bitstream example
00000000  f0 0f f0 0f f0 0f f0 0f  00 32 30 36 34 50 43 36  |.........2064PC6|
00000010  38 00 00 00 00 00 31 31  32 2f 30 39 2f 30 33 31  |8.....112/09/031|
00000020  32 3a 30 31 3a 34 33 00  46 49 52 53 54 50 41 52  |2:01:43.FIRSTPAR|
00000030  2e 6c 63 61 00 00 00 00  00 00 00 00 00 00 00 00  |.lca............|
00000040  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
00000070  00 00 00 00 00 30 ff 20  02 f1 1f 75 fd fe ff fe  |.....0. ...u....|
00000080  ff 7f 7f ff ed bf bf df  ff df ef ef ff fd ff ef  |................|
00000090  f7 f7 f7 fb fb fb ff bf  ff ff ff ff ff ff ff ff  |................|
000000a0  f7 ff bf df df df ef ef  ef fe ff ff ff ff ff ff  |................|
000000b0  ff ff ff df ff ff ff ff  ff ff ff ff fb ff ff ff  |................|
000000c0  ff ff ff ff ff ff 7f ff  ff ff ff ff ff ff ff ef  |................|
000000d0  ff ff ff ff ff ff ff ff  fd ff ff ff ff ff ff ff  |................|
000000e0  ff ff bf ff ff ff ff ff  ff ff ff f7 ff ff ff ff  |................|
000000f0  ff ff ff ff fe ff ff ff  ff ff ff ff ff ff df ff  |................|
00000100  ff ff ff ff ff ff ff fb  ff ff ff ff ff ff ff ff  |................|
00000110  ff 3f ff ff ff ff ff ff  ff fe ef 5f 5f af af af  |.?.........__...|
00000120  d7 d7 d7 fc ff ff ff ff  ff ff ff ff fb bf ff ff  |................|
00000130  ff ff ff ff ff ff f7 ff  ff ff ff ff ff ff ff fe  |................|
00000140  ff ff ff ff ff ff ff ff  ff cf ff ff ff ff ff ff  |................|
00000150  ff ff b9 ff ff ff ff ff  ff ff ff f7 3e fe ff 7f  |............>...|
00000160  7f 7f bf bf be ef ff ff  ff ff ff ff ff ff fd ff  |................|
00000170  ff ff ff ff ff ff ff ff  bf ff ff ff ff ff ff ff  |................|
00000180  ff f7 ff ff ff ff ff ff  ff ff fe ff ff ff ff ff  |................|
00000190  ff ff ff ff df ff ff ff  ff ff ff ff ff fb ff ff  |................|
000001a0  ff ff ff ff ff ff ff 7f  ff ff ff ff ff ff ff ff  |................|
000001b0  ef ff ff ff ff ff ff ff  ff fc ff ff ff ff ff ff  |................|
000001c0  ff ff fb bd 7d 7e be be  bf 5f 5f 5f f3 ff ff ff  |....}~...___....|
000001d0  ff ff ff ff ff ee ff ff  ff ff ff ff ff ff ff df  |................|
000001e0  ff ff ff ff ff ff ff ff  fb ff ff ff ff ff ff ff  |................|
000001f0  ff ff 3f ff ff ff ff ff  ff ff fe e7 ff ff ff ff  |..?.............|
00000200  ff ff ff ff dc fb fb fd  fd fd fe fe fe fb bf ff  |................|
00000210  ff ff ff ff ff ff ff f7  ff ff ff ff ff ff ff ff  |................|
00000220  fe ff ff ff ff ff ff ff  ff ff df ff ff ff ff ff  |................|
00000230  ff ff ff fb ff ff ff ff  ff ff ff ff ff 7f ff ff  |................|
00000240  ff ff ff ff ff ff ef ff  ff ff ff ff ff ff ff fd  |................|
00000250  ff ff ff ff ff ff ff ff  ff bf ff ff ff ff ff ff  |................|
00000260  ff ff f7 ff ff ff ff ff  ff ff ff fe ff ff ff ff  |................|
00000270  ff ff ff ff ff cf ff ff  ff ff ff ff ff ff bb d7  |................|
00000280  d7 eb eb eb f5 f5 f5 ff  3f ff ff ff ff ff ff ff  |........?.......|
00000290  fe ef ff ff ff ff ff ff  ff ff fd ff ff ff ff ff  |................|
000002a0  ff ff ff ff bf ff ff ff  ff ff ff ff ff f3 ff ff  |................|
000002b0  ff ff ff ff ff ff ee 7f  ff ff ff ff ff ff ff fd  |................|
000002c0  cf bf bf df df df ef ef  ef bb ff ff ff ff ff ff  |................|
000002d0  ff ff ff 7f ff ff ff ff  ff ff ff ff ef ff ff ff  |................|
000002e0  ff ff ff ff ff fd ff ff  ff ff ff ff ff ff ff bf  |................|
000002f0  ff ff ff ff ff ff ff ff  f7 ff ff ff ff ff ff ff  |................|
00000300  ff fe ff ff ff ff ff ff  ff ff ff df ff ff ff ff  |................|
00000310  ff ff ff ff fb ff ff ff  ff ff ff ff ff ff 3f ff  |..............?.|
00000320  ff ff ff ff ff ff fe ef  5f 5f af af af d7 d7 d7  |........__......|
00000330  fc ff ff ff ff ff ff ff  ff fb bf ff ff ff ff ff  |................|
00000340  ff ff ff f7 ff ff ff ff  ff ff ff ff fe ff ff ff  |................|
00000350  ff ff ff ff ff ff cf ff  ff ff ff ff ff ff ff b9  |................|
00000360  ff ff ff ff ff ff ff ff  f7 3e fe ff 7f 7f 7f bf  |.........>......|
00000370  bf be ef ff ff ff ff ff  ff ff ff fd ff ff ff ff  |................|
00000380  ff ff ff ff ff bf ff ff  ff ff ff ff ff ff f7 ff  |................|
00000390  ff ff ff ff ff ff ff fe  ff ff ff ff ff ff ff ff  |................|
000003a0  ff df ff ff ff ff ff ff  ff ff fb ff ff ff ff ff  |................|
000003b0  ff ff ff ff 7f ff ff ff  ff ff ff ff ff ef ff ff  |................|
000003c0  ff ff ff ff ff ff fc ff  ff ff ff ff ff ff ff fb  |................|
000003d0  bd 7d 7e be be bf 5f 5f  5f f3 ff ff ff ff ff ff  |.}~...___.......|
000003e0  ff ff ee ff ff ff ff ff  ff ff ff ff df ff ff ff  |................|
000003f0  ff ff ff ff ff fb ff ff  ff ff ff ff ff ff ff 3f  |...............?|
00000400  ff ff ff ff ff ff ff fe  e7 ff ff ff ff ff ff ff  |................|
00000410  ff dc fb fb fd fd fd fe  fe fe fb bf ff ff ff ff  |................|
00000420  ff ff ff ff f7 ff ff ff  ff ff ff ff ff fe ff ff  |................|
00000430  ff ff ff ff ff ff ff df  ff ff ff ff ff ff ff ff  |................|
00000440  fb ff ff ff ff ff ff ff  ff ff 7f ff ff ff ff ff  |................|
00000450  ff ff ff ef ff ff ff ff  ff ff ff ff fd ff ff ff  |................|
00000460  ff ff ff ff ff ff bf ff  ff ff ff ff ff ff ff f7  |................|
00000470  ff ff ff ff ff ff ff ff  fe ff ff ff ff ff ff ff  |................|
00000480  ff ff cf ff ff ff ff ff  ff ff ff bb d7 d7 eb eb  |................|
00000490  eb f5 f5 f5 ff 3f ff ff  ff ff ff ff ff fe ef ff  |.....?..........|
000004a0  ff ff ff ff ff ff ff fd  ff ff ff ff ff ff ff ff  |................|
000004b0  ff bf ff ff ff ff ff ff  ff ff f3 ff ff ff ff ff  |................|
000004c0  ff ff ff ee 7f ff ff ff  ff ff ff ff fd cf bf bf  |................|
000004d0  df df df ef ef ef bb ff  ff ff ff ff ff ff ff ff  |................|
000004e0  7f ff ff ff ff ff ff ff  ff ef ff ff ff ff ff ff  |................|
000004f0  ff ff fd ff ff ff ff ff  ff ff ff ff bf ff ff ff  |................|
00000500  ff ff ff ff ff f7 ff ff  ff ff ff ff ff ff fe ff  |................|
00000510  ff ff ff ff ff ff ff ff  df ff ff ff ff ff ff ff  |................|
00000520  ff fb ff ff ff ff ff ff  ff fe ff 3f ff ff ff ff  |...........?....|
00000530  ff ff ff fe ef 5f 5f af  af af d7 d7 d7 fc ff ff  |.....__.........|
00000540  ff ff ff ff ff ff fb bf  ff ff ff ff ff ff ff ff  |................|
00000550  f7 ff ff ff ff ff ff ff  ff fe ff ff ff ff ff ff  |................|
00000560  ff ff ff cf ff ff ff ff  ff ff ff ff b9 ff ff ff  |................|
00000570  ff ff ff ff ff f7 3e fe  ff 7f 7f 7f bf bf bd ef  |......>.........|
00000580  ff ff ff ff ff ff ff ff  fd ff ff ff ff ff ff ff  |................|
00000590  ff fb bf ff ff ff ff ff  ff ef 2f f7 ff ff ff ff  |........../.....|
000005a0  ff ff ff ef fe ff ff ff  ff ff ff ff ed ff df ff  |................|
000005b0  ff ff ff ff ff ff bf fb  ff ff ff ff ff ff fe f5  |................|
000005c0  ff 7f ff ff ff ff ff ff  fe 5f ef ff ff ff ff ff  |........._......|
000005d0  ff ff ef fc ff ff ff ff  ff ff ff df fb bd 7d 7e  |..............}~|
000005e0  be be bf 5f 5f df f3 ff  ff ff ff ff ff ff ff ee  |...__...........|
000005f0  ff ff ff ff ff ff ff fe  ff df ff ff ff ff ff ff  |................|
00000600  ff df fb ff ff ff ff ff  ff ff f7 ff 3f ff ff ff  |............?...|
00000610  ff ff ff fe fe e7 ff ff  ff ff ff ff ff df dc fb  |................|
00000620  fb fd fd fd fe fe fa bb  bf ff ff ff ff ff ff ff  |................|
00000630  7f f7 ff ff ff ff ff ff  ff e7 fe 7f ff ff ff ff  |................|
00000640  ff ff ff ff cf de 9f 4f  5f 4f a7 a7 af fb ff bf  |.......O_O......|
00000650  bf df ff df ef ef ff ff  ff ff ff ff ff ff ff ff  |................|
00000660  ff ff ff ff ff ff ff ff  ff ff ff ff ff ff ff ff  |................|
00000670  ff ff ff ff ff 42 00 87  00 00 00 00 00 00 00 00  |.....B..........|
00000680  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
000007f0  00 00 00 00 00 00 00 04  42 49 4e 00 00 00 00 04  |........BIN.....|
00000800  41 49 4e 00 00 00 00 00  00 00 00 00 00 00 00 00  |AIN.............|
00000810  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
00000830  00 00 00 00 00 00 00 00  00 00 00 02 58 00 00 00  |............X...|
00000840  00 05 58 4f 55 54 00 00  00 00 00 00 00 00 00 00  |..XOUT..........|
00000850  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
000008a0  00 00 00                                          |...|
000008a3
'''

from bitstream import *

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
		
	def dump(self):
		data = self.data
		self.handler.parse_begin(len(data))
		
		self.parse_header()
			
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


