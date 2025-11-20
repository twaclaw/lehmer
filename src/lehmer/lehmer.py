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
        """Creates an instance of the Lehmer class for encoding and decoding permutations.

        Args:
            n (int): Size of the permutations/codes.
            squeeze (bool, optional): Defines the global, default behavior for
                whether results of shape (1, n) should be squeezed. Defaults to False.
            dtype (numpy.dtype, optional): Global, default type for results. Must
                be an instance of numpy.integer. Defaults to np.uint64.
            precompute_factorials (bool, optional): Defines whether factorials are
                precomputed. Defaults to True. If factorials are not precomputed,
                decoding is not possible.
            validate_inputs (bool, optional): Defines whether inputs (arrays and dtype)
                should be validated. Defaults to False.

        Examples:
            >>> from lehmer import Lehmer
            >>> lc = Lehmer(4)
            >>> lc.encode([2, 0, 3, 1])
            array([13], dtype=uint64)
            >>> lc.decode([13])
            array([[2, 0, 3, 1]], dtype=uint64)

            >>> lc.encode([[2, 0, 3, 1], [1, 2, 0, 3], [0, 1, 3, 2], [0, 1, 2, 3]])
            array([13,  8,  1,  0], dtype=uint64)
            >>> lc.decode([13, 8, 1, 0])
            array([[2, 0, 3, 1],
                   [1, 2, 0, 3],
                   [0, 1, 3, 2],
                   [0, 1, 2, 3]], dtype=uint64)
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

        self._validate_type(dtype)

    @staticmethod
    def _validate_type(dtype: Any):
        if not np.issubdtype(dtype, np.integer):
            raise ValueError(f"Invalid dtype: {dtype}. dtype must be a subinstance of numpy.integer")

    def perm2code(
        self,
        perms: np.ndarray | list,
        minvalue: np.ndarray | list[int] | int | None = None,
        squeeze: bool | None = None,
        return_minvalue: bool = False,
    ) -> np.ndarray | tuple[np.ndarray, np.ndarray]:
        """Converts a batch of  permutations to Lehmer codes.

        Args:
            perms (numpy.ndarray | list): Can be a list or a
                numpy array of shape (b, n), where b is the batch size and n is
                the permutation length.
            minvalue (numpy.ndarray | list[int] | int,  optional): The
                minimum value required to make the permutations 0-indexed. If None, it is computed
                automatically. Can be a scalar or an array of shape (b,) for
                batch processing. Defaults to None.
            squeeze (bool | None, optional): Whether to squeeze the result if
                batch size is 1. If None, uses the instance's global squeeze setting.
                Defaults to None.
            return_minvalue (bool, optional): Whether to return the computed minvalue
                along with the Lehmer codes. Defaults to False.

        Returns:
            numpy.ndarray: An array of shape (b, n), where b is the batch size
                and n is the code length.
            tuple[numpy.ndarray, numpy.ndarray]: If return_minvalue is True,

        Raises:
            ValueError: If validate_inputs is True and an invalid permutation or dtype is found.

        Examples:
            >>> lc = Lehmer(5)
            >>> codes = lc.perm2code([2, 4, 1, 3, 0])
            >>> codes.shape
            (1, 5)

            >>> codes = lc.encode([[2, 4, 1, 3, 0]] * 10)
            >>> codes.shape
            (10,)
            >>> codes = lc.perm2code([[2, 4, 1, 3, 0]] * 10)
            >>> codes.shape
            (10, 5)
        """

        dtype = perms.dtype if isinstance(perms, np.ndarray) else self.dtype

        perms = np.asarray(perms, dtype=self.dtype)

        if perms.ndim < 2:
            perms = perms[np.newaxis, :]

        if minvalue is None:
            minvalue = np.min(perms, axis=1, keepdims=True)

        minvalue = [minvalue] if isinstance(minvalue, int) else minvalue
        minvalue = np.asarray(minvalue, dtype=dtype).reshape(-1, 1)

        if self.validate_inputs:
            self._validate_type(dtype)
            tiles = np.tile(np.arange(self.n), (perms.shape[0], 1))
            if not np.all(np.sort(perms, axis=-1) - minvalue == tiles):
                raise ValueError("Invalid permutation found!")

            if minvalue.ndim > 0 and minvalue.shape[0] != perms.shape[0]:
                raise ValueError("minvalue must be a scalar or have the same batch size as perms")

        perms = perms - minvalue
        comparison = perms[..., np.newaxis] > perms[:, np.newaxis, :]
        upper_triangle = np.triu(comparison, k=1)
        if squeeze is None:
            squeeze = self.squeeze
        results = np.sum(upper_triangle, axis=2, dtype=self.dtype)
        results =  results.squeeze() if squeeze else results
        if return_minvalue:
            return results, minvalue.squeeze()
        return results

    def code2index(self, code: np.ndarray | list, squeeze: bool | None = None) -> int:
        """Converts Lehmer codes to factorial number system indices.

        Args:
            code (numpy.ndarray | list): Lehmer code(s) to convert. Can be a single
                code or batch of codes with shape (b, n).
            squeeze (bool | None, optional): Whether to return a scalar for single
                codes. If None, uses the instance's squeeze setting. Defaults to None.

        Returns:
            int | numpy.ndarray: The factorial index/indices. Returns int if squeeze=True
                and batch size is 1, otherwise returns numpy.ndarray.

        Raises:
            ValueError: If factorials were not precomputed, or if validate_inputs is
                True and an invalid code is found.

        Examples:
            >>> from lehmer import Lehmer
            >>> lc = Lehmer(n=4)
            >>> code = [2, 0, 1, 0]
            >>> lc.code2index(code)
            array([13], dtype=uint64)

            >>> codes = [[2, 0, 1, 0], [2, 0, 1, 1], [1, 2, 1, 0]]
            >>> lc.code2index(codes)
            array([13, 14, 11], dtype=uint64)
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
        """Converts factorial number system indices to Lehmer codes.

        Args:
            index (numpy.ndarray | list | int): The factorial index/indices to convert.
            squeeze (bool | None, optional): Whether to squeeze the result if batch
                size is 1. If None, uses the instance's squeeze setting. Defaults to None.

        Returns:
            numpy.ndarray: The Lehmer code(s) of shape (b, n). If b=1 and squeeze=True,
                returns shape (n,).

        Raises:
            ValueError: If factorials were not precomputed.

        Examples:
            >>> from lehmer import Lehmer
            >>> lc = Lehmer(4)
            >>> lc.index2code(13)
            array([[2, 0, 1, 0]], dtype=uint64)
            >>> lc.index2code([13, 11, 7, 12])
            array([[2, 0, 1, 0],
                   [1, 2, 1, 0],
                   [1, 0, 1, 0],
                   [2, 0, 0, 0]], dtype=uint64)
        """
        dtype = index.dtype if isinstance(index, np.ndarray) else self.dtype

        if self.validate_inputs:
            self._validate_type(dtype)

        index = [index] if isinstance(index, int) else index

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
        """Converts Lehmer codes to permutations.

        Args:
            codes (numpy.ndarray | list): Lehmer code(s) to convert. Can be a single
                code or batch of codes with shape (b, n).
            minvalue (int | list[int] | numpy.ndarray | None, optional): The minimum
                value to add to the permutation elements. If None, permutations start
                from 0. Defaults to None.
            squeeze (bool | None, optional): Whether to squeeze the result if batch
                size is 1. If None, uses the instance's squeeze setting. Defaults to None.

        Returns:
            numpy.ndarray: The permutation(s) of shape (b, n). If b=1 and squeeze=True,
                returns shape (n,).

        Examples:
        >>> from lehmer import Lehmer
        >>> lc = Lehmer(4)
        >>> lc.code2perm([2, 0, 1, 0])
        array([[2, 0, 3, 1]], dtype=uint64)

        >>> lc.code2perm([[2, 0, 1, 0], [2, 0, 0, 0], [1, 2, 1, 0]])
        array([[2, 0, 3, 1],
               [2, 0, 1, 3],
               [1, 3, 2, 0]], dtype=uint64)
        """
        dtype = codes.dtype if isinstance(codes, np.ndarray) else self.dtype

        if minvalue is not None:
            minvalue = [minvalue] if isinstance(minvalue, int) else minvalue
            minvalue = np.asarray(minvalue, dtype=dtype).reshape(-1, 1)

        if self.validate_inputs:
            self._validate_type(dtype)

            if minvalue.ndim > 0 and minvalue.shape[0] != codes.shape[0]:
                raise ValueError("minvalue must be a scalar or have the same batch size as perms")

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

        squeeze  = squeeze or self.squeeze

        if minvalue is not None:
            perm += minvalue
        return perm.squeeze() if squeeze else perm

    def encode(self, perm: np.ndarray, minvalue: np.ndarray | list | int | None = None, squeeze: bool | None = None) -> int:
        """Encodes a permutation directly to its factorial index.

        This is a convenience method that combines perm2code and code2index.

        Args:
            perm (numpy.ndarray): The permutation(s) to encode.
            minvalue (numpy.ndarray | list | int | None, optional): The minimum value
                in the permutation. If None, computed automatically. Defaults to None.
            squeeze (bool | None, optional): Whether to return a scalar for single
                permutations. If None, uses the instance's squeeze setting. Defaults to None.

        Returns:
            int | numpy.ndarray: The factorial index/indices.

        Examples:
            >>> lehmer = Lehmer(n=4)
            >>> perm = [2, 0, 3, 1]
            >>> idx = lehmer.encode(perm, squeeze=True)
            >>> idx
            13
        """
        code = self.perm2code(perm, minvalue, squeeze=False)
        return self.code2index(code, squeeze=squeeze)

    def decode(
        self,
        index: np.ndarray | int,
        minvalue: int | None = None,
        squeeze: bool | None = None,
    ) -> np.ndarray:
        """Decodes a factorial index directly to its permutation.

        This is a convenience method that combines index2code and code2perm.

        Args:
            index (numpy.ndarray | int): The factorial index/indices to decode.
            minvalue (int | None, optional): The minimum value to add to the
                permutation elements. If None, permutations start from 0.
                Defaults to None.
            squeeze (bool | None, optional): Whether to squeeze the result if batch
                size is 1. If None, uses the instance's squeeze setting. Defaults to None.

        Returns:
            numpy.ndarray: The decoded permutation(s).

        Examples:
            >>> lehmer = Lehmer(n=4)
            >>> idx = 13
            >>> perm = lehmer.decode(idx, squeeze=True)
            >>> perm
            array([2, 0, 3, 1])
        """
        codes = self.index2code(index, squeeze=False)
        return self.code2perm(codes, squeeze=squeeze)
