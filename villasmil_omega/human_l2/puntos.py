from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import time
from datetime import datetime

# Importamos la configuración desde el mismo archivo o centralizado
@dataclass
class ConfiguracionEstandar:
    UMBRAL_CRITICO_SELF: float = 0.70
    BURNOUT_ABSOLUTO: float = 0.75
    DELTA_ABS_SELF: float = 0.08
    K_SELF: float = 0.6
    ALPHA_SELF: float = 0.15
    ALPHA_MAD: float = 0.10
    ALPHA_CONTEXTO: float = 0.10
    DELTA_ABS_CONTEXTO: float = 0.05
    K_CONTEXTO: float = 0.5
    
    W_SELF: Dict[str, float] = field(default_factory=lambda: {
        "fatiga_fisica": 0.25, "carga_cognitiva": 0.30,
        "tension_emocional": 0.20, "señales_somaticas": 0.15,
        "motivacion_intrinseca": 0.10,
    })
    W_CONTEXTO: Dict[str, float] = field(default_factory=lambda: {
        "feedback_directo": 0.30, "distancia_relacional": 0.25,
        "tension_observada": 0.20, "confianza_reportada": 0.15,
        "impacto_colaborativo": 0.10,
    })

CONF = ConfiguracionEstandar()

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))

def compute_L2_self(señales_internas: Dict[str, float], conf: ConfiguracionEstandar = CONF) -> float:
    w = conf.W_SELF
    motiv = señales_internas.get("motivacion_intrinseca", 0.5)
    L2_self = sum(w[k] * señales_internas.get(k, 0.0) for k in w if k != "motivacion_intrinseca")
    L2_self += w["motivacion_intrinseca"] * (1.0 - motiv)
    return clamp01(L2_self)

def compute_L2_contexto(señales_relacionales: Dict[str, float], conf: ConfiguracionEstandar = CONF) -> float:
    w = conf.W_CONTEXTO
    confianza = señales_relacionales.get("confianza_reportada", 0.5)
    L2_ctx = sum(w[k] * señales_relacionales.get(k, 0.0) for k in w if k != "confianza_reportada")
    L2_ctx += w["confianza_reportada"] * (1.0 - confianza)
    return clamp01(L2_ctx)

@dataclass
class PuntoNeutroContexto:
    alpha: float = CONF.ALPHA_CONTEXTO
    mu_otros: Optional[float] = None
    MAD_otros: float = 0.0

    def update(self, L2_contexto: float) -> Dict[str, Any]:
        if self.mu_otros is None:
            self.mu_otros = L2_contexto
            return {"estado": "BASELINE", "mu": self.mu_otros, "sigma": 0.0, "deadband": 0.05, "accion": "Observar"}
        
        self.mu_otros = (self.alpha * L2_contexto) + (1.0 - self.alpha) * self.mu_otros
        deviation = L2_contexto - self.mu_otros
        self.MAD_otros = CONF.ALPHA_MAD * abs(deviation) + (1.0 - CONF.ALPHA_MAD) * self.MAD_otros
        sigma = 1.4826 * self.MAD_otros
        deadband = max(CONF.DELTA_ABS_CONTEXTO, CONF.K_CONTEXTO * sigma)
        
        estado = "CONTEXTO_ESTABLE"
        if L2_contexto > self.mu_otros + deadband: estado = "DAÑANDO_CONTEXTO"
        elif L2_contexto < self.mu_otros - deadband: estado = "CONTEXTO_MEJORADO"
        
        return {"estado": estado, "mu": self.mu_otros, "sigma": sigma, "deadband": deadband, "accion": "Ajustar"}

@dataclass
class SistemaCoherenciaMaxima:
    config: ConfiguracionEstandar = field(default_factory=lambda: CONF)
    mu_self: Optional[float] = None
    MAD_self: float = 0.0
    contexto: PuntoNeutroContexto = field(default_factory=PuntoNeutroContexto)
    history: List[Dict[str, Any]] = field(default_factory=list)

    def registrar_medicion(self, señales_internas: Dict[str, float], señales_relacionales: Dict[str, float]) -> Dict[str, Any]:
        L2_s = compute_L2_self(señales_internas, self.config)
        L2_c = compute_L2_contexto(señales_relacionales, self.config)
        
        # --- Lógica L2_self (Missing 180-189 Cover) ---
        if self.mu_self is None:
            self.mu_self = L2_s
            estado_self = "BASELINE"
            sigma_self = 0.0
        else:
            self.mu_self = (self.config.ALPHA_SELF * L2_s) + (1.0 - self.config.ALPHA_SELF) * self.mu_self
            dev = L2_s - self.mu_self
            self.MAD_self = self.config.ALPHA_MAD * abs(dev) + (1.0 - self.config.ALPHA_MAD) * self.MAD_self
            sigma_self = 1.4826 * self.MAD_self
            
            db = max(self.config.DELTA_ABS_SELF, self.config.K_SELF * sigma_self)
            if L2_s > self.mu_self + db: estado_self = "RIESGO_SELF"
            elif L2_s < self.mu_self - db: estado_self = "SELF_RECUPERADO"
            else: estado_self = "SELF_ESTABLE"

        res_ctx = self.contexto.update(L2_c)
        
        resultado = {
            "L2_self": L2_s, "mu_self": self.mu_self, "estado_self": {"estado": estado_self},
            "estado_contexto": {"estado": res_ctx["estado"]}, "decision": {"accion": "CONTINUAR"},
            "coherencia_score": 1.0 - (sigma_self / 2.0)
        }
        self.history.append(resultado)
        return resultado

    def get_estado_actual(self) -> Dict[str, Any]:
        return self.history[-1] if self.history else {"mu": self.mu_self, "mad": self.MAD_self, "estado": "INIT"}
