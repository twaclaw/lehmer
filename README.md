# Lehmer

> A minimal, vectorized, and batchable implementation of Lehmer codes.

<div align="center">
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Rubik%27s_cube.svg/375px-Rubik%27s_cube.svg.png" alt="Rubik's Cube" width="150"/>
</div>


[Lehmer codes](https://en.wikipedia.org/wiki/Lehmer_code), named after [D.H. Lehmer](https://en.wikipedia.org/wiki/D._H._Lehmer), offer a method for enumerating the permutations of a set. The Lehmer code counts the number of inversions in a permutation. Together with the factoradic base, they provide a way to uniquely encode permutations as integers. Therefore, this  encoding provides a bijection between integers and permutations. In other words, it is a perfect, memory-efficient hashing function for permutations.

## Installation

Installing from PyPI:

```bash
[uv] pip install lehmer
```

Installing from source:

```bash
git clone https://github.com/twaclaw/lehmer.git
cd lehmer
uv venv
source .venv/bin/activate
uv sync
```

## Description

The `Lehmer` class provides two pairs of methods depicted below in blue. There are also two convenience functions, `encode` and `decode`,  that combine the pairs for encoding and decoding permutations to and from integer indices (depicted below in orange).

$$
\underbrace{\text{permutation} \xrightarrow{\text{\color{blue}{perm2code}}} \text{code} \xrightarrow{\text{\color{blue}{code2index}}} \text{index} \in \mathbb{Z}}_{\text{\color{orange}{encode}}}
$$

$$
\underbrace{\text{permutation} \xleftarrow{\text{\color{blue}{code2perm}}} \text{code} \xleftarrow{\text{\color{blue}{index2code}}} \text{index} \in \mathbb{Z}}_{\text{\color{orange}{decode}}}
$$

## Examples

### Simple encoding and decoding

```python
from lehmer import Lehmer

lc = Lehmer(n=4)
perm = [2, 0, 3, 1] # can also be a numpy array
lc.encode(perm, squeeze=True)
# 13

lc.decode(13, squeeze=True)
# array([2, 0, 3, 1], dtype=uint64) -> dtype defaults to np.uint64
```

### Batch encoding and decoding

```python
from lehmer import Lehmer
import numpy as np
N, BATCH = 5, 6
s = np.arange(N)
perms = np.array([np.random.permutation(s) for _ in range(BATCH)])
print(perms)

lc = Lehmer(n=N, dtype=np.uint16)
idx = lc.encode(perms)

# [[2 3 1 0 4]
#  [4 3 1 2 0]
#  [4 1 0 2 3]
#  [0 1 2 4 3]
#  [4 2 1 3 0]
#  [1 3 2 0 4]]

perms2 = lc.decode(idx)
print(perms2)

# [[2 3 1 0 4]
#  [4 3 1 2 0]
#  [4 1 0 2 3]
#  [0 1 2 4 3]
#  [4 2 1 3 0]
#  [1 3 2 0 4]]
```

### Additional options

```python
N = 20
lc = Lehmer(n=N)
perms = np.array([np.random.permutation(np.arange(N)) + i for i in range(50)])
print(perms.shape)
# (50, 20)

# Return the calculated minimum values along with the codes
codes, minvalues = lc.perm2code(perms, return_minvalue=True)
print(codes.shape, minvalues.shape)
# (50, 20) (50, )

# validate inputs: dtypes and shapes
lc2 = Lehmer(n=4, validate_inputs=True)
code = np.arange(4, dtype=float)
lc2.code2perm(code)
# ValueError: Invalid dtype: float64. dtype must be a subinstance of numpy.integer
```

See the docstrings for more details.

## A note on the performance

`perm2code` doesn't have any Python loops. `code2perm` has a single Python loop over `n`,
which I didn't manage to eliminate yet. I implemented a second version of `perm2code`, namely `perm2code_2`, which has a loop over `n` but can be faster or more memory efficient depending on `n` and the batch size (for instance if `n` or `b` are "big"). See [this notebook](notebooks/performance_comp.ipynb) for a performance comparison. You have to see which implementation works better for your use case.


## Contributing

That would be awesome! Please read the [contributing guidelines](CONTRIBUTING.md) if you wish to contribute to this project.

## Credits

- Image source: [Wikimedia](https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Rubik%27s_cube.svg/375px-Rubik%27s_cube.svg.png)
