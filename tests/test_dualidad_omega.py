# tests/test_dualidad_omega.py
"""
TEST DE DUALIDAD - YIN Y YANG
Prueba transiciones entre extremos opuestos
"""

import pytest
from villasmil_omega import core
from villasmil_omega.l2_model import compute_L2_final
from villasmil_omega.respiro import should_apply, RespiroState, RespiroConfig
from villasmil_omega.cierre.invariancia import Invariancia
from villasmil_omega.human_l2.puntos import SistemaCoherenciaMaxima


def test_transicion_guerra_a_paz():
    """Guerra → Paz: Sistema debe recuperarse"""
    sistema = SistemaCoherenciaMaxima()
    
    for i in range(10):
        guerra = sistema.registrar_medicion(
            {"fatiga_fisica": 0.9, "carga_cognitiva": 0.9, "tension_emocional": 0.9},
            {"feedback_directo": 0.8, "distancia_relacional": 0.9}
        )
    
    L2_guerra = guerra["L2_self"]
    
    for i in range(10):
        paz = sistema.registrar_medicion(
            {"fatiga_fisica": 0.1, "motivacion_intrinseca": 0.9},
            {"feedback_directo": 0.1, "confianza_reportada": 0.9}
        )
    
    L2_paz = paz["L2_self"]
    
    assert L2_paz < L2_guerra


def test_transicion_paz_a_guerra():
    """Paz → Guerra: Sistema debe detectar aumento de estrés"""
    sistema = SistemaCoherenciaMaxima()
    
    for i in range(10):
        paz = sistema.registrar_medicion(
            {"fatiga_fisica": 0.2, "motivacion_intrinseca": 0.8},
            {"confianza_reportada": 0.8}
        )
    
    L2_paz = paz["L2_self"]
    
    for i in range(10):
        guerra = sistema.registrar_medicion(
            {"fatiga_fisica": 0.9, "tension_emocional": 0.9},
            {"feedback_directo": 0.9}
        )
    
    L2_guerra = guerra["L2_self"]
    
    assert L2_guerra > L2_paz


def test_oscilacion_extrema_50_ciclos():
    """50 ciclos alternando guerra/paz - sistema debe mantenerse estable"""
    sistema = SistemaCoherenciaMaxima()
    historial_L2 = []
    
    for ciclo in range(50):
        if ciclo % 2 == 0:
            r = sistema.registrar_medicion(
                {"fatiga_fisica": 0.9},
                {"feedback_directo": 0.8}
            )
        else:
            r = sistema.registrar_medicion(
                {"fatiga_fisica": 0.2},
                {"confianza_reportada": 0.8}
            )
        
        historial_L2.append(r["L2_self"])
    
    assert all(0 <= L2 <= 1 for L2 in historial_L2)
    assert max(historial_L2) < 0.9
    assert min(historial_L2) >= 0.1


def test_dualidad_mc_ci_simultanea():
    """MC alto + CI bajo VS MC bajo + CI alto"""
    coherencia1 = {
        "estado_self": {"estado": "NORMAL"},
        "decision": {"accion": "CONTINUAR"},
        "coherencia_score": 0.7
    }
    mc1, ci1 = core.ajustar_mc_ci_por_coherencia(0.9, 0.3, coherencia1)
    
    coherencia2 = {
        "estado_self": {"estado": "NORMAL"},
        "decision": {"accion": "CONTINUAR"},
        "coherencia_score": 0.7
    }
    mc2, ci2 = core.ajustar_mc_ci_por_coherencia(0.3, 0.9, coherencia2)
    
    assert mc1 > mc2
    assert ci2 > ci1


def test_theta_oscilante_conflicto_paz():
    """Theta oscila entre conflicto máximo y paz total"""
    cluster_conflicto = ["model a"] * 5 + ["model b"] * 5
    theta_conflicto = core.compute_theta(cluster_conflicto)
    
    cluster_paz = ["harmonious data"] * 10
    theta_paz = core.compute_theta(cluster_paz)
    
    assert theta_conflicto == 1.0
    assert theta_paz == core.THETA_BASE


