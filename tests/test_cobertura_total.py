import pytest
import numpy as np
from villasmil_omega.core import ajustar_mc_ci_por_coherencia, indice_mc, penalizar_MC_CI, actualizar_L2
from villasmil_omega.respiro import should_apply
from villasmil_omega.cierre.invariancia import InvarianciaOmega
from villasmil_omega.human_l2.puntos import SistemaCoherenciaMaxima, ConfiguracionEstandar

# 1. COBERTURA: core.py (Líneas 82, 84, 90-94, 134)
def test_core_precision_milimetrica():
    # Test de indice_mc con denominador cero (Línea 134)
    assert indice_mc(0, 0) == 0.0
    
    # Test de penalización en bordes
    assert penalizar_MC_CI(1.0, 1.0, 0.0, factor=2.0) >= 0.0
    
    # Test de actualizar_L2 con clamps (min/max)
    # Forzamos que intente ir por debajo de 0.1 y por encima de 0.9
    assert actualizar_L2(0.2, -1.0, 0.1, 0.9) == 0.1
    assert actualizar_L2(0.8, 1.0, 0.1, 0.9) == 0.9

# 2. COBERTURA: respiro.py (Líneas 40-41)
def test_respiro_bloqueo_por_costo():
    # Caso donde el costo supera el umbral (debe devolver False / No aplicar)
    # should_apply(current_coherence, prev_state, current_state, cost_threshold)
    paz, _ = should_apply(0.5, {"f": 0.5}, {"f": 0.6}, cost_threshold=0.001)
    assert paz is False

# 3. COBERTURA: invariancia.py (Línea 12)
def test_invariancia_limite():
    inv = InvarianciaOmega()
    # Forzamos el estado de "no historia" o validación de invariante único
    assert inv.verificar_invariancia([]) is True 

# 4. COBERTURA: human_l2/puntos.py (Ramas complejas 131-247)
def test_puntos_estadistica_extrema():
    config = ConfiguracionEstandar()
    sistema = SistemaCoherenciaMaxima(config)
    
    # A. Cobertura de historia insuficiente (Líneas 66, 69)
    assert sistema.get_estado_actual() is None
    
    # B. Forzar Tie-break y Ranking (Líneas 180-189)
    # Registramos mediciones con valores idénticos para forzar lógica de desempate
    for _ in range(5):
        sistema.registrar_medicion({"f": 0.5}, {"contexto": 0.5})
    
    estado = sistema.get_estado_actual()
    assert estado is not None
    
    # C. Forzar MAD y Sigma (Líneas 131-144)
    # Generamos una ráfaga de datos altamente volátiles
    for i in range(50):
        val = 0.99 if i % 2 == 0 else 0.01
        sistema.registrar_medicion({"f": val}, {"contexto": 1.0 - val})
    
    final = sistema.get_estado_actual()
    assert "L2_self" in final

# 5. COBERTURA: l2_model.py (Ramas biométricas y stress)
def test_l2_model_biometria_y_clamps():
    from villasmil_omega.l2_model import L2Model
    model = L2Model()
    
    # Forzamos desviación de HR > 0.35 (Líneas 52-53)
    res_high = model.compute_L2_enhanced(
        phi_C=0.5, theta_C=0.5, MC=0.5, CI=0.5, 
        heart_rate=110, baseline_hr=60 # HR muy alta
    )
    assert res_high['bio_adjustment'] < 0
    
    # Forzamos estrés subjetivo máximo y clamps (Líneas 103-107)
    res_clamp = model.compute_L2_enhanced(
        phi_C=0.9, theta_C=0.9, MC=0.1, CI=0.1,
        subjective_stress=10, min_L2=0.2, max_L2=0.8
    )
    assert 0.2 <= res_clamp['L2'] <= 0.8
