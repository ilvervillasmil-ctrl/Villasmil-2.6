# tests/test_to_100_percent.py
"""Tests para cubrir líneas faltantes"""

import pytest
from villasmil_omega.human_l2.puntos import (
    ConfiguracionEstandar,
    compute_L2_contexto,
    compute_L2_self,
    PuntoNeutroContexto,
    SistemaCoherenciaMaxima
)
from villasmil_omega.respiro import should_apply
from villasmil_omega.cierre.invariancia import Invariancia


def test_puntos_W_custom():
    """Líneas 66, 69: compute_L2 con pesos custom"""
    conf = ConfiguracionEstandar()
    conf.W_CONTEXTO = {
        "feedback_directo": 0.5,
        "distancia_relacional": 0.3,
        "tension_observada": 0.1,
        "confianza_reportada": 0.05,
        "impacto_colaborativo": 0.05,
    }
    conf.W_SELF = {
        "fatiga_fisica": 0.4,
        "carga_cognitiva": 0.3,
        "tension_emocional": 0.15,
        "señales_somaticas": 0.10,
        "motivacion_intrinseca": 0.05,
    }
    
    L2_ctx = compute_L2_contexto({"feedback_directo": 0.5}, conf)
    L2_slf = compute_L2_self({"fatiga_fisica": 0.6}, conf)
    
    assert 0 <= L2_ctx <= 1
    assert 0 <= L2_slf <= 1


def test_punto_neutro():
    """PuntoNeutro inicialización"""
    punto = PuntoNeutroContexto()
    r1 = punto.update(0.5)
    assert r1["estado"] == "BASELINE_INICIAL"
    r2 = punto.update(0.6)
    assert punto.mu_otros is not None


def test_sistema_coherencia():
    """Sistema completo"""
    sistema = SistemaCoherenciaMaxima(
        baseline_personal=0.4,
        enable_logging=False
    )
    
    for i in range(3):
        resultado = sistema.registrar_medicion(
            {"fatiga_fisica": 0.3, "carga_cognitiva": 0.4},
            {"feedback_directo": 0.2, "confianza_reportada": 0.8}
        )
        assert 0 <= resultado["L2_self"] <= 1


def test_respiro_should_apply():
    """Líneas 39-40: should_apply"""
    apply1, gain1 = should_apply(0.5, {"a": 0.9}, {"a": 1.0}, 0.5)
    apply2, gain2 = should_apply(0.9, {"a": 0.1}, {"a": 0.11}, 1.0)
    assert isinstance(apply1, bool)


def test_invariancia_edge():
    """Línea 12: invariancia edge cases"""
    inv = Invariancia(epsilon=1e-3, ventana=5)
    
    # Todos iguales
    assert inv.es_invariante([0.5] * 5) == True
    
    # No suficientes datos
    assert inv.es_invariante([0.5] * 3) == False
    
    # Con cambio
    assert inv.es_invariante([0.5, 0.5, 0.5, 0.5, 0.8]) == False


def test_compute_L2_extremos():
    """compute_L2 valores extremos"""
    L2_s1 = compute_L2_self({})
    L2_s2 = compute_L2_self({
        "fatiga_fisica": 1.0,
        "carga_cognitiva": 1.0,
        "motivacion_intrinseca": 0.0,
    })
    
    L2_c1 = compute_L2_contexto({})
    L2_c2 = compute_L2_contexto({
        "feedback_directo": 1.0,
        "confianza_reportada": 0.0,
    })
    
    assert all(0 <= x <= 1 for x in [L2_s1, L2_s2, L2_c1, L2_c2])
