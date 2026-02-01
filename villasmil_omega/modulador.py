import math

class ModuladorAD:
    def __init__(self, alpha=0.1, roi_low=0.2, rigidity_high=0.7, **kwargs):
        self.role = "system_adjustment_tool"
        self.alpha = alpha
        self.roi_low = roi_low
        self.rigidity_high = rigidity_high
        
        # Slew Rate calibrado para respuesta ágil
        self.max_factor = kwargs.get('max_factor', 0.95)
        self.max_delta = kwargs.get('max_delta', 0.3) 
        self.factor_exploration = kwargs.get('base_factor', 0.2)
        
        self.ewma_benefit = 0.5
        self.ewma_cost = 0.1
        self.ewma_entropy = 0.5
        self.cooldown = 0

    def update(self, metrics):
        self.ewma_benefit = (self.alpha * metrics.get('benefit', 0)) + (1 - self.alpha) * self.ewma_benefit
        self.ewma_cost = (self.alpha * metrics.get('cost', 0)) + (1 - self.alpha) * self.ewma_cost
        self.ewma_entropy = (self.alpha * metrics.get('entropy', 0.5)) + (1 - self.alpha) * self.ewma_entropy
        
        roi = self.ewma_benefit / (self.ewma_cost + 1e-6)
        rigidez = 1 - self.ewma_entropy
        
        # Objetivo de la herramienta
        target = self.max_factor if (roi < self.roi_low or rigidez > self.rigidity_high) else 0.2
        action = "force_probe" if target == self.max_factor else "monitor"

        # Aplicación del Slew Rate
        diff = target - self.factor_exploration
        self.factor_exploration += math.copysign(min(abs(diff), self.max_delta), diff)
        self.factor_exploration = round(self.factor_exploration, 2)
        
        return {
            "action": action,
            "factor_exploration": self.factor_exploration,
            "target_thresholds": {"theta_min": 0.0, "fatiga_max": 1.0, "respiro_prob": 1.0},
            "role": self.role,
            "reason": "Intervención por rigidez" if action == "force_probe" else "Estabilidad"
        }
