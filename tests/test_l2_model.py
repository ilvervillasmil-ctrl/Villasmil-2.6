from villasmil_omega.l2_model import (
    compute_L2_base,
    apply_bio_adjustment,
    compute_L2_final,
)


def test_compute_L2_base_basico():
    phi_c = 0.5
    theta_c = 0.5
    mc = 0.8
    ci = 0.9
    L2_base = compute_L2_base(phi_c, theta_c, mc, ci)
    assert 0.0 <= L2_base <= 1.0


def test_apply_bio_adjustment_limite():
    bio_terms = [0.1, 0.2, 0.3]
    adj = apply_bio_adjustment(bio_terms, bio_max=0.25)
    assert adj == 0.25  # no debe pasar de bio_max


def test_L2_clamp_min():
    res = compute_L2_final(
        phi_c=0.0,
        theta_c=0.0,
        mc=1.0,
        ci=1.0,
        bio_terms=[-1.0],
        bio_max=0.0,
        context_mult=0.5,
        min_L2=0.10,
        max_L2=0.95,
    )
    assert res["L2"] == 0.10


def test_L2_clamp_max():
    res = compute_L2_final(
        phi_c=1.0,
        theta_c=1.0,
        mc=0.0,
        ci=0.0,
        bio_terms=[1.0],
        bio_max=0.5,
        context_mult=2.0,
        min_L2=0.10,
        max_L2=0.95,
    )
    assert res["L2"] == 0.95


def test_L2_swap_min_max_si_vienen_mal():
    res = compute_L2_final(
        phi_c=0.5,
        theta_c=0.5,
        mc=0.5,
        ci=0.5,
        bio_terms=[],
        bio_max=0.2,
        context_mult=1.0,
        min_L2=0.9,
        max_L2=0.1,  # mal ordenados a propósito
    )
    # Debe corregir internamente y seguir en [0.1, 0.9]
    assert 0.1 <= res["L2"] <= 0.9
