import pytest
from villasmil_omega.modulador import ModuladorAD

def test_mad_logic_certification():
    mad = ModuladorAD(alpha=0.5, roi_low=0.2, rigidity_high=0.7)
    
    # ESCENARIO A: Normalidad
    res_normal = mad.update({'benefit': 0.8, 'cost': 0.1, 'entropy': 0.9})
    assert res_normal['action'] == "monitor"
    assert res_normal['factor_exploration'] == 0.2

    # ESCENARIO B: Estancamiento Crítico (Respuesta Inmediata)
    # Enviamos métricas de fallo total
    res_fail = mad.update({'benefit': 0.0, 'cost': 1.0, 'entropy': 0.0})
    
    assert res_fail['action'] == "force_probe"
    assert res_fail['factor_exploration'] == 0.95
    assert res_fail['role'] == "system_adjustment_tool"
