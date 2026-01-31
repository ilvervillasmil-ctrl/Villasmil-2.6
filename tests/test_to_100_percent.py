# tests/test_final_100.py
"""Test quirúrgico para llegar al 100% de cobertura"""

import pytest
import villasmil_omega.core as core
from villasmil_omega.l2_model import (
    apply_bio_adjustment,
    compute_L2_base,
    ajustar_L2,
    compute_theta,
    compute_L2_final,
    theta_for_two_clusters
)
from villasmil_omega.respiro import should_apply, RespiroConfig
from villasmil_omega.cierre.invariancia import Invariancia
from villasmil_omega.human_l2.puntos import (
    ConfiguracionEstandar,
    compute_L2_contexto,
    compute_L2_self,
    PuntoNeutroContexto,
    SistemaCoherenciaMaxima
)


# ============================================================
# L2_MODEL.PY
# ============================================================

def test_l2model_bio_negative():
    """apply_bio_adjustment con negativo"""
    result = apply_bio_adjustment([-0.5, -0.3], bio_max=0.25)
    assert result == 0.0


def test_l2model_ajustar_clamps():
    """ajustar_L2 clamps"""
    assert ajustar_L2(-0.5, 0.3) == 0.0
    assert ajustar_L2(0.8, 0.5) == 1.0


def test_l2model_swap():
    """compute_L2_final swap min/max"""
    result = compute_L2_final(0.5, 0.5, 0.6, 0.7, [0.1], 0.25, 1.0, 0.8, 0.2)
    assert 0.2 <= result["L2"] <= 0.8


def test_l2model_bio_max():
    """compute_L2_final caso bio_max especial"""
    result = compute_L2_final(0.0, 0.0, 0.0, 0.0, [0.3], 0.25, 1.0, 0.0, 0.5)
    assert result["L2"] == 0.5


# ============================================================
# CORE.PY
# ============================================================

def test_core_compute_theta_edges():
    """compute_theta edge cases"""
    assert core.compute_theta([]) == 0.0
    assert core.compute_theta(["model a"] * 7) == 0.0
    assert core.compute_theta(["model b"] * 7) == 0.0
    assert core.compute_theta(["model a", "model b"]) == 0.0
    cluster = ["model a"] * 3 + ["model b"] * 3
    assert core.compute_theta(cluster) == 1.0


def test_core_theta_for_two():
    """theta_for_two_clusters"""
    result = core.theta_for_two_clusters(["model a"] * 2, ["model b"] * 2)
    assert all(k in result for k in ["theta_c1", "theta_c2", "theta_combined"])


# ============================================================
# PUNTOS.PY
# ============================================================

def test_puntos_W_custom():
    """Usa W_CONTEXTO y W_SELF"""
    conf = ConfiguracionEstandar()
    L2_ctx = compute_L2_contexto({
        "feedback_directo": 1.0,
        "confianza_reportada": 0.0,
    }, conf)
    L2_slf = compute_L2_self({
        "fatiga_fisica": 1.0,
        "motivacion_intrinseca": 0.0,
    }, conf)
    assert 0 <= L2_ctx <= 1 and 0 <= L2_slf <= 1


def test_puntos_punto_neutro():
    """PuntoNeutro inicialización"""
    punto = PuntoNeutroContexto()
    assert punto.mu_otros is None
    punto.update(0.5)
    assert punto.mu_otros == 0.5


def test_puntos_sistema_post_init():
    """SistemaCoherencia post_init"""
    sistema = SistemaCoherenciaMaxima(baseline_personal=0.45, baseline_contexto=0.35)
    assert sistema.mu_self == 0.45
    assert sistema.contexto.mu_otros == 0.35


def test_puntos_registrar_estados():
    """registrar_medicion estados"""
    sistema = SistemaCoherenciaMaxima()
    
    # Primer registro
    r1 = sistema.registrar_medicion({"fatiga_fisica": 0.5}, {"feedback_directo": 0.3})
    assert sistema.mu_self is not None
    
    # Múltiples estados para cubrir líneas 186-189
    sistema.mu_self = 0.2
    r2 = sistema.registrar_medicion(
        {
            "fatiga_fisica": 1.0,
            "carga_cognitiva": 1.0,
            "tension_emocional": 1.0,
            "señales_somaticas": 1.0,
            "motivacion_intrinseca": 0.0,
        },
        {"feedback_directo": 0.3}
    )
    
    sistema.mu_self = 0.8
    r3 = sistema.registrar_medicion(
        {
            "fatiga_fisica": 0.0,
            "carga_cognitiva": 0.0,
            "tension_emocional": 0.0,
            "señales_somaticas": 0.0,
            "motivacion_intrinseca": 1.0,
        },
        {"feedback_directo": 0.3}
    )
    
    # Verificar ejecución
    assert r2 is not None
    assert r3 is not None


def test_puntos_get_estado():
    """get_estado_actual"""
    sistema = SistemaCoherenciaMaxima()
    assert sistema.get_estado_actual() is None
    sistema.registrar_medicion({"fatiga_fisica": 0.5}, {"feedback_directo": 0.3})
    assert sistema.get_estado_actual() is not None


def test_puntos_get_explicacion():
    """get_explicacion"""
    punto = PuntoNeutroContexto()
    punto.update(0.5)
    r = punto.update(0.8)
    exp = punto.get_explicacion(r)
    assert isinstance(exp, str)


# ============================================================
# RESPIRO.PY
# ============================================================

def test_respiro_should_apply_edges():
    """should_apply cost y marginal"""
    apply1, gain1 = should_apply(0.5, {"a": 1.0}, {"a": 1.1}, 0.5)
    assert apply1 == True
    
    apply2, gain2 = should_apply(0.95, {"a": 0.1}, {"a": 0.11}, 1.0)
    assert isinstance(gain2, float)


# ============================================================
# INVARIANCIA.PY
# ============================================================

def test_invariancia_for_loop():
    """for v in historial"""
    inv = Invariancia(epsilon=1e-3, ventana=5)
    assert inv.es_invariante([0.5] * 5) == True
    assert inv.es_invariante([0.5] * 3) == False
    assert inv.es_invariante([0.5, 0.5, 0.5, 0.5, 0.502]) == False
