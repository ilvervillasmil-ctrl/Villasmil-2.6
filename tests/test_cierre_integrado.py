import pytest
from villasmil_omega.respiro import evaluar_paz_sistematica
from villasmil_omega.cierre.cierre import CierreSistema
from villasmil_omega.cierre.invariancia import Invariancia

def test_activacion_paz_total():
    """Este test camina por todas las líneas que faltan."""
    # 1. Creamos un historial invariante (Paz)
    historial_estable = [0.95, 0.9501, 0.9499, 0.95, 0.95]
    
    # 2. Llamamos a la conexión en respiro (Limpia respiro.py 67-68)
    paz_detectada = evaluar_paz_sistematica(historial_estable)
    assert paz_detectada is True
    
    # 3. Validamos el objeto Cierre (Limpia cierre.py e invariancia.py)
    inv = Invariancia(ventana=5)
    cierre = CierreSistema(inv, historial_estable)
    assert cierre.evaluar() is True

def test_resistencia_al_cierre_falso():
    """Asegura que el sistema NO cierra si hay caos."""
    historial_caotico = [0.1, 0.9, 0.2, 0.8, 0.5]
    assert evaluar_paz_sistematica(historial_caotico) is False
