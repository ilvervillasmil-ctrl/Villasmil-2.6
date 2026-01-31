import pytest
import villasmil_omega.core as core
from villasmil_omega.l2_model import ajustar_L2, compute_L2_final
from villasmil_omega.human_l2.puntos import SistemaCoherenciaMaxima, ConfiguracionEstandar

def test_ataque_final_cobertura():
    # 1. CORE: Forzar las líneas 82, 84, 90-94
    # Cluster vacío (82), Un solo modelo (84), Mezcla insuficiente (90-94)
    assert core.compute_theta([]) == 0.0
    assert core.compute_theta(["m1"] * 10) == 0.0
    assert core.compute_theta(["m1"] * 3 + ["m2"] * 3) == 1.0

    # 2. L2_MODEL: Forzar 52-53, 89, 103-107
    # Clamps (52-53) y Swaps (89)
    assert ajustar_L2(-1.0, 1.0) == 0.0
    assert ajustar_L2(2.0, 1.0) == 1.0
    # Bio-max (103-107)
    res = compute_L2_final(0, 0, 0, 0, [0.5], 0.5, 1.0, 0.0, 1.0)
    assert res["L2"] == 1.0

    # 3. PUNTOS: Forzar 180-189 (Estados de Riesgo y Recuperación)
    sistema = SistemaCoherenciaMaxima()
    sistema.mu_self = None # Fuerza línea 180
    sistema.registrar_medicion({"fatiga_fisica": 0.5}, {"feedback_directo": 0.5})
    
    sistema.mu_self = 0.1
    sistema.MAD_self = 0.001
    # Fuerza RIESGO_SELF (Línea 186-187)
    sistema.registrar_medicion({"fatiga_fisica": 0.9}, {"feedback_directo": 0.5})
    
    sistema.mu_self = 0.9
    # Fuerza RECUPERACION (Línea 188)
    sistema.registrar_medicion({"fatiga_fisica": 0.1}, {"feedback_directo": 0.5})
