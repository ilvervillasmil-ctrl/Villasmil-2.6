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
        import math
from villasmil_omega.human_l2.puntos import (
    SistemaCoherenciaMaxima,
    ConfiguracionEstandar,
)

def test_sistema_riesgo_self():
    # Config con deltas pequeños para disparar RIESGO_SELF fácil
    conf = ConfiguracionEstandar(
        DELTA_ABS_SELF=0.01,
        ALPHA_SELF=0.5,
    )
    sistema = SistemaCoherenciaMaxima(config=conf)

    # Primera medición: establece baseline
    señales_internas1 = {
        "fatiga_fisica": 0.2,
        "carga_cognitiva": 0.2,
        "tension_emocional": 0.2,
        "señales_somaticas": 0.2,
        "motivacion_intrinseca": 0.8,
    }
    señales_relacionales = {
        "feedback_directo": 0.0,
        "distancia_relacional": 0.0,
        "tension_observada": 0.0,
        "confianza_reportada": 1.0,
        "impacto_colaborativo": 0.0,
    }
    sistema.registrar_medicion(señales_internas1, señales_relacionales)

    # Segunda medición: self se dispara
    señales_internas2 = {
        "fatiga_fisica": 1.0,
        "carga_cognitiva": 1.0,
        "tension_emocional": 1.0,
        "señales_somaticas": 1.0,
        "motivacion_intrinseca": 0.0,
    }
    resultado = sistema.registrar_medicion(señales_internas2, señales_relacionales)

    assert resultado["estado_self"] == "RIESGO_SELF"
    assert "Reduce carga" in resultado["accion_self"]


def test_sistema_self_recuperado():
    conf = ConfiguracionEstandar(
        DELTA_ABS_SELF=0.01,
        ALPHA_SELF=0.5,
    )
    sistema = SistemaCoherenciaMaxima(config=conf)

    # Baseline alto
    señales_internas1 = {
        "fatiga_fisica": 0.9,
        "carga_cognitiva": 0.9,
        "tension_emocional": 0.9,
        "señales_somaticas": 0.9,
        "motivacion_intrinseca": 0.1,
    }
    señales_relacionales = {
        "feedback_directo": 0.0,
        "distancia_relacional": 0.0,
        "tension_observada": 0.0,
        "confianza_reportada": 1.0,
        "impacto_colaborativo": 0.0,
    }
    sistema.registrar_medicion(señales_internas1, señales_relacionales)

    # Segunda medición: mejora fuerte
    señales_internas2 = {
        "fatiga_fisica": 0.0,
        "carga_cognitiva": 0.0,
        "tension_emocional": 0.0,
        "señales_somaticas": 0.0,
        "motivacion_intrinseca": 1.0,
    }
    resultado = sistema.registrar_medicion(señales_internas2, señales_relacionales)

    assert resultado["estado_self"] == "SELF_RECUPERADO"
    assert "Puedes asumir algo más" in resultado["accion_self"]


def test_sistema_danando_contexto_y_mejorando():
    conf = ConfiguracionEstandar(
        DELTA_ABS_CONTEXTO=0.01,
        ALPHA_CONTEXTO=0.5,
    )
    sistema = SistemaCoherenciaMaxima(config=conf)

    señales_internas = {
        "fatiga_fisica": 0.5,
        "carga_cognitiva": 0.5,
        "tension_emocional": 0.5,
        "señales_somaticas": 0.5,
        "motivacion_intrinseca": 0.5,
    }

    # Primera medición: contexto neutro
    señales_relacionales1 = {
        "feedback_directo": 0.5,
        "distancia_relacional": 0.5,
        "tension_observada": 0.5,
        "confianza_reportada": 0.5,
        "impacto_colaborativo": 0.5,
    }
    sistema.registrar_medicion(señales_internas, señales_relacionales1)

    # Segunda: contexto alto, confianza baja -> DAÑANDO_CONTEXTO
    señales_relacionales2 = {
        "feedback_directo": 1.0,
        "distancia_relacional": 1.0,
        "tension_observada": 1.0,
        "confianza_reportada": 0.0,
        "impacto_colaborativo": 1.0,
    }
    resultado2 = sistema.registrar_medicion(señales_internas, señales_relacionales2)
    assert resultado2["estado_contexto"] == "DAÑANDO_CONTEXTO"

    # Tercera: contexto muy bajo -> CONTEXTO_MEJORADO
    señales_relacionales3 = {
        "feedback_directo": 0.0,
        "distancia_relacional": 0.0,
        "tension_observada": 0.0,
        "confianza_reportada": 1.0,
        "impacto_colaborativo": 0.0,
    }
    resultado3 = sistema.registrar_medicion(señales_internas, señales_relacionales3)
    assert resultado3["estado_contexto"] == "CONTEXTO_MEJORADO"

