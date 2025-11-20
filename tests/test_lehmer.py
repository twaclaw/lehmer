from itertools import permutations

import numpy as np

from lehmer import Lehmer


class TestLehmer:
    def test_roundtrip(self):
        n = 20
        lc = Lehmer(n=n)
        a = np.arange(n)
        perms = np.array([np.random.permutation(a) for _ in range(100)])
        idx = lc.perm2code(perms)
        perms2 = lc.code2perm(idx)

        assert np.all(perms == perms2)

        codes = lc.perm2code(perms)
        codes2 = lc.perm2code(perms2)
        assert np.all(codes == codes2)

    def test_all_permutations(self):
        """
        Verifies that unique indices are generated for all permutations of length n.
        """
        n = 7
        s = set(range(n))
        perms = np.array(list(permutations(s)))
        lc = Lehmer(n=n)
        idx = lc.encode(perms)
        assert (np.sort(idx) == np.arange(len(perms))).all()
        perms2 = lc.decode(idx)
        assert (perms == perms2).all()

    def test_minvalue(self):
        n = 7
        s = np.arange(n)
        p0 = np.array([np.random.permutation(s) for _ in range(10)])
        p1 = [p0[i] + i for i in range(10)]

        lc = Lehmer(n=n, validate_inputs=True)
        c0, minvalues = lc.perm2code(p1, return_minvalue=True, squeeze=True)
        c1 = lc.perm2code(p0)
        assert np.all(c0 == c1)
        assert np.all(minvalues == np.arange(10))

        p0_recon = lc.code2perm(c0, minvalue=minvalues)
        assert np.all(p0_recon == p1)



