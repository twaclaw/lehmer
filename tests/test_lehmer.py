from itertools import permutations

import numpy as np
import pytest

from lehmer import Lehmer


class TestLehmer:
    @pytest.mark.parametrize("validate_inputs", [True, False])
    def test_roundtrip(self, validate_inputs):
        n = 20
        lc = Lehmer(n=n, validate_inputs=validate_inputs)
        a = np.arange(n)
        perms = np.array([np.random.permutation(a) for _ in range(100)])
        idx = lc.perm2code(perms)
        perms2 = lc.code2perm(idx)

        assert np.all(perms == perms2)

        codes = lc.perm2code(perms)
        codes2 = lc.perm2code(perms2)
        assert np.all(codes == codes2)

    @pytest.mark.parametrize("validate_inputs", [True, False])
    def test_all_permutations(self, validate_inputs):
        """
        Verifies that unique indices are generated for all permutations of length n.
        """
        n = 7
        s = set(range(n))
        perms = np.array(list(permutations(s)))
        lc = Lehmer(n=n, validate_inputs=validate_inputs)
        idx = lc.encode(perms)
        assert (np.sort(idx) == np.arange(len(perms))).all()
        perms2 = lc.decode(idx)
        assert (perms == perms2).all()

    @pytest.mark.parametrize("validate_inputs", [True, False])
    def test_minvalue(self, validate_inputs):
        n = 7
        s = np.arange(n)
        p0 = np.array([np.random.permutation(s) for _ in range(10)])
        p1 = [p0[i] + i for i in range(10)]

        # Internal computation of minvalue
        lc = Lehmer(n=n, validate_inputs=validate_inputs)
        c0, minvalues = lc.perm2code(p1, return_minvalue=True, squeeze=True)
        c1 = lc.perm2code(p0)
        assert np.all(c0 == c1)
        assert np.all(minvalues == np.arange(10))

        p0_recon = lc.code2perm(c0, minvalue=minvalues)
        assert np.all(p0_recon == p1)

        # Pass a single minvalue: int
        lc = Lehmer(n=n, validate_inputs=validate_inputs)
        p1 = [p0[i] + 3 for i in range(10)]
        c0 = lc.perm2code(p1, minvalue=3)
        c1 = lc.perm2code(p0)
        assert np.all(c0 == c1)

    @pytest.mark.parametrize("validate_inputs", [True, False])
    def test_dtypes(self, validate_inputs):
        n = 10
        lc = Lehmer(n=n, dtype=np.uint64, validate_inputs=validate_inputs)

        # uses input dtype
        a = np.arange(n, dtype=np.int32)
        assert lc.perm2code(a).dtype == np.int32
        assert lc.encode(a).dtype == np.int32
        assert lc.decode(np.arange(10, dtype=np.uint8)).dtype == np.uint8

        # uses class dtype
        assert lc.perm2code(list(range(n))).dtype == np.uint64
        assert lc.encode(list(range(n))).dtype == np.uint64
        assert lc.decode(list(range(n))).dtype == np.uint64

    def test_perm2code(self):
        for n in range(5, 30):
            lc = Lehmer(n=n)
            for b in range(1, 30):
                a = np.arange(n)
                perms = np.array([np.random.permutation(a) for _ in range(b)])
                codes1 = lc.perm2code(perms)
                codes2 = lc.perm2code_2(perms)
                assert np.all(codes1 == codes2)
