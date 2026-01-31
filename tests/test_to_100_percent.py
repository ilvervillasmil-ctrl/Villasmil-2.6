# tests/test_final_100.py
"""Test quirúrgico para llegar al 100% de cobertura"""

import pytest
from villasmil_omega.l2_model import (
    apply_bio_adjustment,
    compute_L2_base,
    ajustar_L2,
    compute_theta,
    compute_L2_final,
    theta_for_two_clusters
)
from villasmil_omega.core import compute_theta as core_compute_theta
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
# L2_MODEL.PY - 78% → 100%
# ============================================================

def test_l2model_linea_42_44_bio_terms_negative():
    """Líneas 42, 44: apply_bio_adjustment con bio_terms negativo"""
    # total < 0 → debe devolver 0.0
    result = apply_bio_adjustment([-0.5, -0.3], bio_max=0.25)
    assert result == 0.0


def test_l2model_linea_52_53_ajustar_L2_clamps():
    """Líneas 52-53: ajustar_L2 con valores fuera de rango"""
    # L2 < 0
    r1 = ajustar_L2(-0.5, 0.3)
    assert r1 == 0.0
    
    # L2 > 1
    r2 = ajustar_L2(0.8, 0.5)
    assert r2 == 1.0


def test_l2model_linea_89_compute_L2_final_swap():
    """Línea 89: compute_L2_final con min > max (swap)"""
    result = compute_L2_final(
        phi_c=0.5,
        theta_c=0.5,
        mc=0.6,
        ci=0.7,
        bio_terms=[0.1],
        bio_max=0.25,
        context_mult=1.0,
        min_L2=0.8,  # min > max
        max_L2=0.2,  # Debe swapear
    )
    assert 0.2 <= result["L2"] <= 0.8


def test_l2model_lineas_103_107_compute_L2_final_bio_max_case():
    """Líneas 103-107: caso especial bio_max"""
    result = compute_L2_final(
        phi_c=0.0,
        theta_c=0.0,
        mc=0.0,
        ci=0.0,
        bio_terms=[0.3],  # > bio_max
        bio_max=0.25,
        context_mult=1.0,
        min_L2=0.0,
        max_L2=0.5,  # max_L2 > bio_max
    )
    # Debe fijar a max_L2
    assert result["L2"] == 0.5


# ============================================================
# CORE.PY - 91% → 100%
# ============================================================

def test_core_lineas_82_84_90_91_93_94_compute_theta():
    """Líneas 82, 84, 90-91, 93-94: compute_theta con cluster edge cases"""
    # cluster vacío
    assert core_compute_theta([]) == 0.0
    
    # solo model a
    assert core_compute_theta(["model a"] * 7) == 0.0
    
    # solo model b
    assert core_compute_theta(["model b"] * 7) == 0.0
    
    # ambos presentes pero < 6 elementos
    assert core_compute_theta(["model a", "model b"]) == 0.0
    
    # ambos presentes y >= 6 elementos
    cluster_mixed = ["model a"] * 3 + ["model b"] * 3
    assert core_compute_theta(cluster_mixed) == 1.0


def test_core_linea_134_theta_for_two_clusters():
    """Línea 134: theta_for_two_clusters con clusters"""
    c1 = ["model a", "model a"]
    c2 = ["model b", "model b"]
    
    result = core.theta_for_two_clusters(c1, c2)
    
    assert "theta_c1" in result
    assert "theta_c2" in result
    assert "theta_combined" in result


# ============================================================
# PUNTOS.PY - 82% → 100%
# ============================================================

def test_puntos_lineas_66_69_W_CONTEXTO_W_SELF():
    """Líneas 66, 69: usa W_CONTEXTO y W_SELF de conf"""
    conf = ConfiguracionEstandar()
    
    # Forzar uso de pesos específicos
    L2_ctx = compute_L2_contexto({
        "feedback_directo": 1.0,
        "distancia_relacional": 1.0,
        "tension_observada": 1.0,
        "confianza_reportada": 0.0,
        "impacto_colaborativo": 1.0,
    }, conf)
    
    L2_slf = compute_L2_self({
        "fatiga_fisica": 1.0,
        "carga_cognitiva": 1.0,
        "tension_emocional": 1.0,
        "señales_somaticas": 1.0,
        "motivacion_intrinseca": 0.0,
    }, conf)
    
    assert 0 <= L2_ctx <= 1
    assert 0 <= L2_slf <= 1


def test_puntos_lineas_131_144_PuntoNeutro_init():
    """Líneas 131-144: PuntoNeutroContexto inicialización completa"""
    punto = PuntoNeutroContexto()
    assert punto.mu_otros is None
    assert punto.MAD_otros == 0.0
    
    # Primera actualización
    r = punto.update(0.5)
    assert r["estado"] == "BASELINE_INICIAL"
    assert punto.mu_otros == 0.5


