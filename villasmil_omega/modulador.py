import time

class ModuladorAD:
    """
    MAD: Modulador de Ajuste Dinámico.
    Vigila el ROI de los ajustes y decide cuándo forzar la exploración (probes)
    para romper estancamientos de cobertura o coherencia.
    """
    def __init__(self, alpha=0.1, roi_low=0.2, rigidity_high=0.7):
        self.alpha = alpha
        self.roi_low = roi_low
        self.rigidity_high = rigidity_high
        
        # Estados EWMA (Exponential Weighted Moving Average)
        self.ewma_benefit = 0.5
        self.ewma_cost = 0.1
        self.ewma_entropy = 0.5
        self.last_probe_time = 0
        self.cooldown = 900  # 15 minutos

    def update(self, metrics):
        """
        metrics: dict con 'benefit', 'cost', 'entropy'
        returns: dict con la decisión ('action', 'factor_exploration')
        """
        # Actualización de series temporales suaves
        self.ewma_benefit = (self.alpha * metrics.get('benefit', 0)) + (1 - self.alpha) * self.ewma_benefit
        self.ewma_cost = (self.alpha * metrics.get('cost', 0)) + (1 - self.alpha) * self.ewma_cost
        self.ewma_entropy = (self.alpha * metrics.get('entropy', 0.5)) + (1 - self.alpha) * self.ewma_entropy
        
        roi = self.ewma_benefit / (self.ewma_cost + 1e-6)
        rigidez = 1 - self.ewma_entropy
        
        ahora = time.time()
        puedo_actuar = (ahora - self.last_probe_time) > self.cooldown

        # Lógica de Decisión
        if roi < self.roi_low and rigidez > self.rigidity_high and puedo_actuar:
            self.last_probe_time = ahora
            return {
                "action": "force_probe",
                "factor_exploration": 0.8,
                "reason": "Bajo ROI + Alta Rigidez: El sistema está estancado."
            }
        
        return {
            "action": "monitor",
            "factor_exploration": 0.2,
            "reason": "Sistema en equilibrio operativo."
        }
