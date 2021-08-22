#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: BSD-3 (https://tldrlegal.com/license/bsd-3-clause-license-(revised))
# Copyright (c) 2016-2021, Cabral, Juan; Luczywo, Nadia
# All rights reserved.

# =============================================================================
# DOCS
# =============================================================================

"""MCDA methods."""

# =============================================================================
# IMPORTS
# =============================================================================

from ._maut import WeightedProductModel, WeightedSumModel, wpm, wsm
from ._moora import RatioMOORA, ratio
from ._similarity import TOPSIS, topsis
from ._simus import SIMUS, simus

# =============================================================================
# ALL
# =============================================================================

__all__ = [
    "SIMUS",
    "TOPSIS",
    "WeightedSumModel",
    "WeightedProductModel",
    "simus",
    "topsis",
    "wpm",
    "wsm",
]
