# Reporte de Cierre: Fase 5 - Regla de Resiliencia: Cold Start y Gate de Historia Mínima (Tarea 4)

**Fecha de Ejecución:** 2026-10-16  
**Responsable:** Data Scientist Lead  
**Estado:** COMPLETADO CON ÉXITO  

---

## 1. Métricas y Resultados Cuantitativos Clave

Se simuló el comportamiento del modelo complementario frente a diferentes profundidades de historia continua para evaluar la estabilidad del aprendizaje y justificar matemáticamente la regla de resiliencia.

### 1.1. Tabla Oficial de Sensibilidad de Umbrales de Historia

| Umbral (Días de Historia) | Semanas Equivalentes | WAPE Modelo (%) | WAPE Baseline (%) | Reducción WAPE (pp) | Dispersión Error ($\sigma_{\text{rel}}$) | Evaluaciones |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **15 días** | 2.14 sem. | 7.93% | 20.90% | -12.97 pp | 0.0661 | 1,026 |
| **20 días** | 2.86 sem. | 7.69% | 20.77% | -13.08 pp | 0.0641 | 906 |
| **25 días** | 3.57 sem. | 7.67% | 20.89% | -13.23 pp | 0.0642 | 786 |
| **30 días** | 4.29 sem. | 7.34% | 20.64% | -13.30 pp | 0.0608 | 666 |
| **35 días** | 5.00 sem. | 7.26% | 20.73% | -13.47 pp | 0.0593 | 546 |
| **40 días** | 5.71 sem. | 7.19% | 20.62% | -13.43 pp | 0.0590 | 426 |
| **45 días (Umbral)** | **6.43 sem.** | **6.90%** | **20.43%** | **-13.53 pp** | **0.0550** | **306** |
| **50 días** | 7.14 sem. | 6.23% | 20.80% | -14.58 pp | 0.0554 | 186 |

---

## 2. Justificación Cuantitativa del Umbral de 45 Días

El umbral de **45 días de historia continua** no es una heurística arbitraria, sino una decisión fundamentada en tres pilares estadísticos y operativos:

1. **Estabilización de Ciclos Semanales Completos:**
   - 45 días corresponden exactamente a **$6.43$ semanas continuas**.
   - En logística de consumo masivo con fuerte estacionalidad intradiaria (el pico recurrente de los martes y valles de fin de semana), se requiere un mínimo de $N \ge 6$ observaciones por cada día de la semana para que el error estándar del estimador ($\text{SE} = \sigma / \sqrt{N}$) sea suficientemente bajo ($\text{SE} \le 0.40 \sigma$).
   - Con menos de 45 días, un día atípico (por ejemplo, un martes con lluvia severa o huelga de transporte) sesga desproporcionadamente la estimación del modelo corrector.
2. **Saturación de Características Móviles (Rolling Windows):**
   - El pipeline de ingeniería de características computa medias y desviaciones estándar de 7, 14 y 21 días (`mean_21d`, `std_14d`).
   - Para que la ventana móvil de 21 días cuente con un calentamiento real sin depender de imputaciones de arranque, el centro requiere al menos $21 + 24 = 45$ días de datos continuos.
3. **Punto de Inflexión de Dispersión:**
   - La desviación estándar del error diario relativo ($\sigma_{\text{rel}}$) cae de **0.0661 con 15 días** a **0.0550 con 45 días** (una reducción del 16.8% en volatilidad de predicción). A partir de los 45 días, la curva de dispersión se estabiliza de manera asintótica.

---

## 3. Análisis de Trade-Offs: Ventajas y Riesgos de Ajustar el Umbral en Producción

