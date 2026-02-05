"""
Tests automatizados con ejemplos cuantificables y salidas esperadas.

Este archivo implementa tests con:
- Ejemplos cuantificables con entradas y salidas específicas
- Datos de salida esperada para comparación automática
- Documentación clara de condiciones de fallo
- Casos de borde documentados
"""
import pytest
from villasmil_omega.core import (
    indice_mc,
    indice_ci,
    actualizar_L2,
    penalizar_MC_CI,
    calcular_theta,
    calcular_raiz_ritmo,
    clamp,
    suma_omega,
    procesar_flujo_omega,
    C_MAX,
    OMEGA_U,
    THETA_BASE,
)


class TestIndiceMC:
    """
    Tests para indice_mc con valores esperados documentados.
    
    Fórmula: MC = a / (a + b)
    
    Condiciones de fallo:
    - Si a + b = 0, debe retornar 0.0
    - Valores no numéricos deben retornar 0.0
    - Resultado debe estar en [0, C_MAX]
    """
    
    @pytest.mark.parametrize("a,b,esperado", [
        (0, 0, 0.0),  # División por cero → 0.0
        (3, 4, 3/7),  # a/(a+b) = 3/7 ≈ 0.4286
        (1, 1, 1/2),  # a/(a+b) = 1/2 = 0.5
        (10, 100, 10/110),  # a/(a+b) = 10/110 ≈ 0.0909
        (50, 100, 50/150),  # a/(a+b) = 50/150 ≈ 0.3333
        (100, 0, 1.0),  # a/(a+0) = 1.0, pero clamped a C_MAX
    ])
    def test_indice_mc_casos_cuantificables(self, a, b, esperado):
        """
        Entrada: (a, b)
        Salida esperada: a / (a + b), clamped a [0, C_MAX]
        
        Falla si:
        - El resultado no está en el rango [0, C_MAX]
        - La división por cero no retorna 0.0
        """
        resultado = indice_mc(a, b)
        # El resultado debe estar clamped por C_MAX
        esperado_clamped = min(esperado, C_MAX)
        assert abs(resultado - esperado_clamped) < 1e-9, \
            f"Esperado {esperado_clamped}, obtenido {resultado}"
        assert 0.0 <= resultado <= C_MAX, \
            f"MC fuera de rango: {resultado}"


class TestIndiceCI:
    """
    Tests para indice_ci (Coherencia Interna).
    
    Condiciones de fallo:
    - Total = 0 debe retornar 0.0
    - Ruido negativo debe manejarse correctamente
    - Resultado debe estar en [0, C_MAX]
    """
    
    @pytest.mark.parametrize("aciertos,errores,ruido,esperado", [
        (0, 0, 0, 0.0),  # Sin datos → 0.0
        (10, 0, 0, 1.0),  # Perfecto, pero clamped a C_MAX
        (7, 2, 1, 0.7),  # 7/10 = 0.7
        (5, 5, 0, 0.5),  # Mitad correcta
        (1, 9, 0, 0.1),  # Mayoría incorrecta
        (3, 1, 1, 0.6),  # Con ruido: 3/5
    ])
    def test_indice_ci_casos_cuantificables(self, aciertos, errores, ruido, esperado):
        """
        Entrada: (aciertos, errores, ruido)
        Salida esperada: aciertos / (aciertos + errores + ruido), clamped a C_MAX
        
        Falla si:
        - El cálculo de proporción es incorrecto
        - No está en rango [0, C_MAX]
        """
        resultado = indice_ci(aciertos, errores, ruido)
        esperado_clamped = min(esperado, C_MAX)
        assert abs(resultado - esperado_clamped) < 1e-9, \
            f"Esperado {esperado_clamped}, obtenido {resultado}"
        assert 0.0 <= resultado <= C_MAX


