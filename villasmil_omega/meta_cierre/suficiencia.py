from dataclasses import dataclass

@dataclass
class EstadoSuficiencia:
    coherencia_actual: float
    delta_presion: float
    delta_retiro: float

    def es_suficiente(self, epsilon: float = 0.01) -> bool:
        # Si la variación bajo estrés y alivio es mínima, hay estabilidad sólida.
        return (abs(self.delta_presion) < epsilon and 
                abs(self.delta_retiro) < epsilon)
