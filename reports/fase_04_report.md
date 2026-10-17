# Reporte de Cierre: Fase 4 - Ingeniería de Características, Modelo Corrector y Rolling Backtest (Tarea 3)

**Fecha de Ejecución:** 2026-10-16  
**Responsable:** Data Scientist Lead  
**Estado:** COMPLETADO CON ÉXITO  

## 1. Fórmulas Matemáticas y Metodología de Cálculo (Tarea 3)

Para subsanar las desviaciones sistemáticas del baseline sin perder la trazabilidad de negocio, se diseñó e implementó la siguiente formulación matemática rigurosa:

### 1.1. Arquitectura de Corrección Residual Aditiva
En lugar de entrenar un modelo que prediga la demanda absoluta desde cero, se modela analíticamente el residuo del baseline:
$$\epsilon_{cd, t, h} = y_{cd, t+h}^{\text{real}} - \hat{y}_{cd, t+h \mid t}^{\text{base}}$$
La predicción corregida final se obtiene mediante la suma del pronóstico base y el residuo estimado, acotada por una función de activación ReLU no negativa:
$$\hat{y}_{cd, t+h \mid t}^{\text{corregido}} = \max\left(0, \; \hat{y}_{cd, t+h \mid t}^{\text{base}} + \hat{\epsilon}_{cd, t, h}\right)$$
donde $\hat{\epsilon}_{cd, t, h} = f(\mathbf{x}_{cd, t, h})$ representa el ajuste inferido por el modelo de Machine Learning.

### 1.2. Función Objetivo de Optimización (Ridge Regression $L_2$)
El estimador de corrección optimiza la función de pérdida cuadrática regularizada por norma $L_2$:
$$\min_{\mathbf{w}} \left\{ \frac{1}{2 n} \sum_{i=1}^n \left( \epsilon_i - \mathbf{w}^T \mathbf{x}_i \right)^2 + \frac{\alpha}{2} \|\mathbf{w}\|_2^2 \right\}$$
Su solución analítica de forma cerrada está dada por:
$$\mathbf{w}^* = \left( \mathbf{X}^T \mathbf{X} + \alpha \mathbf{I} \right)^{-1} \mathbf{X}^T \boldsymbol{\epsilon}$$
- **Hiperparámetro:** $\alpha = 10.0$.
- **Justificación Matemática:** Garantiza que la matriz $(\mathbf{X}^T \mathbf{X} + \alpha \mathbf{I})$ esté estrictamente bien condicionada (condición $\lambda_{\min} \ge \alpha > 0$), eliminando la varianza inducida por la multicolinealidad entre variables de calendario y lags, y evitando el sobreajuste (*overfitting*) en ventanas cortas de tiempo.

### 1.3. Protocolo Estricto de Cero Filtración Temporal (*Zero Data Leakage*)
Para cualquier emisión ejecutada a las 06:00 AM de la fecha $t$ proyectando a horizonte $h \in \{1, 2, 3, 4\}$, el conjunto de información admisible es:
$$\mathcal{F}_t = \left\{ y_{cd, \tau}^{\text{real}} \mid \tau \le t - 1 \right\}$$
Las variables de nivel y volatilidad se calculan sobre ventanas móviles retrospectivas de tamaño $W \in \{7, 14, 21\}$ días:
$$\mu_{W}(cd, t) = \frac{1}{W} \sum_{k=1}^W y_{cd, t-k}^{\text{real}}$$
$$\sigma_{W}(cd, t) = \sqrt{\frac{1}{W-1} \sum_{k=1}^W \left( y_{cd, t-k}^{\text{real}} - \mu_{W}(cd, t) \right)^2}$$
$$\text{ratio\_base\_to\_mean7}(cd, t, h) = \frac{\hat{y}_{cd, t+h \mid t}^{\text{base}}}{\mu_7(cd, t) + 10^{-4}}$$
Queda prohibido por construcción el uso de $y_{cd, t}^{\text{real}}$ o de información posterior a la fecha de corte $t-1$.

