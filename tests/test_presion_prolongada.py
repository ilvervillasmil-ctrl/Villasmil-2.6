import pytest
from villasmil_omega.core import compute_theta
from villasmil_omega.l2_model import compute_L2_final
from villasmil_omega.human_l2.puntos import SistemaCoherenciaMaxima
from villasmil_omega.respiro import should_apply
# Corregido: Importamos la clase o función base según tus reportes previos
from villasmil_omega.cierre.cierre import Cierre 

def test_presion_prolongada_sin_colapso():
    """
    Test Ω: Somete al sistema a una deriva de datos hasta forzar
    la activación de las ramas de seguridad.
    """
    sistema_puntos = SistemaCoherenciaMaxima()
    historial_modelos = []
    coherencia_final = 0.0

    for i in range(120):
        # 1. CORE: Diversidad de modelos
        tag = "model_a" if i % 3 == 0 else "model_b"
        historial_modelos.append(f"data_{i}_{tag}")
        theta = compute_theta(historial_modelos[-10:])

        # 2. PUNTOS: Deriva de fatiga
        fatiga = min(0.99, 0.1 + (i * 0.01))
        sistema_puntos.registrar_medicion(
            {"fatiga_fisica": fatiga}, 
            {"feedback": 0.5}
        )

        # 3. RESPIRO: Detección de costo
        pedir_respiro, _ = should_apply(
            theta, {"e": fatiga}, {"e": fatiga + 0.01}, cost_threshold=0.5
        )

        # 4. L2 & CIERRE: Activación de pánico
        if pedir_respiro or i == 119:
            l2_data = compute_L2_final(
                phi_C=theta, theta_C=theta, MC=0.5, CI=0.5,
                puntos_hist=[0.5], mu_self=sistema_puntos.mu_self,
                MAD_self=sistema_puntos.MAD_self, fatiga=fatiga, feedback=0.5
            )
            # Usamos el objeto de cierre estándar
            c = Cierre()
            coherencia_final = c.evaluar(theta, l2_data['L2'])
            break

    assert coherencia_final >= 0.0
