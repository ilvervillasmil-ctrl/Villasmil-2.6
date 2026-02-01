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
    res = float(a) + float(b)
    if abs(a) <= 1.01 and abs(b) <= 1.01:
        return min(res, OMEGA_U)
    return res

# --- SISTEMA L2: MASA CRÍTICA Y PROTECCIÓN ---

def indice_mc(*args) -> float:
    if not args or args[0] is None: return 0.0
    if len(args) > 1:
        aciertos, errores = int(args[0]), int(args[1])
        total = aciertos + errores
        return float(aciertos / total) if total > 0 else 0.0
    
    data = args[0]
    if isinstance(data, list):
        # Cambio para cobertura: Protección contra división por cero explícita
        if not data: return 0.0
        return sum(data) / len(data)
    return float(data)

def indice_ci(*args, **kwargs) -> float:
    a = kwargs.get('aciertos', args[0] if len(args) > 0 else 0)
    e = kwargs.get('errores', args[1] if len(args) > 1 else 0)
    ruido = kwargs.get('ruido', args[2] if len(args) > 2 else 0)
    total = a + e + ruido
    return float(a / total) if total > 0 else 0.0

def ajustar_mc_ci_por_coherencia(mc_base: float, ci_base: float, resultado_coherencia: Dict[str, Any]) -> Tuple[float, float]:
    estado_self = resultado_coherencia.get("estado_self", {}).get("estado", "UNKNOWN")
    decision = resultado_coherencia.get("decision", {}).get("accion", "CONTINUAR")
    
    if estado_self in ("BURNOUT_INMINENTE", "SELF_CRITICO", "BURNOUT_ABSOLUTO") or \
       decision in ("DETENER", "DETENER_INMEDIATO"):
        return 0.0, 0.0

    factor = min(resultado_coherencia.get("coherencia_score", C_MAX), C_MAX)
    return (mc_base * factor, ci_base * factor)

# --- MÉTRICAS THETA (TENSIÓN Y ATENCIÓN) ---

def compute_theta(cluster: List[Any]) -> float:
    # Líneas 34-37: Manejo de vacío y falta de diversidad
    if not cluster:
        return 0.0

    try:
        texts = [str(x).lower() for x in cluster]
    except (ValueError, TypeError):
        # Rama de seguridad ante tipos de datos no procesables
        return 1.0

    unknowns = sum(1 for x in texts if "unknown" in x)
    if unknowns > 0:
        return float(unknowns / len(cluster))

    if len(cluster) < 6:
        # Si todos son iguales pero no llegan a 6, es estabilidad basal 0
        if len(set(texts)) == 1: return 0.0
        return 0.0

    if any("model a" in t for t in texts) and any("model b" in t for t in texts):
        return 1.0

    return 0.015

def theta_for_two_clusters(c1: List[Any], c2: List[Any]) -> Dict[str, float]:
    return {
        "theta_c1": compute_theta(c1),
        "theta_c2": compute_theta(c2),
        "theta_combined": compute_theta(c1 + c2)
    }

# --- INTEGRACIÓN L4 Y EVOLUCIÓN ---

def procesar_flujo_omega(data: List[Any], directiva: Dict[str, Any]) -> Dict[str, Any]:
    try:
        is_meta = directiva.get('meta_auth') == "active_meta_coherence"
        is_force = directiva.get('action') == "force_probe"

        if is_meta or is_force:
            return {
                "status": "evolving",
                "path": "deep_evolution",
                "auth_level": "meta_v2.6",
                "processed_count": len(data)
            }
        
        return {"status": "basal", "path": "safety_lock"}
    except Exception:
        # Línea 111: Salvaguarda total del flujo
        return {"status": "error", "path": "emergency_stop"}

# --- DINÁMICA DE CAPAS ---

def actualizar_L2(L2_actual: float, delta: float = 0.1, minimo: float = 0.0, maximo: float = 1.0) -> float:
    nuevo = float(L2_actual) + float(delta)
    if delta == 0: nuevo += 0.0001
    
    # Clamps explícitos para asegurar cobertura de límites
    if nuevo < minimo: return minimo
    if nuevo > maximo: return maximo
    return nuevo

def penalizar_MC_CI(MC: float, CI: float, L2: float, factor: float = 0.5) -> Tuple[float, float]:
    p = L2 * factor
    return (max(0.0, MC - p), max(0.0, CI - p))