### 1.4. Algoritmo de Evaluación Secuencial (Rolling-Origin Backtest)
1. **Fase de Calentamiento Inicial (*Warmup*):**
   $$T_{\text{warmup}} = 28 \text{ días} \quad (\text{4 semanas completas de historia})$$
2. **Iteración Temporal Secuencial:** Para cada fecha de emisión $t = T_{\text{warmup}}, \dots, T_{\max}-1$:
   - Entrenar $\mathbf{w}_t^*$ sobre el conjunto histórico acumulado:
     $$\mathcal{D}_t = \{(\mathbf{x}_i, \epsilon_i) \mid \text{fecha\_despacho}_i \le t - 1\}$$
   - Predecir simultáneamente los 4 horizontes fuera de muestra:
     $$\hat{\epsilon}_{cd, t, h} = (\mathbf{w}_t^*)^T \mathbf{x}_{cd, t, h} \quad \forall cd \in \{1,\dots,6\}, \; h \in \{1,2,3,4\}$$
     $$\hat{y}_{cd, t+h \mid t}^{\text{corregido}} = \max\left(0, \; \hat{y}_{cd, t+h \mid t}^{\text{base}} + \hat{\epsilon}_{cd, t, h}\right)$$
   - Registrar métricas y avanzar el origen temporal a $t + 1$.

### 1.5. Demostración Aritmética Paso a Paso (Backtest Out-of-Time, $N = 708$)
- **Volumen Total Real Evaluado:** $\sum_{i=1}^{708} y_i^{\text{real}} = 1,043,907.03 \text{ unidades}$
- **Baseline Oficial:**
  - $\sum |y_i^{\text{real}} - \hat{y}_i^{\text{base}}| = 216,396.96 \text{ unidades}$
  $$\text{WAPE}_{\text{base}} = \frac{216,396.96}{1,043,907.03} = \mathbf{20.7295\%} \approx \mathbf{20.73\%}$$
  - $\sum (y_i^{\text{real}} - \hat{y}_i^{\text{base}}) = +69,820.65 \text{ unidades}$
  $$\text{Bias}_{\text{base}} = \frac{+69,820.65}{1,043,907.03} = \mathbf{+6.6884\%} \approx \mathbf{+6.69\%}$$
- **Modelo Corrector ML:**
  - $\sum |y_i^{\text{real}} - \hat{y}_i^{\text{corregido}}| = 76,001.35 \text{ unidades}$
  $$\text{WAPE}_{\text{modelo}} = \frac{76,001.35}{1,043,907.03} = \mathbf{7.2805\%} \approx \mathbf{7.28\%}$$
  - $\sum (y_i^{\text{real}} - \hat{y}_i^{\text{corregido}}) = +7,185.34 \text{ unidades}$
  $$\text{Bias}_{\text{modelo}} = \frac{+7,185.34}{1,043,907.03} = \mathbf{+0.6883\%} \approx \mathbf{+0.69\%}$$
- **Diferencial de Rendimiento:**
  $$\Delta \text{WAPE} = 7.2805\% - 20.7295\% = \mathbf{-13.4490 \text{ pp}} \quad \left( \frac{-13.4490}{20.7295} \times 100\% = \mathbf{-64.88\%} \right)$$
  $$\Delta \text{Pérdida Asimétrica} = 13.26\% - 41.30\% = \mathbf{-28.04 \text{ pp}} \quad (\mathbf{-67.89\% \text{ en costo logístico}})$$

---

## 2. Métricas y Resultados Cuantitativos Clave

La validación se ejecutó mediante un **Rolling-Origin Backtest** estricto con ventana de calentamiento inicial de 28 días (4 semanas completas), evaluando 31 fechas continuas de emisión y un total de **708 pronósticos fuera de muestra (*out-of-time*)** sin filtración de información futura (*zero data leakage*).

### 1.1. Comparativa Global: Modelo Corrector vs Baseline Oficial

