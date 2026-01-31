import math
import time
from typing import Dict

def distribute_action(base_effort: float, sensitivities: Dict[str, float]) -> Dict[str, float]:
    """Regla: Nunca atacar una sola capa. Reparte el esfuerzo en L1..L6."""
    total_sens = sum(sensitivities.values()) or 1.0
    # Normalización con pesos adaptativos
    weights = {k: v / total_sens for k, v in sensitivities.items()}
    # Aplicamos micro-ajustes (max 0.5 por capa para no forzar el límite)
    return {k: min(base_effort * w, 0.5) for k, w in weights.items()}

def detect_respiro(interv_count: int, deadband_frac: float, marginal_gain: float) -> bool:
    """Métrica de éxito: Reducir intervenciones y maximizar estabilidad."""
    return (interv_count < 4 and deadband_frac > 0.6 and marginal_gain < 0.02)
