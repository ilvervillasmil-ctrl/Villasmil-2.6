from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple
import math
import time

@dataclass
class RespiroConfig:
    """Reglas prácitcas para el controlador (Mente Relajada)."""
    max_total_effort: float = 1.0
    min_component: float = 0.0
    max_component: float = 0.6
    interv_threshold_per_hour: float = 5.0
    min_deadband_fraction: float = 0.5
    marginal_gain_epsilon: float = 0.02

@dataclass
class RespiroState:
    """Estado de autorregulación (Propósito Claro)."""
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

def distribute_action(
    base_effort: float,
    sensitivities: Dict[str, float],
    cfg: RespiroConfig,
) -> Dict[str, float]:
    """
    REGLA 1: Nunca atacar una sola capa.
    Distribuye la carga entre L1 y L6 para no romper el límite.
    """
    base_effort = max(0.0, min(base_effort, cfg.max_total_effort))
    s_sum = sum(max(0.0, v) for v in sensitivities.values())
    
    if s_sum <= 0.0:
        return {k: 0.0 for k in sensitivities}
    
    weights = {k: max(0.0, v) / s_sum for k, v in sensitivities.items()}
    raw = {k: base_effort * weights[k] for k in sensitivities}
    
    return {
        k: max(cfg.min_component, min(v, cfg.max_component)) 
        for k, v in raw.items()
    }

@dataclass
class SimulatedOutcome:
    R_final: float
    cost: float

def simulate_apply(current_R: float, effort: Dict[str, float]) -> SimulatedOutcome:
    """Simula el impacto: Beneficio saturable y coste de reacción."""
    total_effort = sum(effort.values())
    delta_R = 0.2 * (1.0 - math.exp(-total_effort))
    cost = total_effort ** 2
    return SimulatedOutcome(R_final=current_R + delta_R, cost=cost)

def should_apply(
    current_R: float,
    effort_soft: Dict[str, float],
    effort_hard: Dict[str, float],
    cost_threshold: float,
) -> Tuple[bool, float]:
    """REGLA 2: No forzar el límite. Compara si el empuje extra vale la pena."""
    soft = simulate_apply(current_R, effort_soft)
    hard = simulate_apply(current_R, effort_hard)
    marginal_gain = hard.R_final - soft.R_final
    
    # "Podría empujar más... pero no hace falta."
    can_apply = soft.cost <= cost_threshold and marginal_gain < 0.02
    return can_apply, marginal_gain

def detect_respiro(
    state: RespiroState,
    cfg: RespiroConfig,
    marginal_gain_probe: float,
) -> bool:
    """REGLA 3: El éxito es no reaccionar."""
    interv_per_hour, frac_deadband = state.metrics()
    return (
        interv_per_hour < cfg.interv_threshold_per_hour and
        frac_deadband >= cfg.min_deadband_fraction and
        marginal_gain_probe < cfg.marginal_gain_epsilon
    )
