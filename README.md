# Lehmer

> A minimal, vectorized, and batchable implementation of Lehmer codes.

<div align="center">
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Rubik%27s_cube.svg/375px-Rubik%27s_cube.svg.png" alt="Rubik's Cube" width="150"/>
</div>


[Lehmer codes](https://en.wikipedia.org/wiki/Lehmer_code), named after [D.H. Lehmer](https://en.wikipedia.org/wiki/D._H._Lehmer), offer a method for enumerating the permutations of a set. The Lehmer code counts the number of inversions in a permutation. Together with the factoradic base, it provides a way to uniquely encode permutations as integers. This encoding therefore provides a bijection between integers and permutations. In other words, it is a perfect, memory-efficient hashing function for permutations.

## Installation

Installing from PyPI:

```bash
[uv] pip install lehmer
```

Installing from source:

```bash
git clone ...
cd lehmer
uv venv
uv sync
```

## Description

The class `Lehmer` provides two pairs of methods (depicted below in blue). Additionally, there are two convenience functions `encode` and `decode` (depicted below in orange) that combine the pairs for encoding and decoding permutations to and from integer indices.

$$
\underbrace{\text{permutation} \xrightarrow{\text{\color{blue}{perm2code}}} \text{code} \xrightarrow{\text{\color{blue}{code2index}}} \text{index} \in \mathbb{Z}}_{\text{\color{orange}{encode}}}
$$

$$
\underbrace{\text{permutation} \xleftarrow{\text{\color{blue}{code2perm}}} \text{code} \xleftarrow{\text{\color{blue}{index2code}}} \text{index} \in \mathbb{Z}}_{\text{\color{orange}{decode}}}
$$

## Examples

Coming soon

## Contributing

Please read the [contributing guidelines](CONTRIBUTING.md) if you wish to contribute to this project.

## Credits

- Image source [Wikimedia](https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Rubik%27s_cube.svg/375px-Rubik%27s_cube.svg.png)
