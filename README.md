mif
---

[![PyPI](https://img.shields.io/pypi/v/mif)](https://pypi.org/project/mif/)
[![Travis CI](https://img.shields.io/travis/com/agrif/mif/master)](https://travis-ci.com/agrif/mif)
[![Read the Docs](https://img.shields.io/readthedocs/mif/latest)][docs]

 [docs]: https://mif.readthedocs.io/en/latest/

`mif` is a Python module to read and write [Memory Initialization
Files][mif], used by Quartus to interact with memory blocks on Intel
FPGAs. They are similar to [Intel HEX][hex] files, except they support
arbitrary memory widths as first-class citizens.

 [mif]: https://www.intel.com/content/www/us/en/programmable/quartushelp/13.0/mergedProjects/reference/glossary/def_mif.htm
 [hex]: https://en.wikipedia.org/wiki/Intel_HEX

## Installation

Install via `pip`:

```python
pip install mif
```

## Basic Use

Use with `load` / `loads` and `dump` / `dumps`, similar to the `json` module:

```python
with open('memory.mif') as f:
    mem = mif.load(f)

print(mif.dumps(mem))
```

The resulting `mem` is a numpy array of unpacked bits, where the first
dimension is the address in memory, and the second are the bits in
little-endian order. For example, to access the least significant bit
at address `0x12`:

```python
mem[0x12][0]
```

For more detailed information, please [read the documentation][docs].
