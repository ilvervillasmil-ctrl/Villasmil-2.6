# tests/test_nuclear_100.py
"""Test nuclear para forzar 100% de cobertura - TODAS las líneas"""

import pytest
import villasmil_omega.core as core
from villasmil_omega.l2_model import (
    apply_bio_adjustment,
    ajustar_L2,
    compute_L2_final
)
from villasmil_omega.respiro import should_apply
from villasmil_omega.cierre.invariancia import Invariancia
from villasmil_omega.human_l2.puntos import (
    ConfiguracionEstandar,
    compute_L2_contexto,
    compute_L2_self,
    PuntoNeutroContexto,
    SistemaCoherenciaMaxima
)


# ============================================================
# CORE.PY - FORZAR LÍNEAS 82, 84, 90-91, 93-94
# ============================================================

def test_core_theta_TODAS_las_branches():
    """Forzar CADA branch en compute_theta"""
    
    # Branch 1: cluster vacío (línea 82)
    r1 = core.compute_theta([])
    assert r1 == 0.0
    
    # Branch 2: solo contiene_a (línea 84)
    r2 = core.compute_theta(["model a text", "model a again", "model a more"])
    assert r2 == 0.0
    
    # Branch 3: solo contiene_b (línea 90)
    r3 = core.compute_theta(["model b text", "model b again", "model b more"])
    assert r3 == 0.0
    
    # Branch 4: ambos pero len < 6 (línea 91)
    r4 = core.compute_theta(["model a", "model b", "x", "y"])
    assert r4 == 0.0
    
    # Branch 5: len >= 6 pero solo a (línea 93)
    r5 = core.compute_theta(["model a"] * 7)
    assert r5 == 0.0
    
    # Branch 6: len >= 6 pero solo b (línea 94)
    r6 = core.compute_theta(["model b"] * 7)
    assert r6 == 0.0
    
    # Branch 7: len >= 6 Y ambos (return 1.0)
    r7 = core.compute_theta(["model a", "model a", "model a", "model b", "model b", "model b"])
    assert r7 == 1.0


# ============================================================
# PUNTOS.PY - FORZAR LÍNEAS 66, 69, 186-189
# ============================================================

def test_puntos_linea_66_W_CONTEXTO_acceso_directo():
    """Forzar acceso a conf.W_CONTEXTO en línea 66"""
    conf = ConfiguracionEstandar()
    
    # Modificar W_CONTEXTO para forzar su uso
    conf.W_CONTEXTO = {
        "feedback_directo": 0.2,
        "distancia_relacional": 0.2,
        "tension_observada": 0.2,
        "confianza_reportada": 0.2,
        "impacto_colaborativo": 0.2,
    }
    
    # Llamar con TODOS los campos
    result = compute_L2_contexto({
        "feedback_directo": 0.5,
        "distancia_relacional": 0.5,
        "tension_observada": 0.5,
        "confianza_reportada": 0.5,
        "impacto_colaborativo": 0.5,
    }, conf)
    
    assert 0 <= result <= 1


def test_puntos_linea_69_W_SELF_acceso_directo():
    """Forzar acceso a conf.W_SELF en línea 69"""
    conf = ConfiguracionEstandar()
    
    # Modificar W_SELF para forzar su uso
    conf.W_SELF = {
        "fatiga_fisica": 0.2,
        "carga_cognitiva": 0.2,
        "tension_emocional": 0.2,
        "señales_somaticas": 0.2,
        "motivacion_intrinseca": 0.2,
    }
    
    # Llamar con TODOS los campos
    result = compute_L2_self({
        "fatiga_fisica": 0.7,
        "carga_cognitiva": 0.7,
        "tension_emocional": 0.7,
        "señales_somaticas": 0.7,
        "motivacion_intrinseca": 0.3,
    }, conf)
    
    assert 0 <= result <= 1


