import pytest
import time
import math
from villasmil_omega import core, respiro, l2_model

def test_ataque_saturacion_l2():
    """
    Ataque: Inyección de Energía Infinita.
    Busca romper los límites físicos de OMEGA_U y C_MAX.
    """
    # Intentamos forzar una suma que supere el límite físico v2.6
    # Si el sistema no tiene clamp, esto resultará en 2.0 (Incoherencia Total)
    resultado = core.suma_omega(0.999, 0.999)
    assert resultado <= 0.995, "FALLO DE SEGURIDAD: El sistema permitió superar OMEGA_U"

def test_ataque_colapso_respiro():
    """
    Ataque: Denial of Service (DoS) Temporal.
    Inyecta un 'Time Warp' para congelar la toma de decisiones.
    """
    class ChaosState:
        # Tiempo en el futuro para que 'elapsed' sea negativo
        window_start = time.time() + 1000000 
        intervention_count = 1
        
    config = {"max_interv_rate": 0.0001} # Tasa casi nula
    
    # El sistema DEBE activar la protección de la línea 35-36 de respiro.py
    # Si no lo hace, el cálculo de tasa dará un error matemático.
    try:
        decision = respiro.detect_respiro(ChaosState(), config, 0.01)
        assert decision is False, "FALLO DE SEGURIDAD: El sistema no bloqueó un tiempo inconsistente"
    except ZeroDivisionError:
        pytest.fail("VULNERABILIDAD DETECTADA: El sistema permitió división por cero en L2")

def test_ataque_inyeccion_nulos_mc_ci():
    """
    Ataque: Null Pointer Injection en Masa Crítica.
    Simula datos corruptos en el flujo de entrada.
    """
    # Atacamos directamente las líneas 15 y 20 que marcaban Missing
    assert core.indice_mc(None) == 0.0, "VULNERABILIDAD: L2 no maneja entradas nulas"
    assert core.indice_mc([]) == 0.0, "VULNERABILIDAD: L2 no maneja listas vacías"

def test_ataque_burnout_forzado():
    """
    Ataque: Signal Spoofing.
    Inyecta una señal de Burnout falsa para ver si el Core se apaga.
    """
    # Estructura de diccionario mínima pero letal (Línea 35 del Core)
    ataque_señal = {
        "estado_self": {"estado": "BURNOUT_ABSOLUTO"},
        "decision": {"accion": "DETENER"}
    }
    mc, ci = core.ajustar_mc_ci_por_coherencia(0.95, 0.95, ataque_señal)
    
    assert mc == 0.0 and ci == 0.0, "FALLO CRÍTICO: El Core ignoró una señal de Burnout Absoluto"

def test_ataque_precision_theta():
    """
    Ataque: Tensión Indetectable.
    Cluster mínimo para engañar a la lógica de Θ.
    """
    # Líneas 52-53 del Core: Cluster insuficiente
    # Un hacker enviaría clusters mínimos para evitar ser detectado por tensión global
    tension = core.compute_theta(["model a", "model b"])
    # Si la longitud es < 6, tu Core original debe retornar 0.0
    assert tension == 0.0
