import math
import pytest
from villasmil_omega import core

def test_calcular_raiz_ritmo_vacio():
    assert core.calcular_raiz_ritmo([]) == core.OMEGA_U
    assert core.calcular_raiz_ritmo([0.5]) == core.OMEGA_U

def test_calcular_raiz_ritmo_centro_pequena_variacion():
    centro = core.C_MAX / 2.0
    hist = [centro for _ in range(10)]
    assert core.calcular_raiz_ritmo(hist, centro=centro) == core.OMEGA_U

    hist2 = [centro + (0.01 if i % 2 == 0 else -0.01) for i in range(10)]
    ritmo = core.calcular_raiz_ritmo(hist2, centro=centro)
    assert 0.0 <= ritmo <= core.OMEGA_U
    assert ritmo < core.OMEGA_U

def test_rmse_handles_nonfinite_and_outliers():
    # Provide outliers and non-finite but expect function to handle gracefully
    hist = [0.5, 0.6, float('nan'), float('inf'), -1e6]
    ritmo = core.calcular_raiz_ritmo(hist)
    # ritmo must be finite and within bounds
    assert isinstance(ritmo, float)
    assert 0.0 <= ritmo <= core.OMEGA_U
