"""
villasmil_omega.human_l2.puntos

Sistema de Coherencia Máxima con doble punto de referencia y equilibrio dinámico.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import time
import json
from datetime import datetime
from pathlib import Path


# ============================================================
# CONFIGURACIÓN ESTÁNDAR
# ============================================================

@dataclass
class ConfiguracionEstandar:
    UMBRAL_CRITICO_SELF: float = 0.70
    BURNOUT_ABSOLUTO: float = 0.75
    UMBRAL_CRITICO_CONTEXTO: float = 0.75
    UMBRAL_SEGURIDAD_TERCEROS: float = 0.85

    DELTA_ABS_SELF: float = 0.08
    DELTA_ABS_CONTEXTO: float = 0.05
    K_SELF: float = 0.6
    K_CONTEXTO: float = 0.5

    ALPHA_SELF: float = 0.15
    ALPHA_CONTEXTO: float = 0.10
    ALPHA_MAD: float = 0.10

    MIN_L2: float = 0.0
    MAX_L2: float = 1.0
    MIN_L2_OPERATIVO: float = 0.10
    MAX_L2_OPERATIVO: float = 0.95

    COOLDOWN_SECONDS: int = 300
    VENTANA_HISTORIA_HORAS: int = 72

    W_CONTEXTO: Dict[str, float] = field(default_factory=lambda: {
        "feedback_directo": 0.30,
        "distancia_relacional": 0.25,
        "tension_observada": 0.20,
        "confianza_reportada": 0.15,
        "impacto_colaborativo": 0.10,
    })

    W_SELF: Dict[str, float] = field(default_factory=lambda: {
        "fatiga_fisica": 0.25,
        "carga_cognitiva": 0.30,
        "tension_emocional": 0.20,
        "señales_somaticas": 0.15,
        "motivacion_intrinseca": 0.10,
    })

    LOG_DIR: str = "./villasmil_omega_logs"
    ENABLE_LOGGING: bool = True


CONF = ConfiguracionEstandar()


# ============================================================
# UTILIDADES BÁSICAS
# ============================================================

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def clamp(x: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, float(x)))


def timestamp_iso() -> str:
    return datetime.now().isoformat()


# ============================================================
# L2_contexto y L2_self
# ============================================================

def compute_L2_contexto(señales_relacionales: Dict[str, float],
                        conf: ConfiguracionEstandar = CONF) -> float:
    w = conf.W_CONTEXTO

    confianza = señales_relacionales.get("confianza_reportada", 0.5)
    confianza_invertida = 1.0 - confianza

    L2_ctx = (
        w["feedback_directo"] * señales_relacionales.get("feedback_directo", 0.0)
        + w["distancia_relacional"] * señales_relacionales.get("distancia_relacional", 0.0)
        + w["tension_observada"] * señales_relacionales.get("tension_observada", 0.0)
        + w["confianza_reportada"] * confianza_invertida
        + w["impacto_colaborativo"] * señales_relacionales.get("impacto_colaborativo", 0.0)
    )
    return clamp01(L2_ctx)


def compute_L2_self(señales_internas: Dict[str, float],
                    conf: ConfiguracionEstandar = CONF) -> float:
    w = conf.W_SELF

    motiv = señales_internas.get("motivacion_intrinseca", 0.5)
    motiv_invertida = 1.0 - motiv

    L2_self = (
        w["fatiga_fisica"] * señales_internas.get("fatiga_fisica", 0.0)
        + w["carga_cognitiva"] * señales_internas.get("carga_cognitiva", 0.0)
        + w["tension_emocional"] * señales_internas.get("tension_emocional", 0.0)
        + w["señales_somaticas"] * señales_internas.get("señales_somaticas", 0.0)
        + w["motivacion_intrinseca"] * motiv_invertida
    )
    return clamp01(L2_self)


# ============================================================
# MAD ROBUSTA
# ============================================================

def update_mad(prev_mad: float, deviation: float,
               alpha: float = CONF.ALPHA_MAD) -> float:
    return alpha * abs(deviation) + (1.0 - alpha) * prev_mad


def mad_to_sigma(mad_value: float) -> float:
    return 1.4826 * mad_value


# ============================================================
# PUNTO NEUTRO (μ_otros)
# ============================================================

@dataclass
class PuntoNeutroContexto:
    alpha: float = CONF.ALPHA_CONTEXTO
    mu_otros: Optional[float] = None
    MAD_otros: float = 0.0
    history: List[Dict[str, Any]] = field(default_factory=list)

    def update(self, L2_contexto: float,
               timestamp: Optional[float] = None) -> Dict[str, Any]:
        L2_contexto = clamp01(L2_contexto)
        ts = timestamp if timestamp is not None else time.time()

        if self.mu_otros is None:
            self.mu_otros = L2_contexto
            self.MAD_otros = 0.0
            result = {
                "estado": "BASELINE_INICIAL",
                "accion": "Observar - estableciendo baseline",
                "L2_contexto": L2_contexto,
                "mu": self.mu_otros,
                "sigma": 0.0,
                "deadband": CONF.DELTA_ABS_CONTEXTO,
                "desviacion": 0.0,
                "timestamp": ts,
            }
            self.history.append(result)
            return result

        self.mu_otros = (
            self.alpha * L2_contexto
            + (1.0 - self.alpha) * self.mu_otros
        )

        deviation = L2_contexto - self.mu_otros
        self.MAD_otros = update_mad(self.MAD_otros, deviation)
        sigma = mad_to_sigma(self.MAD_otros)
        deadband = max(CONF.DELTA_ABS_CONTEXTO, CONF.K_CONTEXTO * sigma)

        if L2_contexto > self.mu_otros + deadband:
            estado = "DAÑANDO_CONTEXTO"
            accion = "Reducir impacto en otros"
        elif L2_contexto < self.mu_otros - deadband:
            estado = "CONTEXTO_MEJORADO"
            accion = "Continúa - contexto responde bien"
        else:
            estado = "CONTEXTO_ESTABLE"
            accion = "Observar - dentro de rango normal"

        result = {
            "estado": estado,
            "accion": accion,
            "L2_contexto": L2_contexto,
            "mu": self.mu_otros,
            "sigma": sigma,
            "deadband": deadband,
            "desviacion": deviation,
            "timestamp": ts,
        }
        self.history.append(result)
        return result

    def get_explicacion(self, resultado: Dict[str, Any]) -> str:
        L2 = resultado["L2_contexto"]
        mu = resultado["mu"]
        estado = resultado["estado"]

        if estado == "DAÑANDO_CONTEXTO":
            return (f"CONTEXTO: L₂={L2:.2f} > μ={mu:.2f}+deadband. "
                    f"Generas tensión. Reduce impacto.")
        elif estado == "CONTEXTO_MEJORADO":
            return (f"CONTEXTO: L₂={L2:.2f} < μ={mu:.2f}. "
                    f"Relaciones mejoran. Continúa.")
        else:
            return (f"CONTEXTO: L₂={L2:.2f} ≈ μ={mu:.2f}. "
                    f"Situación estable.")
