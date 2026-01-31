"""
Villasmil-Ω v2.6 — A2.2 Adversarial Scenarios
High local coherence vs global incompatibility.

This test module checks that Θ(C) detects tension when
two locally coherent clusters of premises contradict each other.
"""

from villasmil_omega import core


def build_cluster_1():
    """
    Locally coherent cluster C1.
    Example: system asserts that model A is the only valid one.
    """
    return [
        "Model A is valid for this task.",
        "All deployed agents must follow Model A.",
        "No agent is allowed to use Model B.",
    ]


def build_cluster_2():
    """
    Locally coherent cluster C2.
    Example: system asserts that model B is the only valid one.
    """
    return [
        "Model B is valid for this task.",
        "All deployed agents must follow Model B.",
        "No agent is allowed to use Model A.",
    ]


def test_a22_no_conflict_inside_clusters():
    """
    A2.2 baseline:
    Θ(C1) and Θ(C2) separately should be low (no internal contradictions).
    """
    c1 = build_cluster_1()
    c2 = build_cluster_2()

    theta_c1 = core.compute_theta(c1)   # type: ignore[attr-defined]
    theta_c2 = core.compute_theta(c2)   # type: ignore[attr-defined]

    # We do not require exact 0.0, only that internal tension is small.
    assert theta_c1 <= 0.1
    assert theta_c2 <= 0.1


def test_a22_conflict_between_clusters():
    """
    A2.2 adversarial:
    When C1 and C2 are combined, Θ(C1 ∪ C2) should be clearly higher,
    reflecting the global contradiction between the two clusters.
    """
    c1 = build_cluster_1()
    c2 = build_cluster_2()

    combined = c1 + c2
    theta_c1 = core.compute_theta(c1)       # type: ignore[attr-defined]
    theta_c2 = core.compute_theta(c2)       # type: ignore[attr-defined]
    theta_combined = core.compute_theta(combined)  # type: ignore[attr-defined]

    # Global tension must be greater than the internal tensions.
    assert theta_combined >= theta_c1
    assert theta_combined >= theta_c2

    # And significantly above a small baseline (clear conflict signal).
    assert theta_combined > 0.2
