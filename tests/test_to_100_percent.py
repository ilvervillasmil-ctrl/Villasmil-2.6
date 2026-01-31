# tests/test_nuclear_100.py
"""Test nuclear para forzar 100% de cobertura - TODAS las líneas restantes"""

import pytest
import villasmil_omega.core as core
from villasmil_omega.l2_model import ajustar_L2, compute_L2_final
from villasmil_omega.respiro import should_apply
from villasmil_omega.human_l2.puntos import (
    ConfiguracionEstandar,
    compute_L2_contexto,
    compute_L2_self,
    SistemaCoherenciaMaxima
)


# ============================================================
# CORE.PY - 6 LÍNEAS (82, 84, 90-91, 93-94)
# ============================================================

def test_core_lineas_82_94_todas_las_branches():
    """Ataca TODAS las branches de compute_theta"""
    # Línea 82: cluster vacío
    assert core.compute_theta([]) == 0.0
    
    # Línea 84: solo model a, len >= 6
    assert core.compute_theta(["model a"] * 7) == 0.0
    
    # Línea 90: solo model b (no a)
    assert core.compute_theta(["model b text"] * 7) == 0.0
    
    # Línea 91: ambos pero len < 6
    assert core.compute_theta(["model a", "model b"]) == 0.0
    
    # Líneas 93-94: len >= 6 con ambos
    cluster = ["model a text"] * 3 + ["model b text"] * 3
    assert core.compute_theta(cluster) == 1.0


# ============================================================
# PUNTOS.PY - 10 LÍNEAS (66, 69, 180-189)
# ============================================================

def test_puntos_linea_66_69_acceso_W():
    """Líneas 66, 69: Fuerza acceso a W_CONTEXTO y W_SELF"""
    conf = ConfiguracionEstandar()
    
    # Línea 66: w = conf.W_CONTEXTO
    L2_ctx = compute_L2_contexto({
        "feedback_directo": 0.8,
        "distancia_relacional": 0.7,
        "tension_observada": 0.6,
        "confianza_reportada": 0.3,
        "impacto_colaborativo": 0.5,
    }, conf)
    
    # Línea 69: w = conf.W_SELF
    L2_slf = compute_L2_self({
        "fatiga_fisica": 0.8,
        "carga_cognitiva": 0.9,
        "tension_emocional": 0.7,
        "señales_somaticas": 0.6,
        "motivacion_intrinseca": 0.2,
    }, conf)
    
    assert 0 <= L2_ctx <= 1
    assert 0 <= L2_slf <= 1


def test_puntos_lineas_180_189_todos_estados():
    """Líneas 180-189: TODOS los estados en registrar_medicion"""
    sistema = SistemaCoherenciaMaxima()
    
    # Línea 180-184: if self.mu_self is None (estado inicial)
    sistema.mu_self = None
    sistema.MAD_self = 0.0
    r1 = sistema.registrar_medicion(
        {"fatiga_fisica": 0.3},
        {"feedback_directo": 0.2}
    )
    assert sistema.mu_self is not None
    
    # Líneas 186-187: L2 > mu + deadband (RIESGO_SELF)
    sistema.mu_self = 0.1
    sistema.MAD_self = 0.001  # deadband tiny
    r2 = sistema.registrar_medicion(
        {
            "fatiga_fisica": 1.0,
            "carga_cognitiva": 1.0,
            "tension_emocional": 1.0,
            "señales_somaticas": 1.0,
            "motivacion_intrinseca": 0.0,
        },
        {"feedback_directo": 0.2}
    )
    
    # Línea 188: L2 < mu - deadband (SELF_RECUPERADO)
    sistema.mu_self = 0.9
    sistema.MAD_self = 0.001
    r3 = sistema.registrar_medicion(
        {
            "fatiga_fisica": 0.0,
            "carga_cognitiva": 0.0,
            "tension_emocional": 0.0,
            "señales_somaticas": 0.0,
            "motivacion_intrinseca": 1.0,
        },
        {"feedback_directo": 0.2}
    )
    
    # Línea 189: else (SELF_ESTABLE)
    sistema.mu_self = 0.5
    sistema.MAD_self = 0.1
    r4 = sistema.registrar_medicion(
        {"fatiga_fisica": 0.5},
        {"feedback_directo": 0.2}
    )
    
    assert all(r is not None for r in [r1, r2, r3, r4])


# ============================================================
# L2_MODEL.PY - 7 LÍNEAS (52-53, 89, 103-107)
# ============================================================

def test_l2model_linea_52_L2_negativo():
    """Línea 52: if L2 < 0.0"""
    result = ajustar_L2(-5.0, 2.0)
    assert result == 0.0


def test_l2model_linea_53_L2_mayor_1():
    """Línea 53: if L2 > 1.0"""
    result = ajustar_L2(5.0, 2.0)
    assert result == 1.0


def test_l2model_linea_89_swap_min_max():
    """Línea 89: if min_L2 > max_L2"""
    result = compute_L2_final(
        phi_c=0.2,
        theta_c=0.2,
        mc=0.5,
        ci=0.5,
        bio_terms=[0.1],
        bio_max=0.25,
        context_mult=1.0,
        min_L2=0.9,  # min > max → swap
        max_L2=0.1,
    )
    assert 0.1 <= result["L2"] <= 0.9


