# Villasmil‑Ω v2.6 — Framework & Tests

Python package: `villasmil_omega`  
Author: Ilver Villasmil — The Arquitecto  
Repository: https://github.com/ilvervillasmil/Villasmil-2.6  

Estado actual:
- Todas las pruebas automatizadas pasan tanto en local (Codespaces) como en GitHub Actions.
- El paquete está estructurado como módulo Python (`villasmil_omega`) con tests en `tests/`.
- Se ha verificado el comportamiento básico de tensión global Θ(C), campo de integración dinámica L2 y penalizaciones MC/CI.

---

## 1. Qué es Villasmil‑Ω v2.6

Villasmil‑Ω v2.6 es un framework experimental para evaluar **coherencia global** en sistemas de información y agentes de IA.  
El paquete implementa funciones para:

- Calcular tensión global Θ(C) en conjuntos de premisas.
- Actualizar el campo de integración dinámica L2.
- Aplicar penalizaciones sobre MC (Meta‑Coherencia) y CI (Coherencia Interna).
- Calcular relevancia \\(R(C)\\) y producir sugerencias PPR estructuradas.

El objetivo de esta versión es dejar una **base sólida y testeada** sobre la cual puedan crecer versiones posteriores más complejas.

---

## 2. Estructura del repositorio

- `villasmil_omega/`  
  - `__init__.py` — punto de entrada del paquete, expone las funciones núcleo.  
  - `core.py` — implementación de lógica principal (Θ(C), L2, penalizaciones, R, PPR).

- `tests/`  
  - `test_basic.py` — harness inicial de pruebas.  
  - `test_core_edges.py` — pruebas dirigidas a bordes de L2 y penalizaciones.  
  - `test_core_more.py` — casos adicionales sobre funciones de core.  

- `.github/workflows/`  
  - `test.yml` — pipeline de CI que ejecuta pytest en GitHub Actions.

---

## 3. Estado de pruebas

Historia breve:
- Al inicio, varias ejecuciones de CI fallaban (imports rotos, archivos de test en rutas incorrectas, nombres de archivo mal formados).
- Se reestructuró el paquete (`__init__.py`, `core.py`) y se normalizó la carpeta `tests/`.
- Actualmente, los tests pasan de forma consistente en local y en GitHub Actions.

Estado actual de la suite:
- Total de tests (aprox.): 8  
- Pasan: 8  
- Fallan: 0  

Aspectos verificados:

1. **Θ(C) — tensión global básica**  
   - No inventa conflicto cuando las premisas son compatibles.  
   - Produce tensión no nula en presencia de contradicciones simples.

2. **Campo L2**  
   - `update_L2` ajusta L2 en la dirección esperada (convergencia hacia el valor óptimo en casos simples).  
   - Se comprueba que L2 no se mueve de manera arbitraria.

3. **Penalizaciones MC/CI**  
   - `penalizar_MC_CI` reduce MC y CI cuando L2 se aleja del óptimo.  
   - Se validan casos de desviación y de valor óptimo.

4. **Utilidades de core**  
   - `compute_R` devuelve relevancia positiva bajo parámetros plausibles.  
   - `ppr_suggest` devuelve un diccionario estructurado con claves como `accepted` y `alternative`.

Estos tests no prueban todo el framework, pero sí dan **confianza alta** en los invariantes más críticos que ya están implementados.

---

## 4. Cómo ejecutar las pruebas

En local (por ejemplo, Codespaces):

```bash
# Desde la carpeta raíz del repo
cd tests
PYTHONPATH=.. pytest -q
