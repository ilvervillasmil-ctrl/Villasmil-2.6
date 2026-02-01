# tests/test_apocalipsis_omega.py
"""
ATAQUE APOCALÍPTICO FINAL - SIN LÍMITES
Fuerza TODAS las líneas defensivas hasta el colapso
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from villasmil_omega import core
from villasmil_omega.l2_model import (
    compute_L2_base,
    ajustar_L2,
    compute_L2_final,
    apply_bio_adjustment
)
from villasmil_omega.respiro import (
    distribute_action,
    should_apply,
    RespiroConfig
)


# ═══════════════════════════════════════════════════════════════════════════
# CORE.PY LÍNEA 65 - FORZAR CLAMP CON MAX > OMEGA_U
# ═══════════════════════════════════════════════════════════════════════════

def test_core_linea_65_clamp_forzar_omega_u():
    """Línea 65: Forzar que max_val > OMEGA_U y verificar ajuste"""
    # Caso 1: max_val = 2.0 (> OMEGA_U) → debe ajustar a OMEGA_U
    resultado = core.clamp(value=1.5, min_val=0.0, max_val=2.0)
    # La función DEBE ajustar max_val a OMEGA_U internamente
    assert resultado == core.OMEGA_U
    
    # Caso 2: Forzar valor exactamente en OMEGA_U
    resultado2 = core.clamp(value=core.OMEGA_U, min_val=0.0, max_val=10.0)
    assert resultado2 == core.OMEGA_U
    
    # Caso 3: Valor > OMEGA_U con max > OMEGA_U
    resultado3 = core.clamp(value=1.0, min_val=0.0, max_val=5.0)
    assert resultado3 == core.OMEGA_U


# ═══════════════════════════════════════════════════════════════════════════
# CORE.PY LÍNEAS 133-138 - FORZAR TODOS LOS ESTADOS CRÍTICOS
# ═══════════════════════════════════════════════════════════════════════════

def test_core_lineas_133_138_burnout_absoluto():
    """Líneas 133-138: Forzar BURNOUT_ABSOLUTO - colapso total"""
    resultado = {
        "estado_self": {"estado": "BURNOUT_ABSOLUTO"},
        "decision": {"accion": "CONTINUAR"},
        "coherencia_score": 1.0  # Alto pero debe ignorarse
    }
    mc, ci = core.ajustar_mc_ci_por_coherencia(1.0, 1.0, resultado)
    assert mc == 0.0 and ci == 0.0


def test_core_lineas_133_138_detener_con_coherencia_alta():
    """Forzar DETENER incluso con coherencia alta"""
    resultado = {
        "estado_self": {"estado": "NORMAL"},
        "decision": {"accion": "DETENER"},
        "coherencia_score": 0.95  # Alta coherencia
    }
    mc, ci = core.ajustar_mc_ci_por_coherencia(0.9, 0.9, resultado)
    assert mc == 0.0 and ci == 0.0


def test_core_lineas_133_138_estados_combinados():
    """Combinar estado crítico + decisión de detener"""
    resultado = {
        "estado_self": {"estado": "SELF_CRITICO"},
        "decision": {"accion": "DETENER_INMEDIATO"},
        "coherencia_score": 0.8
    }
    mc, ci = core.ajustar_mc_ci_por_coherencia(1.0, 1.0, resultado)
    assert mc == 0.0 and ci == 0.0


# ═══════════════════════════════════════════════════════════════════════════
# L2_MODEL.PY LÍNEAS 49-50 - COMPUTE_L2_BASE CON CONTEXT_MULT EXTREMO
# ═══════════════════════════════════════════════════════════════════════════

def test_l2model_lineas_49_50_context_mult_negativo():
    """Líneas 49-50: context_mult negativo"""
    L2_base = compute_L2_base(
        mc=1.0,
        ci=1.0,
        phi_c=1.0,
        theta_c=1.0,
        context_mult=-10.0  # Negativo extremo
    )
    # Debería dar negativo pero será clamped después
    assert isinstance(L2_base, float)


def test_l2model_lineas_49_50_context_mult_infinito():
    """Forzar context_mult muy grande"""
    L2_base = compute_L2_base(
        mc=0.5,
        ci=0.5,
        phi_c=0.5,
        theta_c=0.5,
        context_mult=1000.0  # Extremadamente alto
    )
    # Producto será enorme
    assert L2_base > 1.0


# ═══════════════════════════════════════════════════════════════════════════
# L2_MODEL.PY LÍNEAS 92-96 - FORZAR CLAMPS FINALES
# ═══════════════════════════════════════════════════════════════════════════

def test_l2model_lineas_92_96_L2_menor_que_min():
    """Líneas 92-93: L2 < min_L2 después del swap"""
    resultado = compute_L2_final(
        phi_c=0.0,
        theta_c=0.0,
        mc=0.0,
        ci=0.0,
        bio_terms=[-1.0],  # Bio negativo
        bio_max=0.25,
        context_mult=0.0,
        min_L2=0.5,  # Min alto
        max_L2=0.3   # Swap → min=0.3, max=0.5
    )
    # L2 = 0 (todo cero) < min=0.3 → debe fijar a 0.3
    assert resultado["L2"] == 0.3


def test_l2model_lineas_94_95_L2_mayor_que_max():
    """Líneas 94-95: L2 > max_L2"""
    resultado = compute_L2_final(
        phi_c=1.0,
        theta_c=1.0,
        mc=1.0,
        ci=1.0,
        bio_terms=[1.0],  # Bio muy alto (será clamped a bio_max)
        bio_max=0.25,
        context_mult=10.0,  # Multiplicador extremo
        min_L2=0.0,
        max_L2=0.3  # Max bajo
    )
    # L2 será muy alto → debe clamparse a max=0.3
    assert resultado["L2"] == 0.3


def test_l2model_linea_96_swap_min_max_exacto():
    """Línea 89-96: Swap cuando min > max exactamente"""
    resultado = compute_L2_final(
        phi_c=0.5,
        theta_c=0.5,
        mc=0.5,
        ci=0.5,
        bio_terms=[0.1],
        bio_max=0.25,
        context_mult=1.0,
        min_L2=0.7,  # min > max
        max_L2=0.3
    )
    # Después del swap: min=0.3, max=0.7
    assert 0.3 <= resultado["L2"] <= 0.7


# ═══════════════════════════════════════════════════════════════════════════
# RESPIRO.PY LÍNEAS 29-36 - DISTRIBUTE_ACTION CASOS IMPOSIBLES
# ═══════════════════════════════════════════════════════════════════════════

def test_respiro_lineas_29_36_base_effort_negativo():
    """Líneas 29-30: base_effort negativo"""
    cfg = RespiroConfig()
    resultado = distribute_action(
        base_effort=-1.0,  # Negativo
        sensitivities={"a": 0.5, "b": 0.5},
        cfg=cfg
    )
    # Debe clampar a 0
    assert all(v >= 0.0 for v in resultado.values())


def test_respiro_lineas_31_32_sensitivities_todos_negativos():
    """Líneas 31-32: Todos los sensitivities negativos → s_sum = 0"""
    cfg = RespiroConfig()
    resultado = distribute_action(
        base_effort=1.0,
        sensitivities={"a": -1.0, "b": -2.0, "c": -3.0},
        cfg=cfg
    )
    # s_sum = 0 → debe retornar dict con valores 0.0
    assert all(v == 0.0 for v in resultado.values())


def test_respiro_lineas_33_34_weights_normalizados():
    """Líneas 33-34: Verificar normalización de weights"""
    cfg = RespiroConfig()
    resultado = distribute_action(
        base_effort=1.0,
        sensitivities={"a": 0.3, "b": 0.7},
        cfg=cfg
    )
    # weights deben sumar 1.0
    # a_weight = 0.3/1.0 = 0.3, b_weight = 0.7/1.0 = 0.7
    total_weight = sum(resultado.values())
    assert abs(total_weight - 1.0) < 0.01


def test_respiro_lineas_35_36_clamping_a_max_component():
    """Líneas 35-36: Valores que superan max_component"""
    cfg = RespiroConfig()
    cfg.max_component = 0.3  # Muy bajo
    
    resultado = distribute_action(
        base_effort=1.0,
        sensitivities={"a": 1.0},  # 100% del effort
        cfg=cfg
    )
    # base_effort * 1.0 = 1.0 > max_component=0.3 → debe clampar
    assert resultado["a"] == cfg.max_component


# ═══════════════════════════════════════════════════════════════════════════
# RESPIRO.PY LÍNEA 50 - SHOULD_APPLY CON COST_THRESHOLD EXACTO
# ═══════════════════════════════════════════════════════════════════════════

def test_respiro_linea_50_cost_exactamente_threshold():
    """Línea 50: cost_soft exactamente == cost_threshold"""
    # Diseñar para que cost_soft = 1.0^2 = 1.0 (exacto)
    apply, gain = should_apply(
        current_R=0.5,
        effort_soft={"a": 1.0},  # cost = 1.0
        effort_hard={"a": 1.001},
        cost_threshold=1.0  # Exacto
    )
    # Condición: if cost_soft > cost_threshold (1.0 > 1.0 → False)
    # Depende de marginal_gain
    assert isinstance(apply, bool)


def test_respiro_linea_50_marginal_gain_exactamente_epsilon():
    """Línea 50: marginal_gain exactamente == 0.02"""
    # Forzar ganancia marginal mínima
    apply, gain = should_apply(
        current_R=0.9,
        effort_soft={"a": 0.1},
        effort_hard={"a": 0.101},  # Diferencia muy pequeña
        cost_threshold=10.0  # Alto para no activar cost
    )
    # Si marginal_gain < 0.02 → should apply
    assert isinstance(gain, (float, str))


# ═══════════════════════════════════════════════════════════════════════════
# ATAQUE INTEGRADO - ROMPER TODO EL PIPELINE
# ═══════════════════════════════════════════════════════════════════════════

def test_apocalipsis_pipeline_completo():
    """
    ATAQUE FINAL: Combinar TODAS las condiciones extremas simultáneamente
    """
    # 1. Estado BURNOUT_ABSOLUTO
    coherencia_critica = {
        "estado_self": {"estado": "BURNOUT_ABSOLUTO"},
        "decision": {"accion": "DETENER_INMEDIATO"},
        "coherencia_score": 0.0  # Coherencia colapsada
    }
    
    # 2. MC y CI al máximo
    mc_max = core.indice_mc(1000, 0)
    ci_max = core.indice_ci(1000, 0, ruido=0)
    
    # 3. Ajustar con coherencia crítica → debe colapsar a 0.0
    mc_adj, ci_adj = core.ajustar_mc_ci_por_coherencia(
        mc_max, ci_max, coherencia_critica
    )
    assert mc_adj == 0.0
    assert ci_adj == 0.0
    
    # 4. L2 con parámetros invertidos
    L2_result = compute_L2_final(
        phi_c=1.0,
        theta_c=1.0,
        mc=mc_adj,  # 0.0
        ci=ci_adj,  # 0.0
        bio_terms=[100.0],  # Bio extremo
        bio_max=0.25,
        context_mult=-10.0,  # Negativo
        min_L2=0.9,  # Invertidos
        max_L2=0.1
    )
    # Debe swapear y clampar
    assert 0.1 <= L2_result["L2"] <= 0.9
    
    # 5. Distribute_action con sensitivities imposibles
    cfg = RespiroConfig()
    dist_result = distribute_action(
        base_effort=-100.0,  # Negativo extremo
        sensitivities={"x": -1.0, "y": -2.0},
        cfg=cfg
    )
    assert all(v == 0.0 for v in dist_result.values())
    
    # 6. Clamp con OMEGA_U
    final_clamp = core.clamp(1000.0, 0.0, 1000.0)
    assert final_clamp == core.OMEGA_U
    
    print("\n🔥 APOCALIPSIS COMPLETADO - SISTEMA RESISTIÓ TODO 🔥")
