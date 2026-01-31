"""
Paquete villasmil_omega

Exporta las funciones principales de core.
"""

from .core import (
    run_core,
    suma_omega,
    indice_mc,
    indice_ci,
    actualizar_L2,
    penalizar_MC_CI,
    compute_theta,
    theta_for_two_clusters,
)

__all__ = [
    "run_core",
    "suma_omega",
    "indice_mc",
    "indice_ci",
    "actualizar_L2",
    "penalizar_MC_CI",
    "compute_theta",
    "theta_for_two_clusters",
]