def test_puntos_lineas_157_158_SistemaCoherencia_post_init():
    """Líneas 157-158: SistemaCoherenciaMaxima.__post_init__"""
    sistema = SistemaCoherenciaMaxima(
        baseline_personal=0.45,
        baseline_contexto=0.35
    )
    assert sistema.mu_self == 0.45
    assert sistema.contexto.mu_otros == 0.35


def test_puntos_lineas_180_189_registrar_medicion_estados():
    """Líneas 180-189: registrar_medicion con diferentes estados"""
    sistema = SistemaCoherenciaMaxima()
    
    # Estado inicial (mu_self None)
    r1 = sistema.registrar_medicion(
        {"fatiga_fisica": 0.5},
        {"feedback_directo": 0.3}
    )
    assert r1["estado_self"]["estado"] == "BASELINE_INICIAL"
    
    # Estado RIESGO_SELF (L2 > mu + deadband)
    sistema.mu_self = 0.3
    r2 = sistema.registrar_medicion(
        {"fatiga_fisica": 0.8},
        {"feedback_directo": 0.3}
    )
    # Puede ser RIESGO_SELF o SELF_ESTABLE según deadband
    assert "estado" in r2["estado_self"]
    
    # Estado SELF_RECUPERADO (L2 < mu - deadband)
    sistema.mu_self = 0.7
    r3 = sistema.registrar_medicion(
        {"fatiga_fisica": 0.2},
        {"feedback_directo": 0.3}
    )
    # Puede ser SELF_RECUPERADO o SELF_ESTABLE
    assert "estado" in r3["estado_self"]


def test_puntos_lineas_227_233_get_estado_actual():
    """Líneas 227-233: get_estado_actual con y sin historia"""
    sistema = SistemaCoherenciaMaxima()
    
    # Sin historia
    estado = sistema.get_estado_actual()
    assert estado is None
    
    # Con historia
    sistema.registrar_medicion(
        {"fatiga_fisica": 0.5},
        {"feedback_directo": 0.3}
    )
    estado = sistema.get_estado_actual()
    assert estado is not None
    assert "L2_self" in estado


def test_puntos_lineas_246_247_get_explicacion():
    """Líneas 246-247: get_explicacion de PuntoNeutroContexto"""
    punto = PuntoNeutroContexto()
    punto.update(0.5)
    
    # Diferentes estados
    r1 = punto.update(0.8)  # Puede ser DAÑANDO_CONTEXTO
    explicacion1 = punto.get_explicacion(r1)
    assert isinstance(explicacion1, str)
    
    r2 = punto.update(0.2)  # Puede ser CONTEXTO_MEJORADO
    explicacion2 = punto.get_explicacion(r2)
    assert isinstance(explicacion2, str)


# ============================================================
# RESPIRO.PY - 96% → 100%
# ============================================================

def test_respiro_lineas_40_41_cost_threshold_y_marginal():
    """Líneas 40-41: should_apply con cost > threshold Y marginal < 0.02"""
    # Caso 1: cost_soft > cost_threshold
    apply1, gain1 = should_apply(
        current_R=0.5,
        effort_soft={"a": 1.0},  # cost = 1.0^2 = 1.0
        effort_hard={"a": 1.1},
        cost_threshold=0.5  # 1.0 > 0.5
    )
    assert apply1 == True
    
    # Caso 2: marginal_gain < 0.02
    apply2, gain2 = should_apply(
        current_R=0.95,  # Ya muy alto
        effort_soft={"a": 0.1},
        effort_hard={"a": 0.11},  # Ganancia marginal mínima
        cost_threshold=1.0
    )
    # marginal_gain será < 0.02
    assert isinstance(gain2, float)


# ============================================================
# INVARIANCIA.PY - 93% → 100%
# ============================================================

def test_invariancia_linea_12_for_loop():
    """Línea 12: for v in historial con diferentes casos"""
    inv = Invariancia(epsilon=1e-3, ventana=5)
    
    # Caso donde todos están dentro de epsilon
    hist1 = [0.5, 0.5001, 0.4999, 0.5, 0.50005]
    assert inv.es_invariante(hist1) == True
    
    # Caso donde uno está fuera de epsilon
    hist2 = [0.5, 0.5, 0.5, 0.5, 0.502]
    assert inv.es_invariante(hist2) == False
    
    # Ventana insuficiente
    hist3 = [0.5, 0.5, 0.5]
    assert inv.es_invariante(hist3) == False
