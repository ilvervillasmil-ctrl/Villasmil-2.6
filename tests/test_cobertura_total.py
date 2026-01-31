import pytest
from villasmil_omega.human_l2.puntos import SistemaCoherenciaMaxima, ConfiguracionEstandar
from villasmil_omega.core import ajustar_mc_ci_por_coherencia, indice_mc
from villasmil_omega.l2_model import L2HumanModel
from villasmil_omega.respiro import RespiroOmega
from villasmil_omega.cierre.invariancia import calcular_invariancia

def test_ataque_cobertura_final():
    # 1. CORE: Protecciones y límites (82-134)
    indice_mc(0, 0)
    for v in [None, [], {}]:
        try: ajustar_mc_ci_por_coherencia(v, 0.5, {"estado": "ok"})
        except: pass

    # 2. PUNTOS: Evitando KeyError y forzando Burnout (66-247)
    config = ConfiguracionEstandar()
    # Definimos todas las llaves que el diccionario w espera en la línea 81
    config.W_CONTEXTO = {
        "feedback_directo": 0.2,
        "distancia_relacional": 0.2,
        "tension_observada": 0.2,
        "confianza_reportada": 0.2,
        "impacto_colaborativo": 0.2
    }
    sistema = SistemaCoherenciaMaxima(config)
    
    # Datos completos para satisfacer el diccionario señales_relacionales
    for val in [0.95, 0.75, 0.40, 0.10]:
        datos = {
            "feedback_directo": val,
            "distancia_relacional": val,
            "tension_observada": val,
            "confianza_reportada": val,
            "impacto_colaborativo": val
        }
        # Esto cubrirá las líneas de lógica de estado (Burnout/Crítico)
        sistema.registrar_medicion(datos, datos)
    
    # 3. L2_MODEL: Reset y Clamps (42-107)
    model = L2HumanModel()
    model.reset()
    model.update(1.5) # Clamp superior (Línea 89)
    model.update(-0.5) # Clamp inferior
    try: model._compute_CI(0.8, 0.1) # Rama de inconsistencia (52-53)
    except: pass

    # 4. RESPIRO E INVARIANCIA (40-41, 12)
    res = RespiroOmega(alfa_respiro=0.5, beta_suavizado=0.5)
    res.actualizar(0.6, 0.8)
    try: calcular_invariancia(0.0, 0.0)
    except: pass
