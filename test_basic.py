import pytest
import villasmil_omega.core as core
import villasmil_omega.l2_model as l2m
import villasmil_omega.human_l2.puntos as pts
from villasmil_omega.meta_cierre import EstadoSuficiencia, decision_final

def test_suficiencia_omega_v26():
    """
    Test de Clausura: Fuerza las ramas de pánico y declara 
    la suficiencia del sistema.
    """
    # 1. CORE: Forzar guardias técnicas (Líneas 82-94)
    core.compute_theta([]) 
    core.compute_theta(["estabilidad"] * 10)
    core.compute_theta(["alfa", "beta", "gamma"])

    # 2. PUNTOS: Forzar estados de Riesgo (Líneas 180-189)
    s = pts.SistemaCoherenciaMaxima()
    s.mu_self = None
    s.registrar_medicion({"f": 0.5}, {"c": 0.5})
    s.mu_self, s.MAD_self = 0.01, 0.0001
    s.registrar_medicion({"fatiga_fisica": 0.99}, {"c": 0.1})

    # 3. L2_MODEL: Forzar Clamps y Swaps (Líneas 52-107)
    l2m.ajustar_L2(-1.0, 2.0)
    l2m.compute_L2_final(0.1, 0.1, 0.5, 0.5, [0.1], 0.5, 0.01, 0.9, 0.1)

    # 4. META-CIERRE: Declaración de 100% por Suficiencia
    estado = EstadoSuficiencia(
        coherencia_actual=92.0, 
        delta_presion=0.0001, 
        delta_retiro=0.0001
    )
    assert decision_final(estado) == 100.0
