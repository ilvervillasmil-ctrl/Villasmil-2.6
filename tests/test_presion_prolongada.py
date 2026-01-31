import pytest
from villasmil_omega.core import compute_theta
from villasmil_omega.l2_model import compute_L2_final
from villasmil_omega.human_l2.puntos import SistemaCoherenciaMaxima
from villasmil_omega.respiro import should_apply
from villasmil_omega.cierre.cierre import cierre_integrado

def test_presion_prolongada_sin_colapso():
    """
    Test Ω: Somete al sistema a una deriva de datos hasta forzar
    la activación de las ramas de seguridad (92% -> 100%).
    """
    sistema_puntos = SistemaCoherenciaMaxima()
    historial_modelos = []
    coherencia_final = 0.0

    # Simulamos 120 ciclos de presión incremental
    for i in range(120):
        # 1. CORE: Generamos modelos con balance degradado
        # Esto atacará core.py: 84, 90-94
        tag = "model a" if i % 3 == 0 else "model b"
        historial_modelos.append(f"data_stream_{i}_{tag}")
        
        theta = compute_theta(historial_modelos[-10:]) # Ventana móvil

        # 2. PUNTOS: Inyectamos deriva biométrica sostenida
        # Esto atacará puntos.py: 180-189 (Riesgo/Recuperación)
        fatiga = min(0.99, 0.1 + (i * 0.01))
        feedback = max(0.01, 0.9 - (i * 0.01))
        sistema_puntos.registrar_medicion(
            {"fatiga_fisica": fatiga}, 
            {"feedback_directo": feedback}
        )

        # 3. RESPIRO: ¿El sistema detecta el costo de seguir?
        # Ataca respiro.py: 40-41
        pedir_respiro, ganancia = should_apply(
            theta, 
            {"e": fatiga}, 
            {"e": fatiga + 0.01}, 
            cost_threshold=0.5
        )

        # 4. CIERRE: Si hay saturación o el respiro es necesario
        if pedir_respiro or i == 119:
            # Ataca l2_model.py: 103-107 (Saturación Bio-max)
            l2_data = compute_L2_final(
                phi_C=theta, theta_C=theta, MC=0.5, CI=0.5,
                puntos_hist=[0.5], mu_self=sistema_puntos.mu_self,
                MAD_self=sistema_puntos.MAD_self, fatiga=fatiga, feedback=feedback
            )
            
            # Cierre final de ciclo
            coherencia_final = cierre_integrado(theta, l2_data['L2'])
            break

    # Validación de Autonomía Defensiva
    assert coherencia_final > 0.0
    assert sistema_puntos.mu_self is not None
