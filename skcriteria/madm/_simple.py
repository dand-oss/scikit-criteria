#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: BSD-3 (https://tldrlegal.com/license/bsd-3-clause-license-(revised))
# Copyright (c) 2016-2021, Cabral, Juan; Luczywo, Nadia
# All rights reserved.

# =============================================================================
# DOCS
# =============================================================================

"""Implementation of functionalities for inverting minimization criteria and \
converting them into maximization ones.

In addition to the main functionality, an agnostic MCDA function is offered
that inverts columns of a matrix based on a mask.

"""

# =============================================================================
# IMPORTS
# =============================================================================


import numpy as np

from ..base import SKCRankerMixin
from ..data import Objective, RankResult
from ..utils import doc_inherit, rank

# =============================================================================
# SAM
# =============================================================================


def wsm(matrix, weights):
    """Execute weighted sum model without any validation."""
    # calculate ranking by inner prodcut

    rank_mtx = np.inner(matrix, weights)
    score = np.squeeze(rank_mtx)

    return rank(score, reverse=True), score


class WeightedSumModel(SKCRankerMixin):
    r"""The weighted sum model.

    WSM is the best known and simplest multi-criteria decision analysis for
    evaluating a number of alternatives in terms of a number of decision
    criteria. It is very important to state here that it is applicable only
    when all the data are expressed in exactly the same unit. If this is not
    the case, then the final result is equivalent to "adding apples and
    oranges". To avoid this problem a previous normalization step is necessary.

    In general, suppose that a given MCDA problem is defined on :math:`m`
    alternatives and :math:`n` decision criteria. Furthermore, let us assume
    that all the criteria are benefit criteria, that is, the higher the values
    are, the better it is. Next suppose that :math:`w_j` denotes the relative
    weight of importance of the criterion :math:`C_j` and :math:`a_{ij}` is
    the performance value of alternative :math:`A_i` when it is evaluated in
    terms of criterion :math:`C_j`. Then, the total (i.e., when all the
    criteria are considered simultaneously) importance of alternative
    :math:`A_i`, denoted as :math:`A_{i}^{WSM-score}`, is defined as follows:

    .. math::

        A_{i}^{WSM-score} = \sum_{j=1}^{n} w_j a_{ij},\ for\ i = 1,2,3,...,m

    For the maximization case, the best alternative is the one that yields
    the maximum total performance value.

    Raises
    ------
    ValueError:
        If some objective is for minimization.


    References
    ----------

    .. [fishburn1967additive] Fishburn, P. C. (1967). Letter to the
       editor-additive utilities with incomplete product sets: application
       to priorities and assignments. Operations Research, 15(3), 537-542.
    .. [2] Weighted sum model. In Wikipedia, The Free Encyclopedia. Retrieved
       from https://en.wikipedia.org/wiki/Weighted_sum_model
    .. [3] Tzeng, G. H., & Huang, J. J. (2011). Multiple attribute decision
       making: methods and applications. CRC press.

    """

    @doc_inherit(SKCRankerMixin._validate_data)
    def _validate_data(self, objectives, **kwargs):
        if Objective.MIN.value in objectives:
            raise ValueError(
                "WeightedSumModel can't operate with minimize objective"
            )

    @doc_inherit(SKCRankerMixin._rank_data)
    def _rank_data(self, matrix, weights, **kwargs):
        rank, score = wsm(matrix, weights)
        return rank, {"score": score}

    @doc_inherit(SKCRankerMixin._make_result)
    def _make_result(self, anames, rank, extra):
        return RankResult(
            "WeightedSumModel", anames=anames, rank=rank, extra=extra
        )


# =============================================================================
# WPROD
# =============================================================================


def wpm(matrix, weights):
    """Execute weighted product model without any validation."""

    # instead of multiply we sum the logarithms
    lmtx = np.log10(matrix)

    # add the weights to the mtx
    rank_mtx = np.multiply(lmtx, weights)

    score = np.sum(rank_mtx, axis=1)

    return rank.rankdata(score, reverse=True), score


class WeightedProductModel(SKCRankerMixin):
    @doc_inherit(SKCRankerMixin._validate_data)
    def _validate_data(self, matrix, objectives, **kwargs):
        if Objective.MIN.value in objectives:
            raise ValueError("WSM can't operate with minimize objective")
        if np.any(matrix <= 0):
            raise ValueError("WPM can't operate with values <= 0")

    @doc_inherit(SKCRankerMixin._rank_data)
    def _rank_data(self, matrix, weights, **kwargs):
        rank, score = wpm(matrix, weights)
        return rank, {"score": score}

    @doc_inherit(SKCRankerMixin._make_result)
    def _make_result(self, anames, rank, extra):
        return RankResult(
            "WeightedProductModel", anames=anames, rank=rank, extra=extra
        )
