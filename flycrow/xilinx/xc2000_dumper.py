from flycrow.xilinx.dumper import *
from bitarray import bitarray
import binascii

'''
Summary
    Device        Non-data bits
    XC2018        826        
    XC2064        678        

XC2000.pdf
    Device        Logic (gates)    CLBs    Max IOBs    Config bits
    XC2018        1000-1500        100        74            17878
    XC2064        600-1000        64        58            12038

XC2000FM.pdf
    Agrees on config bits
                Config frames        Data bits / frame     Net data bits
    XC2018        196                    87                    17052
    XC2064        160                    71                    11360
        + 4 metadata bits / frame => 75 * 160 = 12,000 bits => 1500 bytes
'''

def sbin(bytes):
    b = bitarray()
    b.frombytes(bytes)
    return b.to01()

class Handler:
    def __init__(self, options):
        self.opt = options
    
    def on_pre_magic(self, magic):
        pass
    
    def on_post_magic(self, magic):
        pass
        
    def on_header_hack(self):
        pass
        
    def on_frame_bits(self):
        pass
        
    def on_end(self):
        pass
        
class StringHandler(Handler):
    def __init__(self, *args, **kwargs):
        Handler.__init__(self, *args, **kwargs)
        self.buffer = ''
    
    def write(self, s):
        self.buffer += s + '\n'

    def on_header_hack(self):
        self.write('''Xilinx LCA SBAPR.lca 2064PC68'
File SBAPR.rbt
Sat Sep  8 00:31:12 2012
Sat Sep  8 00:31:12 2012
Source
Version
Produced by makebits version 5.2.1''')

    def on_frame_bits(self, framei, frame_bits):
        prefix = ''
        if self.opt.prefix:
            prefix = '%04X: ' % framei
        self.write('%s%s' % (prefix, frame_bits.to01()))
        
    def on_footer(self, rest):
        prefix = ''
        if self.opt.prefix:
            prefix = 'Footer: '
        self.write('%s%s' % (prefix, sbin(rest[0:2])))
        if self.opt.verbose:
            self.write('FIXME')
            #self.write('%d bytes left' % self.left())
            self.write('Footer: %s' % binascii.hexlify(rest))
        
    def on_bitstream_header(self, bits):
        prefix = ''
        if self.opt.prefix:
            prefix = 'Bitstream header (40 bits): '
        self.write('%s%s' % (prefix, bits.to01()))
        
    def on_end(self):
        return self.buffer
    
class PrintHandler(StringHandler):
    def write(self, s):
        print s

class FrameDumper(BitDumperBase):
    def __init__(self, data, options, handler):
        BitDumperBase.__init__(self, data)
        self.handler = handler 
        self.frames = 0
        self.opt = options
        
    def next(self):
        frame = self.consume(75)
        self.handler.on_frame_bits(self.frames, frame)
        # First bit should be 0 (just 'cause)
        if frame[0]:
            raise Exception('First bit should be 0')
        # and last three should be 1's
        if frame[len(frame) - 3:] != bitarray('111'):
            raise Exception("Last three bits sould be 1's")
        self.frames += 1

    def done(self):
        return self.pos == len(self.data)

class Options:
    def __init__(self):
        self.verbose = False
        self.prefix = False
        self.core = False

