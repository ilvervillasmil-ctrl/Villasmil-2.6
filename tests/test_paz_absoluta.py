# tests/test_paz_absoluta.py
"""
TEST DE PAZ ABSOLUTA - RELAJACIÓN EXTREMA
Permite que el sistema opere en condiciones ideales: sin estrés, sin conflicto, en flujo perfecto.
"""

import pytest
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
    detect_respiro,
    RespiroState,
    RespiroConfig
)
from villasmil_omega.cierre.invariancia import Invariancia
from villasmil_omega.human_l2.puntos import SistemaCoherenciaMaxima


def test_core_estado_optimo_total():
    """Sistema operando en coherencia máxima perfecta"""
    coherencia_perfecta = {
        "estado_self": {"estado": "RECUPERADO"},
        "decision": {"accion": "CONTINUAR"},
        "coherencia_score": core.C_MAX
    }
    
    mc_optimo = core.indice_mc(963, 37)
    ci_optimo = core.indice_ci(963, 37, ruido=0)
    
    mc_final, ci_final = core.ajustar_mc_ci_por_coherencia(
        mc_optimo, ci_optimo, coherencia_perfecta
    )
    
    assert mc_final > 0.9
    assert ci_final > 0.9


def test_core_suma_omega_valores_normales_sin_saturacion():
    """suma_omega con valores que NO saturan"""
    assert core.suma_omega(0.1, 0.1) == 0.2
    assert core.suma_omega(0.3, 0.3) == 0.6
    assert core.suma_omega(0.4, 0.4) == 0.8


def test_core_clamp_valores_dentro_de_rango():
    """clamp cuando valores están perfectamente dentro del rango"""
    assert core.clamp(0.25, 0.0, 1.0) == 0.25
    assert core.clamp(0.50, 0.0, 1.0) == 0.50
    assert core.clamp(0.75, 0.0, 1.0) == 0.75
    assert core.clamp(0.963, 0.0, 1.0) == 0.963


def test_core_compute_theta_sin_conflicto():
    """compute_theta con clusters sin tensión"""
    cluster_paz = ["data harmonious"] * 10
    theta_paz = core.compute_theta(cluster_paz)
    assert theta_paz == core.THETA_BASE


def test_core_procesar_flujo_omega_con_paz_invariante():
    """procesar_flujo con datos invariantes"""
    datos_estables = [0.5] * 20
    resultado = core.procesar_flujo_omega(datos_estables, {})
    
    assert resultado["status"] == "basal"
    assert resultado["invariante"] == True
    assert resultado["energia_ahorrada"] == True


def test_l2model_compute_L2_base_valores_armonicos():
    """compute_L2_base con valores balanceados"""
    L2_base = compute_L2_base(
        mc=0.5, ci=0.5, phi_c=0.5, theta_c=0.5, context_mult=1.0
    )
    assert abs(L2_base - 0.5) < 0.01


def test_l2model_ajustar_L2_sin_ajustes():
    """ajustar_L2 cuando L2 ya está en rango perfecto"""
    L2_perfecto = ajustar_L2(L2_base=0.5, bio_effect=0.2)
    assert L2_perfecto == 0.7


def test_l2model_apply_bio_adjustment_positivo_moderado():
    """apply_bio_adjustment con términos positivos moderados"""
    bio_terms = [0.05, 0.03, 0.02]
    bio_effect = apply_bio_adjustment(bio_terms, bio_max=0.25)
    assert bio_effect == 0.10


def test_l2model_compute_L2_final_sin_swap_sin_clamp():
    """compute_L2_final donde min < max y L2 dentro de rango"""
    resultado = compute_L2_final(
        phi_c=0.3, theta_c=0.3, mc=0.5, ci=0.5,
        bio_terms=[0.1], bio_max=0.25, context_mult=1.0,
        min_L2=0.2, max_L2=0.8
    )
    assert 0.2 <= resultado["L2"] <= 0.8


def test_respiro_distribute_action_valores_positivos_balanceados():
    """distribute_action con sensitivities balanceados"""
    cfg = RespiroConfig()
    resultado = distribute_action(
        0.5,
        {"a": 0.25, "b": 0.25, "c": 0.25, "d": 0.25},
        cfg
    )
    valores = list(resultado.values())
    assert all(abs(v - valores[0]) < 0.01 for v in valores)


