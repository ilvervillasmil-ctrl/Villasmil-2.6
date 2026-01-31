# tests/test_to_100_percent.py
"""Tests para llegar al 100% - solo puntos.py"""

import pytest
from villasmil_omega.human_l2.puntos import (
    ConfiguracionEstandar, 
    compute_L2_contexto, 
    compute_L2_self,
    PuntoEquilibrioSelfDinamico, 
    PuntoNeutroContexto,
    ProtocoloPrioridad
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


def test_puntos_recalcular_mu_todas_ramas():
    """Líneas 180-189: _recalcular_mu_dinamico todas las fases"""
    eq = PuntoEquilibrioSelfDinamico(baseline_personal=0.40)
    
    # Acumular historia
    eq.history_L2 = [0.5] * 75
    
    # Sprint
    eq.set_estado("sprint", urgencia=0.9, contexto_demanda=0.8, fase="sprint")
    
    # Deuda alta
    eq.history_L2 = [0.65] * 75
    eq.set_estado("sprint2", urgencia=0.9, contexto_demanda=0.8, fase="sprint")
    
    # Recuperado
    eq.history_L2 = [0.25] * 75
    eq.set_estado("sprint3", urgencia=0.9, contexto_demanda=0.8, fase="sprint")
    
    # Recuperación
    eq.set_estado("recup", urgencia=0.1, contexto_demanda=0.2, fase="recuperacion")
    
    # Demanda alta
    eq.set_estado("alta", urgencia=0.5, contexto_demanda=0.85, fase="normal")
    
    # Demanda baja
    eq.set_estado("baja", urgencia=0.5, contexto_demanda=0.15, fase="normal")
    
    assert 0.1 <= eq.mu_self <= 0.8


def test_puntos_protocolo_seguridad():
    """Líneas 246-247: Protocolo con/sin seguridad"""
    # Con seguridad
    d1 = ProtocoloPrioridad.evaluar(0.50, 0.90, dominio_seguridad=True)
    assert d1["prioridad"] == 1
    assert d1["accion"] == "DETENER_INMEDIATO"
    
    # Sin seguridad
    d2 = ProtocoloPrioridad.evaluar(0.50, 0.90, dominio_seguridad=False)
    assert d2["prioridad"] != 1


def test_punto_neutro_inicializacion():
    """Líneas 131-144: PuntoNeutro inicialización"""
    punto = PuntoNeutroContexto()
    resultado = punto.update(0.5)
    assert resultado["estado"] == "BASELINE_INICIAL"
    assert punto.mu_otros == 0.5


def test_equilibrio_update_estados():
    """Líneas 227-233: Update con diferentes estados"""
    eq = PuntoEquilibrioSelfDinamico()
    
    # Burnout
    r1 = eq.update(0.80)
    assert "BURNOUT" in r1["estado"] or "CRITICO" in r1["estado"]
    
    # Crítico
    r2 = eq.update(0.72)
    assert "CRITICO" in r2["estado"] or "TENSION" in r2["estado"]
    
    # Medio
    r3 = eq.update(0.50)
    
    # Bajo
    r4 = eq.update(0.20)
    assert "RECUPERADO" in r4["estado"] or "EQUILIBRIO" in r4["estado"]


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
