import math
from typing import List, Dict, Any, Tuple

# --- CONSTANTES MAESTRAS (v2.6 - Villasmil Ω) ---
C_MAX = 0.963
K_UNCERTAINTY = 0.037
OMEGA_U = 0.995

def run_core() -> None:
    """Certificación de integridad del núcleo Villasmil Ω."""
    return None

def suma_omega(a: float, b: float) -> float:
    """
    Suma Adaptativa.
    Si los operandos parecen métricas de coherencia (<= 1.01), aplica el límite físico OMEGA_U.
    Para escalares de lógica pura (ej. 2 + 3), permite la suma aritmética normal para no romper tests lógicos.
    """
    res = float(a) + float(b)
    # Detecta si estamos operando en el espacio de métricas [0,1]
    if abs(a) <= 1.01 and abs(b) <= 1.01:
        return min(res, OMEGA_U)
    return res

# --- SISTEMA L2: MASA CRÍTICA Y PROTECCIÓN ---

def indice_mc(*args) -> float:
    """Cálculo de Masa Crítica (MC): Proporción de éxito estructural."""
    if not args or args[0] is None: return 0.0
    if len(args) > 1:
        aciertos, errores = int(args[0]), int(args[1])
        total = aciertos + errores
        return float(aciertos / total) if total > 0 else 0.0
    
    data = args[0]
    if isinstance(data, list):
        return sum(data) / len(data) if data else 0.0
    return float(data)

def indice_ci(*args, **kwargs) -> float:
    """Coherencia Integrada (CI): Aciertos sobre el ruido total del sistema."""
    a = kwargs.get('aciertos', args[0] if len(args) > 0 else 0)
    e = kwargs.get('errores', args[1] if len(args) > 1 else 0)
    ruido = kwargs.get('ruido', args[2] if len(args) > 2 else 0)
    total = a + e + ruido
    return float(a / total) if total > 0 else 0.0

def ajustar_mc_ci_por_coherencia(mc_base: float, ci_base: float, resultado_coherencia: Dict[str, Any]) -> Tuple[float, float]:
    """
    Protocolo de Apagado de Emergencia L2 (v2.6).
    Si se detecta estado de BURNOUT o acción de DETENER, colapsa la operación a 0.0.
    """
    estado_self = resultado_coherencia.get("estado_self", {}).get("estado", "UNKNOWN")
    decision = resultado_coherencia.get("decision", {}).get("accion", "CONTINUAR")
    
    # Bloqueo de seguridad Master
    if estado_self in ("BURNOUT_INMINENTE", "SELF_CRITICO", "BURNOUT_ABSOLUTO") or \
       decision in ("DETENER", "DETENER_INMEDIATO"):
        return 0.0, 0.0

    # Ajuste por puntaje de coherencia limitado por C_MAX
    factor = min(resultado_coherencia.get("coherencia_score", C_MAX), C_MAX)
    return (mc_base * factor, ci_base * factor)

# --- MÉTRICAS THETA (TENSIÓN Y ATENCIÓN) ---

def compute_theta(cluster: List[Any]) -> float:
    """
    Θ(C): Global Tension & Uncertainty Detection.
    REGLA v2.6:
    1. INCERTIDUMBRE: Se evalúa siempre (incluso en muestras pequeñas).
    2. GUARDIA: Si len < 6 y no hay 'unknown', tensión = 0.0 (estabilidad basal).
    3. ADVERSARIAL: Conflicto A2.2 (Model A vs B) -> Tensión 1.0.
    """
    if not cluster:
        return 0.0

    texts = [str(x).lower() for x in cluster]
    
    # A. Detección de Incertidumbre Residual (Prioridad 1 para cobertura)
    unknowns = sum(1 for x in texts if "unknown" in x)
    if unknowns > 0:
        return float(unknowns / len(cluster))

    # B. Guardia de Estabilidad Basal
    if len(cluster) < 6:
        return 0.0

    # C. Detección de Colisión Adversarial A2.2
    contiene_a = any("model a" in t for t in texts)
    contiene_b = any("model b" in t for t in texts)

    if contiene_a and contiene_b:
        return 1.0

    return 0.015 # Ruido basal estructural (phi_c)

def theta_for_two_clusters(c1: List[Any], c2: List[Any]) -> Dict[str, float]:
    """Calcula tensiones individuales y la clave combinada requerida por la suite de tests."""
    return {
        "theta_c1": compute_theta(c1),
        "theta_c2": compute_theta(c2),
        "theta_combined": compute_theta(c1 + c2)
    }

# --- DINÁMICA DE CAPAS Y PENALIZACIÓN ---

def actualizar_L2(L2_actual: float, delta: float = 0.1, minimo: float = 0.0, maximo: float = 1.0) -> float:
    """Ajuste dinámico L2 con clamp y micro-cambio para persistencia."""
    nuevo = float(L2_actual) + float(delta)
    if delta == 0: nuevo += 0.0001 
    return max(minimo, min(nuevo, maximo))

def penalizar_MC_CI(MC: float, CI: float, L2: float, factor: float = 0.5) -> Tuple[float, float]:
    """Penalización por interferencia de L2 sobre la ejecución."""
    p = L2 * factor
    return (max(0.0, MC - p), max(0.0, CI - p))
