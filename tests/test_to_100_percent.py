# tests/test_to_100_percent.py
"""Tests para cubrir líneas faltantes en puntos.py"""

import pytest
from villasmil_omega.human_l2.puntos import (
    ConfiguracionEstandar,
    compute_L2_contexto,
    compute_L2_self,
    PuntoNeutroContexto,
    SistemaCoherenciaMaxima
)
from villasmil_omega.respiro import RespiroOmega
from villasmil_omega.cierre.invariancia import calcular_invariancia


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


def test_punto_neutro_inicializacion():
    """PuntoNeutro inicialización y update"""
    punto = PuntoNeutroContexto()
    
    # Primera medición
    r1 = punto.update(0.5)
    assert r1["estado"] == "BASELINE_INICIAL"
    assert punto.mu_otros == 0.5
    
    # Segunda medición
    r2 = punto.update(0.6)
    assert punto.mu_otros is not None


def test_sistema_coherencia_maxima():
    """Sistema completo con registrar_medicion"""
    sistema = SistemaCoherenciaMaxima(
        baseline_personal=0.4,
        baseline_contexto=0.3,
        enable_logging=False
    )
    
    # Registrar varias mediciones
    for i in range(5):
        resultado = sistema.registrar_medicion(
            señales_internas={
                "fatiga_fisica": 0.3 + i*0.1,
                "carga_cognitiva": 0.4,
                "tension_emocional": 0.3,
                "señales_somaticas": 0.2,
                "motivacion_intrinseca": 0.7,
            },
            señales_relacionales={
                "feedback_directo": 0.2,
                "distancia_relacional": 0.3,
                "tension_observada": 0.2,
                "confianza_reportada": 0.8,
                "impacto_colaborativo": 0.1,
            }
        )
        
        assert 0 <= resultado["L2_self"] <= 1
        assert 0 <= resultado["L2_contexto"] <= 1
        assert "estado_self" in resultado
        assert "estado_contexto" in resultado
    
    # Verificar get_estado_actual
    estado = sistema.get_estado_actual()
    assert estado is not None
    assert "L2_self" in estado


def test_respiro_custom():
    """Líneas 40-41: RespiroOmega custom"""
    r1 = RespiroOmega()
    r1.actualizar(phi_C=0.6, R=0.8)
    
    r2 = RespiroOmega(alfa_respiro=0.3, beta_suavizado=0.2)
    r2.actualizar(phi_C=0.6, R=0.8)
    
    r3 = RespiroOmega(alfa_respiro=0.9, beta_suavizado=0.9)
    r3.actualizar(phi_C=0.6, R=0.8)
    
    assert all(0 <= r.ppr <= 1 for r in [r1, r2, r3])


def test_invariancia_edge():
    """Línea 12: invariancia casos edge"""
    inv1 = calcular_invariancia(0.0, 0.0)
    assert inv1 == 1.0
    
    inv2 = calcular_invariancia(0.5, 0.5)
    assert inv2 == 1.0
    
    inv3 = calcular_invariancia(0.0, 1.0)
    assert 0 <= inv3 <= 1


def test_compute_L2_valores_extremos():
    """Probar compute_L2 con valores extremos"""
    # Todos ceros
    L2_s1 = compute_L2_self({})
    assert 0 <= L2_s1 <= 1
    
    # Todos máximos
    L2_s2 = compute_L2_self({
        "fatiga_fisica": 1.0,
        "carga_cognitiva": 1.0,
        "tension_emocional": 1.0,
        "señales_somaticas": 1.0,
        "motivacion_intrinseca": 0.0,
    })
    assert 0 <= L2_s2 <= 1
    
    # Contexto extremos
    L2_c1 = compute_L2_contexto({})
    L2_c2 = compute_L2_contexto({
        "feedback_directo": 1.0,
        "distancia_relacional": 1.0,
        "tension_observada": 1.0,
        "confianza_reportada": 0.0,
        "impacto_colaborativo": 1.0,
    })
    
    assert 0 <= L2_c1 <= 1
    assert 0 <= L2_c2 <= 1