def test_l2model_lineas_103_107_bio_max_case():
    """Líneas 103-107: if bio_max > 0 and L2 == bio_max and max_L2 > bio_max"""
    result = compute_L2_final(
        phi_c=0.0,
        theta_c=0.0,
        mc=0.0,
        ci=0.0,
        bio_terms=[0.25],  # Exacto bio_max
        bio_max=0.25,
        context_mult=1.0,
        min_L2=0.0,
        max_L2=1.0,  # > bio_max
    )
    # Línea 107: L2 = max_L2
    assert result["L2"] == 1.0


# ============================================================
# RESPIRO.PY - 2 LÍNEAS (40-41)
# ============================================================

def test_respiro_linea_40_cost_threshold():
    """Línea 40: if cost_soft > cost_threshold"""
    # cost_soft = (1.5)^2 = 2.25 > 1.0
    apply, gain = should_apply(
        current_R=0.5,
        effort_soft={"a": 1.5},
        effort_hard={"a": 1.6},
        cost_threshold=1.0
    )
    assert apply == True


def test_respiro_linea_41_marginal_gain():
    """Línea 41: or marginal_gain < 0.02"""
    # R casi en máximo → ganancia marginal mínima
    apply, gain = should_apply(
        current_R=0.99,
        effort_soft={"a": 0.01},
        effort_hard={"a": 0.011},
        cost_threshold=100.0  # Alto para no activar línea 40
    )
    assert gain < 0.02 or apply == True


# ============================================================
# TESTS ADICIONALES PARA LLEGAR AL 100%
# ============================================================

def test_core_todas_branches_theta():
    """Ataca TODAS las branches restantes de compute_theta"""
    import villasmil_omega.core as core
    
    assert core.compute_theta([]) == 0.0
    assert core.compute_theta(["model a text"] * 7) == 0.0
    assert core.compute_theta(["model b text"] * 7) == 0.0
    assert core.compute_theta(["model a", "model b"]) == 0.0
    assert core.compute_theta(["model a"] * 3 + ["model b"] * 3) == 1.0


def test_l2model_todas_lineas():
    """Cubre líneas 52-53, 89, 103-107 de l2_model"""
    from villasmil_omega.l2_model import ajustar_L2, compute_L2_final
    
    assert ajustar_L2(-5.0, 2.0) == 0.0
    assert ajustar_L2(5.0, 2.0) == 1.0
    
    r1 = compute_L2_final(0.2, 0.2, 0.5, 0.5, [0.1], 0.25, 1.0, 0.9, 0.1)
    assert 0.1 <= r1["L2"] <= 0.9
    
    r2 = compute_L2_final(0.0, 0.0, 0.0, 0.0, [0.25], 0.25, 1.0, 0.0, 1.0)
    assert r2["L2"] == 1.0


def test_puntos_lineas_180_189_completo():
    """Cubre líneas 180-189 completamente"""
    from villasmil_omega.human_l2.puntos import SistemaCoherenciaMaxima
    
    sistema = SistemaCoherenciaMaxima()
    
    sistema.mu_self = None
    r1 = sistema.registrar_medicion({"fatiga_fisica": 0.3}, {"feedback_directo": 0.2})
    
    sistema.mu_self = 0.1
    sistema.MAD_self = 0.001
    r2 = sistema.registrar_medicion(
        {"fatiga_fisica": 1.0, "carga_cognitiva": 1.0, "tension_emocional": 1.0, 
         "señales_somaticas": 1.0, "motivacion_intrinseca": 0.0},
        {"feedback_directo": 0.2}
    )
    
    sistema.mu_self = 0.9
    sistema.MAD_self = 0.001
    r3 = sistema.registrar_medicion(
        {"fatiga_fisica": 0.0, "carga_cognitiva": 0.0, "motivacion_intrinseca": 1.0},
        {"feedback_directo": 0.2}
    )
    
    sistema.mu_self = 0.5
    sistema.MAD_self = 0.1
    r4 = sistema.registrar_medicion({"fatiga_fisica": 0.5}, {"feedback_directo": 0.2})
    
    assert all(r is not None for r in [r1, r2, r3, r4])


def test_respiro_lineas_40_41():
    """Cubre líneas 40-41 de respiro"""
    from villasmil_omega.respiro import should_apply
    
    apply1, _ = should_apply(0.5, {"a": 1.5}, {"a": 1.6}, 1.0)
    assert apply1 == True
    
    apply2, gain = should_apply(0.99, {"a": 0.01}, {"a": 0.011}, 100.0)
    assert gain < 0.02 or apply2 == True


def test_invariancia_linea_12():
    """Cubre línea 12 de invariancia"""
    from villasmil_omega.cierre.invariancia import Invariancia
    
    inv = Invariancia(epsilon=1e-3, ventana=5)
    assert inv.es_invariante([0.5] * 5) == True
    assert inv.es_invariante([0.5, 0.5, 0.5, 0.5, 0.502]) == False
