import pytest
from villasmil_omega.modulador import ModuladorAD

def test_mad_logic_certification():
    # Inicializamos herramienta con delta controlado
    mad = ModuladorAD(alpha=0.5, roi_low=0.2, rigidity_high=0.7, max_delta=0.2)
    
    # ESCENARIO A: Monitorización
    res = mad.update({'benefit': 0.8, 'cost': 0.1, 'entropy': 0.9})
    assert res['action'] == "monitor"

    # ESCENARIO B: Estancamiento. Debe subir gradualmente.
    metrics_stagnant = {'benefit': 0.0, 'cost': 1.0, 'entropy': 0.0}
    
    # Tras 3 iteraciones con max_delta=0.2, partiendo de 0.2, debería estar en ~0.8
    for _ in range(3):
        res = mad.update(metrics_stagnant)
    
    assert res['action'] == "force_probe"
    # Validamos que está en el rango de autoridad de la herramienta
    assert res['factor_exploration'] >= 0.75 
    assert res['role'] == "system_adjustment_tool"
