from dataclasses import dataclass
from typing import List

@dataclass
class Invariancia:
    epsilon: float = 1e-3
    ventana: int = 5

    def es_invariante(self, historial: List[float]) -> bool:
        """
        Si nada cambia, el sistema no tiene por qué seguir actuando.
        Certifica la paz del sistema bajo un umbral épsilon.
        """
        # Rama 1: Ventana insuficiente (Missing 16)
        # Se activa cuando el historial es más corto que el parámetro 'ventana'.
        if len(historial) < self.ventana:
            return False

        base = historial[-1]
        
        # Rama 2: Comprobación de estabilidad (Missing 25)
        # Comprobamos si toda la ventana está dentro del épsilon de paz.
        for v in historial[-self.ventana:]:
            if abs(v - base) > self.epsilon:
                # Rama 3: Ruptura de invariancia detectada.
                # Si un solo valor escapa del épsilon, el sistema debe seguir actuando.
                return False
                
        # Rama 4: Éxito de invariancia.
        # Todo el historial reciente está en calma.
        return True
