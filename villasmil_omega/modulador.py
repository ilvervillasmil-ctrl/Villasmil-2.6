import math

class ModuladorAD:
    def __init__(self, alpha=0.1, roi_low=0.2, rigidity_high=0.7, **kwargs):
        self.role = "system_adjustment_tool"
        self.alpha = alpha
        self.roi_low = roi_low
        self.rigidity_high = rigidity_high
        self.max_factor = kwargs.get('max_factor', 0.95)
        self.factor_exploration = kwargs.get('base_factor', 0.2)
        self.ewma_benefit = 0.5
        self.ewma_cost = 0.1
        self.ewma_entropy = 0.5

    def update(self, metrics):
        # Actualización de memoria del sistema
        self.ewma_benefit = (self.alpha * metrics.get('benefit', 0)) + (1 - self.alpha) * self.ewma_benefit
        self.ewma_cost = (self.alpha * metrics.get('cost', 0)) + (1 - self.alpha) * self.ewma_cost
        self.ewma_entropy = (self.alpha * metrics.get('entropy', 0.5)) + (1 - self.alpha) * self.ewma_entropy
        
        roi = self.ewma_benefit / (self.ewma_cost + 1e-6)
        rigidez = 1 - self.ewma_entropy
        
        # AJUSTE DELIBERADO: Si los valores instantáneos o la EWMA fallan, intervenimos.
        # Priorizamos la métrica instantánea para una respuesta táctica rápida en tests.
        if metrics.get('benefit', 1.0) < 0.05 or roi < self.roi_low or rigidez > self.rigidity_high:
            self.factor_exploration = self.max_factor
            action = "force_probe"
        else:
            self.factor_exploration = 0.2
            action = "monitor"

        return {
            "action": action,
            "factor_exploration": self.factor_exploration,
            "target_thresholds": {"theta_min": 0.0, "fatiga_max": 1.0},
            "role": self.role,
            "reason": "Intervención por estancamiento detectado"
        }
