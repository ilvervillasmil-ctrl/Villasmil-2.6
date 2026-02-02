# Sesiones en Villasmil-Ω v2.6 | Sessions in Villasmil-Ω v2.6

## 🇪🇸 Español

### ¿Para qué es esta sesión?

Una **sesión** en el contexto de Villasmil-Ω v2.6 es un **período continuo de trabajo o evaluación** durante el cual el sistema monitorea la coherencia global, la fatiga cognitiva y el estado de salud del agente o sistema bajo análisis.

### Propósitos de una Sesión

Las sesiones en Villasmil-Ω v2.6 sirven para:

1. **Monitoreo Continuo de Coherencia**
   - Evaluar la tensión global Θ(C) sobre conjuntos de premisas
   - Detectar contradicciones y conflictos en tiempo real
   - Mantener la coherencia interna (CI) y meta-coherencia (MC)

2. **Prevención de Burnout**
   - Monitorear señales internas: fatiga física, carga cognitiva, tensión emocional
   - Calcular el campo L2_self para detectar riesgo de agotamiento
   - Aplicar el mecanismo de "Respiro" cuando se detecta sobrecarga

3. **Evaluación del Contexto Relacional**
   - Observar señales relacionales: feedback directo, distancia relacional, confianza
   - Calcular L2_contexto para medir el impacto del entorno
   - Detectar cuándo el contexto está dañando al sistema

4. **Gestión de Energía**
   - Determinar cuándo el sistema está en paz (invariancia - L1)
   - Evitar procesamiento innecesario cuando no hay tensión
   - Cerrar sesiones cuando se alcanza un estado de paz sistemática

5. **Decisiones de Continuación o Detención**
   - Evaluar si es seguro continuar el trabajo
   - Detectar estados críticos (BURNOUT_INMINENTE, SELF_CRITICO)
   - Aplicar acciones correctivas: CONTINUAR, PAUSAR, DETENER

### Ciclo de Vida de una Sesión

```
1. INICIO → Registro de baseline (mu inicial, estado BASELINE)
2. TRABAJO → Registro continuo de mediciones
   - Actualización de L2_self y L2_contexto
   - Detección de desviaciones del punto neutro
   - Aplicación de penalizaciones si es necesario
3. EVALUACIÓN → Análisis de invariancia y ritmo
   - ¿El sistema está en paz? → Cierre natural
   - ¿Hay arritmia o burnout? → Aplicar respiro
4. CIERRE → Cuando se alcanza invariancia o se detecta riesgo crítico
```

### Componentes Clave

- **L1 - Invariancia (Guardián de Paz)**: Detecta cuando el sistema alcanza un estado estable
- **L2 - Coherencia**: Monitorea la carga interna (self) y externa (contexto)
- **L3 - Ritmo/Tensión**: Calcula estabilidad (metrónomo) y conflictos (theta)
- **L4 - Procesador Omega**: Ingesta datos y toma decisiones de flujo

### Ejemplo Práctico

Una sesión típica de evaluación de un agente IA:

```python
from villasmil_omega.human_l2.puntos import SistemaCoherenciaMaxima

# Iniciar sesión
sistema = SistemaCoherenciaMaxima()

# Registrar mediciones durante la sesión
resultado = sistema.registrar_medicion(
    señales_internas={
        "fatiga_fisica": 0.3,
        "carga_cognitiva": 0.6,
        "tension_emocional": 0.2
    },
    señales_relacionales={
        "feedback_directo": 0.1,
        "confianza_reportada": 0.8
    }
)

# Evaluar si continuar
if resultado["estado_self"]["estado"] == "RIESGO_SELF":
    print("⚠️ Aplicar respiro - sesión en riesgo")
elif resultado["estado_self"]["estado"] == "SELF_ESTABLE":
    print("✓ Sesión saludable - continuar")
```

---

## 🇬🇧 English

### What is this session for?

A **session** in the context of Villasmil-Ω v2.6 is a **continuous period of work or evaluation** during which the system monitors global coherence, cognitive fatigue, and the health status of the agent or system under analysis.

### Purposes of a Session

Sessions in Villasmil-Ω v2.6 serve to:

1. **Continuous Coherence Monitoring**
   - Evaluate global tension Θ(C) over premise sets
   - Detect contradictions and conflicts in real-time
   - Maintain internal coherence (CI) and meta-coherence (MC)

2. **Burnout Prevention**
   - Monitor internal signals: physical fatigue, cognitive load, emotional tension
   - Calculate L2_self field to detect burnout risk
   - Apply "Respiro" (respite) mechanism when overload is detected

3. **Relational Context Evaluation**
   - Observe relational signals: direct feedback, relational distance, trust
   - Calculate L2_context to measure environmental impact
   - Detect when context is harming the system

4. **Energy Management**
   - Determine when the system is at peace (invariance - L1)
   - Avoid unnecessary processing when there's no tension
   - Close sessions when systematic peace state is reached

5. **Continue or Stop Decisions**
   - Evaluate if it's safe to continue working
   - Detect critical states (BURNOUT_IMMINENT, CRITICAL_SELF)
   - Apply corrective actions: CONTINUE, PAUSE, STOP

### Session Life Cycle

```
1. START → Baseline registration (initial mu, BASELINE state)
2. WORK → Continuous measurement recording
   - Update of L2_self and L2_context
   - Detection of deviations from neutral point
   - Application of penalties if necessary
3. EVALUATION → Invariance and rhythm analysis
   - Is the system at peace? → Natural closure
   - Is there arrhythmia or burnout? → Apply respite
4. CLOSURE → When invariance is reached or critical risk is detected
```

### Key Components

- **L1 - Invariance (Peace Guardian)**: Detects when system reaches stable state
- **L2 - Coherence**: Monitors internal (self) and external (context) load
- **L3 - Rhythm/Tension**: Calculates stability (metronome) and conflicts (theta)
- **L4 - Omega Processor**: Ingests data and makes flow decisions

### Practical Example

A typical AI agent evaluation session:

```python
from villasmil_omega.human_l2.puntos import SistemaCoherenciaMaxima

# Start session
sistema = SistemaCoherenciaMaxima()

# Record measurements during session
resultado = sistema.registrar_medicion(
    señales_internas={
        "fatiga_fisica": 0.3,
        "carga_cognitiva": 0.6,
        "tension_emocional": 0.2
    },
    señales_relacionales={
        "feedback_directo": 0.1,
        "confianza_reportada": 0.8
    }
)

# Evaluate whether to continue
if resultado["estado_self"]["estado"] == "RIESGO_SELF":
    print("⚠️ Apply respite - session at risk")
elif resultado["estado_self"]["estado"] == "SELF_ESTABLE":
    print("✓ Healthy session - continue")
```

---

## Recursos Adicionales | Additional Resources

- **README.md**: Descripción general del framework | Framework overview
- **villasmil_omega/core.py**: Implementación de las capas L1-L4 | L1-L4 layer implementation
- **villasmil_omega/human_l2/**: Sistema de monitoreo de salud | Health monitoring system
- **villasmil_omega/respiro.py**: Detección de necesidad de descanso | Rest detection
- **villasmil_omega/cierre/**: Evaluación de cierre de sesión | Session closure evaluation

---

**Autor | Author**: Ilver Villasmil — The Arquitecto  
**Versión | Version**: 2.6  
**Licencia | License**: Apache License
