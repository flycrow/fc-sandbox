from bitarray import bitarray

class DumperBase:
	def __init__(self, data):
		self.pos = 0
		self.data = data
		
	def consume(self, bytes=1):
		ret = self.data[self.pos:self.pos+bytes]
		if len(ret) != bytes:
			raise Exception('Not enough data')
		self.pos += bytes
		return ret
		
	def consume_cstr(self, bytes):
		raw = self.consume(bytes)
		# Keep going until null
		# All bytes after should also be null
		ret = ''
		consuming = False
		for c in raw:
			if consuming:
				if c != '\x00':
					raise Exception('Expected solid null bytes')
			else:
				if c == '\x00':
					consuming = True
				else:
					ret += c
		return ret
		
	def consume_to(self, pos):
		'''Consume to pos where pos is the next byte that will be availible'''
		if pos < self.pos:
			raise ValueError("Can't go to less than current pos")
		return self.consume(pos - self.pos)
		
	def find(self, s):
		return self.data.find(s, self.pos)
		
	def token(self):
		'''Parse next null terminated C string'''
		
		token = ''
		while ord(self.data[self.pos]):
			token += self.data[self.pos]
			self.pos += 1
		# Advance past the null
		self.pos += 1
		return token
		
	def byte(self):
		return ord(self.consume(1))
		
	def uint8(self):
		return self.byte()
	
	def uint16(self):
		# Big endian
		return (self.byte() << 8) + (self.byte() << 0)
		
	def uint32(self):
		# Big endian
		return (self.byte() << 24) + (self.byte() << 16) + (self.byte() << 8) + (self.byte() << 0)
		
	def str2u32(self, s):
		if len(s) != 4:
			raise Exception('Require 4 bytes')
		return (ord(s[0]) << 24) + (ord(s[1]) << 16) + (ord(s[2]) << 8) + (ord(s[3]) << 0)
		
	def end(self):
		return self.pos >= len(self.data)

	def left(self):
		return len(self.data) - self.pos

class BitDumperBase:
	def __init__(self, data):
		self.pos = 0
		self.data = bitarray()
		self.data.frombytes(data)
		
	def consume(self, bytes=1):
		ret = self.data[self.pos:self.pos+bytes]
		if len(ret) != bytes:
			raise Exception('Not enough data')
		self.pos += bytes
		return ret
		
	def consume_to(self, pos):
		'''Consume to pos where pos is the next byte that will be availible'''
		if pos < self.pos:
			raise ValueError("Can't go to less than current pos")
		return self.consume(pos - self.pos)
		
	def find(self, s):
		return self.data.find(s, self.pos)
		
	def u8(self):
		return ord(self.consume(8).tobytes())
	
	def u16(self):
		# Big endian
		return (self.byte() << 8) + (self.byte() << 0)
		
	def u32(self):
		# Big endian
		return (self.byte() << 24) + (self.byte() << 16) + (self.byte() << 8) + (self.byte() << 0)
		
	def end(self):
		return self.pos >= len(self.data)

