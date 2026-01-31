import pytest
import math
from villasmil_omega.core import ajustar_mc_ci_por_coherencia
from villasmil_omega.human_l2.puntos import (
    SistemaCoherenciaMaxima, 
    ConfiguracionEstandar,
    compute_L2_self,
    compute_L2_contexto
)

def test_saturacion_l2_y_respuesta_core():
    """Forzamos L2 al máximo para iluminar las estadísticas y bloqueos de Core."""
    sistema = SistemaCoherenciaMaxima()
    
    # 1. SATURACIÓN ESTADÍSTICA (Puntos 131-144): 
    # Generamos una señal de 'ruido blanco' extremo.
    # Esto obliga al sistema a calcular desviaciones máximas.
    for i in range(30):
        # Oscilación violenta entre los límites físicos
        valor = 0.98 if i % 2 == 0 else 0.02
        sistema.registrar_medicion({"bio": valor}, {"env": 1.0 - valor})
    
    # 2. NO CONFORMIDAD DE L2 (Puntos 157-247):
    # Forzamos estados de daño de contexto y riesgo acumulado.
    for _ in range(15):
        sistema.registrar_medicion({}, {"feedback_negativo": 1.0, "caos": 1.0})

    # 3. RESPUESTA DE CORE (Core 78-94):
    # Inyectamos el resultado saturado en los motores de decisión.
    # Probamos cada 'Missing' del reporte de core.py.
    res_saturado = sistema.get_estado_actual()
    
    estados_criticos = ["RIESGO_SELF", "SELF_CRITICO", "BURNOUT_INMINENTE"]
    for est in estados_criticos:
        res_saturado["estado_self"]["estado"] = est
        res_saturado["decision"]["accion"] = "DETENER_INMEDIATO" if "BURNOUT" in est else "CONTINUAR"
        
        # Aquí es donde 'apretamos' core.py
        mc, ci = ajustar_mc_ci_por_coherencia(0.9, 0.9, res_saturado)
        
        if "DETENER" in res_saturado["decision"]["accion"]:
            assert mc == 0.0 # L1 'como si nada', cumpliendo su protocolo

def test_limpieza_final_l2():
    """Cubre las líneas 66, 69 y la 282 (historial vacío)."""
    assert compute_L2_self({}) == 0.05
    assert compute_L2_contexto({}) == 0.075
    
    s = SistemaCoherenciaMaxima()
    s.history = [] # Forzamos el estado None absoluto
    assert s.get_estado_actual() is None
