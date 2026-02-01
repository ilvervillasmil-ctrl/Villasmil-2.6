import pytest
from villasmil_omega import l2_model, core

def test_ataque_paradoja_l2():
    """
    ATAQUE: Paradoja de Identidad.
    MC=1.0 (Éxito total) vs CI=0.0 (Nula coherencia).
    Busca activar las líneas de 'ajuste de emergencia' en l2_model.py.
    """
    # Intentamos forzar la lógica de integración de l2_model
    # Si el modelo tiene una función de 'update' o 'step', la atacamos con la paradoja
    if hasattr(l2_model, 'L2Model'):
        model = l2_model.L2Model()
        # Inyectamos el estado contradictorio
        resultado = model.update(mc=1.0, ci=0.0, contexto="adversarial")
        
        # El sistema debería detectar que un MC alto con CI cero es una anomalía
        # y aplicar una penalización drástica (Líneas 92-96)
        assert resultado.estabilidad < 0.5, "VULNERABILIDAD: L2 aceptó una paradoja sin penalizar"

def test_ataque_shadow_data():
    """
    ATAQUE: Shadow Data (Datos Sombra).
    Envía una señal de 1.01 (ligeramente por encima del límite) 
    para ver si el redondeo rompe la invarianza.
    """
    # Atacamos la suma omega con el valor crítico de transición
    # Esto busca forzar errores de precisión en el Core
    res = core.suma_omega(0.505, 0.505)
    assert res <= 0.995, "FALLO DE CLAMP: El sistema permitió fuga de energía > OMEGA_U"

def test_ataque_induccion_error_l2():
    """
    ATAQUE: Inducción de Recursión.
    Busca que l2_model se llame a sí mismo hasta agotar el stack 
    si las líneas 49-50 no tienen guardia.
    """
    # Si existe una función que procesa deltas, enviamos el delta más pequeño posible
    # para forzar miles de iteraciones de ajuste.
    if hasattr(l2_model, 'ajustar'):
        # Forzamos al sistema a procesar un ajuste infinitesimal pero infinito
        for _ in range(100):
            l2_model.ajustar(0.0000000001)
