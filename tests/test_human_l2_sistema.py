import math
from villasmil_omega.human_l2.puntos import (
    SistemaCoherenciaMaxima,
    ConfiguracionEstandar,
)

def test_sistema_basico_estado_inicial():
    sistema = SistemaCoherenciaMaxima(
        baseline_personal=0.4,
        baseline_contexto=0.3,
        config=ConfiguracionEstandar(),
    )

    assert math.isclose(sistema.mu_self, 0.4, rel_tol=1e-6)
    assert sistema.contexto.mu_otros == 0.3
    assert sistema.get_estado_actual() is None


def test_sistema_registrar_medicion_actualiza_historia():
    sistema = SistemaCoherenciaMaxima()

    señales_internas = {
        "fatiga_fisica": 0.2,
        "carga_cognitiva": 0.3,
        "tension_emocional": 0.4,
        "señales_somaticas": 0.1,
        "motivacion_intrinseca": 0.8,
    }
    señales_relacionales = {
        "feedback_directo": 0.3,
        "distancia_relacional": 0.2,
        "tension_observada": 0.1,
        "confianza_reportada": 0.7,
        "impacto_colaborativo": 0.4,
    }

    resultado = sistema.registrar_medicion(
        señales_internas=señales_internas,
        señales_relacionales=señales_relacionales,
    )

    # Se registró en el historial
    assert len(sistema.history) == 1
    assert sistema.get_estado_actual() is resultado

    # Claves básicas presentes
    for key in [
        "L2_self",
        "L2_contexto",
        "mu_self",
        "estado_self",
        "accion_self",
        "estado_contexto",
        "accion_contexto",
    ]:
        assert key in resultado
