from bitarray import bitarray
import sys

l = sys.argv[1]
r = sys.argv[2]

lb = bitarray(l)
rb = bitarray(r)

d = lb ^ rb
print d.to01()


