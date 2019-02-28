# Rainforest hash module for Python

This package implements the [Rainforest](https://github.com/bschn2/rainforest) hashing algorithm.

## Usage

```python
    import rainforest
    data = '\x00'
    digest = rainforest.get_hash(data, len(data))
```

## Warning

For some unknown reason this module works incorrectly on macOS. It fails to run `rotl64` function correctly. Please, consider running `test.py` before using this module.

```
	python3 test.py
```

P.s. Any help with solving this issue woul be appriciated :)