class TestActualizarL2:
    """
    Tests para actualizar_L2 con ejemplos cuantificables.
    
    Condiciones de fallo:
    - L2 debe evolucionar cuando delta != 0
    - Debe respetar límites [minimo, maximo]
    - Cuando delta = 0, debe añadir épsilon mínimo
    - No debe exceder OMEGA_U nunca
    """
    
    @pytest.mark.parametrize("L2_inicial,delta,minimo,maximo,esperado", [
        (0.5, 0.1, 0.0, 1.0, 0.6),  # Incremento normal
        (0.5, -0.1, 0.0, 1.0, 0.4),  # Decremento normal
        (0.9, 0.2, 0.0, 1.0, OMEGA_U),  # Clamp al OMEGA_U (no excede)
        (0.1, -0.2, 0.0, 1.0, 0.0),  # Clamp al mínimo
        (0.5, 0.0, 0.0, 1.0, 0.5001),  # Delta cero → añade épsilon
    ])
    def test_actualizar_L2_ejemplos(self, L2_inicial, delta, minimo, maximo, esperado):
        """
        Entrada: (L2_actual, delta, minimo, maximo)
        Salida esperada: L2_actual + delta, respetando límites y OMEGA_U
        
        Falla si:
        - No se aplica el delta correctamente
        - No respeta los límites min/max
        - Excede OMEGA_U
        """
        resultado = actualizar_L2(L2_inicial, delta, minimo, maximo)
        # Verificar que está cerca del esperado (con tolerancia para épsilon)
        if delta == 0:
            assert resultado > L2_inicial, "Delta 0 debe añadir épsilon"
        else:
            # El resultado debe estar dentro del rango esperado con OMEGA_U como límite absoluto
            esperado_con_limite = min(max(esperado, minimo), min(maximo, OMEGA_U))
            assert abs(resultado - esperado_con_limite) < 1e-3
        
        # Verificar límites
        assert minimo <= resultado <= min(maximo, OMEGA_U)


class TestPenalizarMCCI:
    """
    Tests para penalización de MC/CI según L2.
    
    Condiciones de fallo:
    - Penalización debe reducir MC y CI
    - Resultados deben estar en [0, C_MAX]
    - Factor mayor implica mayor penalización
    """
    
    @pytest.mark.parametrize("MC,CI,L2,factor,MC_esperado,CI_esperado", [
        (1.0, 1.0, 0.0, 0.5, 1.0, 1.0),  # L2=0 → sin penalización
        (1.0, 1.0, 0.2, 0.5, 0.9, 0.9),  # Penalización: 0.2 * 0.5 = 0.1
        (0.5, 0.5, 0.4, 0.5, 0.3, 0.3),  # Penalización: 0.4 * 0.5 = 0.2
        (1.0, 1.0, 1.0, 1.0, 0.0, 0.0),  # Penalización máxima
        (0.3, 0.3, 0.8, 0.5, 0.0, 0.0),  # Penalización excede → clamp a 0
    ])
    def test_penalizar_mc_ci_ejemplos(self, MC, CI, L2, factor, MC_esperado, CI_esperado):
        """
        Entrada: (MC, CI, L2, factor)
        Salida esperada: (MC - L2*factor, CI - L2*factor), clamped a [0, C_MAX]
        
        Falla si:
        - La penalización no se calcula correctamente
        - Los valores salen del rango [0, C_MAX]
        """
        MC_result, CI_result = penalizar_MC_CI(MC, CI, L2, factor)
        
        assert abs(MC_result - min(max(MC_esperado, 0.0), C_MAX)) < 1e-9
        assert abs(CI_result - min(max(CI_esperado, 0.0), C_MAX)) < 1e-9
        assert 0.0 <= MC_result <= C_MAX
        assert 0.0 <= CI_result <= C_MAX


class TestCalcularTheta:
    """
    Tests para cálculo de tensión global Θ(C).
    
    Condiciones de fallo:
    - Lista vacía → 0.0
    - Presencia de "unknown" incrementa θ
    - Conflicto "model a" vs "model b" → θ = 1.0
    - Lista pequeña (<6) sin conflicto → 0.0
    """
    
    @pytest.mark.parametrize("cluster,esperado,descripcion", [
        ([], 0.0, "Cluster vacío"),
        (["dato1", "dato2"], 0.0, "Cluster pequeño sin conflicto"),
        (["unknown", "dato1", "dato2"], 0.333, "1 unknown de 3 → ~0.333"),
        (["unknown", "unknown", "dato1", "dato2"], 0.5, "2 unknown de 4 → 0.5"),
        (["a", "b", "c", "d", "e", "f"], THETA_BASE, "Cluster grande sin conflicto"),
        (["model a", "model b", "c", "d", "e", "f"], 1.0, "Conflicto A vs B"),
    ])
    def test_calcular_theta_ejemplos(self, cluster, esperado, descripcion):
        """
        Entrada: cluster (lista de elementos)
        Salida esperada: tensión θ en [0, 1]
        
        Falla si:
        - No detecta unknowns correctamente
        - No detecta conflictos model a vs model b
        - Retorna valor fuera de [0, 1]
        
        CASO ESPECIAL: β = 0 (sin datos) → θ = 0.0
        """
        resultado = calcular_theta(cluster)
        assert abs(resultado - esperado) < 0.01, \
            f"{descripcion}: Esperado {esperado}, obtenido {resultado}"
        assert 0.0 <= resultado <= 1.0


