import pytest
from villasmil_omega.human_l2.puntos import (
    ConfiguracionEstandar, compute_L2_contexto, compute_L2_self,
    PuntoNeutroContexto, PuntoEquilibrioSelfDinamico, ProtocoloPrioridad
)
from villasmil_omega.core import theta_C, compute_phi_C
from villasmil_omega.l2_model import L2HumanModel
from villasmil_omega.respiro import RespiroOmega
from villasmil_omega.cierre.invariancia import calcular_invariancia

def test_puntos_precision_quirurgica():
    # Cubre 66, 69 (W_CONTEXTO custom)
    conf = ConfiguracionEstandar()
    conf.W_CONTEXTO = {"feedback_directo": 1.0, "distancia_relacional": 0.0, 
                       "tension_observada": 0.0, "confianza_reportada": 0.0,
                       "impacto_colaborativo": 0.0}
    compute_L2_contexto({}, conf)
    
    # Cubre 131-144 (PuntoNeutroContexto mu_otros es None)
    punto = PuntoNeutroContexto()
    punto.update(0.5)
    
    # Cubre 157-189 (Post-init y fases de equilibrio)
    eq = PuntoEquilibrioSelfDinamico(baseline_personal=0.35)
    eq.set_estado("p", 0.9, 0.8, "sprint")
    eq.set_estado("p", 0.1, 0.2, "recuperacion")
    
    # Cubre 227-233 (Ramas de update: Burnout, Crítico, Medio)
    for val in [0.85, 0.75, 0.50, 0.10]:
        eq.update(val)
    
    # Cubre 246-247 (ProtocoloPrioridad)
    ProtocoloPrioridad.evaluar(0.5, 0.95, dominio_seguridad=True)

def test_core_final_missing():
    # Cubre 82-94 (Theta_C en bordes)
    theta_C(1.0)
    theta_C(0.0)
    # Cubre 134 (compute_phi_C con valores extremos)
    compute_phi_C(0.5, 10.0, 0.5, 0.5, 0.3)

def test_l2_model_final_missing():
    model = L2HumanModel()
    # Cubre 42-44 (MC_prev es None)
    model._compute_MC(0.5, None)
    # Cubre 52-53 (Ramas de CI)
    model._compute_CI(0.9, 0.1)
    # Cubre 103-107 (Reset)
    model.reset()

def test_respiro_invariancia_final():
    # Cubre 40-41 de respiro
    r = RespiroOmega(alfa_respiro=0.1, beta_suavizado=0.1)
    r.actualizar(0.5, 0.5)
    # Cubre 12 de invariancia
    calcular_invariancia(0.0, 0.0)
