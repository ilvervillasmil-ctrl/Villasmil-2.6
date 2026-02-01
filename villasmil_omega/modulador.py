import math

class ModuladorAD:
    def __init__(self, alpha=0.1, roi_low=0.2, rigidity_high=0.7, **kwargs):
        self.role = "system_adjustment_tool"
        self.alpha = alpha
        self.roi_low = roi_low
        self.rigidity_high = rigidity_high
        
        # Parámetros de robustez
        self.max_factor = kwargs.get('max_factor', 0.95)
        self.max_delta = kwargs.get('max_delta', 0.2) # Cambio máximo por update
        self.factor_exploration = kwargs.get('base_factor', 0.2)
        
        self.ewma_benefit = 0.5
        self.ewma_cost = 0.1
        self.ewma_entropy = 0.5
        self.last_probe_time = 0
        self.cooldown = 0

    def update(self, metrics):
        # Actualización EWMA
        self.ewma_benefit = (self.alpha * metrics.get('benefit', 0)) + (1 - self.alpha) * self.ewma_benefit
        self.ewma_cost = (self.alpha * metrics.get('cost', 0)) + (1 - self.alpha) * self.ewma_cost
        self.ewma_entropy = (self.alpha * metrics.get('entropy', 0.5)) + (1 - self.alpha) * self.ewma_entropy
        
        roi = self.ewma_benefit / (self.ewma_cost + 1e-6)
        rigidez = 1 - self.ewma_entropy
        
        # Determinar target_raw
        if roi < self.roi_low or rigidez > self.rigidity_high:
            target_factor = self.max_factor
            action = "force_probe"
        else:
            target_factor = 0.2
            action = "monitor"

        # Movimiento limitado por paso (Slew Rate Limit)
        delta = target_factor - self.factor_exploration
        if abs(delta) > self.max_delta:
            delta = math.copysign(self.max_delta, delta)
        
        self.factor_exploration = round(self.factor_exploration + delta, 2)
        
        return {
            "action": action,
            "factor_exploration": self.factor_exploration,
            "target_thresholds": {"theta_min": 0.0, "fatiga_max": 1.0, "respiro_prob": 1.0},
            "role": self.role,
            "reason": "Ajuste deliberado por rigidez" if action == "force_probe" else "Estabilidad"
        }
