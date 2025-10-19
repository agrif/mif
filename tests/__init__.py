import unittest

import importlib_resources

import mif


RADIXES = ['BIN', 'HEX', 'OCT', 'DEC', 'UNS']


def get_data_path(n):
    return importlib_resources.files(__name__) / 'data' / n


class TestPacked(unittest.TestCase):
    def test_round_trip(self):
        import numpy as np
        dat = np.ndarray([32, 4], dtype=np.ubyte)
        for i in range(32):
            valb = int.to_bytes((1 << i), length=4, byteorder="little")
            dat[i] = np.frombuffer(valb, dtype=np.ubyte)

        mifstr = mif.dumps(dat, packed=True, data_radix="HEX")
        _, dat_out = mif.loads(mifstr, packed=True)

        for i, v in enumerate(dat_out):
            exp = int.from_bytes(dat[i], byteorder="little")
            act = int.from_bytes(v, byteorder="little")
            self.assertEqual(exp, act)


class TestLoadDump(unittest.TestCase):
    def test_parse(self):
        with get_data_path('example.mif').open() as f:
            mem = mif.load(f)
        for i, v in enumerate(mem):
            expected = '00000000'
            if i <= 12:
                expected = '{:08b}'.format(i)
            val = ''.join(str(b) for b in reversed(v))
            self.assertEqual(expected, val)

    def test_round_trip(self):
        with get_data_path('example.mif').open() as f:
            mem = mif.load(f)
        memlist = [list(m) for m in mem]
        for a in RADIXES:
            for b in RADIXES:
                s = mif.dumps(mem, address_radix=a, data_radix=b)
                newmem = mif.loads(s)
                self.assertEqual(memlist, [list(m) for m in newmem])


class TestLoadDumpWide(unittest.TestCase):
    def test_parse(self):
        with get_data_path('example-wide.mif').open() as f:
            mem = mif.load(f)
        expected_blob = [
            '1000000100111111001000000001000000001000000001000000001000000001',
            '0001000011111000111111001111111011111111111111110000000000000000',
            '1111000000001000000001000000001000000001000000010000000000000000',
            '1000000100111111001000000001000000001000000001000000001000000001',
        ]
        expected = list(int(i) for i in reversed(''.join(expected_blob)))
        self.assertEqual(list(mem[0]), expected)

    def test_round_trip(self):
        with get_data_path('example-wide.mif').open() as f:
            mem = mif.load(f)
        memlist = [list(m) for m in mem]
        for a in RADIXES:
            for b in RADIXES:
                s = mif.dumps(mem, address_radix=a, data_radix=b)
                newmem = mif.loads(s)
                self.assertEqual(memlist, [list(m) for m in newmem])
