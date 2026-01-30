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


if __name__ == "__main__":
    run_core()
