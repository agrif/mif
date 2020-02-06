mif
---

`mif` is a Python module to read and write [Memory Initialization
Files](https://www.intel.com/content/www/us/en/programmable/quartushelp/13.0/mergedProjects/reference/glossary/def_mif.htm),
used by Quartus to interact with memory blocks on Intel FPGAs. They
are similar to [Intel HEX](https://en.wikipedia.org/wiki/Intel_HEX)
files, except they support arbitrary memory widths as first-class
citizens.

Install via `pip`:

```python
pip install mif
```

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

Of course, unpacked bits are sometimes convenient, but very memory ineffecient. To instead load packed bytes (still in little-endian order):

```python
with open('memory.mif') as f:
    width, mem = mif.load(f, packed=True)

print(mif.dumps(mem, width=width))
```

Note that `load` now returns an extra `width` value, since there is
otherwise no way to know the exact width of the returned memory if it
is not divisible by 8. This can also be provided to `dump` to force an
output width; normally, it is inferred.
