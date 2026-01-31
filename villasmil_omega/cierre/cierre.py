from dataclasses import dataclass
from villasmil_omega.cierre.invariancia import Invariancia

@dataclass
class CierreSistema:
    invariancia: Invariancia
    historial_score: list

    def evaluar(self) -> bool:
        """El cierre no es ganar, es dejar de gastar energía."""
        return self.invariancia.es_invariante(self.historial_score)