class BitstreamDumper(DumperBase):
    def __init__(self, bitstream, options = None, handler=None):
        self.data = bitstream
        self.pos = 0
        if options is None:
            options = Options()
        self.opt = options
        if handler is None:
            handler = PrintHandler(options)
        self.handler = handler
        self.handler.options = options
        
    def parse_bit_header(self):
        '''
        RBT doesn't begin until 
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
        Sample
            .bit
                00000000  f0 0f f0 0f f0 0f f0 0f  00 32 30 36 34 50 43 36  |.........2064PC6|
                00000010  38 00 00 00 00 00 31 31  32 2f 30 39 2f 30 34 32  |8.....112/09/042|
                00000020  30 3a 31 34 3a 33 32 00  53 42 41 50 52 2e 6c 63  |0:14:32.SBAPR.lc|
                00000030  61 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |a...............|
                00000040  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
                *
                00000070  00 00 00 00 00 30<ff 20  02 f1 1f>75 fd fe ff fe  |.....0. ...u....|
                ...
            .rbt
                Xilinx LCA SBAPR.lca 2064PC68
                File SBAPR.rbt
                Tue Sep  4 20:14:32 2012
                Tue Sep  4 20:14:32 2012
                Source
                Version
                Produced by makebits version 5.2.1            
        Sample .bit
            00000000  f0 0f f0 0f f0 0f f0 0f  00 32 30 36 34 50 43 36  |.........2064PC6|
            00000010  38 00 00 00 00 00 31 31  32 2f 30 39 2f 30 33 31  |8.....112/09/031|
            00000020  32 3a 30 31 3a 34 33 00  46 49 52 53 54 50 41 52  |2:01:43.FIRSTPAR|
            00000030  2e 6c 63 61 00 00 00 00  00 00 00 00 00 00 00 00  |.lca............|
            00000040  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
            *
            00000070  00 00 00 00 00 30 ff 20  02 f1 1f 75 fd fe ff fe  |.....0. ...u....|
            ...
        Assume for now that header is fixed at 0x76 bytes based off of that
        In practice it looks more like 0x70 maybe + some other data I don't understand
        '''
        magic = self.consume(8)
        self.handler.on_pre_magic(magic)
        if magic != '\xf0\x0f\xf0\x0f\xf0\x0f\xf0\x0f':
            raise Exception('Bad magic')
        self.handler.on_post_magic(magic)
        pad = self.consume()
        if pad != '\x00':
            raise Exception('Missing padding')
        part_str = self.consume_cstr(13)
        
        # Throw away the rest for now
        self.consume_to(0x76)
        if not self.opt.core:
            self.handler.on_header_hack()
        
    def parse_bitstream_header(self):
        '''
        The first actual part of the data is the bitstream header occupying 40 bits
        Example:
            1111111100100000000000101111000100011111
            00000070  00 00 00 00 00 30<ff 20  02 f1 1f>75 fd fe ff fe  |.....0. ...u....|
        '''
        header = self.consume(40 / 8)
        bits = bitarray(endian='big')
        bits.frombytes(header)
        self.handler.on_bitstream_header(bits)
        
    def parse_footer(self):
        '''
        Looks like it has some tags as to what pin goes to what
        '''
        rest = self.consume(self.left())
        self.handler.on_footer(rest)
        
    def dump(self):
        data = self.data
        
        self.parse_bit_header()
        self.parse_bitstream_header()
            
        '''
        Following should be first frame
        RBT:
            011101011111110111111110111111111111111011111111011111110111111111111111111
            '75 fd fe ff fe ff 7f 7f ff e0'
        00000070  00 00 00 00 00 30 ff 20  02 f1 1f<75 fd fe ff fe  |.....0. ...u....|
        00000080  ff 7f 7f ff e>dbf bf df  ff df ef ef ff fd ff ef  |................|
        
        Next frame:
        RBT:
            011011011111110111111110111111111111111011111111011111110111111111111111111
            Removing first bit: 'd bf bf df ff df ef ef ff fc'
            
        00000080  ff 7f 7f ff<ed bf bf df  ff df ef ef ff>fd ff ef  |................|
        And so on
        So, it needs to be parsed as bitarray
        '''
        # WARNING: XC2018 is not a byte multiple....will deal with that later
        # What I'd guess to be the 24 bit length is 02 f1 1f => 192799
        # totoal bits = 75 * 160 = 12000 => 0x002EE0
        # ah no its count for ALL devices in the daisy chain so it must be calculated dynamically
        frames = self.consume(75 * 160 / 8)
        fd = FrameDumper(frames, self.opt, self.handler)
        while not fd.done():
            fd.next()
        self.parse_footer()
        
        if not self.end():
            raise Exception('Unparsed data')
        return self.handler.on_end()
        
    