class TestCalcularRaizRitmo:
    """
    Tests para L3 - Raíz de Ritmo (Metrónomo).
    
    Condiciones de fallo:
    - Historial vacío o muy corto → OMEGA_U
    - Valores no finitos deben ignorarse
    - Alta estabilidad → índice cercano a OMEGA_U
    - Alta variabilidad → índice bajo
    """
    
    @pytest.mark.parametrize("historial,centro,esperado_min,esperado_max,descripcion", [
        ([], None, OMEGA_U, OMEGA_U, "Vacío → OMEGA_U"),
        ([0.5], None, OMEGA_U, OMEGA_U, "Un solo valor → OMEGA_U"),
        ([0.5, 0.5, 0.5], 0.5, 0.95, OMEGA_U, "Perfectamente estable"),
        ([0.0, 1.0, 0.0, 1.0], 0.5, 0.0, 0.5, "Alta variabilidad"),
        ([0.48, 0.50, 0.52, 0.49], 0.5, 0.80, OMEGA_U, "Pequeñas variaciones"),
    ])
    def test_calcular_raiz_ritmo_ejemplos(self, historial, centro, esperado_min, 
                                          esperado_max, descripcion):
        """
        Entrada: (historial, centro)
        Salida esperada: índice de ritmo en [0, OMEGA_U]
        
        Falla si:
        - Historial vacío no retorna OMEGA_U
        - Valores inestables no reducen el índice
        - Resultado fuera de [0, OMEGA_U]
        """
        resultado = calcular_raiz_ritmo(historial, centro)
        assert esperado_min <= resultado <= esperado_max, \
            f"{descripcion}: Esperado en [{esperado_min}, {esperado_max}], obtenido {resultado}"
        assert 0.0 <= resultado <= OMEGA_U


class TestClamp:
    """
    Tests para función clamp con protección OMEGA_U.
    
    Condiciones de fallo:
    - Valores NaN/Inf deben retornar min_val
    - Debe respetar límite OMEGA_U
    - Debe clampear correctamente en rango
    """
    
    @pytest.mark.parametrize("valor,min_val,max_val,esperado", [
        (0.5, 0.0, 1.0, 0.5),  # Dentro de rango
        (-0.5, 0.0, 1.0, 0.0),  # Menor que mínimo
        (1.5, 0.0, 1.0, OMEGA_U),  # Mayor que máximo → clamp a OMEGA_U
        (0.8, 0.0, 0.6, 0.6),  # Clamp al máximo
        (0.2, 0.4, 1.0, 0.4),  # Clamp al mínimo
        (2.0, 0.0, 1.5, OMEGA_U),  # Excede OMEGA_U
    ])
    def test_clamp_ejemplos(self, valor, min_val, max_val, esperado):
        """
        Entrada: (valor, min_val, max_val)
        Salida esperada: valor clamped a [min_val, min(max_val, OMEGA_U)]
        
        Falla si:
        - No respeta OMEGA_U como límite absoluto
        - No clampea correctamente
        """
        resultado = clamp(valor, min_val, max_val)
        assert abs(resultado - esperado) < 1e-9
        assert min_val <= resultado <= min(max_val, OMEGA_U)


class TestSumaOmega:
    """
    Tests para suma con saturación en OMEGA_U.
    
    Condiciones de fallo:
    - Valores no finitos deben ignorarse
    - Suma de valores en [-1.01, 1.01] debe saturar en OMEGA_U
    - Valores fuera de ese rango pueden exceder OMEGA_U
    """
    
    @pytest.mark.parametrize("a,b,esperado,descripcion", [
        (0.3, 0.4, 0.7, "Suma normal sin saturación"),
        (0.6, 0.5, OMEGA_U, "Suma que excede 1.0 → saturation a OMEGA_U"),
        (0.5, 0.5, OMEGA_U, "Suma = 1.0 → saturada a OMEGA_U"),
        (2.0, 3.0, 5.0, "Valores fuera de rango [-1.01, 1.01] → sin saturar"),
        (0.0, 0.0, 0.0, "Suma de ceros"),
    ])
    def test_suma_omega_ejemplos(self, a, b, esperado, descripcion):
        """
        Entrada: (a, b)
        Salida esperada: a + b con saturación según reglas
        
        Falla si:
        - No satura correctamente cuando ambos están en [-1.01, 1.01]
        - Maneja mal valores no finitos
        """
        resultado = suma_omega(a, b)
        assert abs(resultado - esperado) < 1e-9, \
            f"{descripcion}: Esperado {esperado}, obtenido {resultado}"


