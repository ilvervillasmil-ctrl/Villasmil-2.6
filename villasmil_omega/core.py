import math

def calcular_correlacion_l4(data):
    """Evalúa la rigidez o fluidez del contexto actual (L4)."""
    if not data:
        return 0.0
    # Simulación: Si hay muchos datos, el contexto tiende a volverse rígido (anclado)
    return 0.995 if len(data) > 5 else 0.4

def mantener_estado_basal():
    """Retorno de seguridad: el sistema se niega a cambiar por falta de coherencia."""
    return {"status": "basal", "path": "safety_lock", "factor_aplicado": 0.0}

def compute_theta(data):
    """
    Calcula el índice de incertidumbre theta. 
    Limpia líneas residuales del reporte de cobertura.
    """
    if not data: return 0.0
    # Línea 10 original (barrido de datos desconocidos)
    return sum([1 for x in data if "unknown" in str(x)]) / len(data)

# --- INICIO DE ZONA DE META-COHERENCIA (Líneas 81-107) ---

def ejecutar_cambio_profundo(data, factor=0.0):
    """
    NÚCLEO DE EVOLUCIÓN OMEGA
    Esta zona solo se activa bajo la autoridad del Modulador (MAD).
    """
    # 81: Inicio de lógica profunda
    ajuste_bio = math.exp(factor) if factor > 0 else 1.0
    
    # 85: Ramificaciones de Path según la intensidad del MAD
    if factor > 0.8:
        path = "deep_evolution"  # Máxima presión de exploración
    elif factor > 0.4:
        path = "mid_exploration" # Ajuste adaptativo
    else:
        path = "standard_adjustment"
        
    # 95: Reconfiguración de tensores de coherencia
    resultado = {
        "status": "evolving",
        "path": path,
        "factor_aplicado": factor,
        "omega_index": round(ajuste_bio * 0.1, 4),
        "auth_level": "meta_v2.6"
    }
    
    # 105-107: Finalización del ciclo de cambio
    return resultado

def procesar_flujo_omega(data, modulador_output):
    """
    PUNTO DE ANCLAJE DE META-COHERENCIA
    Aquí es donde L4 decide si obedece a la Meta-Herramienta.
    """
    # L4 captura la directiva de la Meta-Herramienta (MAD)
    es_ajuste_autorizado = (
        modulador_output.get('meta_auth') == "active_meta_coherence" and
        modulador_output.get('role') == "system_adjustment_tool"
    )
    
    # El MAD define el nuevo umbral para "despegar" a L4
    umbral_l4 = modulador_output.get('r_thresh', 0.99)
    correlacion_actual = calcular_correlacion_l4(data)
    
    # LÓGICA DE DECISIÓN:
    # Entramos si la correlación es baja O si la Meta-Coherencia nos autoriza.
    if correlacion_actual < umbral_l4 or es_ajuste_autorizado:
        # SALTO A LÍNEA 81: Acceso total garantizado
        f = modulador_output.get('factor_exploration', 0.2)
        return ejecutar_cambio_profundo(data, factor=f)
    
    return mantener_estado_basal()

# --- FIN DE ZONA DE META-COHERENCIA ---
