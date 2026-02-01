import math

class ModuladorAD:
    def __init__(self, **kwargs):
        # Identidad y Seguridad
        self.role = "system_adjustment_tool"
        self.cooldown_period = kwargs.get('cooldown', 300)
        self.last_update_time = 0
        
        # Parámetros de Control (Estado actual)
        self.factor_exploration = kwargs.get('base_factor', 0.2)
        self.r_thresh = kwargs.get('base_r_thresh', 0.95)
        
        # Límites de Seguridad (Hard Constraints)
        self.limits = {
            'factor': (0.0, 0.95),
            'r_thresh': (0.85, 0.995),
            'max_delta_f': 0.15,
            'max_delta_r': 0.02
        }
        
        # Media Móvil (EWMA) para estabilidad
        self.alpha = kwargs.get('alpha', 0.1)
        self.roi_s = 0.5
        self.cost_s = 0.1

    def update(self, metrics, anchoring=None):
        """
        Paso de control automático. 
        anchoring: dict con {'severity': float, 'is_anchored': bool}
        """
        # 1. Actualizar Telemetría Suavizada
        benefit = metrics.get('benefit', 0.5)
        cost = metrics.get('cost', 0.1)
        self.roi_s = (self.alpha * (benefit / (cost + 1e-6))) + (1 - self.alpha) * self.roi_s
        self.cost_s = (self.alpha * cost) + (1 - self.alpha) * self.cost_s
        
        # 2. Influencia de L4 (Anchoring)
        severity = anchoring.get('severity', 0.0) if anchoring else 0.0
        rigidez = 1.0 - metrics.get('diversity_index', 0.5)
        
        # 3. Calcular Targets (Fórmulas de tu propuesta)
        # target_f = base + k_r*(1-ROI) + k_g*Rigidez + k_a*Severity
        t_factor = 0.2 + 0.4 * (1.0 - min(self.roi_s, 1.0)) + 0.2 * rigidez + 0.3 * severity
        t_r_thresh = 0.95 - (0.1 * severity) # Bajar umbral si hay anclaje para facilitar desapego
        
        # 4. Aplicar Slew Rate Limit & Clamping
        self.factor_exploration = self._step_limit(
            self.factor_exploration, t_factor, 
            self.limits['max_delta_f'], self.limits['factor']
        )
        self.r_thresh = self._step_limit(
            self.r_thresh, t_r_thresh, 
            self.limits['max_delta_r'], self.limits['r_thresh']
        )
        
        return {
            "action": "adjust" if self.roi_s < 0.5 or severity > 0.7 else "monitor",
            "factor_exploration": round(self.factor_exploration, 2),
            "r_thresh": round(self.r_thresh, 3),
            "roi_smoothed": round(self.roi_s, 2),
            "role": self.role
        }

    def _step_limit(self, current, target, max_delta, bounds):
        target = max(bounds[0], min(target, bounds[1]))
        delta = target - current
        step = math.copysign(min(abs(delta), max_delta), delta)
        return current + step
