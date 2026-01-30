# Villasmil-Ω v2.6 — Framework & Tests

Python package: `villasmil_omega`  
Author: Ilver Villasmil — The Arquitecto  
Repository: https://github.com/ilvervillasmil/Villasmil-2.6  

Current status:
- All automated tests pass both locally (Codespaces) and on GitHub Actions.
- The package is structured as a standard Python module (`villasmil_omega`) with tests under `tests/`.
- The current suite validates basic behavior for global tension Θ(C), the Dynamic Integration Field L2, MC/CI penalties, and minimal PPR structure.

---

## 1. What is Villasmil‑Ω v2.6?

Villasmil‑Ω v2.6 is an experimental framework for evaluating **global coherence** in information systems and AI agents.  
The package implements functions to:

- Compute global tension Θ(C) over sets of premises.
- Update the Dynamic Integration Field L2.
- Apply penalties over MC (Meta‑Coherence) and CI (Internal Coherence).
- Compute relevance \\(R(C)\\) and produce structured PPR suggestions.

The goal of this version is to provide a **clean, tested baseline** on top of which more complex versions of the framework can be built.

---

## 2. Repository layout

- `villasmil_omega/`  
  - `__init__.py` — package entry point, exposes the core functions.  
  - `core.py` — main logic implementation (Θ(C), L2, penalties, R, PPR).

- `tests/`  
  - `test_basic.py` — initial test harness.  
  - `test_core_edges.py` — edge‑oriented tests for L2 and penalty behavior.  
  - `test_core_more.py` — additional cases covering `core.py` functions.  

- `.github/workflows/`  
  - `python-tests.yml` — CI pipeline running pytest with coverage on GitHub Actions.

---

## 3. Test status

Short history:
- Early CI runs failed due to import issues, misplaced test files and inconsistent filenames.
- The package structure (`__init__.py`, `core.py`) and the `tests/` folder were normalized.
- The current state is stable: tests pass consistently both locally and in CI.

Current suite:
- Total tests: 9
- Passed: 9
- Failed: 0
- Coverage (villasmil_omega): 100 % of lines on GitHub Actions (pytest-cov).

Verified aspects:

1. **Global tension Θ(C)**  
   - Returns zero tension when premises are compatible (no hallucinated conflicts).  
   - Returns non‑zero tension in the presence of simple contradictions.

2. **Dynamic Integration Field L2**  
   - `update_L2` moves L2 in the expected direction (convergence toward the optimal value in simple cases).  
   - L2 does not change arbitrarily.

3. **MC/CI penalties**  
   - `penalizar_MC_CI` reduces MC and CI when L2 deviates from the optimum.  
   - Both deviation and optimal cases are exercised.

4. **Core utilities**  
   - `compute_R` returns a positive relevance value for plausible inputs.  
   - `ppr_suggest` returns a structured dictionary with keys such as `accepted` and `alternative`.

These tests do not prove the entire framework, but they provide **high confidence** in the most critical invariants that are currently implemented.

---

## 4. How to run the tests

Local (e.g. GitHub Codespaces):

```bash
# From the repository root
cd tests
PYTHONPATH=.. pytest -q


# Villasmil‑Ω v2.6 — Marco y Pruebas

Paquete Python: `villasmil_omega`  
Autor: Ilver Villasmil — The Arquitecto  
Repositorio: https://github.com/ilvervillasmil/Villasmil-2.6  

Estado actual:
- Todas las pruebas automatizadas pasan tanto en local (Codespaces) como en GitHub Actions.
- El paquete está estructurado como un módulo Python estándar (`villasmil_omega`) con pruebas en `tests/`.
- La batería actual valida el comportamiento básico de la tensión global Θ(C), el Campo de Integración Dinámica L2, las penalizaciones MC/CI y la estructura mínima de PPR.

---

## 1. Qué es Villasmil‑Ω v2.6

Villasmil‑Ω v2.6 es un framework experimental para evaluar la **coherencia global** en sistemas de información y agentes de IA.  
El paquete implementa funciones para:

- Calcular la tensión global Θ(C) sobre conjuntos de premisas.
- Actualizar el Campo de Integración Dinámica L2.
- Aplicar penalizaciones sobre MC (Meta‑Coherencia) y CI (Coherencia Interna).
- Calcular la relevancia \\(R(C)\\) y producir sugerencias PPR estructuradas.

El objetivo de esta versión es ofrecer una **base limpia y testeada** sobre la cual puedan crecer versiones más complejas del marco.

---

## 2. Estructura del repositorio

- `villasmil_omega/`  
  - `__init__.py` — punto de entrada del paquete, expone las funciones núcleo.  
  - `core.py` — implementación principal (Θ(C), L2, penalizaciones, R, PPR).

- `tests/`  
  - `test_basic.py` — arnés inicial de pruebas.  
  - `test_core_edges.py` — pruebas de borde para L2 y penalizaciones.  
  - `test_core_more.py` — casos adicionales sobre las funciones de `core.py`.  

- `.github/workflows/`  
  - `python-tests.yml` — pipeline de CI que ejecuta pytest con cobertura en GitHub Actions.

---

## 3. Estado de las pruebas

Historia breve:
- Al inicio, varias ejecuciones de CI fallaban por problemas de imports, archivos de test mal ubicados y nombres inconsistentes.
- Se normalizó la estructura del paquete (`__init__.py`, `core.py`) y la carpeta `tests/`.
- El estado actual es estable: las pruebas pasan de forma consistente en local y en CI.

Batería actual:
- Total de tests: 9  
- Pasan: 9  
- Fallan: 0  
- Cobertura (villasmil_omega): 100 % de líneas en GitHub Actions (pytest-cov).

Aspectos verificados:

1. **Tensión global Θ(C)**  
   - Devuelve tensión cero cuando las premisas son compatibles (no inventa conflictos).  
   - Devuelve tensión distinta de cero ante contradicciones simples.

2. **Campo de Integración Dinámica L2**  
   - `update_L2` mueve L2 en la dirección esperada (convergencia hacia el valor óptimo en casos simples).  
   - L2 no cambia de forma arbitraria.

3. **Penalizaciones MC/CI**  
   - `penalizar_MC_CI` reduce MC y CI cuando L2 se aleja del óptimo.  
   - Se ejercitan casos de desviación y de valor óptimo.

4. **Utilidades de core**  
   - `compute_R` devuelve relevancia positiva para parámetros plausibles.  
   - `ppr_suggest` devuelve un diccionario estructurado con claves como `accepted` y `alternative`.

Estas pruebas no demuestran todo el framework, pero sí dan **alta confianza** en los invariantes más críticos que están implementados ahora.

---

## 4. Cómo ejecutar las pruebas

En local (por ejemplo, GitHub Codespaces):

```bash
# Desde la raíz del repositorio
cd tests
PYTHONPATH=.. pytest -q
