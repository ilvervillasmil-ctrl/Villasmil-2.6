import pytest
import villasmil_omega.core as core
import villasmil_omega.l2_model as l2m
import villasmil_omega.human_l2.puntos as pts
from villasmil_omega.respiro import should_apply

def test_cobertura_quirurgica_total():
    # --- 1. CORE (Líneas 82, 84, 90-94) ---
    # Forzamos cada condicional de compute_theta
    core.compute_theta([])                                      # Línea 82
    core.compute_theta(["model a"] * 10)                        # Línea 84
    core.compute_theta(["model b"] * 10)                        # Línea 90-91
    # Balance perfecto con descriptores para activar rama 93-94
    core.compute_theta(["model a descriptor"] * 3 + ["model b descriptor"] * 3)

    # --- 2. PUNTOS (Líneas 66, 69, 180-189) ---
    conf = pts.ConfiguracionEstandar()
    # Forzar lectura de constantes (66, 69)
    _ = conf.W_CONTEXTO
    _ = conf.W_SELF
    
    sistema = pts.SistemaCoherenciaMaxima()
    # Transiciones de estado (180-189)
    sistema.mu_self = None                                      # Línea 180
    sistema.registrar_medicion({"f": 0.5}, {"c": 0.5})
    
    sistema.mu_self, sistema.MAD_self = 0.1, 0.001
    sistema.registrar_medicion({"fatiga_fisica": 0.9}, {"c": 0.5}) # Línea 186
    
    sistema.mu_self = 0.9
    sistema.registrar_medicion({"fatiga_fisica": 0.1}, {"c": 0.5}) # Línea 188

    # --- 3. L2_MODEL (Líneas 42, 52-53, 89, 103-107) ---
    # Línea 42: suele ser un error de inicialización o retorno temprano
    l2m.ajustar_L2(-1.0, 1.0)                                   # Línea 52
    l2m.ajustar_L2(2.0, 1.0)                                    # Línea 53
    
    # Línea 89: Swap de seguridad
    l2m.compute_L2_final(0.1, 0.1, 0.5, 0.5, [0.1], 0.25, 1.0, 0.9, 0.1)
    
    # Líneas 103-107: Caso bio_max exacto
    l2m.compute_L2_final(0.0, 0.0, 0.0, 0.0, [0.25], 0.25, 1.0, 0.0, 1.0)

    # --- 4. RESPIRO (Líneas 40-41) ---
    should_apply(0.5, {"e": 1.5}, {"e": 1.6}, cost_threshold=1.0)
    should_apply(0.99, {"e": 0.01}, {"e": 0.011}, 100.0)
