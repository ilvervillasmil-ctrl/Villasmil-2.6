import time

class ModuladorAD:
    def __init__(self, alpha=0.1, roi_low=0.2, rigidity_high=0.7):
        self.alpha = alpha
        self.roi_low = roi_low
        self.rigidity_high = rigidity_high
        self.ewma_benefit = 0.5
        self.ewma_cost = 0.1
        self.ewma_entropy = 0.5
        self.last_probe_time = 0
        self.cooldown = 0 # En modo ajuste deliberado bajamos la guardia

    def update(self, metrics):
        self.ewma_benefit = (self.alpha * metrics.get('benefit', 0)) + (1 - self.alpha) * self.ewma_benefit
        self.ewma_cost = (self.alpha * metrics.get('cost', 0)) + (1 - self.alpha) * self.ewma_cost
        self.ewma_entropy = (self.alpha * metrics.get('entropy', 0.5)) + (1 - self.alpha) * self.ewma_entropy
        
        roi = self.ewma_benefit / (self.ewma_cost + 1e-6)
        rigidez = 1 - self.ewma_entropy
        
        # AJUSTE DELIBERADO
        if roi < self.roi_low or rigidez > self.rigidity_high:
            return self.ejecutar_ajuste_deliberado()
        
        return {"action": "monitor", "factor": 0.2, "reason": "estabilidad"}

    def ejecutar_ajuste_deliberado(self):
        """Calcula una corrección activa para forzar la salida del estancamiento."""
        ajuste = {
            "action": "force_probe",
            "factor_exploration": 0.95, # Presión máxima
            "target_thresholds": {
                "theta_min": 0.0, 
                "fatiga_max": 1.0,
                "respiro_prob": 1.0
            },
            "reason": "Ajuste deliberado por rigidez detectada"
        }
        return ajuste
