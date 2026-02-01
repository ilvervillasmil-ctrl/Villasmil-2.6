# tests/test_paz_absoluta.py
"""
TEST DE PAZ ABSOLUTA - RELAJACIÓN EXTREMA
Permite que el sistema opere en condiciones ideales: sin estrés, sin conflicto, en flujo perfecto.
Este test descubre las líneas que solo se ejecutan cuando TODO va bien.
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


# ═══════════════════════════════════════════════════════════════════════════
# CORE.PY - OPERACIÓN EN CONDICIONES ÓPTIMAS
# ═══════════════════════════════════════════════════════════════════════════

def test_core_estado_optimo_total():
    """Sistema operando en coherencia máxima perfecta"""
    # Coherencia perfecta: todo al máximo permitido
    coherencia_perfecta = {
        "estado_self": {"estado": "RECUPERADO"},
        "decision": {"accion": "CONTINUAR"},
        "coherencia_score": core.C_MAX  # 0.963 - techo de coherencia
    }
    
    # MC y CI óptimos
    mc_optimo = core.indice_mc(963, 37)  # Ratio perfecto = C_MAX
    ci_optimo = core.indice_ci(963, 37, ruido=0)
    
    # Ajustar - debe MANTENER los valores (no penalizar)
    mc_final, ci_final = core.ajustar_mc_ci_por_coherencia(
        mc_optimo, ci_optimo, coherencia_perfecta
    )
    
    # En estado óptimo, mantiene valores altos
    assert mc_final > 0.9
    assert ci_final > 0.9
    
    print(f"✨ PAZ ABSOLUTA: MC={mc_final:.3f}, CI={ci_final:.3f}")


def test_core_suma_omega_valores_normales_sin_saturacion():
    """suma_omega con valores que NO saturan - flujo natural"""
    # Valores pequeños que NO activan OMEGA_U
    resultado1 = core.suma_omega(0.1, 0.1)
    assert resultado1 == 0.2  # Sin saturación
    
    resultado2 = core.suma_omega(0.3, 0.3)
    assert resultado2 == 0.6  # Sin saturación
    
    resultado3 = core.suma_omega(0.4, 0.4)
    assert resultado3 == 0.8  # Sin saturación
    
    print(f"🌊 Flujo natural sin saturación: {resultado1}, {resultado2}, {resultado3}")


def test_core_clamp_valores_dentro_de_rango():
    """clamp cuando valores están perfectamente dentro del rango"""
    # Valores que NO necesitan ajuste
    assert core.clamp(0.25, 0.0, 1.0) == 0.25
    assert core.clamp(0.50, 0.0, 1.0) == 0.50
    assert core.clamp(0.75, 0.0, 1.0) == 0.75
    assert core.clamp(0.963, 0.0, 1.0) == 0.963  # Exactamente C_MAX
    
    print("✅ Todos los valores en rango óptimo")


def test_core_compute_theta_sin_conflicto():
    """compute_theta con clusters sin tensión - paz total"""
    # Cluster homogéneo (sin model a ni model b)
    cluster_paz = ["data harmonious"] * 10
    theta_paz = core.compute_theta(cluster_paz)
    
    # Debe retornar THETA_BASE (0.015) - tensión mínima
    assert theta_paz == core.THETA_BASE
    
    print(f"🕊️ Tensión basal en paz: θ={theta_paz}")


def test_core_procesar_flujo_omega_con_paz_invariante():
    """procesar_flujo con datos invariantes - sistema en reposo"""
    # Datos perfectamente estables (sin varianza)
    datos_estables = [0.5] * 20
    
    resultado = core.procesar_flujo_omega(datos_estables, {})
    
    # Sistema debe detectar invariancia y entrar en modo basal
    assert resultado["status"] == "basal"
    assert resultado["invariante"] == True
    assert resultado["energia_ahorrada"] == True
    
    print("💤 Sistema en reposo - energía conservada")


# ═══════════════════════════════════════════════════════════════════════════
# L2_MODEL - OPERACIÓN ARMONIOSA
# ═══════════════════════════════════════════════════════════════════════════

def test_l2model_compute_L2_base_valores_armonicos():
    """compute_L2_base con valores balanceados y armónicos"""
    # Valores balanceados: mc=ci, phi=theta, context normal
    L2_base = compute_L2_base(
        mc=0.5,
        ci=0.5,
        phi_c=0.5,
        theta_c=0.5,
        context_mult=1.0  # Sin amplificación
    )
    
    # L2_base = 1.0 * (0.5*0.5 + 0.5*0.5) = 0.5
    assert abs(L2_base - 0.5) < 0.01
    
    print(f"⚖️ Balance perfecto: L2_base={L2_base:.3f}")


def test_l2model_ajustar_L2_sin_ajustes():
    """ajustar_L2 cuando L2 ya está en rango perfecto"""
    # L2 perfecto dentro de [0,1] sin necesidad de ajuste
    L2_perfecto = ajustar_L2(L2_base=0.5, bio_effect=0.2)
    
    # 0.5 + 0.2 = 0.7 (dentro de rango)
    assert L2_perfecto == 0.7
    
    print(f"✨ L2 armónico: {L2_perfecto}")


def test_l2model_apply_bio_adjustment_positivo_moderado():
    """apply_bio_adjustment con términos biológicos positivos pero moderados"""
    # Bio positivo pero NO satura
    bio_terms = [0.05, 0.03, 0.02]  # Suma = 0.10 < bio_max=0.25
    
    bio_effect = apply_bio_adjustment(bio_terms, bio_max=0.25)
    
    assert bio_effect == 0.10  # Sin saturación
    
    print(f"🌱 Bio efecto saludable: {bio_effect}")


def test_l2model_compute_L2_final_sin_swap_sin_clamp():
    """compute_L2_final donde min < max y L2 dentro de rango"""
    resultado = compute_L2_final(
        phi_c=0.3,
        theta_c=0.3,
        mc=0.5,
        ci=0.5,
        bio_terms=[0.1],
        bio_max=0.25,
        context_mult=1.0,
        min_L2=0.2,  # min < max (correcto)
        max_L2=0.8
    )
    
    # No hay swap, no hay clamps extremos
    L2_final = resultado["L2"]
    assert 0.2 <= L2_final <= 0.8
    
    print(f"🎯 L2 final en zona segura: {L2_final:.3f}")


# ═══════════════════════════════════════════════════════════════════════════
# RESPIRO - OPERACIÓN SIN PRESIÓN
# ═══════════════════════════════════════════════════════════════════════════

def test_respiro_distribute_action_valores_positivos_balanceados():
    """distribute_action con sensitivities positivos y balanceados"""
    cfg = RespiroConfig()
    
    # Sensitivities positivos, balanceados
    resultado = distribute_action(
        0.5,  # base_effort moderado
        {"a": 0.25, "b": 0.25, "c": 0.25, "d": 0.25},  # Equitativo
        cfg
    )
    
    # Debe distribuir equitativamente
    valores = list(resultado.values())
    assert all(abs(v - valores[0]) < 0.01 for v in valores)
    
    print(f"⚖️ Distribución equitativa: {resultado}")


def test_respiro_should_apply_sin_presion():
    """should_apply cuando esfuerzo soft es suficiente"""
    # current_R bajo, effort_soft bajo, cost_threshold alto
    apply, gain = should_apply(
        current_R=0.3,  # Bajo R
        effort_soft={"L1": 0.1},  # Esfuerzo suave
        effort_hard={"L1": 0.5},  # Esfuerzo duro
        cost_threshold=10.0  # Muy permisivo
    )
    
    # Puede o no aplicar, pero sin errores
    assert isinstance(apply, bool)
    assert isinstance(gain, (float, str))
    
    print(f"🌊 Evaluación sin presión: apply={apply}")


def test_respiro_detect_respiro_estado_paz():
    """detect_respiro cuando sistema está en paz"""
    state = RespiroState()
    state.start_window()
    state.interv_count = 1  # Pocas intervenciones
    state.deadband_seconds = 3500  # Mucho tiempo en deadband
    
    cfg = RespiroConfig()
    cfg.interv_threshold_per_hour = 5.0
    cfg.min_deadband_fraction = 0.5
    cfg.marginal_gain_epsilon = 0.02
    
    # marginal_gain muy bajo (paz)
    es_respiro = detect_respiro(state, cfg, marginal_gain_probe=0.001)
    
    # Debe detectar que está en paz
    assert es_respiro == True
    
    print("😌 Sistema en paz detectado")


# ═══════════════════════════════════════════════════════════════════════════
# INVARIANCIA - PAZ SISTÉMICA
# ═══════════════════════════════════════════════════════════════════════════

def test_invariancia_paz_perfecta():
    """Invariancia con historial perfectamente estable"""
    inv = Invariancia(epsilon=1e-3, ventana=5)
    
    # Historial sin variación alguna
    historial_paz = [0.5000] * 10
    
    assert inv.es_invariante(historial_paz) == True
    
    print("🕊️ Paz perfecta detectada - varianza = 0")


def test_invariancia_micro_variaciones_dentro_epsilon():
    """Variaciones microscópicas dentro de epsilon"""
    inv = Invariancia(epsilon=1e-3, ventana=5)
    
    # Variaciones imperceptibles
    historial = [
        0.500000,
        0.500001,
        0.499999,
        0.500000,
        0.500001
    ]
    
    assert inv.es_invariante(historial) == True
    
    print("✨ Micro-variaciones toleradas - sistema estable")


# ═══════════════════════════════════════════════════════════════════════════
# INTEGRACIÓN - FLUJO PERFECTO DE PRINCIPIO A FIN
# ═══════════════════════════════════════════════════════════════════════════

def test_flujo_perfecto_end_to_end():
    """
    Pipeline completo en condiciones ideales:
    - Sin conflictos
    - Sin estrés
    - Sin saturación
    - Coherencia máxima
    """
    print("\n" + "="*70)
    print("🌟 INICIANDO FLUJO PERFECTO - PAZ ABSOLUTA")
    print("="*70)
    
    # 1. Invariancia: datos estables
    inv = Invariancia(epsilon=1e-3, ventana=5)
    historial_paz = [0.5] * 10
    
    if inv.es_invariante(historial_paz):
        print("✅ Paso 1: Sistema en paz - invarianza detectada")
    
    # 2. Sistema de coherencia en estado óptimo
    sistema = SistemaCoherenciaMaxima(
        baseline_personal=0.4,
        baseline_contexto=0.4
    )
    
    # Señales internas saludables
    señales_internas = {
        "fatiga_fisica": 0.2,  # Baja fatiga
        "carga_cognitiva": 0.3,
        "tension_emocional": 0.2,
        "motivacion_intrinseca": 0.8  # Alta motivación
    }
    
    # Señales relacionales armónicas
    señales_relacionales = {
        "feedback_directo": 0.2,  # Bajo conflicto
        "confianza_reportada": 0.8  # Alta confianza
    }
    
    resultado_coherencia = sistema.registrar_medicion(
        señales_internas,
        señales_relacionales
    )
    
    print(f"✅ Paso 2: Coherencia registrada - Score={resultado_coherencia['coherencia_score']:.3f}")
    
    # 3. MC y CI en rango óptimo
    mc = core.indice_mc(80, 20)  # 80% aciertos
    ci = core.indice_ci(75, 20, ruido=5)  # Con poco ruido
    
    print(f"✅ Paso 3: MC={mc:.3f}, CI={ci:.3f}")
    
    # 4. Theta sin conflictos
    cluster_armonico = ["harmonious data"] * 10
    theta = core.compute_theta(cluster_armonico)
    
    print(f"✅ Paso 4: Tensión mínima θ={theta:.3f}")
    
    # 5. L2 en rango saludable
    L2_result = compute_L2_final(
        phi_c=0.5,
        theta_c=theta,
        mc=mc,
        ci=ci,
        bio_terms=[0.05, 0.03],  # Bio positivo moderado
        bio_max=0.25,
        context_mult=1.0,
        min_L2=0.0,
        max_L2=1.0
    )
    
    print(f"✅ Paso 5: L2={L2_result['L2']:.3f} (zona saludable)")
    
    # 6. Ajustar por coherencia (sin penalización)
    mc_adj, ci_adj = core.ajustar_mc_ci_por_coherencia(
        mc, ci, resultado_coherencia
    )
    
    print(f"✅ Paso 6: MC_adj={mc_adj:.3f}, CI_adj={ci_adj:.3f}")
    
    # 7. Respiro NO necesario (sistema relajado)
    apply, gain = should_apply(
        current_R=0.5,
        effort_soft={"L1": 0.1},
        effort_hard={"L1": 0.2},
        cost_threshold=5.0
    )
    
    print(f"✅ Paso 7: Respiro evaluado - apply={apply}")
    
    # 8. Suma omega sin saturación
    suma = core.suma_omega(mc_adj, ci_adj)
    
    print(f"✅ Paso 8: Suma Omega={suma:.3f}")
    
    # 9. Actualizar L2 con delta pequeño
    L2_actualizado = core.actualizar_L2(
        L2_result["L2"],
        delta=0.05,  # Evolución suave
        minimo=0.0,
        maximo=1.0
    )
    
    print(f"✅ Paso 9: L2 actualizado={L2_actualizado:.3f}")
    
    print("="*70)
    print("🌟 FLUJO PERFECTO COMPLETADO - SISTEMA EN ARMONÍA TOTAL")
    print("="*70)
    
    # Verificaciones finales
    assert 0.0 <= L2_actualizado <= 1.0
    assert mc_adj > 0.5  # Mantiene buen nivel
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
        
        # Nunca debe colapsar
        assert mc > 0.0
        assert ci > 0.0
    
    print("✅ 100 iteraciones en paz - CERO burnouts")


def test_constantes_respetadas_en_paz():
    """Verificar que las constantes se respetan en operación normal"""
    # C_MAX
    assert core.indice_mc(963, 37) == core.C_MAX
    
    # OMEGA_U (en valores normales)
    assert core.suma_omega(0.5, 0.5) <= core.OMEGA_U
    
    # THETA_BASE
    assert core.compute_theta(["peace"] * 10) == core.THETA_BASE
    
    # K_UNCERTAINTY
    assert core.K_UNCERTAINTY == 1.0 - core.C_MAX
    
    print("✅ Todas las constantes maestras respetadas en paz")
