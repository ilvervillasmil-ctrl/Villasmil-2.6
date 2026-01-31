from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import time
from datetime import datetime

# ============================================================
# CONFIGURACIÓN Y UTILIDADES
# ============================================================

@dataclass
class ConfiguracionEstandar:
    UMBRAL_CRITICO_SELF: float = 0.70
    DELTA_ABS_SELF: float = 0.08
    DELTA_ABS_CONTEXTO: float = 0.05
    K_SELF: float = 0.6
    K_CONTEXTO: float = 0.5
    ALPHA_SELF: float = 0.15
    ALPHA_CONTEXTO: float = 0.10
    ALPHA_MAD: float = 0.10
    
    W_CONTEXTO: Dict[str, float] = field(default_factory=lambda: {
        "feedback_directo": 0.30, "distancia_relacional": 0.25,
        "tension_observada": 0.20, "confianza_reportada": 0.15,
        "impacto_colaborativo": 0.10,
    })
    W_SELF: Dict[str, float] = field(default_factory=lambda: {
        "fatiga_fisica": 0.25, "carga_cognitiva": 0.30,
        "tension_emocional": 0.20, "señales_somaticas": 0.15,
        "motivacion_intrinseca": 0.10,
    })

CONF = ConfiguracionEstandar()

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))

def update_mad(prev_mad: float, deviation: float, alpha: float = 0.1) -> float:
    return alpha * abs(deviation) + (1.0 - alpha) * prev_mad

def mad_to_sigma(mad_value: float) -> float:
    return 1.4826 * mad_value

# ============================================================
# LÓGICA DE CÁLCULO L2
# ============================================================

def compute_L2_contexto(señales: Dict[str, float], conf=CONF) -> float:
    w = conf.W_CONTEXTO
    confianza_inv = 1.0 - señales.get("confianza_reportada", 0.5)
    L2 = (w["feedback_directo"] * señales.get("feedback_directo", 0.0) +
          w["distancia_relacional"] * señales.get("distancia_relacional", 0.0) +
          w["tension_observada"] * señales.get("tension_observada", 0.0) +
          w["confianza_reportada"] * confianza_inv +
          w["impacto_colaborativo"] * señales.get("impacto_colaborativo", 0.0))
    return clamp01(L2)

def compute_L2_self(señales: Dict[str, float], conf=CONF) -> float:
    w = conf.W_SELF
    motiv_inv = 1.0 - señales.get("motivacion_intrinseca", 0.5)
    L2 = (w["fatiga_fisica"] * señales.get("fatiga_fisica", 0.0) +
          w["carga_cognitiva"] * señales.get("carga_cognitiva", 0.0) +
          w["tension_emocional"] * señales.get("tension_emocional", 0.0) +
          w["señales_somaticas"] * señales.get("señales_somaticas", 0.0) +
          w["motivacion_intrinseca"] * motiv_inv)
    return clamp01(L2)

# ============================================================
# SISTEMA DE COHERENCIA
# ============================================================

@dataclass
class PuntoNeutroContexto:
    alpha: float = 0.1
    mu_otros: Optional[float] = None
    MAD_otros: float = 0.0

    def update(self, L2_contexto: float) -> Dict[str, Any]:
        if self.mu_otros is None:
            self.mu_otros = L2_contexto
            return {"estado": "BASELINE", "mu": self.mu_otros, "deadband": 0.05, "accion": "Observar"}
        
        self.mu_otros = self.alpha * L2_contexto + (1.0 - self.alpha) * self.mu_otros
        dev = L2_contexto - self.mu_otros
        self.MAD_otros = update_mad(self.MAD_otros, dev)
        deadband = max(0.05, 0.5 * mad_to_sigma(self.MAD_otros))
        
        estado = "CONTEXTO_ESTABLE"
        if L2_contexto > self.mu_otros + deadband: estado = "DAÑANDO_CONTEXTO"
        elif L2_contexto < self.mu_otros - deadband: estado = "CONTEXTO_MEJORADO"
        
        return {"estado": estado, "mu": self.mu_otros, "deadband": deadband, "accion": "Ajustar impacto"}

@dataclass
class SistemaCoherenciaMaxima:
    config: ConfiguracionEstandar = field(default_factory=lambda: CONF)
    baseline_personal: float = 0.5
    baseline_contexto: float = 0.5
    enable_logging: bool = True
    mu_self: Optional[float] = None
    MAD_self: float = 0.0
    contexto: PuntoNeutroContexto = field(default_factory=PuntoNeutroContexto)
    history: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        if self.mu_self is None: self.mu_self = self.baseline_personal
        if self.contexto.mu_otros is None: self.contexto.mu_otros = self.baseline_contexto

    def registrar_medicion(self, señales_internas, señales_relacionales) -> Dict[str, Any]:
        L2_s = compute_L2_self(señales_internas, self.config)
        L2_c = compute_L2_contexto(señales_relacionales, self.config)
        
        self.mu_self = self.config.ALPHA_SELF * L2_s + (1.0 - self.config.ALPHA_SELF) * self.mu_self
        dev_s = L2_s - self.mu_self
        self.MAD_self = update_mad(self.MAD_self, dev_s)
        db_s = max(self.config.DELTA_ABS_SELF, self.config.K_SELF * mad_to_sigma(self.MAD_self))
        
        est_s = "SELF_ESTABLE"
        acc_s = "Mantén el ritmo"
        if L2_s > self.mu_self + db_s: 
            est_s, acc_s = "RIESGO_SELF", "Reduce carga / descansa"
        elif L2_s < self.mu_self - db_s: 
            est_s, acc_s = "SELF_RECUPERADO", "Puedes asumir algo más"

        res_ctx = self.contexto.update(L2_c)
        
        res = {
            "L2_self": L2_s, "L2_contexto": L2_c, "mu_self": self.mu_self,
            "estado_self": {"estado": est_s}, 
            "accion_self": acc_s,
            "estado_contexto": {"estado": res_ctx["estado"]},
            "accion_contexto": res_ctx["accion"],
            "decision": {"accion": "CONTINUAR"},
            "coherencia_score": 1.0 - clamp01(abs(dev_s))
        }
        self.history.append(res)
        return res

    def get_estado_actual(self):
        return self.history[-1] if self.history else None
