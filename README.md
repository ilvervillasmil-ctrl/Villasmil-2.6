# Villasmil‑Ω v2.6 — Core Module (English)

Author: Ilver Villasmil — The Arquitecto  
Version: 2.6.0 — 2026-01-29  
License: Apache‑2.0

Overview
--------
Villasmil‑Ω v2.6 is a distributed coherence framework prototype focused on:
- Detecting latent premise tension (Θ(C))
- Maintaining dynamic stability of the integration field (L2)
- Applying the Proactive Refinement Protocol (PPR)
- Producing auditable metrics (MC, CI, φC, Δ_sem)

This repository contains a Python reference implementation (prototype), a test harness for adversarial scenarios (A2.2), documentation, and helper scripts designed to work on mobile terminals such as iSH (iOS) or typical Linux shells.

Quick summary of components
---------------------------
- villasmil_omega/core.py — Core logic: Θ(C), L2 control, penalties, PPR suggestion
- tests/test_a2_2.py — A2.2 adversarial attack test harness (example scenarios)
- tests/test_basic.py — Basic sanity tests
- docs/02-architecture.md — Architecture overview and design notes
- deploy_villasmil_omega.sh — Branch & PR helper (edit variables before use)
- run_villasmil.sh — Lightweight runner: loads core and runs tests
- tools/health_check.sh — Basic integrity check
- LICENSE — Apache‑2.0

Mobile-friendly quick start (iSH on iPhone / iPad)
--------------------------------------------------
1. Install iSH from the App Store and open it.
2. Install required packages (Alpine):
   apk update
   apk add git python3 py3-pip
3. Clone the repository:
   git clone https://github.com/ilvervillasmil-ctrl/Villasmil-2.6.git
   cd Villasmil-2.6
4. (Optional) Create a virtual environment:
   python3 -m venv .venv
   source .venv/bin/activate
5. Make runner executable and run:
   chmod +x run_villasmil.sh
   ./run_villasmil.sh

Expected run behavior
---------------------
run_villasmil.sh prints a small banner, loads the core module and executes the A2.2 test harness. Example output snippet:

Θ(C): 0.723 → HIGH TENSION DETECTED ⚠️  
TEST COMPLETE ✓  
>>> DONE

Notes on the environment
------------------------
- The core requires Python 3.x. The minimal prototype has no external dependencies. Optional extensions (embeddings, IPFS) will require additional packages (listed in requirements.txt but commented).
- Ensure you run scripts from the project root so Python can import the `villasmil_omega` package.

Development workflow (recommended)
----------------------------------
1. Prepare local changes and commit.
2. Push to the repo main branch (or push feature branches).
3. Use the included deploy script to create feature branches:
   ./deploy_villasmil_omega.sh
   (Edit variables inside the script before running: REPO_OWNER, REPO_NAME, AUTHOR_EMAIL.)
4. Create PRs in draft mode for review.

Testing & CI
------------
- Run the basic test suite locally:
  python3 -m tests.test_basic
  python3 -m tests.test_a2_2
- Recommended CI: add a GitHub Actions workflow that runs the tests on push/PR.

Security & Privacy
------------------
- Do not commit secrets (tokens, private keys) in the repo. Verify `.gitignore` is set up for local credentials.
- For remote pushes from mobile, prefer `gh auth login` or SSH keys; avoid embedding tokens in remote URLs.

Contributing
------------
- Open a PR to `main` or to feature branches for changes.
- Proposed code changes should include tests or reproducible examples.
- For governance and merges, the lead architect (Ilver Villasmil) is the final approver.

License
-------
Apache‑2.0 — see LICENSE file.

Contact
-------
GitHub: https://github.com/ilvervillasmil-ctrl  
Author: Ilver Villasmil — The Arquitecto (Miami, FL)

----
If you want, I can:
- generate a longer technical README (spec sections, message schemas), or
- create the GitHub Actions CI file and upload it into the repo next.

# Villasmil-Ω v2.6

**Author:** Ilver Villasmil – The Arquitecto  
**Version:** 2.6.0  
**Date:** January 29, 2026  
**License:** Apache-2.0

---

## Overview

Distributed coherence framework with verifiable metrics:

- **MC (Metaconsciousness)** ≥ 0.70  
- **CI (Integrated Coherence)** ≥ 0.95  
- **Θ(C) (Global Tension)** - Incompatibility detection  
- **Dynamic L2** - Automatic control  
- **R(C)** - Optimal context selection

---

## Quick start (mobile-friendly)

1. Create project directory and files (or upload via GitHub mobile app).  
2. From a computer or a mobile terminal app (Termux / iSH / a-Shell), run:

```bash
# clone (replace with your repo if already created)
git clone https://github.com/ilvervillasmil/villasmil-omega-protocol.git
cd villasmil-omega-protocol

# (Optional) create virtualenv
python3 -m venv .venv
source .venv/bin/activate

# Install (no deps for core)
pip install -r requirements.txt

# Run basic tests
python -m tests.test_basic
python -m tests.test_a2_2
```

---

## Project layout