def test_invariancia_ruptura_y_restauracion():
    """Invariancia: Paz → Ruptura → Paz de nuevo"""
    inv = Invariancia(epsilon=1e-3, ventana=5)
    
    paz1 = [0.5] * 10
    assert inv.es_invariante(paz1) == True
    
    ruptura = [0.5, 0.5, 0.8, 0.9, 0.7]
    assert inv.es_invariante(ruptura) == False
    
    paz2 = [0.6] * 10
    assert inv.es_invariante(paz2) == True


def test_respiro_presion_y_relajacion():
    """Respiro: Sistema bajo presión → luego relajación"""
    apply_presion, gain_presion = should_apply(
        current_R=0.9,
        effort_soft={"L1": 0.8},
        effort_hard={"L1": 0.9},
        cost_threshold=0.5
    )
    
    apply_relax, gain_relax = should_apply(
        current_R=0.3,
        effort_soft={"L1": 0.1},
        effort_hard={"L1": 0.2},
        cost_threshold=5.0
    )
    
    assert isinstance(apply_presion, bool)
    assert isinstance(apply_relax, bool)


def test_pipeline_dualidad_completa():
    """Pipeline completo con dualidad: Paz → Guerra → Recuperación"""
    sistema = SistemaCoherenciaMaxima()
    
    for i in range(5):
        sistema.registrar_medicion(
            {"fatiga_fisica": 0.2, "motivacion_intrinseca": 0.8},
            {"confianza_reportada": 0.8}
        )
    
    estado_paz = sistema.get_estado_actual()
    
    for i in range(5):
        sistema.registrar_medicion(
            {"fatiga_fisica": 0.9, "tension_emocional": 0.9},
            {"feedback_directo": 0.9}
        )
    
    estado_guerra = sistema.get_estado_actual()
    
    for i in range(10):
        sistema.registrar_medicion(
            {"fatiga_fisica": 0.1, "motivacion_intrinseca": 0.9},
            {"confianza_reportada": 0.9}
        )
    
    estado_recuperacion = sistema.get_estado_actual()
    
    assert estado_guerra["L2_self"] > estado_paz["L2_self"]
    assert estado_recuperacion["L2_self"] < estado_guerra["L2_self"]


def test_suma_omega_dualidad():
    """suma_omega: valores pequeños vs valores grandes"""
    pequeños = core.suma_omega(0.1, 0.2)
    grandes = core.suma_omega(0.7, 0.7)
    
    assert abs(pequeños - 0.3) < 0.01
    assert grandes == core.OMEGA_U


def test_l2_final_extremos_opuestos():
    """L2_final: mínimo absoluto vs máximo absoluto"""
    L2_min = compute_L2_final(
        phi_c=0.0, theta_c=0.0, mc=0.0, ci=0.0,
        bio_terms=[-1.0], bio_max=0.25, context_mult=0.0,
        min_L2=0.0, max_L2=1.0
    )
    
    L2_max = compute_L2_final(
        phi_c=1.0, theta_c=1.0, mc=1.0, ci=1.0,
        bio_terms=[1.0], bio_max=0.25, context_mult=10.0,
        min_L2=0.0, max_L2=1.0
    )
    
    assert L2_min["L2"] < L2_max["L2"]


def test_burnout_y_recuperacion_ciclica():
    """5 ciclos: Burnout → Recuperación → Burnout..."""
    for ciclo in range(5):
        coherencia_burnout = {
            "estado_self": {"estado": "BURNOUT_ABSOLUTO"},
            "decision": {"accion": "DETENER"},
            "coherencia_score": 0.0
        }
        mc_b, ci_b = core.ajustar_mc_ci_por_coherencia(0.9, 0.9, coherencia_burnout)
        
        coherencia_recuperacion = {
            "estado_self": {"estado": "RECUPERADO"},
            "decision": {"accion": "CONTINUAR"},
            "coherencia_score": 0.95
        }
        mc_r, ci_r = core.ajustar_mc_ci_por_coherencia(0.9, 0.9, coherencia_recuperacion)
        
        assert mc_b == 0.0 and ci_b == 0.0
        assert mc_r > 0.8 and ci_r > 0.8
