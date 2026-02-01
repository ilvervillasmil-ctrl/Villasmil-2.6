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
    Alias principal requerido por test_final y test_presion_prolongada.
    """
    # Línea 25-27: Manejo de inicialización de ventana
    if not hasattr(state, 'window_start') or state.window_start <= 0:
        state.window_start = time.time()
        
    now = time.time()
    elapsed = now - state.window_start
    
    if elapsed < 0.001:
        return False

    # Línea 60: Control de Tasa por Hora
    interv_per_hour = state.intervention_count / (max(elapsed, 1) / 3600)
    if interv_per_hour > getattr(config, 'max_interv_rate', 100):
        return True

    return marginal_gain < getattr(config, 'marginal_gain_threshold', 0.05)

def evaluar_paz_sistematica(state: Any, config: Any, gain: float) -> bool:
    """
    Alias requerido por test_cierre_integrado.
    """
    return should_apply(state, config, gain)

def distribute_action(total_energy: float, sensitivities: Dict[str, float]) -> Dict[str, float]:
    """
    Distribución de energía con protección de suma cero (Línea 74).
    """
    if not sensitivities:
        return {}

    total_sens = sum(sensitivities.values())

    # Línea 74: Si no hay sensibilidad, la energía no se mueve
    if total_sens <= 0:
        return {k: 0.0 for k in sensitivities}

    return {k: (v / total_sens) * total_energy for k, v in sensitivities.items()}
