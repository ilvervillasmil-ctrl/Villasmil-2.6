import pytest
import math
from villasmil_omega.core import ajustar_mc_ci_por_coherencia
from villasmil_omega.human_l2.puntos import (
    SistemaCoherenciaMaxima, 
    ConfiguracionEstandar,
    compute_L2_self,
    compute_L2_contexto
)

def test_ataque_a_la_conformidad_l2():
    """Forzamos a la L2 a salir de su zona de confort."""
    sistema = SistemaCoherenciaMaxima()
    
    # 1. RUPTURA ESTADÍSTICA (Puntos 131-144)
    # Enviamos valores que destruyen el promedio para forzar Sigma/MAD
    for i in range(40):
        # Alternamos entre el abismo y la cima
        v = 0.001 if i % 2 == 0 else 0.999
        sistema.registrar_medicion({"f": v}, {"e": 1.0 - v})
    
    # 2. NO CONFORMIDAD (Puntos 157-247)
    # Inyectamos daño masivo al contexto para activar alertas
    for _ in range(20):
        sistema.registrar_medicion({}, {"caos": 10.0, "feedback_negativo": 10.0})

    # 3. PROPÓSITO CLARO EN CORE (Core 78-94)
    # Tomamos el estado de caos y lo pasamos por todos los estados de colapso
    caos_l2 = sistema.get_estado_actual()
    
    for estado_critico in ["RIESGO_SELF", "SELF_CRITICO", "BURNOUT_INMINENTE"]:
        caos_l2["estado_self"]["estado"] = estado_critico
        # Forzamos la rama de bloqueo total
        caos_l2["decision"]["accion"] = "DETENER_INMEDIATO"
        
        mc, ci = ajustar_mc_ci_por_coherencia(0.8, 0.8, caos_l2)
        # L1 debe estar 'como si nada', cumpliendo su protocolo de apagado
        assert mc == 0.0 and ci == 0.0

def test_limpieza_sombras_l2():
    """Líneas 66, 69 y 281/282 (puntos muertos)."""
    assert compute_L2_self({}) == 0.05
    assert compute_L2_contexto({}) == 0.075
    s = SistemaCoherenciaMaxima()
    s.history = []
    assert s.get_estado_actual() is None