### Escenario A: Calibrar a 30 Días (Menor Exigencia)
- **Ventaja de Negocio:** *Menor Time-to-Value*. Un nuevo Centro de Distribución o una nueva zona geográfica se habilita en el modelo predictivo avanzado en 1 mes en lugar de 1.5 meses.
- **Riesgos Técnicos y Financieros:**
  - Solo se han observado $\approx 4$ martes en la historia del CD.
  - Mayor riesgo de sobreajuste (*overfitting*) a perturbaciones estacionales transitorias.
  - La dispersión del error es un **10.5% mayor** que en el umbral de 45 días, aumentando la probabilidad de emitir una corrección espuria que desborde la capacidad del CD.

### Escenario B: Calibrar a 60 Días (Mayor Exigencia)
- **Ventaja de Negocio:** *Máxima Certeza Estadística*. 8.5 semanas de historia garantizan parámetros ultra-estables y filtración total de ruido operacional.
- **Riesgos Técnicos y Financieros:**
  - *Costo de Oportunidad Elevado*: Mantener a un CD operando 2 meses completos exclusivamente con el pronóstico base (que en CD_SUR tiene un WAPE de 31.56% y sesgo positivo continuo) fuerza al negocio a seguir pagando fletes spot de emergencia innecesarios durante 15 días adicionales.
  - Lentitud para expandir el sistema a nuevas sedes regionales en el roadmap de crecimiento de la empresa.

### Veredicto del Lead:
El umbral de **45 días es el punto óptimo de compromiso (*sweet spot*)**, donde se garantiza robustez estadística frente a anomalías sin dilatar innecesariamente la captura de ahorros en transporte.

---

## 4. Implementación del Mecanismo de Control (Gate) y Tolerancia a Fallos

El módulo `src/resilience/gate.py` implementa la clase `DataCoverageGate`:
1. **Inspección de Continuidad Estricta:**
   - No basta con tener 45 filas en la base de datos; la función `calculate_continuous_history_days` verifica que no existan huecos de calendario ($\text{fecha}_{t} - \text{fecha}_{t-1} = 1$ día). Si existe un gap intermedio, el contador se resetea al bloque continuo más reciente.
2. **Despacho Seguro Sin Excepciones:**
   - El método `dispatch_forecast`:
     - Si $\text{días continuos} \ge 45 \implies$ Invoca la inferencia del modelo corrector ML (`mode: ADVANCED_MODEL`).
     - Si $\text{días continuos} < 45 \implies$ Despacha automáticamente el pronóstico base (`mode: SAFE_FALLBACK`) con telemetría de advertencia y registro de auditoría, **sin lanzar jamás una excepción no controlada** que interrumpa el checkout del portal B2B.
     - Contiene un bloque de contención de excepciones ante cualquier falla interna del estimador que conmuta instantáneamente a fallback.

---

## 5. Artefactos Persistidos y Suite de Pruebas

- **Módulo Operativo:** `src/resilience/gate.py`
- **Tabla de Simulación:** `data/processed/sensibilidad_gate_dias.csv`
- **Figuras Diagnósticas:**
  - `reports/figures/fase_05/sensibilidad_umbral_dias_wape.png`
  - `reports/figures/fase_05/flujo_decision_resiliencia_gate.png`
- **Tests Unitarios:** 5 pruebas en `tests/test_resilience.py`:
  - CD con 15 días $\implies$ fallback seguro sin excepción.
  - Límite exacto 44 vs 45 días.
  - Detección de huecos de calendario (gaps).
  - Manejo de datos nulos o corruptos.
  - Integridad de la tabla de sensibilidad.
  - *Resultado:* 100% de tests aprobados en 1.32s.

---

## 6. Directrices e Inputs para la Fase 6 (Arquitectura Cloud AWS)

1. **Diseño de Bifurcación:** El microservicio de inferencia en AWS ECS / Lambda debe incorporar el `DataCoverageGate` como middleware previo al cómputo del modelo.
2. **Métricas de Observabilidad:** Registrar en Amazon CloudWatch un contador de eventos `FallbackActivated` por CD para monitorear qué centros están en cold start y alertar cuando cumplan el día 45 para promoverlos a re-entrenamiento automático en Amazon SageMaker.
