import math

class ModuladorAD:
    """
    Modulador de Adaptación Dinámica (L4).
    Controla la exploración estratégica respetando la inercia del sistema (Slew Rate).
    """
    def __init__(self, alpha=0.1, roi_low=0.2, rigidity_high=0.7, base_factor=0.2):
        self.alpha = alpha
        self.roi_low = roi_low
        self.rigidity_high = rigidity_high
        self.factor_exploration = base_factor
        
        # Parámetros de Seguridad v2.6
        self.max_slew_rate = 0.15  # Máximo cambio permitido por paso
        self.abs_max_anchored = 0.35 # Techo cuando hay anclaje severo en L4
        self.base_factor = base_factor

    def update(self, metrics: dict, anchoring: dict = None) -> dict:
        """
        Calcula el nuevo factor de exploración aplicando PPR y Slew Rate.
        """
        # 1. Determinar el Target según métricas de beneficio/costo
        benefit = metrics.get('benefit', 0.5)
        cost = metrics.get('cost', 0.5)
        
        # El target ideal según PPR (Proactive Refinement)
        target = (benefit - cost + self.base_factor)
        
        # 2. Gestión de Anclaje (Severidad L4)
        is_anchored = False
        if anchoring and anchoring.get('is_anchored'):
            is_anchored = True
            # El anclaje severo empuja el target hacia arriba (intento de ruptura)
            if anchoring.get('severity', 0) > 0.8:
                target = 0.6  # Intento de salto agresivo
        
        # 3. Aplicación estricta de SLEW RATE (Inercia)
        # No permitimos que el factor cambie más de 0.15 respecto al actual
        delta = target - self.factor_exploration
        
        if abs(delta) > self.max_slew_rate:
            if delta > 0:
                self.factor_exploration += self.max_slew_rate
            else:
                self.factor_exploration -= self.max_slew_rate
        else:
            self.factor_exploration = target

        # 4. Capa de Seguridad Master (Clamping)
        # Si hay anclaje, el techo absoluto es 0.35 para proteger la coherencia
        if is_anchored:
            self.factor_exploration = min(self.factor_exploration, self.abs_max_anchored)
        
        # Asegurar rango [0, 1]
        self.factor_exploration = max(0.0, min(self.factor_exploration, 1.0))

        return {
            "action": "adjust",
            "factor_exploration": round(self.factor_exploration, 2),
            "meta_auth": "active_meta_coherence" if self.factor_exploration > 0.3 else "basal",
            "reason": "Slew rate limited transition" if abs(delta) > self.max_slew_rate else "Target reached"
        }

    def get_current_state(self):
        return self.factor_exploration
