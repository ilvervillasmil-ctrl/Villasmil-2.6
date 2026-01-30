"""
Basic tests for Villasmil-Ω v2.6
Usage: pytest
"""

import sys
from pathlib import Path
import pytest

PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from villasmil_omega.core import (
    compute_theta, update_L2, apply_penalties, compute_R, ppr_suggest
)


def test_theta():
    premises = [
        {'id': 1, 'constraints': {'A': True}},
        {'id': 2, 'constraints': {'A': True}}
    ]
    theta = compute_theta(premises)
    assert theta == pytest.approx(0.0)


def test_L2_update():
    L2_current = 0.10
    L2_new = update_L2(L2_current)
    assert L2_new > L2_current + 1e-9


def test_penalties():
    MC, CI = 0.75, 0.96
    L2_current = 0.20
    MC_pen, CI_pen = apply_penalties(MC, CI, L2_current)
    assert MC_pen < MC
    assert CI_pen < CI


def test_relevance():
    R = compute_R(0.75, 0.96, 0.02, 0.03, 0.05, 1.0, 1)
    assert R > 0


def test_ppr_structure():
    proposal = {'L2': 0.125, 'action': 'integrate'}
    context = {'phi_C': 0.05}
    result = ppr_suggest(proposal, context)
    assert isinstance(result, dict)
    assert 'accepted' in result
    assert 'alternative' in result
