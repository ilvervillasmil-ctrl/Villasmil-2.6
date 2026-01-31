"""
Paquete villasmil_omega

Expone el núcleo core y el modelo L2 mejorado.
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

from . import l2_model

__all__ = [
    "run_core",
    "suma_omega",
    "indice_mc",
    "indice_ci",
    "actualizar_L2",
    "penalizar_MC_CI",
    "compute_theta",
    "theta_for_two_clusters",
    "l2_model",
]
