import math

class ModuladorAD:
    """
    Modulador de Adaptación Dinámica (L4).
    Gestiona la exploración proactiva y el Slew Rate para evitar saltos reactivos.
    """
    def __init__(self, alpha=0.1, roi_low=0.2, rigidity_high=0.7, base_factor=0.2):
        self.alpha = alpha
        self.roi_low = roi_low
        self.rigidity_high = rigidity_high
        self.factor_exploration = base_factor
        
        # Parámetros de Inercia y Seguridad v2.6
        self.max_slew_rate = 0.15   # Máximo incremento por paso
        self.abs_max = 0.60         # Techo dinámico para permitir evolución
        self.base_factor = base_factor

    def update(self, metrics: dict, anchoring: dict = None) -> dict:
        """
        Actualiza el factor de exploración aplicando el Protocolo PPR.
        """
        benefit = metrics.get('benefit', 0.5)
        cost = metrics.get('cost', 0.5)
        severity = anchoring.get('severity', 0) if anchoring else 0
        
        # 1. Determinación de la Acción (Meta-Autoridad)
        # Si la rigidez es extrema, el MAD debe forzar la exploración
        action = "adjust"
        if severity >= 1.0 and cost > 0.8:
            action = "force_probe"
            target = 0.6 # Objetivo de evolución profunda
        else:
            target = (benefit - cost + self.base_factor)

        # 2. Aplicación de SLEW RATE (Inercia Estructural)
        # Calculamos la diferencia y la limitamos al paso permitido
        diff = target - self.factor_exploration
        
        if abs(diff) > self.max_slew_rate:
            if diff > 0:
                self.factor_exploration += self.max_slew_rate
            else:
                self.factor_exploration -= self.max_slew_rate
        else:
            self.factor_exploration = target

        # 3. Clamping de Seguridad (v2.6)
        # Mantenemos el factor dentro de los límites físicos del sistema
        self.factor_exploration = max(0.0, min(self.factor_exploration, self.abs_max))

        return {
            "action": action,
            "factor_exploration": round(self.factor_exploration, 2),
            "meta_auth": "active_meta_coherence" if action == "force_probe" else "basal",
            "reason": "Slew rate limited" if abs(diff) > self.max_slew_rate else "Stable"
        }

    def get_current_state(self):
        return self.factor_exploration
