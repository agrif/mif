import sys
import mif
import numpy

RADIXES = ['BIN', 'HEX', 'OCT', 'DEC', 'UNS']

for fname in sys.argv[1:]:
    with open(fname) as f:
        mem = mif.load(f)
    for a in RADIXES:
        for b in RADIXES:
            s = mif.dumps(mem, data_radix=a, address_radix=b)
            newmem = mif.loads(s)
            assert(numpy.array_equal(mem, newmem))
