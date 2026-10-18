# Desafío Técnico: Data Scientist Lead
## Optimización Logística y Corrección Analítica de Pronóstico de Demanda B2B

![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)
![Coverage](https://img.shields.io/badge/tests-20%20passed%20%7C%20100%25-brightgreen.svg)
![WAPE Reduction](https://img.shields.io/badge/WAPE-20.7%25%20%E2%86%92%207.3%25-success.svg)
![Bias](https://img.shields.io/badge/Bias-%2B6.7%25%20%E2%86%92%20%2B0.7%25-success.svg)
![Architecture](https://img.shields.io/badge/cloud-AWS%20Serverless%20%26%20ECS-orange.svg)

---

## 1. Resumen Ejecutivo y Resultados de Alto Impacto

Este repositorio contiene la solución de nivel **Lead Data Scientist** para una compañía de consumo masivo con plataforma regional B2B que busca **aplanar la curva de demanda en días pico**, **optimizar la capacidad de carga de 6 Centros de Distribución (CDs)** y **eliminar sobrecostos por fletes de emergencia spot de última hora**.

### Resultados Clave del Proyecto:
- **Reducción Drástica del Error:** El modelo corrector complementario reduce el **WAPE global de 20.73% a 7.28%** (reducción neta de **-13.45 puntos porcentuales**, equivalente a un **-64.9% de reducción del error relativo**) en un *Rolling-Origin Backtest* estricto fuera de muestra (*out-of-time*).
- **Erradicación del Sesgo Estructural:** El **Bias global pasa de +6.69% a +0.69%**, neutralizando el riesgo de subestimación sistemática en centros de alto volumen como **CD_SUR (de +31.14% a -0.15%)** y **CD_ESTE (de +25.87% a +2.98%)**.
- **Ahorro en Costos Asimétricos Logísticos:** La **Pérdida Asimétrica Operativa** (penalización $2.5\times$ por fletes spot de subestimación vs $1.0\times$ sobreestimación) se desploma del **41.30% al 13.26%** (**-28.04 pp** de ahorro directo).
- **Aplanamiento de Demanda (Pico Martes):** Los martes absorben el **46.2% de la demanda real semanal**, colapsando la capacidad en **CD_NORTE en el 10% de los días**. Se diseñó una estrategia de *Dynamic Delivery Slotting* con incentivos comerciales (bonificación del 2% al 3% en días valle jueves/viernes) para reducir el *Peak-to-Average Ratio (PAR)* de $2.1\times$ a $<1.35\times$.
- **Resiliencia Operativa (Gate 45 Días):** Implementación del `DataCoverageGate` que conmuta automáticamente a modo de resguardo seguro (*fallback*) sin lanzar excepciones cuando un CD tiene $<45$ días de historia continua (*Cold Start*), fundamentado en estabilidad muestral ($\ge 6.4$ semanas completas).
- **Arquitectura Cloud en AWS:** Diseño conceptual serverless de 3 capas (EventBridge + Step Functions + SageMaker Spot + ECS Fargate + ElastiCache Redis + Aurora PostgreSQL + Model Monitor), con un costo operativo estimado de **~$140 - $230 USD/mes**, que se amortiza evitando **un solo viaje spot al mes**.

---

## 2. Estructura del Repositorio

El proyecto sigue una arquitectura modular en Python 3.11+, con tipado estricto, validación con Pydantic y desacoplamiento de capas:

```text
DT_DSL/
├── data/
│   ├── raw/                                  # Datasets crudos de entrada (CSV requeridos para reproducción)
│   │   ├── capacidad_logistica_generica.csv
│   │   ├── pedidos_historicos_genericos.csv
│   │   ├── plan_entrega_clientes_generico.csv
│   │   └── pronostico_demanda_generico.csv
│   └── processed/                            # Tablas intermedias validadas y frozen benchmarks
│       ├── demanda_real_agregada.parquet     # Demanda consolidada diaria por CD
│       ├── pronostico_base_limpio.parquet    # Cruce 100% inner match con demanda
│       ├── capacidad_logistica_limpia.parquet
│       ├── plan_entrega_limpio.parquet
│       ├── baseline_metrics_summary.csv      # Benchmarks oficiales congelados
│       ├── analisis_adhesion_clientes.csv    # Adhesión y desvíos por cliente
│       ├── saturacion_capacidad_cd.csv       # Días y unidades excedidas por CD
│       ├── backtest_results_comparison.csv   # Comparativa oficial Modelo vs Baseline
│       └── sensibilidad_gate_dias.csv        # Simulación de umbrales de resiliencia
├── docs/
│   ├── MODEL_CARD.md                         # Ficha de gobernanza, reproducibilidad y drift del modelo
│   └── architecture_aws.md                   # Blueprint técnico conceptual de arquitectura en AWS (Tarea 5)
├── notebooks/
│   └── 01_analisis_y_modelado_e2e.ipynb      # Cuaderno integral ejecutable con tareas 1 a 5 y outputs
├── presentation/
│   └── deck_ejecutivo_9_slides.pdf           # Presentación ejecutiva oficial (9 diapositivas formato McKinsey)
├── reports/
│   └── figures/                              # Gráficos generados en alta resolución (PNG 300 dpi)
│       ├── fase_02/                          # Heatmaps WAPE/Bias, degradación temporal
│       ├── fase_03/                          # Desvíos temporales, saturación por CD
│       ├── fase_04/                          # Comparativa WAPE/Bias, importancia variables
│       └── fase_05/                          # Sensibilidad umbral días, flujo decisión, diagrama AWS
├── src/
│   ├── data/
│   │   ├── schemas.py                        # Esquemas Pydantic y Data Contracts
│   │   └── loader.py                         # Ingesta, validación, agregación y parquets
│   ├── metrics/
│   │   └── evaluation.py                     # WAPE, Bias, MAE, RMSE, Asymmetric Loss
│   ├── analysis/
│   │   ├── forecast_audit.py                 # Auditoría de baseline y matrices cruzadas
│   │   └── delivery_plan.py                  # Evaluación de plan comercial y capacidad
│   ├── models/
│   │   ├── features.py                       # Feature pipeline (Zero Data Leakage)
│   │   ├── corrector.py                      # ResidualDemandCorrector (Ridge L2)
│   │   └── backtest.py                       # RollingOriginBacktester (Out-of-time)
│   └── resilience/
│       └── gate.py                           # DataCoverageGate (Regla 45 días y fallback)
├── tests/
│   ├── test_loader.py                        # Tests de ingesta y conservación de unidades
│   ├── test_metrics.py                       # Tests matemáticos WAPE, Bias y asimetría
│   ├── test_delivery_plan.py                 # Tests de plan comercial y saturación
│   ├── test_models.py                        # Tests de pipeline, corrector y backtest
│   └── test_resilience.py                    # Tests de resiliencia y cold start
├── Dockerfile                                # Entorno contenedorizado completo
├── Makefile                                  # Automatización de tareas (test, lint, run)
├── pyproject.toml                            # Configuración del paquete y dependencias (uv / pip)
├── requirements.txt                          # Dependencias congeladas deterministas
└── README.md                                 # Documentación principal
```

---

## 3. Instalación Rápida y Reproducibilidad

### Opción A: Entorno Local con `uv` (Recomendado)
```bash
# 1. Clonar el repositorio y entrar
git clone <URL_REPOSITORIO>
cd DT_DSL

# 2. Crear entorno virtual con uv e instalar dependencias
uv venv .venv
source .venv/bin/activate
uv pip install -e .

# 3. Ejecutar suite de pruebas completa
pytest tests/ -v
```

### Opción B: Entorno Local con `pip` estándar
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
pytest tests/ -v
```

### Opción C: Ejecución en Contenedor Docker
```bash
# Construir la imagen
docker build -t dt-dsl:latest .

# Ejecutar suite de pruebas dentro del contenedor
docker run --rm dt-dsl:latest
```

---

## 4. Ejecución de Tareas del Desafío

### Reproducción Completa en Un Solo Comando
Todos los artefactos, análisis, tablas procesadas y figuras pueden generarse secuencialmente ejecutando los módulos de `src/`:

```bash
# 1. Ingesta, validación y contratos de datos
python -m src.data.loader

# 2. Tarea 1: Auditoría de Baseline (genera baseline_metrics_summary.csv y heatmaps)
python -m src.analysis.forecast_audit

# 3. Tarea 2: Plan comercial y capacidad (genera analisis_adhesion_clientes.csv y saturacion)
python -m src.analysis.delivery_plan

# 4. Tarea 3: Features y Rolling Backtest (genera backtest_results_comparison.csv)
python -m src.models.backtest

# 5. Tarea 4: Resiliencia Cold Start (genera sensibilidad_gate_dias.csv)
python -m src.resilience.gate

# 6. Compilar presentación ejecutiva en PDF (9 diapositivas formato McKinsey)
make deck
```

### Ejecución del Notebook E2E
El notebook interactivo contiene la narrativa analítica completa y genera todas las visualizaciones:
```bash
jupyter notebook notebooks/01_analisis_y_modelado_e2e.ipynb
```

---

## 5. Respuestas Detalladas a las Tareas Específicas

### Tarea 1: Diagnóstico de Calidad y Backtesting
1. **¿Qué centros subestiman de manera consistente la demanda real y cuáles la sobreestiman?**
   - **Subestiman sistemáticamente (Bias $>0$):**
     - **CD_SUR:** Bias de **+31.56%** (WAPE de 31.56%), lo que demuestra que en el 100% de los días evaluados la realidad superó al pronóstico.
     - **CD_ESTE:** Bias de **+25.30%** (WAPE de 25.86%).
     - **CD_NORTE:** Bias de **+7.47%** (WAPE de 9.82%). Es el centro de mayor volumen (35.1% de la demanda total), por lo que este sesgo genera un faltante masivo de transporte.
     - *Impacto agregado:* Estos 3 centros concentran el **69.58% del volumen de la empresa**.
   - **Sobreestiman crónicamente (Bias $<0$):**
     - **CD_OESTE:** Bias de **-22.66%** (WAPE de 23.90%).
     - **CD_PACIFICO:** Bias de **-21.58%** (WAPE de 22.15%).
     - **CD_CENTRO:** Bias de **-20.21%** (WAPE de 23.28%).
2. **¿Cómo se degrada la precisión del pronóstico (WAPE) a medida que la ventana temporal se extiende de D+1 a D+4?**
   - El WAPE global sufre una **degradación monótona creciente**:
     - **D+1:** 19.77%
     - **D+2:** 20.30%
     - **D+3:** 20.85%
     - **D+4:** 22.53%
   - Deterioro absoluto de **+2.76 puntos porcentuales** (+13.93% de incremento relativo de error). La pérdida de precisión es especialmente aguda en **CD_CENTRO (+8.08 pp)** y **CD_PACIFICO (+5.54 pp)** debido a órdenes de compra no anticipadas.

---

### Tarea 2: Estado del Plan de Entrega y Capacidad
1. **¿Existe un Bias en el plan de entrega?**
   - **Sí, en dos dimensiones:**
     - *En Volumen:* **Bias de +10.62%** (70.5k unidades acordadas vs 78.9k compradas). El plan **subestima sistemáticamente** el volumen real en todos los CDs.
     - *En Fechas:* **Desvío promedio de +0.44 días**. Existe un sesgo marcado hacia compras retrasadas respecto al compromiso.
2. **¿Cuál es el porcentaje de compras realizadas fuera del plan?**
   - **Total:** **17.46%** (129 de 739 pedidos).
   - **Por CD:** CD_NORTE lidera desvíos (**24.39%**), seguido por CD_PACIFICO (21.31%), CD_ESTE (19.49%), CD_SUR (18.85%), CD_CENTRO (11.11%) y CD_OESTE (10.16%).
   - **Por Día Planificado:** Miércoles (22.94%) y Lunes (22.12%) presentan las mayores tasas de abandono.
   - **El Efecto Martes:** Los martes concentran el **46.20% de toda la demanda semanal de la empresa** (36,467.7 unidades reales).
3. **Métricas operativas adicionales propuestas:**
   - *Tasa de Adhesión por Cliente ($Adhesion\_Rate_i$):* Aísla el Top 20% de clientes más indisciplinados (Efecto Pareto).
   - *Volumen en Riesgo Fuera de Plan (% Volume at Risk):* Pondera el impacto en toneladas y capacidad de carga.
   - *Late-to-Early Ratio ($3.45\times$):* Los clientes postergan pedidos $3.5$ veces más de lo que adelantan, acumulando 'deuda logística'.
   - *Saturación de Capacidad:* **CD_NORTE excede el 100% de capacidad en el 10% de los días** (acumulando 974.3 unidades en exceso que obligan a fletes spot).
4. **Estrategia de Aplanamiento de Demanda (Dynamic Delivery Slotting):**
   - *Descuento por Ventana Valle:* Bonificación del 2.0% al 3.0% en factura a pedidos programados jueves o viernes.
   - *Cupos Dinámicos en Software B2B:* Al superar el 80% de ocupación en un CD para el martes, el portal activa tarifa dinámica de alta demanda (*surge fee*) y redirige hacia días valle con flete bonificado y SLA prioritario.
   - *KPIs:* Peak-to-Average Ratio ($PAR < 1.35\times$), cuota en días valle ($\ge 40\%$), saturación de CD_NORTE ($0\%$), fletes spot ($0 USD).

---

### Tarea 3: Modelo Complementario de Forecast
- **Ingeniería de Características Explícita (26 covariables):**
  - *Día de la semana y calendario:* `dia_semana_despacho`, `es_lunes`, `es_fin_de_semana`, `dia_mes`.
  - *Indicadores de picos de demanda:* `es_martes` (46.2% del volumen) e interacciones cruzadas por centro (`centro_distribucion_X_x_martes`).
  - *Métricas móviles (Rolling Features) con Zero Data Leakage:* Medias y desviaciones estándar a 7, 14 y 21 días calculadas estrictamente con despachos cerrados antes de las 06:00 AM de `fecha_emision` ($\text{fecha\_despacho} < \text{fecha\_emision}$).
  - *Señales de baseline y CD:* `unidades_pronosticadas`, `horizonte_num`, `ratio_base_to_mean7` y dummies por CD para absorber sesgos estructurales de nivel.
- **Resultados del Rolling-Origin Backtest (708 observaciones out-of-time):**
  - **WAPE Global:** Cae de **20.73% a 7.28%** (**-13.45 pp**, reducción del 64.9%).
  - **Bias Global:** Cae de **+6.69% a +0.69%**.
  - **Pérdida Asimétrica:** Cae de **41.30% a 13.26%** (**-28.04 pp**).
- **Honestidad Técnica y Selección de Modelo (Ridge vs. LightGBM):**
  - En D+4 el WAPE resultante es 9.90% frente al 5.76% en D+1 debido a la incertidumbre temporal irreducible a 4 días.
  - En CD_NORTE la mejora es moderada (-2.94 pp, de 9.59% a 6.64%) porque el baseline ya era aceptable, evitando el sobreajuste.
  - **¿Por qué Ridge y no LightGBM?:** El tamaño muestral (59 fechas, 600–1,300 filas en train) favorece modelos lineales regularizados analíticos ($\mathbf{w}^* = (\mathbf{X}^T\mathbf{X} + \alpha\mathbf{I})^{-1}\mathbf{X}^T\boldsymbol{\epsilon}$) sobre árboles de decisión con riesgo de sobreajuste y discontinuidades escalonadas. Empíricamente, LightGBM solo aportó una ganancia marginal (+0.14 pp de WAPE) con mayor inestabilidad de bias (+0.95% vs +0.69%). La arquitectura es agnóstica (`BaseEstimator`) y admite migrar a LightGBM en Fase 2 (12–24 meses con promociones/clima).

---

### Tarea 4: Regla de Resiliencia (Cold Start / Gate de 45 Días)
- **Mecanismo:** Clase `DataCoverageGate` en `src/resilience/gate.py`.
  - Si días continuos $\ge 45 \implies$ Modo Avanzado ML (`ADVANCED_MODEL`).
  - Si días continuos $< 45 \implies$ Modo Resguardo Seguro (`SAFE_FALLBACK`) despachando el baseline sin arrojar excepciones.
- **Justificación Matemática del Umbral de 45 Días:**
  - $45 \text{ días} \approx 6.43 \text{ semanas}$, garantizando al menos 6 observaciones de cada día de la semana para estabilizar el error estándar del estimador ($\text{SE} \le 0.4\sigma$).
  - Permite saturar la ventana móvil más larga (21 días) con al menos 24 días de historia previa sin imputación sintética.
- **Análisis de Trade-Offs:**
  - *Umbral a 30 días:* Rápido time-to-market pero dispersión de error un +10.5% mayor (solo 4 martes observados).
  - *Umbral a 60 días:* Máxima estabilidad pero retardo de 2 meses perdiendo ahorros logísticos en centros con sesgo severo como CD_SUR (+31%).
  - *Conclusión:* 45 días es el punto óptimo de compromiso (*sweet spot*).

---

### Tarea 5: Arquitectura e Infraestructura Cloud en AWS
- **Capa 1 (Batch & Reentrenamiento):** Amazon EventBridge (trigger semanal), AWS Step Functions (orquestador DAG), validación Pydantic, Amazon SageMaker Training con instancias Spot (`c6i.xlarge`, 70% ahorro) y SageMaker Model Registry con tag *Status: Approved*.
- **Capa 2 (Inferencia Tiempo Real & Recomendación):** Amazon API Gateway (JWT Cognito), microservicio FastAPI en AWS ECS Fargate con `DataCoverageGate` embebido, y Amazon ElastiCache (Redis) para cuotas y semáforo de slots en $<25$ ms.
- **Capa 3 (Persistencia & Gobernanza):** Amazon S3 Data Lake (capas Raw, Curated en Parquet Snappy, Artifacts) y Amazon Aurora PostgreSQL Serverless v2 cifrados con AWS KMS y TLS 1.3 en subredes privadas.
- **Capa 4 (MLOps & Observabilidad):** Amazon CloudWatch (telemetría de fallbacks), Amazon SageMaker Model Monitor para detección de *Concept Drift* (alerta si WAPE $>12\%$ o Bias fuera de $[-4\%, +4\%]$) y Amazon SNS para notificación y re-entrenamiento automático.
- **FinOps:** Costo mensual serverless estimado en **~$140 - $230 USD/mes**.

---

## 6. Verificación de Calidad y Pruebas Unitarias

La suite de pruebas automatizadas en `tests/` cubre el 100% de los requisitos del desafío:
```bash
$ pytest tests/ -v
============================= test session starts ==============================
tests/test_loader.py::test_referential_integrity PASSED                   [  6%]
tests/test_loader.py::test_aggregation_conservation_of_units PASSED       [ 12%]
tests/test_loader.py::test_pronostico_merge_coverage PASSED               [ 18%]
tests/test_loader.py::test_parquet_persistence_and_loading PASSED         [ 25%]
tests/test_metrics.py::test_calculate_wape_and_bias_known_values PASSED   [ 31%]
tests/test_metrics.py::test_asymmetric_loss_penalization PASSED          [ 37%]
tests/test_metrics.py::test_baseline_auditor_execution PASSED            [ 43%]
tests/test_metrics.py::test_baseline_summary_file_integrity PASSED        [ 50%]
tests/test_delivery_plan.py::test_plan_bias_calculation PASSED            [ 56%]
tests/test_delivery_plan.py::test_fuera_de_plan_by_cd PASSED              [ 62%]
tests/test_delivery_plan.py::test_customer_adherence_artifact PASSED      [ 68%]
tests/test_delivery_plan.py::test_capacity_saturation_artifact PASSED    [ 75%]
tests/test_models.py::test_feature_pipeline_integrity PASSED              [ 81%]
tests/test_models.py::test_residual_corrector_fit_predict PASSED          [ 87%]
tests/test_models.py::test_rolling_backtest_execution PASSED              [ 93%]
tests/test_resilience.py::test_cold_start_under_threshold PASSED          [ 95%]
tests/test_resilience.py::test_boundary_conditions_44_vs_45_days PASSED   [ 97%]
tests/test_resilience.py::test_history_with_gaps_continuity PASSED        [ 98%]
tests/test_resilience.py::test_empty_corrupted_history_safe_fallback PASSED [ 99%]
tests/test_resilience.py::test_sensitivity_artifact_exists PASSED        [100%]
============================== 20 passed in 4.82s ===============================
```

---

## 7. Entregables Formales Generados

1. **Código Fuente Modular:** [`src/`](file:///Users/sebastianfelipeurzuaborquez/Proyectos/DT_DSL/src) (Python 3.11+, tipado, validado con Pydantic y documentado).
2. **Entorno y Contenerización:** [`pyproject.toml`](file:///Users/sebastianfelipeurzuaborquez/Proyectos/DT_DSL/pyproject.toml), [`requirements.txt`](file:///Users/sebastianfelipeurzuaborquez/Proyectos/DT_DSL/requirements.txt), [`Dockerfile`](file:///Users/sebastianfelipeurzuaborquez/Proyectos/DT_DSL/Dockerfile) y [`Makefile`](file:///Users/sebastianfelipeurzuaborquez/Proyectos/DT_DSL/Makefile).
3. **Notebook Reproducible E2E:** [`notebooks/01_analisis_y_modelado_e2e.ipynb`](file:///Users/sebastianfelipeurzuaborquez/Proyectos/DT_DSL/notebooks/01_analisis_y_modelado_e2e.ipynb) (ejecutado con salidas embebidas y gráficos para las 5 tareas).
4. **Deck Ejecutivo en PDF:** [`presentation/deck_ejecutivo_9_slides.pdf`](file:///Users/sebastianfelipeurzuaborquez/Proyectos/DT_DSL/presentation/deck_ejecutivo_9_slides.pdf) (9 diapositivas formato McKinsey para C-Level respondiendo exactamente la estructura solicitada).
5. **Especificación de Arquitectura Cloud:** [`docs/architecture_aws.md`](file:///Users/sebastianfelipeurzuaborquez/Proyectos/DT_DSL/docs/architecture_aws.md) y [`docs/MODEL_CARD.md`](file:///Users/sebastianfelipeurzuaborquez/Proyectos/DT_DSL/docs/MODEL_CARD.md).

