# Changelog - Villasmil-Ω v2.6

Todos los cambios notables del proyecto serán documentados en este archivo.

All notable changes to this project will be documented in this file.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added / Agregado
- Tests automatizados con ejemplos cuantificables (52 nuevos tests)
- Documentación completa de testing en TESTING.md
- Datos de salida esperada en cada prueba con @pytest.mark.parametrize
- Documentación de condiciones de fallo para cada función
- Workflow de GitHub Actions mejorado con:
  - Matriz de versiones de Python (3.9, 3.10, 3.11, 3.12)
  - Integración con Codecov para reportes de cobertura
  - Jobs de linting (Black, isort, flake8)
- Workflow de releases automáticas
- CHANGELOG.md para tracking de versiones

### Changed / Cambiado
- GitHub Actions ahora ejecuta en múltiples versiones de Python
- Tests ahora incluyen 179 casos totales (127 originales + 52 nuevos)

### Documented / Documentado
- Casos borde críticos:
  - β = 0 (división por cero)
  - Valores NaN/Inf
  - Listas vacías
  - Penalizaciones negativas
  - Límite OMEGA_U
  - Conflictos Model A vs Model B
  - Presencia de "unknown"
  - Estados de invariancia
  - Autorizaciones meta/force

---

## [2.6.6] - 2024

### Added / Agregado
- Certificación SIL-4
- Cobertura de código 93%
- Sistema L3 - Raíz de Ritmo (Metrónomo)
- Guardián de Invariancia L1
- Procesador Omega L4 con ingestión robusta
- Protección contra valores no finitos (NaN/Inf)
- Saturación universal en OMEGA_U = 0.995

### Changed / Cambiado
- Restauración del orden L1 -> L2 (invariancia antes de meta/force)
- Mejoras en manejo de errores y sanitización de datos

### Fixed / Corregido
- Manejo robusto de división por cero
- Sanitización de valores no finitos
- Clamp con protección OMEGA_U

---

## [2.6.0] - 2024

### Added / Agregado
- Framework inicial Villasmil-Ω v2.6
- Cálculo de tensión global Θ(C)
- Campo de Integración Dinámica L2
- Índices MC (Masa Crítica) y CI (Coherencia Interna)
- Penalizaciones MC/CI
- Sistema de relevancia R(C)
- Sugerencias PPR estructuradas
- Suite inicial de tests
- GitHub Actions CI/CD

### Documentation / Documentación
- README.md completo (bilingüe ES/EN)
- SESION.md - Guía de sesiones
- Estructura del paquete Python `villasmil_omega`

---

## Versionado / Versioning

El proyecto usa [Semantic Versioning](https://semver.org/):

- **MAJOR** version cuando hay cambios incompatibles en la API
- **MINOR** version cuando se añade funcionalidad compatible hacia atrás
- **PATCH** version cuando se corrigen bugs compatibles hacia atrás

---

## Tags y Releases

Para crear un nuevo release:

```bash
# Crear y push del tag
git tag -a v2.6.7 -m "Release v2.6.7 - Descripción"
git push origin v2.6.7

# Esto activará automáticamente el workflow de release
```

El workflow de release automáticamente:
1. Ejecuta todos los tests
2. Genera notas de release
3. Crea el release en GitHub
4. Actualiza este CHANGELOG

---

## Links

- [Repositorio](https://github.com/ilvervillasmil-ctrl/Villasmil-2.6)
- [Issues](https://github.com/ilvervillasmil-ctrl/Villasmil-2.6/issues)
- [Releases](https://github.com/ilvervillasmil-ctrl/Villasmil-2.6/releases)
