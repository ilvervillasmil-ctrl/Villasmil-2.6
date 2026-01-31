from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple
import math
import time
# Esta es la conexión clave:
from villasmil_omega.cierre.invariancia import Invariancia

@dataclass
class RespiroConfig:
    max_total_effort: float = 1.0
    min_component: float = 0.0
    max_component: float = 0.6
    interv_threshold_per_hour: float = 5.0
    min_deadband_fraction: float = 0.5
    marginal_gain_epsilon: float = 0.02

@dataclass
class RespiroState:
    interv_count: int = 0
    deadband_seconds: float = 0.0
    window_seconds: float = 3600.0
    window_start: float = None

    def start_window(self) -> None:
        if self.window_start is None:
            self.window_start = time.time()

    def metrics(self) -> Tuple[float, float]:
        self.start_window()
        elapsed = max(1.0, time.time() - self.window_start)
        interv_per_hour = self.interv_count * 3600.0 / elapsed
        frac_deadband = min(1.0, self.deadband_seconds / elapsed)
        return interv_per_hour, frac_deadband

def distribute_action(base_effort: float, sensitivities: Dict[str, float], cfg: RespiroConfig) -> Dict[str, float]:
    base_effort = max(0.0, min(base_effort, cfg.max_total_effort))
    s_sum = sum(max(0.0, v) for v in sensitivities.values())
    if s_sum <= 0.0: return {k: 0.0 for k in sensitivities}
    weights = {k: max(0.0, v) / s_sum for k, v in sensitivities.items()}
    return {k: max(cfg.min_component, min(base_effort * w, cfg.max_component)) for k, w in weights.items()}

def should_apply(current_R: float, effort_soft: Dict[str, float], effort_hard: Dict[str, float], cost_threshold: float) -> Tuple[bool, float]:
    total_soft = sum(effort_soft.values())
    total_hard = sum(effort_hard.values())
    
    # Ganancia marginal
    r_soft = current_R + (0.2 * (1.0 - math.exp(-total_soft)))
    r_hard = current_R + (0.2 * (1.0 - math.exp(-total_hard)))
    marginal_gain = r_hard - r_soft
    
    # "Podría seguir... pero no vale la pena" (Líneas 39-40)
    cost_soft = total_soft ** 2
    if cost_soft > cost_threshold or marginal_gain < 0.02:
        return True, marginal_gain
    return False, marginal_gain

def detect_respiro(state: RespiroState, cfg: RespiroConfig, marginal_gain_probe: float) -> bool:
    interv_per_hour, frac_deadband = state.metrics()
    return (interv_per_hour < cfg.interv_threshold_per_hour and 
            frac_deadband >= cfg.min_deadband_fraction and 
            marginal_gain_probe < cfg.marginal_gain_epsilon)

# --- EL PUENTE HACIA EL CIERRE ---
def evaluar_paz_sistematica(historial_R: list) -> bool:
    """Consulta al módulo de cierre si el sistema ya llegó a la invarianza."""
    detector = Invariancia(epsilon=1e-3, ventana=5)
    return detector.es_invariante(historial_R)
