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
    max_interv_rate: int = 100
    marginal_gain_threshold: float = 0.05

def should_apply(state: Any, config: Any, marginal_gain: float = 0.0) -> bool:
    """
    Lógica central compartida para detectar la necesidad de un respiro.
    """
    # Inicialización de ventana (Cobertura Líneas 25-27)
    if not hasattr(state, 'window_start') or state.window_start <= 0:
        state.window_start = time.time()
        
    now = time.time()
    elapsed = now - state.window_start
    
    # Protección de tiempo mínimo
    if elapsed < 0.001:
        return False

    # Control de Tasa de Intervención (Cobertura Línea 60)
    # Se usa max(elapsed, 1) para evitar ZeroDivisionError en micro-tiempos
    interv_per_hour = state.intervention_count / (max(elapsed, 1) / 3600)
    max_rate = getattr(config, 'max_interv_rate', 100)
    
    if interv_per_hour > max_rate:
        return True

    # Umbral de ganancia marginal
    threshold = getattr(config, 'marginal_gain_threshold', 0.05)
    return marginal_gain < threshold

def detect_respiro(state: Any, config: Any, marginal_gain: float = 0.0) -> bool:
    """Requerido por tests/test_saturacion_omega.py"""
    return should_apply(state, config, marginal_gain)

def evaluar_paz_sistematica(state: Any, config: Any, gain: float) -> bool:
    """Requerido por tests/test_cierre_integrado.py"""
    return should_apply(state, config, gain)

def distribute_action(total_energy: float, sensitivities: Dict[str, float]) -> Dict[str, float]:
    """
    Distribuye energía basándose en sensibilidades. 
    Protección contra suma cero (Cobertura Línea 74).
    """
    if not sensitivities:
        return {}

    total_sens = sum(sensitivities.values())

    # Rama crítica para cobertura: Sensibilidad nula o negativa
    if total_sens <= 0:
        return {k: 0.0 for k in sensitivities}

    return {k: (v / total_sens) * total_energy for k, v in sensitivities.items()}
