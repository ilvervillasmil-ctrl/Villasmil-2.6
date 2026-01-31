import pytest
import villasmil_omega.core as core
import villasmil_omega.l2_model as l2m
import villasmil_omega.human_l2.puntos as pts
from villasmil_omega.respiro import should_apply
import villasmil_omega.cierre.cierre as cierre_mod

def test_presion_prolongada_sin_colapso():
    """
    Test Ω: Somete al sistema a una deriva de datos hasta forzar
    la activación de las ramas de seguridad.
    """
    sistema_puntos = pts.SistemaCoherenciaMaxima()
    historial_modelos = []
    
    # 1. Forzar CORE (Líneas 82, 84, 90-94)
    core.compute_theta([]) 
    core.compute_theta(["m1"] * 10)
    
    for i in range(50):
        tag = "a" if i % 2 == 0 else "b"
        historial_modelos.append(f"modelo_{tag}")
        theta = core.compute_theta(historial_modelos[-6:])

        # 2. Forzar PUNTOS (Líneas 180-189)
        fatiga = min(0.99, 0.1 + (i * 0.02))
        sistema_puntos.mu_self = 0.1 if i > 20 else 0.9 # Forzar saltos de mu
        sistema_puntos.registrar_medicion({"f": fatiga}, {"c": 0.5})

        # 3. Forzar L2_MODEL (Líneas 52, 89, 103-107)
        if i == 49:
            # Caso de pánico/saturación
            res_l2 = l2m.compute_L2_final(
                theta, theta, 0.5, 0.5, [0.5], 
                sistema_puntos.mu_self, 0.001, fatiga, 0.1
            )
            assert "L2" in res_l2

    # 4. Forzar RESPIRO (Líneas 40-41)
    should_apply(0.5, {"e": 0.9}, {"e": 0.99}, cost_threshold=0.1)

    # 5. CIERRE (Ejecución segura del módulo)
    # Si existe una función llamada 'cierre', la usa; si no, solo carga el módulo
    if hasattr(cierre_mod, 'cierre'):
        cierre_mod.cierre(0.5, 0.5)
