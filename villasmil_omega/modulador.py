import math

class ModuladorAD:
    """
    Modulador de Adaptación Dinámica (L4).
    Gestiona la evolución proactiva y el control de rigidez (r_thresh).
    """
    def __init__(self, alpha=0.1, roi_low=0.2, rigidity_high=0.7, base_factor=0.2):
        self.alpha = alpha
        self.roi_low = roi_low
        self.rigidity_high = rigidity_high
        self.factor_exploration = float(base_factor)
        
        # Parámetros de Inercia Estructural v2.6
        self.max_slew_rate = 0.15 
        self.abs_max = 0.60       
        self.base_factor = float(base_factor)
        self.r_thresh = 0.95  # Umbral de rigidez inicial (v2.6)

    def update(self, metrics: dict, anchoring: dict = None) -> dict:
        """
        Calcula el nuevo estado aplicando PPR y reduciendo r_thresh.
        """
        benefit = metrics.get('benefit', 0.5)
        cost = metrics.get('cost', 0.5)
        severity = anchoring.get('severity', 0) if anchoring else 0
        
        # 1. Determinación de la Acción (Meta-Autoridad v2.6)
        # Si la severidad es máxima (>= 0.9), activamos force_probe
        if severity >= 0.9:
            action = "force_probe"
            target = 0.6
        else:
            action = "adjust"
            target = (benefit - cost + self.base_factor)

        # 2. Slew Rate (Control de Inercia)
        diff = target - self.factor_exploration
        if abs(diff) > self.max_slew_rate:
            step = self.max_slew_rate if diff > 0 else -self.max_slew_rate
            self.factor_exploration += step
        else:
            self.factor_exploration = target

        # 3. Evolución del r_thresh (Requerido por los tests)
        # El umbral de rigidez disminuye inversamente al factor de exploración
        self.r_thresh = max(0.1, 0.95 - (self.factor_exploration * 0.5))

        # Clamp Final
        self.factor_exploration = max(0.0, min(self.factor_exploration, self.abs_max))

        return {
            "action": action,
            "factor_exploration": round(self.factor_exploration, 2),
            "r_thresh": round(self.r_thresh, 3), # Clave crítica para test_mad_real
            "meta_auth": "active_meta_coherence" if action == "force_probe" else "basal",
            "reason": "Slew rate limited" if abs(diff) > self.max_slew_rate else "Stable"
        }
