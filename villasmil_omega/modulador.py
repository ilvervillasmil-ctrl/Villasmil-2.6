import math

class ModuladorAD:
    """
    Modulador de Adaptación Dinámica (L4).
    Controla la exploración proactiva respetando el Slew Rate (v2.6).
    """
    def __init__(self, alpha=0.1, roi_low=0.2, rigidity_high=0.7, base_factor=0.2):
        self.alpha = alpha
        self.roi_low = roi_low
        self.rigidity_high = rigidity_high
        self.factor_exploration = float(base_factor)
        
        # Parámetros de Inercia y Techos Estructurales
        self.max_slew_rate = 0.15  # Incremento máximo permitido por paso
        self.abs_max = 0.60        # Techo para permitir la evolución profunda
        self.base_factor = float(base_factor)

    def update(self, metrics: dict, anchoring: dict = None) -> dict:
        """
        Calcula el nuevo factor aplicando PPR (Proactive Refinement Protocol).
        """
        benefit = metrics.get('benefit', 0.5)
        cost = metrics.get('cost', 0.5)
        severity = anchoring.get('severity', 0) if anchoring else 0
        is_anchored = anchoring.get('is_anchored', False) if anchoring else False
        
        # 1. Determinación del Target
        # Si hay anclaje severo (test L4), el target busca romper la rigidez (0.6)
        if is_anchored and severity > 0.8:
            target = 0.6
            action = "force_probe"
        else:
            # Lógica estándar de balance Beneficio/Costo
            target = (benefit - cost + self.base_factor)
            action = "adjust"

        # 2. Aplicación de SLEW RATE (Evitar saltos reactivos)
        # La diferencia entre el estado actual y el deseado no puede exceder 0.15
        diff = target - self.factor_exploration
        
        if abs(diff) > self.max_slew_rate:
            if diff > 0:
                self.factor_exploration += self.max_slew_rate
            else:
                self.factor_exploration -= self.max_slew_rate
        else:
            self.factor_exploration = target

        # 3. Clamping de Seguridad v2.6
        self.factor_exploration = max(0.0, min(self.factor_exploration, self.abs_max))

        return {
            "action": action,
            "factor_exploration": round(self.factor_exploration, 2),
            "meta_auth": "active_meta_coherence" if action == "force_probe" else "basal",
            "reason": "Slew rate limited" if abs(diff) > self.max_slew_rate else "Stable"
        }

    def get_current_state(self):
        return self.factor_exploration
