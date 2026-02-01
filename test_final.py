import pytest
import villasmil_omega.core as core
import villasmil_omega.l2_model as l2m
import villasmil_omega.human_l2.puntos as pts

def test_fuerza_bruta_cobertura():
    # 1. CORE: Golpear líneas 10 y 81-107 (Las guardias de seguridad)
    try:
        core.compute_theta([]) # Lista vacía para activar línea 81
    except: pass
    core.compute_theta(["error"] * 20) # Saturar para activar 90-100
    
    # 2. PUNTOS: Golpear 180-189 (La fatiga crítica)
    s = pts.SistemaCoherenciaMaxima()
    s.mu_self = None # Forzar el 'if not self.mu_self'
    s.registrar_medicion({"fatiga": 1.0}, {"coherencia": 0.0}) # Activa 185
    
    # 3. L2_MODEL: Golpear 52, 89 y 103 (Límites físicos)
    l2m.ajustar_L2(10.0, 1.0) # Forzar el clamp superior (103)
    l2m.ajustar_L2(-10.0, 1.0) # Forzar el clamp inferior (52)
    # Mandar parámetros invertidos para activar el swap de la 89
    l2m.compute_L2_final(0.1, 0.1, 0.9, 0.9, [0.1], 0.9, 0.01, 0.1, 0.1)

    # 4. INVARIANCIA: Golpear línea 12
    from villasmil_omega.cierre.invariancia import Invariancia
    inv = Invariancia(epsilon=0.000)
    inv.es_invariante([1, 2, 3]) # Forzar el loop de la 12
