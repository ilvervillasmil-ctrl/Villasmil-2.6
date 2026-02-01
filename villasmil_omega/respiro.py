import time
from typing import Dict, Any

class RespiroState:
    def __init__(self):
        self.last_intervention = time.time()
        self.intervention_count = 0
        self.window_start = time.time()

    def start_window(self):
        self.window_start = time.time()
        self.intervention_count = 0

def detect_respiro(state: RespiroState, config: Dict[str, Any], marginal_gain_probe: float = 0.0) -> bool:
    """
    Determina si el sistema debe entrar en fase de 'respiro' (no-intervención).
    Cubre la lógica de ganancia marginal vs. costo operativo.
    """
    # 1. Protección contra ráfagas (Intervenciones por hora)
    elapsed = time.time() - state.window_start
    
    # RAMA DE SEGURIDAD (Missing 58-59): Evita división por cero si el tiempo no ha transcurrido
    if elapsed < 0.001:
        return False 

    interv_per_hour = state.intervention_count / (elapsed / 3600)
    
    if interv_per_hour > config.get('max_interv_rate', 100):
        return True

    # 2. Lógica de Ganancia Marginal (v2.6)
    # Si la ganancia detectada es menor al umbral de esfuerzo, activamos respiro
    threshold = config.get('marginal_gain_threshold', 0.05)
    if marginal_gain_probe < threshold:
        return True

    return False

def distribute_action(total_energy: float, sensitivities: Dict[str, float], config: Dict[str, Any]) -> Dict[str, float]:
    """
    Distribuye la energía de acción entre capas según su sensibilidad.
    """
    # RAMA DE SEGURIDAD (Missing 40-41): Sensibilidades nulas o vacías
    if not sensitivities:
        return {}

    s_sum = sum(sensitivities.values())
    
    # RAMA DE SEGURIDAD: Evita colapso por pesos negativos o nulos
    if s_sum <= 0:
        return {k: 0.0 for k in sensitivities.keys()}

    # Distribución proporcional v2.6
    distribution = {}
    for layer, s_val in sensitivities.items():
        # Aplicamos el ratio de energía respetando el techo de la capa
        share = (s_val / s_sum) * total_energy
        distribution[layer] = round(share, 4)

    return distribution