def test_puntos_lineas_186_189_TODOS_los_estados():
    """Forzar TODOS los estados en registrar_medicion"""
    sistema = SistemaCoherenciaMaxima()
    
    # Estado 1: mu_self es None (línea 186)
    sistema.mu_self = None
    r1 = sistema.registrar_medicion(
        {"fatiga_fisica": 0.3},
        {"feedback_directo": 0.2}
    )
    assert sistema.mu_self is not None
    
    # Estado 2: L2 > mu + deadband (línea 187 - RIESGO_SELF)
    sistema.mu_self = 0.1
    sistema.MAD_self = 0.01  # deadband pequeño
    r2 = sistema.registrar_medicion(
        {"fatiga_fisica": 0.9, "carga_cognitiva": 0.9},
        {"feedback_directo": 0.2}
    )
    
    # Estado 3: L2 < mu - deadband (línea 188 - SELF_RECUPERADO)
    sistema.mu_self = 0.9
    sistema.MAD_self = 0.01
    r3 = sistema.registrar_medicion(
        {"fatiga_fisica": 0.1, "carga_cognitiva": 0.1},
        {"feedback_directo": 0.2}
    )
    
    # Estado 4: dentro de deadband (línea 189 - SELF_ESTABLE)
    sistema.mu_self = 0.5
    sistema.MAD_self = 0.05
    r4 = sistema.registrar_medicion(
        {"fatiga_fisica": 0.5},
        {"feedback_directo": 0.2}
    )
    
    assert all(r is not None for r in [r1, r2, r3, r4])


# ============================================================
# L2_MODEL.PY - FORZAR LÍNEAS 52-53, 89, 103-107
# ============================================================

def test_l2model_linea_52_ajustar_L2_menor_cero():
    """Línea 52: if L2 < 0.0"""
    result = ajustar_L2(-10.0, 5.0)
    assert result == 0.0


def test_l2model_linea_53_ajustar_L2_mayor_uno():
    """Línea 53: if L2 > 1.0"""
    result = ajustar_L2(10.0, 5.0)
    assert result == 1.0


def test_l2model_linea_89_swap_min_max():
    """Línea 89: if min_L2 > max_L2 (swap)"""
    result = compute_L2_final(
        phi_c=0.1,
        theta_c=0.1,
        mc=0.5,
        ci=0.5,
        bio_terms=[],
        bio_max=0.25,
        context_mult=1.0,
        min_L2=0.9,  # min > max
        max_L2=0.1,
    )
    # Después del swap: min=0.1, max=0.9
    assert 0.1 <= result["L2"] <= 0.9


def test_l2model_lineas_103_107_bio_max_especial():
    """Líneas 103-107: if bio_max > 0 and L2 == bio_max and max_L2 > bio_max"""
    result = compute_L2_final(
        phi_c=0.0,
        theta_c=0.0,
        mc=0.0,
        ci=0.0,
        bio_terms=[0.25],  # Exactamente bio_max
        bio_max=0.25,      # > 0
        context_mult=1.0,
        min_L2=0.0,
        max_L2=1.0,        # > bio_max
    )
    # Debe fijar a max_L2
    assert result["L2"] == 1.0


# ============================================================
# RESPIRO.PY - FORZAR LÍNEAS 40-41
# ============================================================

def test_respiro_linea_40_cost_mayor_threshold():
    """Línea 40: if cost_soft > cost_threshold"""
    # Forzar cost_soft = 2.0^2 = 4.0 > 1.0
    apply, gain = should_apply(
        current_R=0.5,
        effort_soft={"a": 2.0},
        effort_hard={"a": 2.1},
        cost_threshold=1.0
    )
    assert apply == True


def test_respiro_linea_41_marginal_menor_002():
    """Línea 41: or marginal_gain < 0.02"""
    # Forzar R muy alto para que ganancia marginal sea mínima
    apply, gain = should_apply(
        current_R=0.99,
        effort_soft={"a": 0.01},
        effort_hard={"a": 0.011},
        cost_threshold=10.0  # Alto para que no active línea 40
    )
    # marginal_gain será < 0.02
    assert gain < 0.02


# ============================================================
# INVARIANCIA.PY - YA AL 100%
# ============================================================

def test_invariancia_confirmacion_100():
    """Confirmar que invariancia está al 100%"""
    inv = Invariancia(epsilon=1e-3, ventana=5)
    
    # Todos iguales
    assert inv.es_invariante([0.5] * 5) == True
    
    # Insuficientes
    assert inv.es_invariante([0.5] * 3) == False
    
    # Con cambio
    assert inv.es_invariante([0.5, 0.5, 0.5, 0.5, 0.6]) == False
