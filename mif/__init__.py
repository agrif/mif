import io
import math
import os.path

import lark
import numpy
import pkg_resources

class MIFError(Exception):
    pass

# get something nicer than a parse tree
class ParseTransformer(lark.Transformer):
    # parsable values
    def value(self, v):
        return str(v[0])

    # recursively-defined updates
    def file(self, entries):
        if len(entries) == 0:
            return {}
        (k, v), old = entries
        old[k] = v
        return old

    # non-recursively defined list
    def datablock(self, entries):
        return list(entries)

    # give content a key
    def content(self, c):
        return ('CONTENT', c[0])

    # parsable addresses
    def addressrange(self, vals):
        a, b = vals
        return (a, b)
    def address(self, val):
        return (val[0],)

    def meta(self, kv):
        return kv

    def data(self, children):
        address, *data = children
        return (address, data)

class Loader:
    # find and load our grammar
    with pkg_resources.resource_stream(__name__, 'grammar.bnf') as f:
        parser = lark.Lark(
            io.TextIOWrapper(f),
            start='file',
            parser='lalr',
            maybe_placeholders=False,
            transformer=ParseTransformer(),
        )

    radixes = ['BIN', 'HEX', 'OCT', 'DEC', 'UNS']

    def __init__(self, text):
        self.parsed = self.parser.parse(text)
        self.depth = self._meta_int('DEPTH')
        self.width = self._meta_int('WIDTH')
        self.address_radix = self._meta_enum('ADDRESS_RADIX', self.radixes)
        self.data_radix = self._meta_enum('DATA_RADIX', self.radixes)
        if not 'CONTENT' in self.parsed:
            raise MIFError('file does not have a CONTENT block')

        self.data = numpy.zeros((self.depth, (self.width + 7) // 8), dtype=numpy.uint8)
        self._fill_data()

    @property
    def bindata(self):
        return numpy.unpackbits(self.data, axis=1, count=self.width, bitorder='little')

    def _parse_data(self, c):
        radix = self.data_radix
        v = self._parse_int(self.data_radix, c, maxval=(1 << self.width))
        out = numpy.zeros(((self.width + 7) // 8,), dtype=numpy.uint8)
        for i in range(len(out)):
            out[i] = v & 0xff
            v = v >> 8
        return out

    def _fill_data(self):
        for addr, content in self.parsed['CONTENT']:
            content = [self._parse_data(c) for c in content]
            modulus = len(content)
            if len(addr) == 1:
                start = self._parse_int(self.address_radix, addr[0], maxval=self.depth)
                end = start + modulus - 1
            else:
                start = self._parse_int(self.address_radix, addr[0], maxval=self.depth)
                end = self._parse_int(self.address_radix, addr[1], maxval=self.depth)
                
            if start < 0 or end >= self.depth or end < start:
                niceaddr = addr[0]
                if len(addr) > 1:
                    niceaddr = '[{}..{}]'.format(*addr)
                raise MIFError('bad address: {}'.format(niceaddr))

            for i in range(end - start + 1):
                self.data[start + i][:] = content[i % modulus]

    def _parse_int(self, radix, val, maxval=None):
        try:
            if radix == 'BIN':
                return int(val, base=2)
            elif radix == 'HEX':
                return int(val, base=16)
            elif radix == 'OCT':
                return int(val, base=8)
            elif radix == 'DEC':
                v = int(val, base=10)
                if maxval and v < 0:
                    v += maxval
                return v
            elif radix == 'UNS':
                v = int(val, base=10)
                if v < 0:
                    raise ValueError('negative')
                return v
            else:
                raise RuntimeError(radix)
        except ValueError:
            raise MIFError('unknown value `{}` for radix {}'.format(val, radix))

    def _meta_int(self, key):
        try:
            return self._parse_int('UNS', self.parsed[key])
        except ValueError:
            raise MIFError('{} key is not a positive integer'.format(key)) from None
        except KeyError:
            raise MIFError('file does not have required {} key'.format(key)) from None

    def _meta_enum(self, key, vals):
        try:
            v = self.parsed[key]
            if not v in vals:
                raise ValueError()
            return v
        except ValueError:
            raise MIFError('{} key has unknown value {}'.format(key, v)) from None
        except KeyError:
            raise MIFError('file does not have required {} key'.format(key)) from None

def load(fp, packed=False):
    return loads(fp.read(), packed=packed)

def loads(s, packed=False):
    l = Loader(s)
    if packed:
        return (l.width, l.data)
    return l.bindata

class Dumper:
    def __init__(self, mem, fp, width, address_radix, data_radix):
        fp.write('WIDTH={};\n'.format(self._format_int('UNS', width)))
        fp.write('DEPTH={};\n'.format(self._format_int('UNS', mem.shape[0])))
        fp.write('\n')
        fp.write('ADDRESS_RADIX={};\n'.format(address_radix))
        fp.write('DATA_RADIX={};\n'.format(data_radix))
        fp.write('\n')
        fp.write('CONTENT BEGIN\n')
        for addr, valbytes in enumerate(mem):
            val = 0
            for i in reversed(valbytes):
                val = val << 8
                val += int(i) # numpy types infect, so exercise clean math
            fp.write('\t')
            fp.write(self._format_int(address_radix, addr, maxval=mem.shape[0]))
            fp.write('  :   ')
            fp.write(self._format_int(data_radix, val, maxval=(1 << width)))
            fp.write(';\n')
        fp.write('END;\n')

    def _format_int(self, radix, val, maxval=None):
        if val < 0:
            raise ValueError('negative')
        if radix == 'DEC' and maxval is not None:
            # this is weird, it can be signed
            if val >= maxval >> 1:
                val -= maxval
        if radix == 'BIN':
            base = 2
            fmt = '{:b}'.format
        elif radix == 'HEX':
            base = 16
            fmt = '{:x}'.format
        elif radix == 'OCT':
            base = 8
            fmt = '{:o}'.format
        elif radix == 'DEC' or radix == 'UNS':
            base = 10
            fmt = '{:d}'.format
        else:
            raise MIFError('unknown radix {}'.format(radix))
        s = fmt(val)
        if maxval is not None:
            width = int(math.ceil(math.log(maxval) / math.log(base)))
            prefix = ''
            if s[0] == '-':
                prefix = '-'
                s = s[1:]
            s = prefix + '0' * (width - len(s)) + s
        return s

def dump(mem, fp, packed=False, width=None, address_radix='HEX', data_radix='BIN'):
    if not packed:
        if width is None:
            _, width = mem.shape
        mem = numpy.packbits(mem, axis=1, bitorder='little')
    if width is None:
        width = mem.shape[1] * 8
    Dumper(mem, fp, width, address_radix, data_radix)

def dumps(mem, packed=False, width=None, address_radix='HEX', data_radix='BIN'):
    with io.StringIO() as fp:
        dump(mem, fp, packed=packed, width=width, address_radix=address_radix, data_radix=data_radix)
        return fp.getvalue()
