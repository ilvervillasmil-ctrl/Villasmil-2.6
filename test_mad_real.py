import pytest
from villasmil_omega.modulador import ModuladorAD

def test_mad_logic_certification():
    # Inicializamos con los defaults que definimos
    mad = ModuladorAD(alpha=0.2, roi_low=0.2, rigidity_high=0.7)
    mad.cooldown = 0  # Eliminamos el tiempo para poder testear ciclos rápidos

    # ESCENARIO A: Sistema Saludable (Buen ROI, Alta Entropía)
    metrics_good = {'benefit': 0.9, 'cost': 0.1, 'entropy': 0.8}
    res_good = mad.update(metrics_good)
    assert res_good['action'] == "monitor"
    assert res_good['factor_exploration'] == 0.2

    # ESCENARIO B: Estancamiento (Bajo ROI, Alta Rigidez/Baja Entropía)
    # Simulamos varias iteraciones para que la EWMA detecte la tendencia
    metrics_stagnant = {'benefit': 0.05, 'cost': 0.6, 'entropy': 0.1}
    for _ in range(10):
        res_stagnant = mad.update(metrics_stagnant)
    
    # Aquí el MAD debe "gritar" que necesitamos explorar (Líneas 33-38)
    assert res_stagnant['action'] == "force_probe"
    assert res_stagnant['factor_exploration'] == 0.8
    assert "Estancado" in res_stagnant['reason']
