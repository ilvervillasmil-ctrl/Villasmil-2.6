import pytest
from villasmil_omega.modulador import ModuladorAD

def test_l4_influence_and_slew_rate():
    mad = ModuladorAD(base_factor=0.2)
    
    # Caso: Anclaje severo en L4
    metrics = {'benefit': 0.1, 'cost': 0.1, 'diversity_index': 0.2}
    anchoring = {'severity': 0.9, 'is_anchored': True}
    
    # Ejecutamos dos pasos para ver el Slew Rate en acción
    res1 = mad.update(metrics, anchoring)
    # factor: 0.2 -> debería subir máximo +0.15 = 0.35
    assert res1['factor_exploration'] <= 0.35
    
    res2 = mad.update(metrics, anchoring)
    # factor: 0.35 -> debería subir a ~0.50
    assert res2['factor_exploration'] > res1['factor_exploration']
    # r_thresh: debería estar bajando desde 0.95
    assert res2['r_thresh'] < 0.95
