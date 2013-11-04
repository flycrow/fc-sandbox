'''
At cursory glance I thought tthis was encryption but its actually just deflate compression
'''

import re
import zlib

def is_encrypted(fn):
	header = open(fn).read(18)
	if len(header) != 18:
		return False
	return header[0:3] == 'Xlx'

def extract(fn):
	return zlib.decompress(open(fn).read()[24:])

def extracts(s):
	return zlib.decompress(s[24:])

def unsign(c):
	return chr(ord(c) & 0x7F)

def unsigns(s):
	return ''.join([unsign(c) for c in s])

'''
Reference implementation: _ZN13Port_Compress13IsEncryptedIpEPKh 
	Port_Compress::IsEncryptedIp(unsigned char const*)
'''
def IsEncryptedIp(s):
	return re.match('XlxV4[2-3]', unsigns(s)) != None

'''
Reference implementation: _ZN13Port_Compress11IsEncryptedEPKh
	Port_Compress::IsEncrypted(unsigned char const*)
'''
def IsEncryptedStr(s):
	if re.match('XlxV[38].E', unsigns(s)):
		return True
	if re.match('XlxV[0-24-79]0E', unsigns(s)):
		return True
	return False

'''
Reference implementation: _ZN13Port_Compress11IsEncryptedEN4Port8FileDescEh
	Port_Compress::IsEncrypted(Port::FileDesc, unsigned char)
'''
def IsEncryptedPortFileDesc(s):
	raise Exception('Not implemented')



