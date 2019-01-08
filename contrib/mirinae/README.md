# mirinae-hash-python

This package implements the [Mirinae](https://github.com/MicroBitcoinOrg/Mirinae) hashing algorithm.

## Usage

```python
    import mirinae
    data = '\x00'
    digest = mirinae.get_hash(data, len(data), 1)
```
