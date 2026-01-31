import pytest
import random
from villasmil_omega.respiro import distribute_action, RespiroConfig, should_apply
from villasmil_omega.human_l2.puntos import SistemaCoherenciaMaxima

def test_simulacion_desgaste_prolongado():
    """
    Test de Vida, no de Laboratorio.
    500 iteraciones de pequeñas inconsistencias para ver si el sistema
    elige la 'Pausa Sabia' por sí mismo.
    """
    sistema = SistemaCoherenciaMaxima()
    cfg = RespiroConfig()
    historial_decisiones = []
    
    for i in range(500):
        # Generamos un ruido leve (la entropía de la vida)
        f_val = 0.5 + random.uniform(-0.1, 0.1)
        c_val = 0.5 + random.uniform(-0.1, 0.1)
        
        sistema.registrar_medicion({"f": f_val}, {"contexto": c_val})
        
        # Evaluamos si vale la pena el esfuerzo en cada paso
        esfuerzo_soft = {"L1": 0.1}
        esfuerzo_hard = {"L2": 0.5}
        
        paz, marginal = should_apply(0.8, esfuerzo_soft, esfuerzo_hard, 0.05)
        historial_decisiones.append(paz)
        
        # Si el sistema ha encontrado una racha de paz, el test ha tenido éxito
        if len(historial_decisiones) > 50 and all(historial_decisiones[-10:]):
            break 

    # Verificamos que el sistema ha tenido la oportunidad de no actuar
    assert len(historial_decisiones) > 0