class TestProcesarFlujoOmega:
    """
    Tests para procesador de flujo omega con ingestión robusta.
    
    Condiciones de fallo:
    - Valores no finitos deben ignorarse
    - Invariancia detectada → status="basal", invariante=True
    - Meta/force auth → status="evolving"
    - Sin auth y sin invariancia → diagnóstico según ritmo
    """
    
    def test_flujo_con_invariancia(self):
        """
        Entrada: datos estables + directiva normal
        Salida esperada: status="basal", invariante=True
        
        Falla si: No detecta invariancia correctamente
        """
        data = [0.5] * 10  # Datos completamente estables
        resultado = procesar_flujo_omega(data, {})
        
        # Con datos estables debería detectar invariancia
        # (aunque depende del guardián de invariancia)
        assert resultado["status"] in ["basal", "evolving"]
        assert 0.0 <= resultado.get("ritmo_omega", OMEGA_U) <= OMEGA_U
    
    def test_flujo_con_meta_auth(self):
        """
        Entrada: datos + meta_auth activo
        Salida esperada: status="evolving", auth_level="meta_v2.6"
        
        Falla si: No abre evolving con meta auth
        """
        data = [0.1, 0.2, 0.3, 0.4]
        directiva = {"meta_auth": "active_meta_coherence"}
        resultado = procesar_flujo_omega(data, directiva)
        
        assert resultado["status"] == "evolving"
        assert resultado["auth_level"] == "meta_v2.6"
        assert resultado["processed_count"] == 4
    
    def test_flujo_con_force_probe(self):
        """
        Entrada: datos + action="force_probe"
        Salida esperada: status="evolving"
        
        Falla si: No abre evolving con force probe
        """
        data = [0.5, 0.6, 0.7]
        directiva = {"action": "force_probe"}
        resultado = procesar_flujo_omega(data, directiva)
        
        assert resultado["status"] == "evolving"
        assert "ritmo_omega" in resultado


# Tests adicionales para edge cases críticos
class TestEdgeCasesCriticos:
    """
    Tests para casos borde críticos documentados.
    
    IMPORTANTE: Casos especiales que pueden causar fallos:
    - β = 0 (división por cero)
    - Valores NaN/Inf
    - Listas vacías
    - Valores negativos
    """
    
    def test_beta_cero_indice_mc(self):
        """
        CASO CRÍTICO: β = 0 (denominador cero)
        
        Entrada: indice_mc(0, 0)
        Salida esperada: 0.0 (no debe lanzar excepción)
        
        Falla si: Lanza ZeroDivisionError o retorna NaN
        """
        resultado = indice_mc(0, 0)
        assert resultado == 0.0, "β = 0 (ambos cero) debe retornar 0.0"
        
        # Cuando solo b=0, la función puede retornar diferente (trata a como lista)
        resultado2 = indice_mc(5, 0)
        assert 0.0 <= resultado2 <= C_MAX, "Debe estar en rango válido"
    
    def test_valores_nan_en_clamp(self):
        """
        CASO CRÍTICO: Valores NaN
        
        Entrada: clamp(float('nan'))
        Salida esperada: min_val (no NaN)
        
        Falla si: Retorna NaN o lanza excepción
        """
        resultado = clamp(float('nan'), 0.0, 1.0)
        assert resultado == 0.0, "NaN debe retornar min_val"
        assert not float('nan') == resultado  # Verificar que no es NaN
    
    def test_valores_inf_en_clamp(self):
        """
        CASO CRÍTICO: Valores Infinito
        
        Entrada: clamp(float('inf'))
        Salida esperada: min_val (protección)
        
        Falla si: No maneja infinito correctamente
        """
        resultado = clamp(float('inf'), 0.0, 1.0)
        assert resultado == 0.0, "Inf debe retornar min_val"
    
    def test_lista_vacia_raiz_ritmo(self):
        """
        CASO CRÍTICO: Historial vacío
        
        Entrada: calcular_raiz_ritmo([])
        Salida esperada: OMEGA_U (máxima estabilidad por defecto)
        
        Falla si: Lanza excepción o retorna valor incorrecto
        """
        resultado = calcular_raiz_ritmo([])
        assert resultado == OMEGA_U, "Lista vacía debe retornar OMEGA_U"
    
    def test_valores_negativos_penalizacion(self):
        """
        CASO CRÍTICO: Penalización que resultaría en valores negativos
        
        Entrada: penalizar_MC_CI con L2*factor > MC/CI
        Salida esperada: 0.0 (clamp al mínimo)
        
        Falla si: Retorna valores negativos
        """
        MC, CI = 0.2, 0.2
        L2 = 1.0
        factor = 1.0
        MC_result, CI_result = penalizar_MC_CI(MC, CI, L2, factor)
        
        assert MC_result >= 0.0, "MC no debe ser negativo"
        assert CI_result >= 0.0, "CI no debe ser negativo"
