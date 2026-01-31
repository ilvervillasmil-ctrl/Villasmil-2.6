import pytest
import math
from villasmil_omega.core import ajustar_mc_ci_por_coherencia
from villasmil_omega.human_l2.puntos import (
    SistemaCoherenciaMaxima, 
    ConfiguracionEstandar,
    compute_L2_self,
    compute_L2_contexto
)

def test_jerarquia_omega_100():
    """L1 estable, L2 inconforme, L4-L6 al límite."""
    # L1: 'Como si nada' - Iniciamos el sistema en paz
    sistema = SistemaCoherenciaMaxima()
    
    # L2: 'Inconforme' - Forzamos el cálculo de Sigma y MAD (Puntos 131-144)
    # Una ráfaga de datos que 'tiemblan' (alta varianza)
    for i in range(25):
        tiembla = 0.5 + 0.49 * (1 if i % 2 == 0 else -1)
        sistema.registrar_medicion({"f": tiembla}, {"e": 1.0 - tiembla})
    
    # Core: 'Máxima capacidad' - Cubrimos las ramas críticas (78-94)
    # Probamos la reacción del sistema ante el colapso inminente
    casos_extremos = [
        ("RIESGO_SELF", 0.4, "CONTINUAR"),
        ("SELF_CRITICO", 0.1, "DETENER"),
        ("BURNOUT_INMINENTE", 0.0, "DETENER_INMEDIATO")
    ]
    
    for estado, score, accion in casos_extremos:
        res = {
            "estado_self": {"estado": estado},
            "estado_contexto": {"estado": "CAOS_EXTERNO"},
            "coherencia_score": score,
            "decision": {"accion": accion}
        }
        # Forzamos a Core a procesar el desequilibrio de L2
        mc, ci = ajustar_mc_ci_por_coherencia(0.9, 0.9, res)
        # En el límite, MC y CI deben ceder o bloquearse (Líneas 90-94)
        if accion.startswith("DETENER"):
            assert mc == 0.0

def test_limpieza_sombras():
    """Ataca las líneas sueltas remanentes."""
    assert compute_L2_self({}) == 0.05
    assert compute_L2_contexto({}) == 0.075
    # Forzar historial vacío línea 282
    s = SistemaCoherenciaMaxima()
    s.history = []
    assert s.get_estado_actual() is None
