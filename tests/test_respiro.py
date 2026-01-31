from villasmil_omega.respiro import (
    distribute_action,
    RespiroConfig,
    RespiroState,
    simulate_apply,
    should_apply,
    detect_respiro,
)


def test_distribute_action_reparte_y_limita():
    cfg = RespiroConfig(max_total_effort=1.0, max_component=0.6)
    sensitivities = {"L1": 1.0, "L2": 2.0, "L3": 3.0}
    effort = distribute_action(1.0, sensitivities, cfg)

    assert set(effort.keys()) == {"L1", "L2", "L3"}
    assert 0.0 <= min(effort.values()) <= cfg.max_component
    assert sum(effort.values()) <= cfg.max_total_effort + 1e-6


def test_simulate_apply_beneficio_saturado():
    e1 = {"L1": 0.1}
    e2 = {"L1": 1.0}
    out1 = simulate_apply(0.0, e1)
    out2 = simulate_apply(0.0, e2)

    assert out2.R_final > out1.R_final
    assert out2.cost > out1.cost


def test_should_apply_prefiere_soft_si_marginal_pequeno():
    soft = {"L1": 0.2}
    hard = {"L1": 0.8}
    apply_soft, marginal = should_apply(
        current_R=0.5,
        effort_soft=soft,
        effort_hard=hard,
        cost_threshold=1.0,
    )
    assert apply_soft is True
    assert marginal >= 0.0


def test_detect_respiro_condiciones_cumplidas():
    cfg = RespiroConfig(
        interv_threshold_per_hour=5.0,
        min_deadband_fraction=0.5,
        marginal_gain_epsilon=0.02,
    )
    st = RespiroState()
    st.start_window()
    # Simulamos que estuvo casi todo el tiempo en deadband y con pocas intervenciones
    st.deadband_seconds = st.window_seconds * 0.8
    st.interv_count = 1

    is_respiro = detect_respiro(st, cfg, marginal_gain_probe=0.0)
    assert is_respiro is True
