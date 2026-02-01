"""
Test Omega - Ataques de Aniquilación Total
Certifica que los búnkeres L1-L4 resisten casos extremos
"""

import pytest
import time
from villasmil_omega import core
from villasmil_omega.respiro import should_apply, detect_respiro, RespiroState, RespiroConfig


def test_core_final_annihilation():
    """
    Ataque L2 - Búnker de Masa Crítica
    Fuerza todos los casos extremos del core
    """
    # 1. Líneas de protección contra Nulos y vacíos
    assert core.indice_mc(None) == 0.0
    assert core.indice_mc([]) == 0.0
    
    # 2. BÚNKER L2 - Protección de Burnout (colapso instantáneo)
    burnout_result = {
        "estado_self": {"estado": "BURNOUT_ABSOLUTO"},
        "decision": {"accion": "DETENER"},
        "coherencia_score": 0.5
    }
    mc, ci = core.ajustar_mc_ci_por_coherencia(1.0, 1.0, burnout_result)
    assert mc == 0.0
    assert ci == 0.0
    
    # 3. BÚNKER L3 - Theta con cluster pequeño
    assert core.compute_theta(["omega", "omega"]) == 0.0
    
    # 4. BÚNKER L4 - Flujo basal sin autorización
    resultado = core.procesar_flujo_omega([1.0, 2.0], {"action": "basal"})
    assert resultado["status"] == "basal"
    assert resultado["path"] == "safety_lock"
    
    # 5. Protección de saturación OMEGA_U
    # actualizar_L2 debe respetar OMEGA_U = 0.995
    L2_saturado = core.actualizar_L2(2.0, delta=0.5, minimo=0.0, maximo=1.0)
    assert L2_saturado == core.OMEGA_U  # 0.995
    
    # 6. Penalización extrema
    mc_pen, ci_pen = core.penalizar_MC_CI(0.8, 0.9, L2=1.0, factor=1.0)
    assert mc_pen == 0.0  # Penalización total
    assert ci_pen == 0.0


def test_respiro_ultra_precision():
    """
    Ataque al sistema de Respiro
    Prueba guardas temporales y detección de anomalías
    """
    # Test 1: should_apply con ganancia marginal mínima
    # Líneas 40-41 en respiro.py
    apply, gain = should_apply(
        current_R=0.99,  # R muy alto
        effort_soft={"L1": 0.01},
        effort_hard={"L1": 0.011},  # Ganancia marginal < 0.02
        cost_threshold=100.0
    )
    assert isinstance(apply, bool)
    assert isinstance(gain, float)
    
    # Test 2: should_apply con cost > threshold
    apply2, gain2 = should_apply(
        current_R=0.5,
        effort_soft={"L1": 1.5},  # cost_soft = 2.25 > 1.0
        effort_hard={"L1": 1.6},
        cost_threshold=1.0
    )
    assert apply2 == True
    
    # Test 3: detect_respiro con configuración custom
    state = RespiroState()
    state.start_window()
    state.interv_count = 2
    state.deadband_seconds = 3500  # Alta fracción de deadband
    
    cfg = RespiroConfig()
    cfg.interv_threshold_per_hour = 5.0
    cfg.min_deadband_fraction = 0.5
    cfg.marginal_gain_epsilon = 0.02
    
    resultado = detect_respiro(state, cfg, marginal_gain_probe=0.001)
    assert isinstance(resultado, bool)


