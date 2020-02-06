import unittest

import io
import os.path
import pkg_resources

import mif

RADIXES = ['BIN', 'HEX', 'OCT', 'DEC', 'UNS']

def load_data(n):
    p = os.path.join('data', n)
    return io.TextIOWrapper(pkg_resources.resource_stream(__name__, p))

class TestLoadDump(unittest.TestCase):
    def test_parse(self):
        with load_data('example.mif') as f:
            mem = mif.load(f)
        for i, v in enumerate(mem):
            expected = '00000000'
            if i <= 12:
                expected = '{:08b}'.format(i)
            val = ''.join(str(b) for b in reversed(v))
            self.assertEqual(expected, val)

    def test_round_trip(self):
        with load_data('example.mif') as f:
            mem = mif.load(f)
        memlist = [list(m) for m in mem]
        for a in RADIXES:
            for b in RADIXES:
                s = mif.dumps(mem, address_radix=a, data_radix=b)
                newmem = mif.loads(s)
                self.assertEqual(memlist, [list(m) for m in newmem])
