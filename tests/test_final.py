import pytest
import villasmil_omega.core as core
import villasmil_omega.l2_model as l2m
import villasmil_omega.human_l2.puntos as pts

def test_recuperacion_sistema():
    # 1. Validar CORE
    theta = core.compute_theta(["estabilidad"])
    assert 0 <= theta <= 1

    # 2. Validar PUNTOS
    s = pts.SistemaCoherenciaMaxima()
    s.registrar_medicion({"f": 0.5}, {"c": 0.5})
    assert s.mu_self is not None

    # 3. Validar L2
    res = l2m.compute_L2_final(theta, 0.5, 0.5, 0.5, [0.5], 0.5, 0.01, 0.5, 0.1)
    assert "L2" in res