| Métrica | Baseline Oficial | Modelo Corrector ML | Impacto Absoluto | Impacto Relativo |
| :--- | :---: | :---: | :---: | :---: |
| **WAPE (%)** | **20.73%** | **7.28%** | **-13.45 pp** | **-64.88% de reducción de error** |
| **Bias (%)** | **+6.69%** | **+0.69%** | **-6.00 pp** | **Erradicación del sesgo estructural** |
| **MAE (unidades)** | 305.21 | 107.20 | -198.01 unid. | -64.88% |
| **RMSE (unidades)** | 404.89 | 164.26 | -240.63 unid. | -59.43% |
| **Pérdida Asimétrica (Costo Logístico)** | **41.30%** | **13.26%** | **-28.04 pp** | **-67.89% en penalización de fletes** |

### 1.2. Comparativa por Centro de Distribución (CD)

| Centro de Distribución | WAPE Baseline | WAPE Modelo | Delta WAPE (pp) | Bias Baseline | Bias Modelo | Diagnóstico del Ajuste |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **CD_SUR** | 31.14% | **6.48%** | **-24.66 pp** | +31.14% | **-0.15%** | Corrección masiva del sesgo de subestimación |
| **CD_ESTE** | 26.44% | **8.08%** | **-18.36 pp** | +25.87% | **+2.98%** | Corrección estructural del sesgo positivo |
| **CD_PACIFICO** | 23.14% | **5.72%** | **-17.43 pp** | -22.52% | **+0.16%** | Eliminación de sobreestimación crónica |
| **CD_OESTE** | 23.45% | **8.24%** | **-15.21 pp** | -21.95% | **-1.89%** | Eliminación de sobreestimación crónica |
| **CD_CENTRO** | 23.04% | **9.70%** | **-13.33 pp** | -19.35% | **+0.48%** | Estabilización de demanda centro |
| **CD_NORTE** | 9.59% | **6.64%** | **-2.94 pp** | +7.76% | **+1.32%** | Captura precisa del pico de martes |

### 1.3. Comparativa por Horizonte de Planificación

| Horizonte | WAPE Baseline | WAPE Modelo | Delta WAPE (pp) | Bias Baseline | Bias Modelo | Pérdida Asimétrica Base | Pérdida Asimétrica Modelo |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **D+1** | 19.33% | **5.76%** | **-13.57 pp** | +6.92% | +0.19% | 39.02% | **10.23%** |
| **D+2** | 20.35% | **6.60%** | **-13.75 pp** | +7.34% | +0.88% | 41.11% | **12.21%** |
| **D+3** | 20.45% | **7.07%** | **-13.38 pp** | +6.94% | +0.97% | 40.99% | **13.10%** |
| **D+4** | 22.98% | **9.90%** | **-13.08 pp** | +5.51% | +0.74% | 44.34% | **17.88%** |

---

## 3. Metodología e Ingeniería de Características

### 3.1. Arquitectura de Corrección Residual
En lugar de sustituir el pronóstico base por un modelo *black-box* que intente estimar la demanda absoluta desde cero, adoptamos un **enfoque complementario residual**:
$$\widehat{y}_{\text{corregido}} = \max\left(0, \; \widehat{y}_{\text{base}} + \widehat{\epsilon}\right)$$
donde $\widehat{\epsilon} = f(X)$ predice analíticamente el residuo del baseline.

**Ventajas clave para un Lead en producción:**
1. **Preservación de la lógica del negocio:** Respeta las reglas operativas ya incorporadas en el baseline y actúa quirúrgicamente sobre sus desvíos sistemáticos.
2. **Restricción de No-Negatividad Física:** El operador $\max(0, \cdot)$ garantiza que jamás se generen órdenes negativas de despacho.
3. **Estabilidad y Rapidez:** Emplea regularización $L_2$ (Ridge con $\alpha=10.0$) que previene el sobreajuste ante muestras de 60 días y produce inferencia sub-milisegundo.