def test_l2_model_anomalies():
    """
    Ataque a L2_model
    Fuerza clamps y límites extremos
    """
    from villasmil_omega.l2_model import (
        ajustar_L2,
        compute_L2_final,
        apply_bio_adjustment
    )
    
    # 1. ajustar_L2 con valores negativos (línea 52)
    L2_neg = ajustar_L2(-5.0, 2.0)
    assert L2_neg == 0.0
    
    # 2. ajustar_L2 con valores > 1 (línea 53)
    L2_pos = ajustar_L2(5.0, 2.0)
    assert L2_pos == 1.0
    
    # 3. compute_L2_final con swap de min/max (línea 89)
    result = compute_L2_final(
        phi_c=0.2,
        theta_c=0.2,
        mc=0.5,
        ci=0.5,
        bio_terms=[0.1],
        bio_max=0.25,
        context_mult=1.0,
        min_L2=0.9,  # min > max
        max_L2=0.1
    )
    assert 0.1 <= result["L2"] <= 0.9
    
    # 4. apply_bio_adjustment con términos negativos (línea 42)
    bio_neg = apply_bio_adjustment([-0.5, -0.3], bio_max=0.25)
    assert bio_neg == 0.0
    
    # 5. compute_L2_final caso especial bio_max (líneas 103-107)
    result_bio = compute_L2_final(
        phi_c=0.0,
        theta_c=0.0,
        mc=0.0,
        ci=0.0,
        bio_terms=[0.25],  # Exacto bio_max
        bio_max=0.25,
        context_mult=1.0,
        min_L2=0.0,
        max_L2=1.0
    )
    assert result_bio["L2"] == 1.0


def test_invariancia_total():
    """
    Ataque al búnker de Invariancia
    Línea 12 de invariancia.py
    """
    from villasmil_omega.cierre.invariancia import Invariancia
    
    inv = Invariancia(epsilon=1e-3, ventana=5)
    
    # Caso 1: Todos iguales (invariante)
    assert inv.es_invariante([0.5] * 5) == True
    
    # Caso 2: Con variación pequeña (dentro de epsilon)
    assert inv.es_invariante([0.5, 0.5001, 0.4999, 0.5, 0.50005]) == True
    
    # Caso 3: Con variación grande (fuera de epsilon)
    assert inv.es_invariante([0.5, 0.5, 0.5, 0.5, 0.502]) == False
    
    # Caso 4: Ventana insuficiente
    assert inv.es_invariante([0.5] * 3) == False


def test_core_theta_todas_branches():
    """
    Ataque completo a compute_theta
    Líneas 82, 84, 90-91, 93-94 del core.py original
    """
    # Branch 1: cluster vacío
    assert core.compute_theta([]) == 0.0
    
    # Branch 2: solo "model a" (>= 6 elementos)
    assert core.compute_theta(["model a text"] * 7) == core.THETA_BASE
    
    # Branch 3: solo "model b" (>= 6 elementos)
    assert core.compute_theta(["model b text"] * 7) == core.THETA_BASE
    
    # Branch 4: ambos pero < 6 elementos
    assert core.compute_theta(["model a", "model b"]) == 0.0
    
    # Branch 5: >= 6 elementos con ambos modelos (CONFLICTO)
    cluster_conflicto = ["model a"] * 3 + ["model b"] * 3
    assert core.compute_theta(cluster_conflicto) == 1.0
    
    # Branch 6: "unknown" presente (incertidumbre)
    cluster_unknown = ["unknown", "unknown", "data", "data"]
    theta_unknown = core.compute_theta(cluster_unknown)
    assert 0.0 < theta_unknown <= 1.0  # Proporción de unknowns


def test_core_saturacion_universal():
    """
    Verifica que OMEGA_U se aplica correctamente
    """
    # suma_omega con valores normales
    suma1 = core.suma_omega(0.5, 0.5)
    assert suma1 == 1.0  # < OMEGA_U, permitido
    
    suma2 = core.suma_omega(0.6, 0.6)
    assert suma2 == core.OMEGA_U  # = 0.995 (saturación)
    
    # indice_mc con valor > C_MAX
    mc_alto = core.indice_mc(100, 0)  # 100% de aciertos
    assert mc_alto == core.C_MAX  # 0.963 (techo de coherencia)


def test_procesar_flujo_con_invariancia():
    """
    Verifica que L1 (Invariancia) bloquea procesamiento innecesario
    """
    # Datos en paz (invariantes)
    datos_paz = [0.5] * 10
    resultado = core.procesar_flujo_omega(datos_paz, {})
    
    assert resultado["status"] == "basal"
    assert resultado["invariante"] == True
    assert resultado["energia_ahorrada"] == True
    
    # Datos con varianza (requieren procesamiento)
    datos_varianza = [0.5, 0.6, 0.7, 0.8, 0.9]
    resultado2 = core.procesar_flujo_omega(datos_varianza, {"meta_auth": "active_meta_coherence"})
    
    assert resultado2["status"] == "evolving"
    assert resultado2["invariante"] == False
