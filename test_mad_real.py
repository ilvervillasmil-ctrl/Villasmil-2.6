import pytest
from villasmil_omega.modulador import ModuladorAD

def test_mad_logic_certification():
    # Inicializamos con parámetros para respuesta rápida
    mad = ModuladorAD(alpha=0.5, roi_low=0.2, rigidity_high=0.7)
    mad.cooldown = 0 

    # ESCENARIO A: Funcionamiento Normal (Monitor)
    metrics_good = {'benefit': 0.8, 'cost': 0.1, 'entropy': 0.9}
    res_good = mad.update(metrics_good)
    assert res_good['action'] == "monitor"

    # ESCENARIO B: Estancamiento (Force Probe)
    # Forzamos la caída de ROI y el aumento de Rigidez
    metrics_stagnant = {'benefit': 0.01, 'cost': 0.8, 'entropy': 0.05}
    
    # Iteramos para que la EWMA absorba el estado de estancamiento
    for _ in range(5):
        res_stagnant = mad.update(metrics_stagnant)
    
    assert res_stagnant['action'] == "force_probe"
    assert res_stagnant['factor_exploration'] == 0.8
    # Corrección de minúsculas para evitar el AssertionError anterior
    assert "estancado" in res_stagnant['reason'].lower()
