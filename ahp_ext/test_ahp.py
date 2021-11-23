#!/usr/bin/env python
# -*- coding: utf-8 -*-

# License: 3 Clause BSD
# http://scikit-criteria.org/


# =============================================================================
# DOC
# =============================================================================

"""test AHP"""


# =============================================================================
# IMPORTS
# =============================================================================

import random

import numpy as np

from skcriteria.tests import tcore

import ahp


# =============================================================================
# BASE CLASS
# =============================================================================


class AHPTest(tcore.SKCriteriaTestCase):
    def test_validate_values(self):
        ahp.validate_values(1)
        ahp.validate_values(2)
        ahp.validate_values(2.3)
        ahp.validate_values(9.9)
        ahp.validate_values([1, 2, 3.8])

        with self.assertRaises(ValueError):
            ahp.validate_values(10)

        with self.assertRaises(ValueError):
            ahp.validate_values(0)

        with self.assertRaises(ValueError):
            ahp.validate_values([10, 1])

        with self.assertRaises(ValueError):
            ahp.validate_values([1, -1])

    def test_saaty_closest_intensity(self):
        for value in range(1, 10):
            scale = ahp.saaty_closest_intensity(value)
            self.assertEqual(value, scale.value)

        scale = ahp.saaty_closest_intensity(9.1)
        self.assertEqual(9, scale.value)

        scale = ahp.saaty_closest_intensity(8.6)
        self.assertEqual(9, scale.value)

        scale = ahp.saaty_closest_intensity(8.5)
        self.assertEqual(8, scale.value)

        with self.assertRaises(ValueError):
            ahp.saaty_closest_intensity(10)

        with self.assertRaises(ValueError):
            ahp.saaty_closest_intensity(0)

    def test_validate_ahp_matrix(self):

        # test if the matrix type is incorrect
        mtxtype = str(random.random())
        rx = "'mtxtype must be 'None', '{}' or '{}'. Found '{}'".format(
            ahp.MTX_TYPE_ALTERNATIVES, ahp.MTX_TYPE_CRITERIA, mtxtype
        )
        with self.assertRaisesRegexp(ValueError, rx):
            ahp.validate_ahp_matrix(12, None, mtxtype)

        # test if the matrix size is <= AHP_LIMIT
        mtxtype = random.choice(
            [ahp.MTX_TYPE_CRITERIA, ahp.MTX_TYPE_ALTERNATIVES]
        )
        rx = "The max number of {} must be <= {}.".format(
            mtxtype, ahp.AHP_LIMIT
        )
        with self.assertRaisesRegexp(ValueError, rx):
            ahp.validate_ahp_matrix(100, None, mtxtype)

        rx = "The max number of rows and columns must be <= {}".format(
            ahp.AHP_LIMIT
        )
        with self.assertRaisesRegexp(ValueError, rx):
            ahp.validate_ahp_matrix(100, None, None)

        # test if the matrix has correct chape
        mtx = np.asarray([[1, 2, 3], [4, 5, 6]])
        shape = 2, 2
        rx = "The shape of {} matrix must be '{}'. Found '{}'".format(
            mtxtype, shape, mtx.shape
        )
        rx = rx.replace("(", r"\(").replace(")", r"\)").replace(".", r"\.")
        with self.assertRaises(ValueError):
            ahp.validate_ahp_matrix(mtxtype, shape[0], mtx)

        # test if the matrix diagonal is only ones (1)
        mtx = np.asarray([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        rx = r"All the diagonal values must be only ones \(1\)"
        with self.assertRaisesRegexp(ValueError, rx):
            ahp.validate_ahp_matrix(3, mtx, mtxtype)

        mtx = np.asarray([[1, 2, 3], [4, 1, 6], [100, 8, 1]])
        rx = "All values must >= {} and <= {}".format(
            ahp.SAATY_MIN + 1, ahp.SAATY_MAX - 1
        )
        with self.assertRaisesRegexp(ValueError, rx):
            ahp.validate_ahp_matrix(3, mtx, mtxtype)

        mtx = np.asarray([[1, 2, 3], [4, 1, 6], [7, 8, 1]])
        rx = r"The matix is not symmetric with reciprocal values"
        with self.assertRaisesRegexp(ValueError, rx):
            ahp.validate_ahp_matrix(3, mtx, mtxtype)

        mtx = np.asarray([[1, 2, 3], [1 / 2.0, 1, 6], [1 / 3.0, 1 / 6.0, 1]])
        ahp.validate_ahp_matrix(3, mtx, mtxtype)

    def test_saaty_ri(self):
        for size in range(1, 16):
            ahp.saaty_ri(size)
        with self.assertRaises(KeyError):
            ahp.saaty_ri(0)
        with self.assertRaises(KeyError):
            ahp.saaty_ri(16)

    def test_t(self):
        tmtx = [[1], [1, 2, 3]]
        rx = (
            "The low triangular matrix for AHP must "
            "have the same number of columns and rows"
        )
        with self.assertRaisesRegexp(ValueError, rx):
            ahp.t(tmtx)

        tmtx = [[1], [1.0, 1], [1 / 3.0, 1 / 6.0, 1]]
        mtx = ahp.t(tmtx)

        for ridx, row in enumerate(tmtx):
            for cidx, value in enumerate(row):
                if not np.isclose(mtx[ridx][cidx], value, atol=1.0e-10):
                    self.fail("Incorect triangular matrix construct")

        mtxtype = random.choice(
            [ahp.MTX_TYPE_CRITERIA, ahp.MTX_TYPE_ALTERNATIVES]
        )
        ahp.validate_ahp_matrix(3, mtx, mtxtype)

    def test_ahp(self):
        rank = [1, 3, 2]
        points = [0.4177, 0.2660, 0.3164]

        crit_vs_crit = ahp.t(
            [[1.0], [1.0 / 3.0, 1.0], [1.0 / 3.0, 1.0 / 2.0, 1.0]]
        )
        alt_vs_alt_by_crit = [
            ahp.t([[1.0], [1.0 / 5.0, 1.0], [1.0 / 3.0, 3.0, 1.0]]),
            ahp.t([[1.0], [9.0, 1.0], [3.0, 1.0 / 5.0, 1.0]]),
            ahp.t([[1.0], [1 / 2.0, 1.0], [5.0, 7.0, 1.0]]),
        ]

        result = ahp.ahp(crit_vs_crit, alt_vs_alt_by_crit)
        rank_result, points_result = result[:2]

        self.assertAllClose(points_result, points, atol=1.0e-3)
        self.assertAllClose(rank_result, rank)

        rx = (
            "The number 'alt_vs_alt_by_crit' must be "
            "the number of criteria '{}'. Found"
        ).format(3, len(alt_vs_alt_by_crit))
        rx = rx.replace("(", r"\(").replace(")", r"\)").replace(".", r"\.")
        with self.assertRaisesRegexp(ValueError, rx):
            ahp.ahp(crit_vs_crit, alt_vs_alt_by_crit[1:])

    def test_cr(self):
        ic = 0.02695218060897031
        cr = 0.051829169847109106
        crit_vs_crit = ahp.t(
            [[1.0], [1.0 / 3.0, 1.0], [1.0 / 3.0, 1.0 / 2.0, 1.0]]
        )
        ic_result, cr_result = ahp.saaty_cr(crit_vs_crit)[:2]
        import ipdb

        ipdb.set_trace()
        self.assertAllClose(ic, ic_result, atol=1.0e-3)
        self.assertAllClose(cr, cr_result, atol=1.0e-3)


if __name__ == "__main__":
    import sys

    from skcriteria.tests import __main__ as main

    main.main(sys.argv[1:])
