import sys
import mif
import numpy

for fname in sys.argv[1:]:
    with open(fname) as f:
        mem = mif.load(f)
        for m in mem:
            print(' '.join(str(b) for b in m))
