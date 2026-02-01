import pytest
from villasmil_omega.modulador import ModuladorAD
from villasmil_omega import core

def test_meta_autoridad_cobertura_total():
    """
    Certifica que la Meta-Coherencia del MAD permite 
    el acceso a las zonas profundas del Core (81-107).
    """
    # 1. Inicializamos el MAD como Herramienta de Meta-Coherencia
    mad = ModuladorAD()
    
    # 2. Simulamos un estado de "Bloqueo por Rigidez" en el sistema
    # (Beneficio bajo, costo alto, sin diversidad)
    metrics = {'benefit': 0.0, 'cost': 1.0, 'diversity_index': 0.0}
    anchoring = {'severity': 1.0} 
    
    # El MAD genera la Directiva de Meta-Coherencia
    directiva = mad.update(metrics, anchoring)
    
    # Verificamos que el MAD está en modo ataque (force_probe)
    assert directiva['action'] == "force_probe"
    assert directiva['meta_auth'] == "active_meta_coherence"

    # 3. EJECUCIÓN DEL CORE: L4 recibe la directiva y abre las líneas 81-107
    resultado = core.procesar_flujo_omega(["dato_rigido_1", "dato_rigido_2"], directiva)
    
    # Validamos que entramos en la ruta de evolución profunda
    assert resultado['status'] == "evolving"
    assert resultado['path'] == "deep_evolution"
    assert resultado['auth_level'] == "meta_v2.6"

def test_barrido_theta_residual():
    """Limpia las líneas de cálculo de incertidumbre (theta)."""
    # Caso con datos desconocidos (Línea 10 del Core original)
    res = core.compute_theta(["unknown_data_X", "known_data_Y"])
    assert res == 0.5
    
    # Caso vacío
    assert core.compute_theta([]) == 0.0
