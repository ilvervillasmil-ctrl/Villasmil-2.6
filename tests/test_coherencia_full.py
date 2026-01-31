def test_limites_biologicos_corregidos():
    """Resuelve la paradoja: Self (0.05) vs Contexto (0.075)"""
    # Validamos los pisos mínimos reales del sistema
    assert compute_L2_self({}) == 0.05 
    assert compute_L2_contexto({}) == 0.075 # Aquí estaba la paradoja
    
    # Caso de historial vacío para cubrir línea 281
    sistema = SistemaCoherenciaMaxima()
    sistema.history = []
    assert sistema.get_estado_actual() is None
    
    # Forzar penalización total para cubrir líneas 92-97 de core.py
    # Usamos un estado que dispare el bloqueo absoluto
    res_bloqueo = {
        "estado_self": {"estado": "BURNOUT_INMINENTE"},
        "estado_contexto": {"estado": "CONTEXTO_ESTABLE"},
        "coherencia_score": 0.0,
        "decision": {"accion": "DETENER_INMEDIATO"}
    }
    mc, ci = ajustar_mc_ci_por_coherencia(0.5, 0.5, res_bloqueo)
    assert mc == 0.0 and ci == 0.0
