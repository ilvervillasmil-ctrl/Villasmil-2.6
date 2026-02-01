import pytest
from villasmil_omega.modulador import ModuladorAD

def test_mad_logic_certification():
    # Inicializamos herramienta con delta 0.4
    mad = ModuladorAD(alpha=0.5, roi_low=0.2, rigidity_high=0.7, max_delta=0.4)
    
    # ESCENARIO A: Monitorización estable
    res = mad.update({'benefit': 0.8, 'cost': 0.1, 'entropy': 0.9})
    assert res['action'] == "monitor"

    # ESCENARIO B: Diagnóstico de Estancamiento
    metrics = {'benefit': 0.0, 'cost': 1.0, 'entropy': 0.0}
    
    # Iteración 1: 0.2 -> 0.6
    # Iteración 2: 0.6 -> 0.95 (alcanza el max_factor)
    for _ in range(2):
        res = mad.update(metrics)
    
    assert res['action'] == "force_probe"
    assert res['factor_exploration'] >= 0.9
    assert res['role'] == "system_adjustment_tool"
