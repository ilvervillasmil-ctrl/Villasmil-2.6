from dataclasses import dataclass
from typing import List

@dataclass
class Invariancia:
    epsilon: float = 1e-3
    ventana: int = 5

    def es_invariante(self, historial: List[float]) -> bool:
        """Si nada cambia, el sistema no tiene por qué seguir actuando."""
        if len(historial) < self.ventana:
            return False

        base = historial[-1]
        # Comprobamos si toda la ventana está dentro del épsilon de paz
        for v in historial[-self.ventana:]:
            if abs(v - base) > self.epsilon:
                return False
        return True
