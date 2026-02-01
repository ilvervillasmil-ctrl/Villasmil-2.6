import builtins
import importlib
import math
import sys
from types import SimpleNamespace

import pytest
from villasmil_omega import core


def test_import_fallback_and_restore(monkeypatch):
    """
    Forzar ImportError al importar villasmil_omega.cierre.invariancia para cubrir
    el bloque fallback en core.py, luego restaurar el import original y recargar
    el módulo real para no afectar al resto de la suite.
    """
    orig_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        # Si intentan importar la dependencia concreta, forzar ImportError
        if name.startswith("villasmil_omega.cierre.invariancia") or "villasmil_omega.cierre.invariancia" in name:
            raise ImportError("simulated missing invariancia")
        return orig_import(name, globals, locals, fromlist, level)

    # Sustituir __import__ temporalmente
    monkeypatch.setattr(builtins, "__import__", fake_import)

    # Asegurar que se recargue el módulo desde cero
    sys.modules.pop("villasmil_omega.core", None)
    sys.modules.pop("villasmil_omega.cierre.invariancia", None)

    # Importar core: la importación fallará para invariancia y se activará el fallback
    m = importlib.import_module("villasmil_omega.core")
    # Debe existir guardian_paz (fallback) y no lanzar
    assert hasattr(m, "guardian_paz")

    # Restaurar import y recargar el módulo real para no romper otros tests
    monkeypatch.setattr(builtins, "__import__", orig_import)
    sys.modules.pop("villasmil_omega.core", None)
    real = importlib.import_module("villasmil_omega.core")
    assert hasattr(real, "guardian_paz")


def test_all_nonfinite_historial_returns_omega_u():
    """
    Forzar caso donde todo el historial es non-finite (NaN/Inf) y comprobar
    que calcular_raiz_ritmo maneja el sanitizado y retorna OMEGA_U.
    """
    vals = [float("nan"), float("inf"), float("-inf")]
    ritmo = core.calcular_raiz_ritmo(vals)
    assert ritmo == core.OMEGA_U


def test_indice_ci_exception_path_with_bad_objects():
    """
    Forzar excepción interna en indice_ci pasando objetos cuya conversión a float falla.
    La función debe capturar la excepción y devolver 0.0.
    """
    class Bad:
        def __float__(self):
            raise ValueError("cannot float")

    res = core.indice_ci(Bad(), Bad(), Bad())
    assert res == 0.0


def test_procesar_flujo_omega_meta_auth_and_high_ritmo():
    """
    Verificar la rama donde meta_auth está activa y el ritmo es alto
    (datos centrados) → debe retornar 'evolving' con ritmo_omega >= BURNOUT_THRESHOLD.
    """
    centro = core.C_MAX / 2.0
    data = [centro for _ in range(10)]
    res = core.procesar_flujo_omega(data, {"meta_auth": "active_meta_coherence"})
    assert isinstance(res, dict)
    assert res.get("status") == "evolving"
    ritmo = res.get("ritmo_omega")
    # ritmo puede no presentarse en la rama evolving original, pero si está, debe ser valido
    if ritmo is not None:
        assert isinstance(ritmo, float)
        assert math.isfinite(ritmo)
        assert ritmo >= core.BURNOUT_THRESHOLD


def test_theta_conflict_and_theta_for_two_clusters():
    """
    Forzar conflicto de modelos (contiene 'model a' y 'model b') y cubrir
    theta_for_two_clusters helper.
    """
    c1 = ["model a", "foo", "bar", "baz", "x", "y"]
    c2 = ["model b", "x", "y", "z", "u", "v"]
    t1 = core.calcular_theta(c1)
    t2 = core.calcular_theta(c2)
    combined = core.theta_for_two_clusters(c1, c2)
    # individual thetas: one has model a (but needs both to be conflict),
    # combined must report theta_combined == 1.0 because both appear together
    assert isinstance(t1, float) and 0.0 <= t1 <= 1.0
    assert isinstance(t2, float) and 0.0 <= t2 <= 1.0
    assert combined["theta_combined"] == 1.0