villasmil-omega-protocol/
├── villasmil_omega/
│   ├── __init__.py
│   └── core.py
├── docs/
│   └── 02-architecture.md
├── protocol/
│   └── messages.proto
├── tests/
│   ├── test_basic.py
│   └── test_a2_2.py
├── tools/
│   └── health_check.sh
├── deploy_villasmil_omega.sh
├── README.md
├── LICENSE
└── requirements.txt

---

## Contact

Ilver Villasmil – The Arquitecto  
GitHub: @ilvervillasmil  
Miami, FL

Status: Active development — Version 2.6.0
# Villasmil‑Ω v2.6 — Módulo Núcleo (Español)

Autor: Ilver Villasmil — The Arquitecto  
Versión: 2.6.0 — 29‑01‑2026  
Licencia: Apache‑2.0

Resumen
-------
Villasmil‑Ω v2.6 es un marco de coherencia distribuida en fase prototipo, diseñado para:
- Detectar tensiones latentes entre premisas (Θ(C))
- Mantener la estabilidad dinámica del campo de integración (L2)
- Aplicar el Proactive Refinement Protocol (PPR)
- Producir métricas auditable (MC, CI, φC, Δ_sem)

El repositorio contiene una implementación de referencia en Python, un harness de pruebas adversariales (A2.2), documentación y scripts móviles (iSH).

Componentes principales
-----------------------
- villasmil_omega/core.py — Lógica central: cálculo de Θ(C), control L2, penalizaciones, PPR
- tests/test_a2_2.py — Prueba adversarial A2.2 (escenarios ejemplo)
- tests/test_basic.py — Tests básicos de integridad
- docs/02-architecture.md — Visión arquitectónica
- deploy_villasmil_omega.sh — Script auxiliar para ramas/PRs (editar variables)
- run_villasmil.sh — Runner ligero: carga core y ejecuta tests
- tools/health_check.sh — Verificador de integridad
- LICENSE — Apache‑2.0

Arranque rápido (iSH en iPhone / iPad)
-------------------------------------
1. Abre iSH (Alpine) en iOS.
2. Instala paquetes:
   apk update
   apk add git python3 py3-pip
3. Clona el repositorio:
   git clone https://github.com/ilvervillasmil-ctrl/Villasmil-2.6.git
   cd Villasmil-2.6
4. (Opcional) Entorno virtual:
   python3 -m venv .venv
   source .venv/bin/activate
5. Haz ejecutable y lanza:
   chmod +x run_villasmil.sh
   ./run_villasmil.sh

Salida esperada
---------------
El script run_villasmil.sh muestra un banner, carga el módulo core y ejecuta la prueba A2.2. Ejemplo:

Θ(C): 0.723 → HIGH TENSION DETECTED ⚠️  
TEST COMPLETE ✓  
>>> DONE

Notas sobre el entorno
----------------------
- El prototipo requiere Python 3.x. Las extensiones (embeddings, IPFS) requieren dependencias adicionales.
- Ejecuta siempre desde la raíz del proyecto para que las importaciones funcionen correctamente.

Flujo de trabajo (recomendado)
------------------------------
1. Haz commits locales y verifica tests.
2. Push a `main` o a ramas feature.
3. Usa el script de despliegue para crear ramas y PR (editar variables internas del script antes de ejecutar).
4. Crea PRs en modo draft para revisión.

Pruebas y CI
------------
- Ejecuta tests locales:
  python3 -m tests.test_basic
  python3 -m tests.test_a2_2
- Se recomienda añadir un workflow de GitHub Actions que ejecute las pruebas en push/PR.

Seguridad
---------
- No subas credenciales ni secrets al repo.
- Para pushes desde móvil: prefiera `gh auth login` o SSH; no incrustes tokens en URLs.

Contribuir
----------
- Abre PRs hacia `main` o ramas feature.
- Incluye pruebas o ejemplos reproducibles para cambios de funcionalidad.
- El arquitecto (Ilver Villasmil) supervisa merges y gobernanza.

Licencia
--------
Apache‑2.0 — ver archivo LICENSE.

Contacto
--------
GitHub: https://github.com/ilvervillasmil-ctrl  
Autor: Ilver Villasmil — The Arquitecto (Miami, FL)

----


Hi ,

I’d like to invite you as a collaborator to the repository:

Repository: https://github.com/ilvervillasmil-ctrl/Villasmil-2.6
Project: Villasmil‑Ω v2.6 — Core Module
Role requested: Write (push + create branches + open PRs)

Purpose:
- Review and help finalize the README and documentation (EN/ES).
- Verify the A2.2 test harness behavior and run basic tests on iSH or desktop.
- Help prepare GitHub Actions CI and the initial PRs (draft mode).

Notes:
- Main contact / lead architect: Ilver Villasmil — The Arquitecto
- Preferred language for reviews: English or Spanish (both accepted)
- License: Apache‑2.0

If you accept, please confirm your GitHub username and I will send the collaborator invite (Write access). Once you accept, I will:
1. Add you as collaborator on the repo.
2. Create two draft PRs for review: feature/test-harness and feature/docs-full.
3. Share the run instructions for iSH and any specific review tasks.

Thanks,
Ilver Villasmil — The Arquitecto

