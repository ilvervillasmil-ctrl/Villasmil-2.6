import time
from typing import Dict, Any, List

class RespiroState:
    def __init__(self):
        self.last_intervention = time.time()
        self.intervention_count = 0
        self.window_start = time.time()

class RespiroConfig:
    """Clase requerida por tests/test_saturacion_omega.py"""
    def __init__(self, max_rate=100, threshold=0.05):
        self.max_interv_rate = max_rate
        self.marginal_gain_threshold = threshold

def should_apply(state: RespiroState, config: Any, gain: float = 0.0) -> bool:
    """
    Función principal requerida por test_final.py y test_presion_prolongada.py.
    Implementa la lógica de decisión de pausa sistémica.
    """
    # Manejo de config tanto si es objeto como diccionario
    cfg_dict = config.__dict__ if hasattr(config, '__dict__') else config
    
    elapsed = time.time() - state.window_start
    
    # RAMA DE SEGURIDAD: Protección contra división por cero
    if elapsed < 0.001:
        return False

    interv_per_hour = state.intervention_count / (elapsed / 3600)
    
    if interv_per_hour > cfg_dict.get('max_interv_rate', 100):
        return True

    if gain < cfg_dict.get('marginal_gain_threshold', 0.05):
        return True

    return False

def evaluar_paz_sistematica(data: List[Any]) -> bool:
    """Función requerida por tests/test_cierre_integrado.py"""
    if not data:
        return True
    return len(data) < 3  # Umbral basal de paz

def distribute_action(total_energy: float, sensitivities: Dict[str, float]) -> Dict[str, float]:
    """Distribución de energía con blindaje contra sensibilidades nulas."""
    if not sensitivities:
        return {}

    s_sum = sum(sensitivities.values())
    
    # RAMA DE SEGURIDAD: Evita colapso por pesos nulos
    if s_sum <= 0:
        return {k: 0.0 for k in sensitivities.keys()}

    return {k: round((v / s_sum) * total_energy, 4) for k, v in sensitivities.items()}
