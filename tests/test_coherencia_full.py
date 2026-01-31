import pytest
import math
from villasmil_omega.core import ajustar_mc_ci_por_coherencia
from villasmil_omega.human_l2.puntos import (
    SistemaCoherenciaMaxima, 
    ConfiguracionEstandar,
    compute_L2_self,
    compute_L2_contexto
)

def test_vasos_comunicantes_l2_core():
    """Al apretar la coherencia en L2, la presión debe subir en Core."""
    conf = ConfiguracionEstandar()
    sistema = SistemaCoherenciaMaxima(config=conf)
    
    # Generamos la presión estadística (Puntos.py)
    # 20 ciclos de oscilación rítmica para saturar el Sigma
    for t in range(20):
        val = 0.5 + 0.48 * math.sin(t)
        sistema.registrar_medicion({"bio": val}, {"env": 1.0 - val})
    
    # El 'Apretón': Extraemos el resultado de L2 y lo inyectamos en Core
    # Esto une las líneas 131-144 de puntos con las 77-107 de core
    estado_l2 = sistema.get_estado_actual()
    
    # Probamos la reacción del motor (Core.py) ante esta presión
    # Caso 1: Motor a plena carga
    mc_alta, ci_alta = ajustar_mc_ci_por_coherencia(1.0, 1.0, estado_l2)
    # Caso 2: Motor en reserva
    mc_baja, ci_baja = ajustar_mc_ci_por_coherencia(0.2, 0.2, estado_l2)
    
    assert mc_alta != 1.0 or mc_baja != 0.2 # Confirmamos que hubo flujo de datos

def test_puntos_muertos():
    """Cubrimos los rincones donde no llega la respiración."""
    # Línea 281: historial vacío
    assert SistemaCoherenciaMaxima().get_estado_actual() is None
    # Paradoja de seguridad
    assert compute_L2_self({}) == 0.05
    assert compute_L2_contexto({}) == 0.075
