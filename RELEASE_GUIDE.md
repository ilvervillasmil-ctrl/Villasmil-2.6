# Guía de Releases / Release Guide

## Villasmil-Ω v2.6 - Proceso de Releases

Este documento describe cómo crear y publicar nuevas versiones del framework Villasmil-Ω.

---

## Versionado / Versioning

El proyecto sigue [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH
```

- **MAJOR**: Cambios incompatibles en la API
- **MINOR**: Nueva funcionalidad compatible hacia atrás
- **PATCH**: Correcciones de bugs compatibles hacia atrás

### Ejemplos / Examples:
- `v2.6.6` → `v2.6.7`: Bug fix (PATCH)
- `v2.6.6` → `v2.7.0`: Nueva funcionalidad (MINOR)
- `v2.6.6` → `v3.0.0`: Breaking changes (MAJOR)

---

## Proceso de Release / Release Process

### 1. Preparación / Preparation

**Antes de crear un release:**

1. ✅ Asegurar que todas las pruebas pasan:
   ```bash
   pytest tests/ -v
   ```

2. ✅ Verificar cobertura de código:
   ```bash
   pytest --cov=villasmil_omega --cov-report=term-missing
   ```

3. ✅ Actualizar versión en archivos relevantes:
   - `villasmil_omega/core.py` → `__version__`
   - `villasmil_omega/__init__.py` → `__version__`

4. ✅ Revisar y actualizar documentación:
   - README.md
   - TESTING.md
   - SESION.md

5. ✅ Commit de cambios:
   ```bash
   git add .
   git commit -m "Prepare release v2.6.7"
   git push origin main
   ```

---

### 2. Crear Tag / Create Tag

**Crear el tag de versión:**

```bash
# Formato: v{MAJOR}.{MINOR}.{PATCH}
git tag -a v2.6.7 -m "Release v2.6.7 - Descripción breve de cambios"

# Verificar el tag
git tag -l -n1

# Push del tag
git push origin v2.6.7
```

---

### 3. Workflow Automático / Automatic Workflow

Al hacer push del tag, **GitHub Actions automáticamente**:

1. ✅ Ejecuta todos los tests
2. ✅ Genera el changelog desde commits
3. ✅ Crea el release en GitHub
4. ✅ Actualiza CHANGELOG.md

**Ubicación del workflow:** `.github/workflows/release.yml`

---

### 4. Verificación / Verification

**Después del release:**

1. Verificar en GitHub:
   - https://github.com/ilvervillasmil-ctrl/Villasmil-2.6/releases

2. Revisar las notas de release generadas

3. Verificar que CHANGELOG.md fue actualizado

---

## Formato de Mensajes de Commit / Commit Message Format

Para que el changelog automático sea útil, usar formato consistente:

### Convención de Commits / Commit Convention:

```
<tipo>: <descripción breve>

[cuerpo opcional]

[footer opcional]
```

### Tipos / Types:

- **feat**: Nueva funcionalidad
- **fix**: Corrección de bug
- **docs**: Cambios en documentación
- **test**: Añadir o modificar tests
- **refactor**: Refactorización de código
- **perf**: Mejoras de rendimiento
- **style**: Cambios de formato (sin cambiar lógica)
- **chore**: Tareas de mantenimiento

### Ejemplos / Examples:

```bash
git commit -m "feat: add automated test examples with expected outputs"
git commit -m "fix: handle division by zero in indice_mc"
git commit -m "docs: update TESTING.md with edge case documentation"
git commit -m "test: add parametrized tests for clamp function"
```

---

## Releases Manuales / Manual Releases

Si necesitas crear un release manualmente (sin workflow automático):

### 1. Ir a GitHub Releases:
https://github.com/ilvervillasmil-ctrl/Villasmil-2.6/releases/new

### 2. Completar el formulario:

**Tag version:** `v2.6.7`

**Release title:** `Release v2.6.7`

**Description:**
```markdown
## Villasmil-Ω v2.6.7

### Cambios / Changes

- Feature 1: Descripción
- Fix 1: Descripción
- Docs: Actualización de documentación

### Métricas de Calidad / Quality Metrics

- ✅ Tests: 179 passing
- 📊 Coverage: 93%+
- 🛡️ Certification: SIL-4
- 🔒 Security: Validated

### Instalación / Installation

\`\`\`bash
git clone https://github.com/ilvervillasmil-ctrl/Villasmil-2.6.git
cd Villasmil-2.6
git checkout v2.6.7
\`\`\`
```

### 3. Opciones:

- ☐ Set as a pre-release (para versiones beta)
- ☑ Set as the latest release (para versión estable)

### 4. Publish release

---

## Pre-releases / Versiones Beta

Para versiones en desarrollo:

```bash
# Formato: v{MAJOR}.{MINOR}.{PATCH}-{pre-release}
git tag -a v2.7.0-beta.1 -m "Beta release v2.7.0-beta.1"
git push origin v2.7.0-beta.1
```

En GitHub, marcar como "pre-release".

---

## Hotfix Release

Para correcciones urgentes en producción:

1. Crear branch desde tag de producción:
   ```bash
   git checkout -b hotfix/v2.6.7 v2.6.6
   ```

2. Hacer el fix y commit:
   ```bash
   git commit -m "fix: critical bug in theta calculation"
   ```

3. Crear tag y push:
   ```bash
   git tag -a v2.6.7 -m "Hotfix v2.6.7 - Critical bug fix"
   git push origin v2.6.7
   ```

4. Merge de vuelta a main:
   ```bash
   git checkout main
   git merge hotfix/v2.6.7
   git push origin main
   ```

---

## Changelog Manual / Manual Changelog

Si necesitas actualizar el CHANGELOG.md manualmente:

```markdown
## [2.6.7] - 2026-02-05

### Added / Agregado
- Nueva característica X
- Función Y

### Changed / Cambiado
- Mejora en función Z

### Fixed / Corregido
- Bug en cálculo de theta
- Manejo de división por cero

### Deprecated / Deprecado
- Función antigua_funcion()

### Removed / Removido
- Código legacy

### Security / Seguridad
- Parche de seguridad para vulnerabilidad X
```

---

## Verificación de Release / Release Checklist

Antes de publicar:

- [ ] Tests pasan (pytest)
- [ ] Cobertura >90%
- [ ] Documentación actualizada
- [ ] CHANGELOG.md actualizado
- [ ] Versión actualizada en archivos de código
- [ ] Tag creado con formato correcto
- [ ] Notas de release completas
- [ ] Security check passed

---

## Recursos / Resources

- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## Contacto / Contact

Para preguntas sobre releases:
- Issues: https://github.com/ilvervillasmil-ctrl/Villasmil-2.6/issues
- Email: ilver@villasmil.com

---

**Última actualización:** 2026-02-05  
**Versión del documento:** 1.0
