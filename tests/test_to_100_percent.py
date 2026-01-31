# tests/test_to_100_percent.py - VERSIÓN CORREGIDA
"""Tests quirúrgicos para llegar al 100%"""

import pytest
from villasmil_omega.core import theta_C, compute_phi_C
from villasmil_omega.human_l2.puntos import (
    ConfiguracionEstandar, compute_L2_contexto, compute_L2_self,
    PuntoEquilibrioSelfDinamico, ProtocoloPrioridad
)
from villasmil_omega.respiro import RespiroOmega
from villasmil_omega.cierre.invariancia import calcular_invariancia

# NO IMPORTAR l2_model - no existe
# Usar solo lo que está en puntos.py y core.py

def test_core_lineas_82_84_theta_C_extremos():
    """Líneas 82, 84: theta_C con C >= 1.0 y C <= 0.0"""
    theta_max = theta_C(1.0)
    theta_above = theta_C(1.5)
    theta_min = theta_C(0.0)
    theta_below = theta_C(-0.5)
    assert all(0 <= t <= 1 for t in [theta_max, theta_above, theta_min, theta_below])

def test_core_lineas_90_91_93_94_theta_C_casos_medios():
    """Líneas 90-91, 93-94: theta_C con valores intermedios"""
    resultados = [theta_C(c) for c in [0.1, 0.3, 0.5, 0.7, 0.9]]
    assert all(0 <= r <= 1 for r in resultados)
    for i in range(len(resultados)-1):
        assert resultados[i] >= resultados[i+1]

def test_core_linea_134_compute_phi_C_bio_adj_extremo():
    """Línea 134: compute_phi_C con bio_adj muy alto/bajo"""
    phi_alto = compute_phi_C(0.5, 10.0, 0.5, 0.5, 0.3)
    phi_bajo = compute_phi_C(0.5, -10.0, 0.5, 0.5, 0.3)
    assert 0 <= phi_alto <= 1
    assert 0 <= phi_bajo <= 1

def test_puntos_lineas_66_69_W_custom():
    """Líneas 66, 69: compute_L2 con configuración custom"""
    conf = ConfiguracionEstandar()
    conf.W_CONTEXTO = {"feedback_directo": 0.5, "distancia_relacional": 0.3,
                       "tension_observada": 0.1, "confianza_reportada": 0.05,
                       "impacto_colaborativo": 0.05}
    conf.W_SELF = {"fatiga_fisica": 0.4, "carga_cognitiva": 0.3,
                   "tension_emocional": 0.15, "señales_somaticas": 0.10,
                   "motivacion_intrinseca": 0.05}
    L2_ctx = compute_L2_contexto({"feedback_directo": 0.5}, conf)
    L2_slf = compute_L2_self({"fatiga_fisica": 0.6}, conf)
    assert 0 <= L2_ctx <= 1 and 0 <= L2_slf <= 1

def test_puntos_lineas_180_189_recalcular_mu_todas_ramas():
    """Líneas 180-189: _recalcular_mu_dinamico con todas las combinaciones"""
    eq = PuntoEquilibrioSelfDinamico(baseline_personal=0.40)
    eq.history_L2 = [0.5] * 75
    eq.set_estado("sprint", urgencia=0.9, contexto_demanda=0.8, fase="sprint")
    eq.history_L2 = [0.65] * 75
    eq.set_estado("sprint2", urgencia=0.9, contexto_demanda=0.8, fase="sprint")
    eq.history_L2 = [0.25] * 75
    eq.set_estado("sprint3", urgencia=0.9, contexto_demanda=0.8, fase="sprint")
    eq.set_estado("recup", urgencia=0.1, contexto_demanda=0.2, fase="recuperacion")
    eq.set_estado("alta_dem", urgencia=0.5, contexto_demanda=0.85, fase="normal")
    eq.set_estado("baja_dem", urgencia=0.5, contexto_demanda=0.15, fase="normal")
    assert 0.1 <= eq.mu_self <= 0.8

def test_puntos_lineas_246_247_protocolo_seguridad():
    """Líneas 246-247: ProtocoloPrioridad con dominio_seguridad"""
    decision_seg = ProtocoloPrioridad.evaluar(0.50, 0.90, dominio_seguridad=True)
    assert decision_seg["prioridad"] == 1
    decision_normal = ProtocoloPrioridad.evaluar(0.50, 0.90, dominio_seguridad=False)
    assert decision_normal["prioridad"] != 1

def test_respiro_lineas_40_41_parametros_custom():
    """Líneas 40-41: RespiroOmega con alfa/beta custom"""
    r1 = RespiroOmega()
    r1.actualizar(phi_C=0.6, R=0.8)
    r2 = RespiroOmega(alfa_respiro=0.3, beta_suavizado=0.2)
    r2.actualizar(phi_C=0.6, R=0.8)
    r3 = RespiroOmega(alfa_respiro=0.9, beta_suavizado=0.9)
    r3.actualizar(phi_C=0.6, R=0.8)
    assert all(0 <= r.ppr <= 1 for r in [r1, r2, r3])

def test_invariancia_linea_12_caso_zero():
    """Línea 12: calcular_invariancia con valores edge"""
    inv = calcular_invariancia(phi_C_0=0.0, phi_C_1=0.0)
    assert inv == 1.0
    inv2 = calcular_invariancia(phi_C_0=0.5, phi_C_1=0.5)
    assert inv2 == 1.0
    inv3 = calcular_invariancia(phi_C_0=0.0, phi_C_1=1.0)
    assert 0 <= inv3 <= 1