def test_respiro_should_apply_sin_presion():
    """should_apply cuando esfuerzo soft es suficiente"""
    apply, gain = should_apply(
        current_R=0.3,
        effort_soft={"L1": 0.1},
        effort_hard={"L1": 0.5},
        cost_threshold=10.0
    )
    assert isinstance(apply, bool)
    assert isinstance(gain, (float, str))


def test_respiro_detect_respiro_estado_paz():
    """detect_respiro cuando sistema está en paz"""
    state = RespiroState()
    state.start_window()
    state.interv_count = 1
    state.deadband_seconds = 3500
    
    cfg = RespiroConfig()
    es_respiro = detect_respiro(state, cfg, marginal_gain_probe=0.001)
    assert isinstance(es_respiro, bool)


def test_invariancia_paz_perfecta():
    """Invariancia con historial perfectamente estable"""
    inv = Invariancia(epsilon=1e-3, ventana=5)
    historial_paz = [0.5000] * 10
    assert inv.es_invariante(historial_paz) == True


def test_invariancia_micro_variaciones_dentro_epsilon():
    """Variaciones microscópicas dentro de epsilon"""
    inv = Invariancia(epsilon=1e-3, ventana=5)
    historial = [0.500000, 0.500001, 0.499999, 0.500000, 0.500001]
    assert inv.es_invariante(historial) == True


def test_flujo_perfecto_end_to_end():
    """Pipeline completo en condiciones ideales"""
    inv = Invariancia(epsilon=1e-3, ventana=5)
    historial_paz = [0.5] * 10
    assert inv.es_invariante(historial_paz)
    
    sistema = SistemaCoherenciaMaxima()
    
    señales_internas = {
        "fatiga_fisica": 0.2,
        "carga_cognitiva": 0.3,
        "tension_emocional": 0.2,
        "motivacion_intrinseca": 0.8
    }
    
    señales_relacionales = {
        "feedback_directo": 0.2,
        "confianza_reportada": 0.8
    }
    
    resultado_coherencia = sistema.registrar_medicion(
        señales_internas, señales_relacionales
    )
    
    mc = core.indice_mc(80, 20)
    ci = core.indice_ci(75, 20, ruido=5)
    
    cluster_armonico = ["harmonious data"] * 10
    theta = core.compute_theta(cluster_armonico)
    
    L2_result = compute_L2_final(
        phi_c=0.5, theta_c=theta, mc=mc, ci=ci,
        bio_terms=[0.05, 0.03], bio_max=0.25,
        context_mult=1.0, min_L2=0.0, max_L2=1.0
    )
    
    mc_adj, ci_adj = core.ajustar_mc_ci_por_coherencia(
        mc, ci, resultado_coherencia
    )
    
    apply, gain = should_apply(
        current_R=0.5,
        effort_soft={"L1": 0.1},
        effort_hard={"L1": 0.2},
        cost_threshold=5.0
    )
    
    suma = core.suma_omega(mc_adj, ci_adj)
    
    L2_actualizado = core.actualizar_L2(
        L2_result["L2"], delta=0.05, minimo=0.0, maximo=1.0
    )
    
    assert 0.0 <= L2_actualizado <= 1.0
    assert mc_adj > 0.5
    assert ci_adj > 0.5
    assert suma <= core.OMEGA_U


def test_sistema_sin_burnout_jamas():
    """Verificar que en condiciones óptimas NUNCA hay burnout"""
    for i in range(100):
        coherencia = {
            "estado_self": {"estado": "RECUPERADO"},
            "decision": {"accion": "CONTINUAR"},
            "coherencia_score": 0.9
        }
        mc, ci = core.ajustar_mc_ci_por_coherencia(0.8, 0.8, coherencia)
        assert mc > 0.0
        assert ci > 0.0


def test_constantes_respetadas_en_paz():
    """Verificar que las constantes se respetan"""
    assert core.indice_mc(963, 37) == core.C_MAX
    assert core.suma_omega(0.5, 0.5) <= core.OMEGA_U
    assert core.compute_theta(["peace"] * 10) == core.THETA_BASE
    assert abs(core.K_UNCERTAINTY - (1.0 - core.C_MAX)) < 0.001
