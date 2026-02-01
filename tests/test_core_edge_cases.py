import math
import pytest
from villasmil_omega import core

def test_clamp_nan_and_nonfinite():
    assert core.clamp(float('nan')) == 0.0
    assert core.clamp(float('inf')) == 0.0
    assert core.clamp(0.5) == 0.5

def test_suma_omega_saturation_and_nonfinite():
    # dentro de [-1.01, 1.01] → aplica saturación
    assert core.suma_omega(0.7, 0.7) == core.OMEGA_U
    # fuera de rango → suma libre (pero filtra non-finite)
    assert core.suma_omega(10.0, 10.0) == 20.0
    # uno non-finite se ignora
    assert core.suma_omega(float('inf'), 1.0) == 1.0

def test_indice_ci_kwargs_and_zero_total():
    assert core.indice_ci(aciertos=80, errores=20, ruido=0) <= core.C_MAX
    assert core.indice_ci(0,0,0) == 0.0

def test_ajustar_mc_ci_por_coherencia_critical_state():
    mc, ci = core.ajustar_mc_ci_por_coherencia(0.8, 0.8, {"estado_self": {"estado": "BURNOUT_ABSOLUTO"}, "decision": {"accion": "CONTINUAR"}})
    assert mc == 0.0 and ci == 0.0

def test_procesar_flujo_omega_parsing_numeric_strings_and_nan_inf():
    data = [ "0.2", 0.4, "nope", float('nan'), "1.1", "-0.5", "0.0" ]  # includes numeric strings and bad values
    res = core.procesar_flujo_omega(data, directiva={})
    assert isinstance(res, dict)
    ritmo = res.get("ritmo_omega")
    # ritmo puede no estar presente si no hay suficientes valores numéricos; si está, debe ser finito y en rango
    if ritmo is not None:
        assert isinstance(ritmo, float) and math.isfinite(ritmo) and 0.0 <= ritmo <= core.OMEGA_U

def test_actualizar_L2_delta_zero_adds_epsilon():
    before = 0.5
    after = core.actualizar_L2(before, delta=0.0)
    assert after != before
    # still clamped and finite
    assert isinstance(after, float)
    assert 0.0 <= after <= core.OMEGA_U
