from itertools import permutations

import numpy as np
import pytest

from lehmer.lehmer import Lehmer


class TestLehmer:
    def test_constructor(self):
        lehmer = Lehmer(n=5)
        assert lehmer.n == 5
        assert lehmer.squeeze is False
        assert len(lehmer.factorials) == 6

        lehmer = Lehmer(n=4, squeeze=True)
        assert lehmer.squeeze

        lehmer = Lehmer(n=6, dtype=np.uint32, precompute_factorials=False)
        assert lehmer.dtype == np.uint32
        assert lehmer.factorials is None

        with pytest.raises(ValueError):
            Lehmer(n=5, dtype=float)

    def test_roundtrip(self):
        n = 20
        lehmer = Lehmer(n=n)
        a = np.arange(n)
        perms = np.array([np.random.permutation(a) for _ in range(100)])
        idx = lehmer.perm2code(perms)
        perms2 = lehmer.code2perm(idx)

        assert np.all(perms == perms2)

        codes = lehmer.perm2code(perms)
        codes2 = lehmer.perm2code(perms2)
        assert np.all(codes == codes2)

    def test_all_permutations(self):
        """
        Verifies that unique indices are generated for all permutations of length n.
        """
        n = 7
        s = set(range(n))
        perms = np.array(list(permutations(s)))
        lehmer = Lehmer(n=n)
        idx = lehmer.encode(perms)
        assert (np.sort(idx) == np.arange(len(perms))).all()
        perms2 = lehmer.decode(idx)
        assert (perms == perms2).all()