### 3.2. Prevención Rigurosa de Data Leakage
Un error común en forecasting logístico es calcular medias móviles usando la fecha de despacho o la demanda del mismo día de emisión. En nuestra arquitectura:
- El pronóstico para `fecha_despacho` se emite en `fecha_emision`.
- Las métricas móviles (`mean_7d`, `mean_14d`, `mean_21d`, `std_7d`) se calculan **estrictamente con las fechas de despacho cerradas antes de `fecha_emision`** ($\text{fecha\_despacho} < \text{fecha\_emision}$).
- Cero filtración temporal: el modelo opera con la misma información que existiría en la bodega a las 06:00 AM del día de emisión.

### 3.3. Top 5 Características Más Determinantes
1. **Dummies de Centro de Distribución:** Capturan el desfase geográfico permanente (peso negativo para CD_CENTRO/CD_OESTE/CD_PACIFICO y positivo para CD_SUR/CD_ESTE).
2. **Interacciones `centro_distribucion_x_martes`:** Ajustan el pico explosivo del martes específicamente en CD_NORTE y CD_SUR.
3. **Móvil 7 días (`mean_7d`):** Provee el nivel reciente de operación del centro.
4. **Ratio Pronóstico a Media Móvil (`ratio_base_to_mean7`):** Identifica cuando el baseline se desalinea de la tendencia observada.
5. **Horizonte Numérico (`horizonte_num`):** Modula la dispersión esperada a medida que nos alejamos de D+1 a D+4.

---

## 4. Honestidad Técnica y Análisis Crítico de Limitaciones

Siguiendo las pautas del desafío, exponemos transparentemente el comportamiento del modelo:
1. **Comportamiento en D+4:**
   - Si bien el WAPE en D+4 disminuye drásticamente de 22.98% a 9.90% ($-13.08$ pp), es el horizonte con menor precisión del modelo corrector (9.90% vs 5.76% en D+1).
   - *Justificación Técnica:* A 4 días de anticipación, las órdenes que ingresan fuera de plan no han sido registradas aún en el sistema, por lo que la incertidumbre irreducible del mercado no puede eliminarse al 100% solo con datos pasados.
2. **Magnitud de Mejora en CD_NORTE:**
   - La mejora en CD_NORTE es de $2.94$ pp (de 9.59% a 6.64%), menor en magnitud comparada con CD_SUR ($-24.66$ pp).
   - *Justificación Técnica:* CD_NORTE ya contaba con un pronóstico base razonablemente calibrado (WAPE $<10\%$). El modelo corrector fue conservador y no forzó adaptaciones espurias, mejorando el error sin desestabilizar la serie.

---

## 5. Artefactos Persistidos y Suite de Pruebas

- **Tabla de Resultados:** `data/processed/backtest_results_comparison.csv` (35 filas cubriendo niveles global, centro, horizonte y cruces detallados).
- **Figuras Diagnósticas:**
  - `reports/figures/fase_04/comparativa_wape_modelo_vs_baseline.png`
  - `reports/figures/fase_04/comparativa_bias_modelo_vs_baseline.png`
  - `reports/figures/fase_04/importancia_caracteristicas_modelo.png`
  - `reports/figures/fase_04/curva_aprendizaje_rolling_origin.png`
- **Tests Unitarios:** 3 pruebas en `tests/test_models.py` (integridad de features sin leakage, ajuste del corrector, y ejecución del backtest) ejecutadas y aprobadas en 2.47s.

---

## 6. Directrices e Inputs para la Fase 5 (Gate de Resiliencia 45 Días)

1. **Requerimiento Mínimo de Muestra:**
   - Para calcular ventanas móviles de 21 días y capturar al menos 3 a 4 ciclos semanales representativos (especialmente la recurrencia del efecto martes), el modelo requiere un volumen suficiente de historia continua.
2. **Fundamento del Umbral de 45 Días:**
   - 45 días representan $\approx 6.4$ semanas completas.
   - En la Fase 5 implementaremos el `DataCoverageGate` que activará el modo seguro (fallback) para cualquier centro con menos de 45 días continuos de historial, protegiendo al negocio de errores por arranque en frío (*cold start*).
