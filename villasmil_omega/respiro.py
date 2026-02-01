import time
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class RespiroState:
    window_start: float = field(default_factory=time.time)
    intervention_count: int = 0
    last_gain: float = 0.0

@dataclass
class RespiroConfig:
    max_interv_rate: int = 100  # Intervenciones por hora
    marginal_gain_threshold: float = 0.05

def detect_respiro(state: RespiroState, config: RespiroConfig, marginal_gain: float = 0.0) -> bool:
    """
    Determina si el sistema necesita un 'respiro' basado en saturación o baja eficiencia.
    """
    # Líneas 25-27: Aseguramos inicialización de ventana (Missing anterior)
    if state.window_start <= 0:
        state.window_start = time.time()
        
    now = time.time()
    elapsed = now - state.window_start
    
    # Evitar división por cero en milisegundos iniciales
    if elapsed < 0.001:
        return False

    # Línea 60: Control de Tasa (Missing anterior)
    # Si superamos la tasa permitida de intervenciones, forzamos respiro
    interv_per_hour = state.intervention_count / (elapsed / 3600)
    if interv_per_hour > config.max_interv_rate:
        return True

    # Lógica de ganancia marginal
    return marginal_gain < config.marginal_gain_threshold

def distribute_action(total_energy: float, sensitivities: Dict[str, float]) -> Dict[str, float]:
    """
    Distribuye la energía de acción proporcionalmente a las sensibilidades detectadas.
    """
    if not sensitivities:
        return {}

    total_sens = sum(sensitivities.values())

    # Línea 74: Protección Crítica (Missing anterior)
    # Si la suma de sensibilidades es 0, no hay dirección de flujo
    if total_sens <= 0:
        return {k: 0.0 for k in sensitivities}

    return {k: (v / total_sens) * total_energy for k, v in sensitivities.items()}
