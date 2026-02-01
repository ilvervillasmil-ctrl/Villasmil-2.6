import math
from types import SimpleNamespace
from villasmil_omega import core


def test_cover_remaining_branches(monkeypatch):
    """
    Test único que forza varias ramas defensivas y de fallback en core.py:
    - excepciones en guardian_paz.es_invariante (verificar_invariancia except)
    - clamp con valores no-finitos y no-convertibles
    - suma_omega con saturación, suma libre y non-finite
    - calcular_raiz_ritmo con datos insuficientes y con non-finite/outliers
    - procesar_flujo_omega con directiva force/meta (path evolving)
    - ajustar_mc_ci_por_coherencia en estado crítico (colapso)
    - actualizar_L2 con delta == 0 (épsilon añadido)
    """
    # 1) Forzar excepción en guardian_paz.es_invariante -> cubrir except branch
    class BrokenGuardian:
        def es_invariante(self, h):
            raise RuntimeError("simulated guardian failure")

    monkeypatch.setattr(core, "guardian_paz", BrokenGuardian())
    # Should not raise; should return False because exception is swallowed
    assert core.verificar_invariancia([0.1, 0.2, 0.1]) is False

    # 2) clamp: non-finite and non-convertible input handling
    assert core.clamp(float("nan")) == 0.0
    assert core.clamp(float("inf")) == 0.0
    # non-convertible string returns min_val
    assert core.clamp("no-number") == 0.0
    # normal value preserved
    assert core.clamp(0.42) == 0.42

    # 3) suma_omega: saturation when operands in [-1.01,1.01]
    assert core.suma_omega(0.7, 0.7) == core.OMEGA_U
    # free-sum when out of normal range
    assert core.suma_omega(10.0, 10.0) == 20.0
    # non-finite operand is ignored; remaining finite summed
    s = core.suma_omega(float("inf"), 1.0)
    assert math.isfinite(s) and s == 1.0

    # 4) calcular_raiz_ritmo: insufficient data -> OMEGA_U
    assert core.calcular_raiz_ritmo([]) == core.OMEGA_U
    assert core.calcular_raiz_ritmo([0.5]) == core.OMEGA_U
    # With non-finite/outliers mixed in, function must handle and return finite index
    ritmo = core.calcular_raiz_ritmo([0.5, 0.6, float("nan"), float("inf"), -1e9])
    assert isinstance(ritmo, float) and 0.0 <= ritmo <= core.OMEGA_U

    # 5) procesar_flujo_omega: directiva force_probe -> evolving path (L2 branch)
    res_force = core.procesar_flujo_omega([0.1, 0.2, 0.3], {"action": "force_probe"})
    assert isinstance(res_force, dict)
    assert res_force.get("status") == "evolving"
    assert res_force.get("path") == "deep_evolution"

    # 6) procesar_flujo_omega: meta_auth also yields evolving (even if meta branch previously short-circuited)
    res_meta = core.procesar_flujo_omega([0.1, 0.2, 0.3], {"meta_auth": "active_meta_coherence"})
    assert isinstance(res_meta, dict)
    assert res_meta.get("status") == "evolving"

    # 7) ajustar_mc_ci_por_coherencia: critical state -> (0.0, 0.0)
    mc, ci = core.ajustar_mc_ci_por_coherencia(
        0.9, 0.9,
        {"estado_self": {"estado": "BURNOUT_ABSOLUTO"}, "decision": {"accion": "CONTINUAR"}}
    )
    assert mc == 0.0 and ci == 0.0

    # 8) actualizar_L2 with delta == 0 adds epsilon and remains clamped/finite
    before = 0.5
    after = core.actualizar_L2(before, delta=0.0)
    assert isinstance(after, float)
    assert after != before
    assert 0.0 <= after <= core.OMEGA_U
