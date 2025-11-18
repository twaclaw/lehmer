from typing import Any

import numpy as np


class Lehmer:
    def __init__(
        self,
        n: int,
        squeeze: bool = False,
        dtype: np.dtype = np.uint64,
        precompute_factorials: bool = True,
        validate_inputs: bool = False,
    ):
        """
        Creates an instance of the Lehmer class that can be used to encode and decode permutations into Lehmer codes.

        Args:
        - n: int. Size of the permutations/codes
        - squeeze: bool. Defines the global, default behavior for whether results of shape (1, n) should be squeezed. Defaults to False.
        - dtype: np.dtype. Global, default type for results. It must a instance of numpy unsigned integer. Defaults to np.uint64.
        - precompute_factorials: bool. Defines whether factorials are precomputed. Defaults to True. If factorials are not precomputed, decoding is not possible.
        - validate_inputs: bool. Defines whether input permutations should be validated. Defaults to False.

        Examples:
        >>> lehmer = Lehmer(n=4)
        >>> perm = [2, 0, 3, 1]
        >>> idx = lehmer.encode(perm)
        """
        self.n = n
        self.squeeze = squeeze
        self.dtype = dtype
        self.validate_inputs = validate_inputs
        if not np.issubdtype(self.dtype, np.integer):
            raise ValueError("dtype must be an unsigned integer type")

        self.factorials = None
        if precompute_factorials:
            self.factorials = np.concatenate([[1], np.cumprod(np.arange(1, self.n + 1).astype(self.dtype))])

    @staticmethod
    def _validate_type(dtype: Any):
        if not np.issubdtype(dtype, np.integer):
            raise ValueError("dtype must be an unsigned integer type")

    def perm2code(
        self,
        perms: np.ndarray | list,
        minvalue: np.ndarray | list[int] | int | None = None,
        squeeze: bool | None = None,
    ) -> np.ndarray:
        """Converts one or multiple permutations to Lehmer codes.

        Args:
            perms (numpy.ndarray | list): Can be a list, a list of lists, or a
                numpy array of shape (b, n), where b is the batch size and n is
                the permutation length.
            minvalue (numpy.ndarray | list[int] | int | None, optional): The
                minimum value in the permutations. If None, it is computed
                automatically. Can be a scalar or an array of shape (b,) for
                batch processing. Defaults to None.
            squeeze (bool | None, optional): Whether to squeeze the result if
                batch size is 1. If None, uses the instance's squeeze setting.
                Defaults to None.

        Returns:
            numpy.ndarray: An array of shape (b, n), where b is the batch size
                and n is the code length. If b=1 and squeeze=True, returns shape (n,).

        Raises:
            ValueError: If validate_inputs is True and an invalid permutation is found.

        Examples:
            >>> lehmer = Lehmer(n=4)
            >>> perm = [2, 0, 3, 1]
            >>> code = lehmer.perm2code(perm, squeeze=True)
            >>> code
            array([2, 0, 1, 0])

            >>> # Batch processing
            >>> perms = [[2, 0, 3, 1], [3, 1, 0, 2]]
            >>> codes = lehmer.perm2code(perms)
            >>> codes.shape
            (2, 4)
        """

        dtype = perms.dtype if isinstance(perms, np.ndarray) else self.dtype

        perms = np.asarray(perms, dtype=self.dtype)

        if perms.ndim < 2:
            perms = perms[np.newaxis, :]

        if minvalue is None:
            minvalue = np.min(perms, axis=1, keepdims=True)

        minvalue = np.asarray(minvalue, dtype=dtype)

        if self.validate_inputs:
            self._validate_type(dtype)
            tiles = np.tile(np.arange(self.n), (self.n, 1))
            if not np.all(np.sort(perms, axis=-1) == tiles):
                raise ValueError("Invalid permutation found!")

            if minvalue.ndim > 0 and minvalue.shape[0] != perms.shape[0]:
                raise ValueError("minvalue must be a scalar or have the same batch size as perms")

        perms = perms - minvalue
        comparison = perms[..., np.newaxis] > perms[:, np.newaxis, :]
        upper_triangle = np.triu(comparison, k=1)
        if squeeze is None:
            squeeze = self.squeeze
        results = np.sum(upper_triangle, axis=2, dtype=self.dtype)
        return results.squeeze() if squeeze else results

    def code2index(self, code: np.ndarray | list, squeeze: bool | None = None) -> int:
        """
        """
        if self.factorials is None:
            raise ValueError("Factorials were not precomputed. Cannot convert index to code.")

        dtype = code.dtype if isinstance(code, np.ndarray) else self.dtype
        code = np.asarray(code, dtype=dtype)

        if self.validate_inputs:
            self._validate_type(dtype)
            if code.shape[-1] != self.n:
                raise ValueError("Lehmer code has incorrect length!")

            if np.any(code < 0) or np.any(code >= self.n):
                raise ValueError("Invalid Lehmer code found!")


        if code.ndim < 2:
            code = code[np.newaxis, :]

        results = np.dot(code[..., ::-1], self.factorials[: self.n]).astype(self.dtype)
        if squeeze is None:
            squeeze = self.squeeze
        squeeze = results.shape == (1,) and squeeze
        return results.item() if squeeze else results

    def index2code(self, index: np.ndarray | list | int, squeeze: bool | None = None) -> np.ndarray:
        """
        """
        dtype = index.dtype if isinstance(index, np.ndarray) else self.dtype

        if self.validate_inputs:
            self._validate_type(dtype)

        index = np.asarray(index, dtype=dtype)

        if self.factorials is None:
            raise ValueError("Factorials were not precomputed. Cannot convert index to code.")

        if index.ndim < 1:
            index = index[np.newaxis, :]

        divisors = np.arange(1, self.n + 1)
        lehmer_code = (index[..., np.newaxis] // self.factorials[: self.n]) % divisors
        if squeeze is None:
            squeeze = self.squeeze
        result = lehmer_code[..., ::-1].astype(dtype)
        return result.squeeze() if squeeze else result

    def code2perm(
        self,
        codes: np.ndarray | list,
        minvalue: int | list[int] | np.ndarray | None = None,
        squeeze: bool | None = None,
    ) -> np.ndarray:
        """
        """
        #TODO: add min values
        dtype = codes.dtype if isinstance(codes, np.ndarray) else self.dtype
        if self.validate_inputs:
            self._validate_type(dtype)

        codes = np.asarray(codes, dtype=dtype)

        if codes.ndim < 2:
            codes = codes[np.newaxis, :]

        ncodes = codes.shape[0]

        factory = np.tile(np.arange(self.n), (ncodes, 1))

        perm = np.zeros_like(codes)

        # TODO check whether this can be factorized
        for i in range(self.n):
            idx = codes[:, i]
            matrix = np.ones_like(factory, dtype=float)
            matrix[np.arange(ncodes), idx] = np.nan
            perm[np.arange(ncodes), i] = factory[np.arange(ncodes), idx]
            factory = factory * matrix
            factory = factory[~np.isnan(factory)].reshape(ncodes, -1)

        if squeeze is None:
            squeeze = self.squeeze
        return perm.squeeze() if squeeze else perm

    def encode(self, perm: np.ndarray, minvalue: np.ndarray | list | int | None = None, squeeze: bool | None = None) -> int:
        code = self.perm2code(perm, minvalue, squeeze=False)
        return self.code2index(code, squeeze=squeeze)

    def decode(
        self,
        index: np.ndarray | int,
        minvalue: int | None = None,
        squeeze: bool | None = None,
    ) -> np.ndarray:
        codes = self.index2code(index, squeeze=False)
        return self.code2perm(codes, squeeze=squeeze)
