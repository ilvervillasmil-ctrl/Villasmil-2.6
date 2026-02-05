# Guía de Testing - Villasmil-Ω v2.6

**Testing Guide - Villasmil-Ω v2.6**

---

## 📋 Tabla de Contenidos / Table of Contents

1. [Estructura de Tests / Test Structure](#estructura-de-tests)
2. [Ejecutar Tests / Running Tests](#ejecutar-tests)
3. [Condiciones de Fallo Documentadas / Documented Failure Conditions](#condiciones-de-fallo)
4. [Ejemplos Automatizados / Automated Examples](#ejemplos-automatizados)
5. [Casos Borde Críticos / Critical Edge Cases](#casos-borde-críticos)
6. [Cobertura / Coverage](#cobertura)
7. [CI/CD](#cicd)

---

## Estructura de Tests

El repositorio contiene múltiples archivos de test organizados por funcionalidad:

### Tests Principales / Main Tests

- **`test_examples_automated.py`** - Tests con ejemplos cuantificables y salidas esperadas
- **`test_core_edges.py`** - Tests de casos borde para funciones core
- **`test_l2_model.py`** - Tests para el modelo L2
- **`test_nuclear_final_100.py`** - Suite completa de cobertura
- **`test_paz_absoluta.py`** - Tests de estados óptimos y paz

### Tests de Seguridad / Security Tests

- **`test_seguridad_hacker.py`** - Tests contra ataques adversariales
- **`test_a22_adversarial.py`** - Tests A2.2 de conflictos adversariales

### Tests de Cobertura / Coverage Tests

- **`test_cobertura_total.py`** - Cobertura total de funcionalidades
- **`test_apocalipsis_omega.py`** - Tests extremos y casos límite
- **`test_brutal_omega.py`** - Aniquilación total de branches

---

## Ejecutar Tests

### Localmente / Locally

```bash
# Desde la raíz del repositorio
cd /home/runner/work/Villasmil-2.6/Villasmil-2.6

# Ejecutar todos los tests
pytest tests/ -v

# Ejecutar con cobertura
pytest tests/ --cov=villasmil_omega --cov-report=term-missing

# Ejecutar tests específicos
pytest tests/test_examples_automated.py -v

# Ejecutar un test específico
pytest tests/test_examples_automated.py::TestIndiceMC::test_indice_mc_casos_cuantificables -v

# Ejecutar tests con parámetro específico
pytest tests/test_examples_automated.py -k "beta_cero"
```

### En CI (GitHub Actions)

Los tests se ejecutan automáticamente en cada:
- Push a `main` o `master`
- Pull Request a `main` o `master`

Ver: `.github/workflows/test.yml`

---

## Condiciones de Fallo

### 1. División por Cero (β = 0)

**Función afectada:** `indice_mc(a, b)`

**Condición:** Cuando `a + b = 0` (denominador es cero)

**Comportamiento esperado:** Retorna `0.0` (no lanza excepción)

**Ejemplo:**
```python
resultado = indice_mc(0, 0)
assert resultado == 0.0  # ✓ Pasa

resultado = indice_mc(5, 0)  
assert resultado == 0.0  # ✓ Pasa (total = 0)
```

**Falla si:**
- Lanza `ZeroDivisionError`
- Retorna `NaN` o `Inf`
- Retorna valor fuera de `[0, C_MAX]`

---

### 2. Valores No Finitos (NaN, Inf)

**Funciones afectadas:** `clamp()`, `suma_omega()`, `calcular_raiz_ritmo()`

**Condición:** Entrada contiene `NaN` o `±Inf`

**Comportamiento esperado:**
- `clamp(NaN)` → retorna `min_val`
- `clamp(Inf)` → retorna `min_val`
- `suma_omega(a, NaN)` → ignora el `NaN`, suma el otro valor
- `calcular_raiz_ritmo([..., NaN, ...])` → ignora valores no finitos

**Ejemplo:**
```python
import math

resultado = clamp(float('nan'), 0.0, 1.0)
assert resultado == 0.0  # ✓ Pasa

resultado = clamp(float('inf'), 0.0, 1.0)
assert resultado == 0.0  # ✓ Pasa

resultado = suma_omega(0.5, float('nan'))
assert resultado == 0.5  # ✓ Ignora NaN
```

**Falla si:**
- Retorna `NaN` o `Inf` en lugar de sanitizar
- Lanza excepción
- No ignora valores no finitos en listas

---

### 3. Listas Vacías

**Funciones afectadas:** `calcular_raiz_ritmo()`, `calcular_theta()`

**Condición:** Historial vacío o lista vacía

**Comportamiento esperado:**
- `calcular_raiz_ritmo([])` → `OMEGA_U` (máxima estabilidad por defecto)
- `calcular_theta([])` → `0.0` (sin tensión)

**Ejemplo:**
```python
from villasmil_omega.core import OMEGA_U

resultado = calcular_raiz_ritmo([])
assert resultado == OMEGA_U  # ✓ Pasa

resultado = calcular_theta([])
assert resultado == 0.0  # ✓ Pasa
```

**Falla si:**
- Lanza `IndexError` o excepción
- Retorna valor inesperado

---

### 4. Penalizaciones Negativas

**Función afectada:** `penalizar_MC_CI(MC, CI, L2, factor)`

**Condición:** `L2 * factor > MC` o `L2 * factor > CI`

**Comportamiento esperado:** Resultados clamped a `[0, C_MAX]` (no negativos)

**Ejemplo:**
```python
MC, CI = 0.2, 0.2
L2 = 1.0
factor = 1.0  # Penalización = 1.0 > 0.2

MC_result, CI_result = penalizar_MC_CI(MC, CI, L2, factor)
assert MC_result == 0.0  # ✓ Clamped a 0
assert CI_result == 0.0  # ✓ Clamped a 0
```

**Falla si:**
- Retorna valores negativos
- No respeta límite inferior de 0.0

---

### 5. Exceder OMEGA_U (Límite Universal)

**Funciones afectadas:** `clamp()`, `actualizar_L2()`, `calcular_raiz_ritmo()`

**Condición:** Valor calculado excede `OMEGA_U = 0.995`

**Comportamiento esperado:** Saturación en `OMEGA_U` (límite absoluto)

**Ejemplo:**
```python
from villasmil_omega.core import OMEGA_U

resultado = clamp(1.5, 0.0, 2.0)
assert resultado == OMEGA_U  # ✓ Saturation

resultado = actualizar_L2(0.9, delta=0.5, minimo=0.0, maximo=2.0)
assert resultado <= OMEGA_U  # ✓ No excede
```

**Falla si:**
- Retorna valor > `OMEGA_U`
- No respeta saturación universal

---

### 6. Conflictos Model A vs Model B

**Función afectada:** `calcular_theta(cluster)`

**Condición:** Cluster contiene "model a" y "model b" simultáneamente

**Comportamiento esperado:** `θ = 1.0` (tensión máxima)

**Ejemplo:**
```python
cluster = ["model a", "data", "model b", "more", "data", "here"]
resultado = calcular_theta(cluster)
assert resultado == 1.0  # ✓ Conflicto detectado
```

**Falla si:**
- No detecta conflicto
- Retorna `θ < 1.0`

---

### 7. Presencia de "Unknown"

**Función afectada:** `calcular_theta(cluster)`

**Condición:** Elementos con texto "unknown" en el cluster

**Comportamiento esperado:** `θ = count(unknown) / len(cluster)`

**Ejemplo:**
```python
cluster = ["unknown", "data1", "data2"]
resultado = calcular_theta(cluster)
assert abs(resultado - 0.333) < 0.01  # ✓ 1/3 ≈ 0.333

cluster = ["unknown", "unknown", "data1", "data2"]
resultado = calcular_theta(cluster)
assert abs(resultado - 0.5) < 0.01  # ✓ 2/4 = 0.5
```

**Falla si:**
- No cuenta unknowns correctamente
- Retorna proporción incorrecta

---

### 8. Invariancia (Estado de Paz)

**Función afectada:** `procesar_flujo_omega(data, directiva)`

**Condición:** Datos completamente estables (invariantes)

**Comportamiento esperado:** 
- `status = "basal"`
- `invariante = True`
- `path = "safety_lock"`
- No procesa (ahorra energía)

**Ejemplo:**
```python
data = [0.5, 0.5, 0.5, 0.5, 0.5]  # Completamente estable
resultado = procesar_flujo_omega(data, {})

# Puede detectar invariancia según el guardián
if resultado.get("invariante"):
    assert resultado["status"] == "basal"
    assert resultado["path"] == "safety_lock"
```

**Falla si:**
- No detecta invariancia cuando debería
- Procesa datos en estado de paz innecesariamente

---

### 9. Meta/Force Authorization

**Función afectada:** `procesar_flujo_omega(data, directiva)`

**Condición:** 
- `directiva["meta_auth"] = "active_meta_coherence"`, o
- `directiva["action"] = "force_probe"`

**Comportamiento esperado:**
- `status = "evolving"`
- `path = "deep_evolution"`
- `auth_level = "meta_v2.6"`

**Ejemplo:**
```python
data = [0.1, 0.2, 0.3]
directiva = {"meta_auth": "active_meta_coherence"}
resultado = procesar_flujo_omega(data, directiva)

assert resultado["status"] == "evolving"  # ✓
assert resultado["auth_level"] == "meta_v2.6"  # ✓
```

**Falla si:**
- No abre evolving con autorización correcta
- No reconoce meta_auth o force_probe

---

## Ejemplos Automatizados

### Test con Datos de Entrada/Salida Esperada

Los tests en `test_examples_automated.py` usan `@pytest.mark.parametrize` para definir múltiples casos con entradas y salidas esperadas:

```python
@pytest.mark.parametrize("aciertos,total,esperado", [
    (0, 0, 0.0),      # División por cero → 0.0
    (3, 4, 0.75),     # Caso normal: 3/4 = 0.75
    (1, 1, 1.0),      # Todos aciertos → 1.0 (pero clamped a C_MAX)
    (10, 100, 0.1),   # Proporción pequeña
    (50, 100, 0.5),   # Mitad
])
def test_indice_mc_casos_cuantificables(self, aciertos, total, esperado):
    resultado = indice_mc(aciertos, total)
    esperado_clamped = min(esperado, C_MAX)
    assert abs(resultado - esperado_clamped) < 1e-9
```

**Ventajas:**
- ✓ Cuantificable: cada caso tiene entrada/salida específica
- ✓ Automatizado: se ejecuta con `pytest`
- ✓ Documentado: el parámetro incluye descripción
- ✓ Verificable: compara resultado con esperado

---

## Casos Borde Críticos

### Resumen de Edge Cases

| Caso | Entrada | Salida Esperada | Falla Si |
|------|---------|-----------------|----------|
| β = 0 | `indice_mc(0, 0)` | `0.0` | Lanza excepción o retorna NaN |
| NaN | `clamp(NaN)` | `min_val` | Retorna NaN |
| Inf | `clamp(Inf)` | `min_val` | Retorna Inf |
| Lista vacía | `calcular_raiz_ritmo([])` | `OMEGA_U` | Lanza excepción |
| Penalización excesiva | `penalizar_MC_CI(0.1, 0.1, 1.0, 1.0)` | `(0.0, 0.0)` | Retorna negativos |
| Exceder OMEGA_U | `clamp(2.0, 0.0, 3.0)` | `OMEGA_U` | Retorna > OMEGA_U |
| Conflicto A vs B | `calcular_theta(["model a", ..., "model b"])` | `1.0` | No detecta conflicto |
| Unknown | `calcular_theta(["unknown", "a", "b"])` | `~0.333` | Proporción incorrecta |

---

## Cobertura

### Métricas Actuales

- **Total de tests:** 127+ (incluyendo nuevos tests automatizados)
- **Cobertura:** >93% de líneas en `villasmil_omega/`
- **Certificación:** SIL-4

### Ver Cobertura

```bash
# Generar reporte de cobertura
pytest --cov=villasmil_omega --cov-report=html

# Abrir reporte en navegador
# El reporte se genera en htmlcov/index.html
```

### Áreas Cubiertas

- ✓ `core.py` - Funciones principales (θ, L2, MC/CI, ritmo)
- ✓ `l2_model.py` - Modelo L2 completo
- ✓ `respiro.py` - Sistema de respiro temporal
- ✓ `modulador.py` - Modulador de coherencia
- ✓ `cierre/` - Sistema de cierre e invariancia
- ✓ `human_l2/` - Interfaz L2 humana

---

## CI/CD

### GitHub Actions Workflow

El repositorio incluye CI automatizado en `.github/workflows/test.yml`:

```yaml
name: Python tests

on:
  push:
    branches: [ "main", "master" ]
  pull_request:
    branches: [ "main", "master" ]

jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: "3.11"
    - name: Install dependencies
      run: |
        pip install pytest pytest-cov
    - name: Run tests with coverage
      run: |
        pytest --cov=villasmil_omega --cov-report=term-missing
```

### Verificar Status de CI

1. Ir a: https://github.com/ilvervillasmil-ctrl/Villasmil-2.6/actions
2. Seleccionar el workflow "Python tests"
3. Ver resultados de ejecución

### Badges de Status

Para añadir badge de CI al README:

```markdown
![Tests](https://github.com/ilvervillasmil-ctrl/Villasmil-2.6/workflows/Python%20tests/badge.svg)
```

---

## Mejores Prácticas

### Al Escribir Tests

1. **Usar nombres descriptivos:**
   ```python
   # ✓ Bueno
   def test_indice_mc_division_por_cero_retorna_cero():
   
   # ✗ Malo
   def test_mc_1():
   ```

2. **Documentar condiciones de fallo:**
   ```python
   """
   Falla si:
   - No maneja división por cero
   - Retorna NaN
   - Lanza excepción
   """
   ```

3. **Usar datos de entrada/salida esperada:**
   ```python
   @pytest.mark.parametrize("entrada,esperado", [
       (input1, output1),
       (input2, output2),
   ])
   ```

4. **Verificar múltiples propiedades:**
   ```python
   resultado = funcion(entrada)
   assert resultado == esperado  # Valor correcto
   assert 0.0 <= resultado <= 1.0  # Dentro de rango
   assert isinstance(resultado, float)  # Tipo correcto
   ```

### Al Ejecutar Tests

1. **Ejecutar tests antes de commit:**
   ```bash
   pytest tests/ -v
   ```

2. **Verificar cobertura regularmente:**
   ```bash
   pytest --cov=villasmil_omega
   ```

3. **Ejecutar tests específicos al desarrollar:**
   ```bash
   pytest tests/test_examples_automated.py -v
   ```

---

## Solución de Problemas

### Test Falla: ImportError

**Problema:** `ImportError: No module named 'villasmil_omega'`

**Solución:**
```bash
# Asegurar que estás en la raíz del repositorio
cd /home/runner/work/Villasmil-2.6/Villasmil-2.6

# Ejecutar con PYTHONPATH
PYTHONPATH=. pytest tests/
```

### Test Falla: AssertionError

**Problema:** `AssertionError: expected X, got Y`

**Solución:**
1. Ver el mensaje de error completo
2. Verificar que la función retorna el tipo correcto
3. Verificar que los datos de entrada son válidos
4. Revisar la documentación de la función

### Tests Pasan Localmente pero Fallan en CI

**Posibles causas:**
- Dependencias diferentes
- Versión de Python diferente
- Archivos temporales no commiteados

**Solución:**
1. Verificar `.github/workflows/test.yml`
2. Asegurar que todas las dependencias están especificadas
3. Probar con la misma versión de Python que CI

---

## Referencias

- **Repositorio:** https://github.com/ilvervillasmil-ctrl/Villasmil-2.6
- **Documentación principal:** [README.md](README.md)
- **Sesiones:** [SESION.md](SESION.md)
- **pytest Documentation:** https://docs.pytest.org/
- **Coverage.py:** https://coverage.readthedocs.io/

---

**Última actualización:** 2026-02-05  
**Versión:** 2.6.6  
**Certificación:** SIL-4
