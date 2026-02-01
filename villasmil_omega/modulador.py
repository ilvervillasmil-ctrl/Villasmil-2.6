import math

class ModuladorAD:
    """
    MODULADOR DE AJUSTE DINÁMICO (MAD) v2.6
    Anclado en L4 como herramienta de Meta-Coherencia.
    """
    def __init__(self, **kwargs):
        self.role = "system_adjustment_tool"
        self.meta_auth = "active_meta_coherence"
        
        # Parámetros de Control
        self.factor_exploration = kwargs.get('base_factor', 0.2)
        self.r_thresh = kwargs.get('base_r_thresh', 0.95)
        
        # Límites de Seguridad y Agilidad (Slew Rate)
        self.limits = {
            'factor': (0.0, 0.95),
            'r_thresh': (0.80, 0.995),
            'max_delta_f': 0.4,  # Respuesta rápida para superar bloqueos
            'max_delta_r': 0.05
        }
        
        # Memoria del Sistema (EWMA)
        self.alpha = kwargs.get('alpha', 0.1)
        self.roi_s = 0.5
        self.rigidez_s = 0.5

    def update(self, metrics, anchoring=None):
        # 1. Suavizado de telemetría
        benefit = metrics.get('benefit', 0.5)
        cost = metrics.get('cost', 0.1)
        diversity = metrics.get('diversity_index', 0.5)
        
        self.roi_s = (self.alpha * (benefit / (cost + 1e-6))) + (1 - self.alpha) * self.roi_s
        self.rigidez_s = (self.alpha * (1.0 - diversity)) + (1 - self.alpha) * self.rigidez_s
        
        severity = anchoring.get('severity', 0.0) if anchoring else 0.0
        
        # 2. Lógica de Meta-Coherencia (Cálculo de Targets)
        # Si hay rigidez o anclaje excesivo, disparamos force_probe
        if self.roi_s < 0.3 or self.rigidez_s > 0.7 or severity > 0.8:
            t_factor = self.limits['factor'][1]
            t_r_thresh = self.limits['r_thresh'][0]
            action = "force_probe"
        else:
            t_factor = 0.2
            t_r_thresh = 0.95
            action = "monitor"

        # 3. Aplicación de Rampa Controlada
        self.factor_exploration = self._step_limit(
            self.factor_exploration, t_factor, 
            self.limits['max_delta_f'], self.limits['factor']
        )
        self.r_thresh = self._step_limit(
            self.r_thresh, t_r_thresh, 
            self.limits['max_delta_r'], self.limits['r_thresh']
        )

        return {
            "action": action,
            "factor_exploration": round(self.factor_exploration, 2),
            "r_thresh": round(self.r_thresh, 3),
            "role": self.role,
            "meta_auth": self.meta_auth,
            "reason": f"Ajuste por {'rigidez' if action == 'force_probe' else 'estabilidad'}"
        }

    def _step_limit(self, current, target, max_delta, bounds):
        target = max(bounds[0], min(target, bounds[1]))
        delta = target - current
        step = math.copysign(min(abs(delta), max_delta), delta)
        return current + step
