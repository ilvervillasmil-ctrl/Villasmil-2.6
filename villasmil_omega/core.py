"""
Villasmil-Ω v2.6 Core Module
Author: Ilver Villasmil – The Arquitecto
"""


def run_core():
    """
    Entry point for basic tests.
    Solo imprime el banner del módulo.
    """
    print("Villasmil-Ω v2.6 Core Module")
    print("Author: Ilver Villasmil – The Arquitecto")
    print("Module loaded successfully ✓")


def suma_omega(a, b):
    """
    Suma básica de prueba para Villasmil-Ω.
    """
    return a + b


def indice_mc(aciertos, errores):
    """
    Índice MC muy simple: aciertos / (aciertos + errores).
    Devuelve un número entre 0 y 1.
    """
    total = aciertos + errores
    if total == 0:
        return 0.0
    return aciertos / total


def indice_ci(aciertos, errores, ruido):
    """
    CI simple: 1 - errores / (aciertos + errores + ruido).
    Si no hay datos (todo 0), devuelve 0.0.
    """
    total = aciertos + errores + ruido
    if total == 0:
        return 0.0
    return 1.0 - (errores / total)


# --- Dynamic L2 control (Villasmil-Ω v2.6) ---


def actualizar_L2(L2_actual, k=0.25, L2_opt=0.125):
    """
    Actualización dinámica de L2 según:
    L2_nuevo = L2_actual + k * (L2_opt - L2_actual)

    Parámetros:
        L2_actual: valor actual de L2
        k: tasa de corrección (0 < k <= 1), por defecto 0.25
        L2_opt: valor óptimo calibrado (0.125 en v2.6)
    """
    return L2_actual + k * (L2_opt - L2_actual)


def penalizar_MC_CI(MC, CI, L2, L2_opt=0.125, alpha=0.5, beta=0.5):
    """
    Aplica penalizaciones a MC y CI cuando L2 se desvía de L2_opt:

        MC_pen = MC * (1 - alpha * |L2 - L2_opt|)
        CI_pen = CI * (1 - beta  * |L2 - L2_opt|)

    Devuelve (MC_pen, CI_pen).
    """
    delta = abs(L2 - L2_opt)
    factor_MC = 1.0 - alpha * delta
    factor_CI = 1.0 - beta * delta
    return MC * factor_MC, CI * factor_CI
