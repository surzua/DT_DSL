# Reporte de Cierre: Fase 4 - Ingeniería de Características, Modelo Corrector y Rolling Backtest (Tarea 3)

**Fecha de Ejecución:** 2026-10-16  
**Responsable:** Data Scientist Lead  
**Estado:** COMPLETADO CON ÉXITO  

---

## 1. Métricas y Resultados Cuantitativos Clave

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

## 2. Metodología e Ingeniería de Características

### 2.1. Arquitectura de Corrección Residual
En lugar de sustituir el pronóstico base por un modelo *black-box* que intente estimar la demanda absoluta desde cero, adoptamos un **enfoque complementario residual**:
$$\widehat{y}_{\text{corregido}} = \max\left(0, \; \widehat{y}_{\text{base}} + \widehat{\epsilon}\right)$$
donde $\widehat{\epsilon} = f(X)$ predice analíticamente el residuo del baseline.

**Ventajas clave para un Lead en producción:**
1. **Preservación de la lógica del negocio:** Respeta las reglas operativas ya incorporadas en el baseline y actúa quirúrgicamente sobre sus desvíos sistemáticos.
2. **Restricción de No-Negatividad Física:** El operador $\max(0, \cdot)$ garantiza que jamás se generen órdenes negativas de despacho.
3. **Estabilidad y Rapidez:** Emplea regularización $L_2$ (Ridge con $\alpha=10.0$) que previene el sobreajuste ante muestras de 60 días y produce inferencia sub-milisegundo.

### 2.2. Prevención Rigurosa de Data Leakage
Un error común en forecasting logístico es calcular medias móviles usando la fecha de despacho o la demanda del mismo día de emisión. En nuestra arquitectura:
- El pronóstico para `fecha_despacho` se emite en `fecha_emision`.
- Las métricas móviles (`mean_7d`, `mean_14d`, `mean_21d`, `std_7d`) se calculan **estrictamente con las fechas de despacho cerradas antes de `fecha_emision`** ($\text{fecha\_despacho} < \text{fecha\_emision}$).
- Cero filtración temporal: el modelo opera con la misma información que existiría en la bodega a las 06:00 AM del día de emisión.

### 2.3. Top 5 Características Más Determinantes
1. **Dummies de Centro de Distribución:** Capturan el desfase geográfico permanente (peso negativo para CD_CENTRO/CD_OESTE/CD_PACIFICO y positivo para CD_SUR/CD_ESTE).
2. **Interacciones `centro_distribucion_x_martes`:** Ajustan el pico explosivo del martes específicamente en CD_NORTE y CD_SUR.
3. **Móvil 7 días (`mean_7d`):** Provee el nivel reciente de operación del centro.
4. **Ratio Pronóstico a Media Móvil (`ratio_base_to_mean7`):** Identifica cuando el baseline se desalinea de la tendencia observada.
5. **Horizonte Numérico (`horizonte_num`):** Modula la dispersión esperada a medida que nos alejamos de D+1 a D+4.

---

## 3. Honestidad Técnica y Análisis Crítico de Limitaciones

Siguiendo las pautas del desafío, exponemos transparentemente el comportamiento del modelo:
1. **Comportamiento en D+4:**
   - Si bien el WAPE en D+4 disminuye drásticamente de 22.98% a 9.90% ($-13.08$ pp), es el horizonte con menor precisión del modelo corrector (9.90% vs 5.76% en D+1).
   - *Justificación Técnica:* A 4 días de anticipación, las órdenes que ingresan fuera de plan no han sido registradas aún en el sistema, por lo que la incertidumbre irreducible del mercado no puede eliminarse al 100% solo con datos pasados.
2. **Magnitud de Mejora en CD_NORTE:**
   - La mejora en CD_NORTE es de $2.94$ pp (de 9.59% a 6.64%), menor en magnitud comparada con CD_SUR ($-24.66$ pp).
   - *Justificación Técnica:* CD_NORTE ya contaba con un pronóstico base razonablemente calibrado (WAPE $<10\%$). El modelo corrector fue conservador y no forzó adaptaciones espurias, mejorando el error sin desestabilizar la serie.

---

## 4. Artefactos Persistidos y Suite de Pruebas

- **Tabla de Resultados:** `data/processed/backtest_results_comparison.csv` (35 filas cubriendo niveles global, centro, horizonte y cruces detallados).
- **Figuras Diagnósticas:**
  - `reports/figures/fase_04/comparativa_wape_modelo_vs_baseline.png`
  - `reports/figures/fase_04/comparativa_bias_modelo_vs_baseline.png`
  - `reports/figures/fase_04/importancia_caracteristicas_modelo.png`
  - `reports/figures/fase_04/curva_aprendizaje_rolling_origin.png`
- **Tests Unitarios:** 3 pruebas en `tests/test_models.py` (integridad de features sin leakage, ajuste del corrector, y ejecución del backtest) ejecutadas y aprobadas en 2.47s.

---

## 5. Directrices e Inputs para la Fase 5 (Gate de Resiliencia 45 Días)

1. **Requerimiento Mínimo de Muestra:**
   - Para calcular ventanas móviles de 21 días y capturar al menos 3 a 4 ciclos semanales representativos (especialmente la recurrencia del efecto martes), el modelo requiere un volumen suficiente de historia continua.
2. **Fundamento del Umbral de 45 Días:**
   - 45 días representan $\approx 6.4$ semanas completas.
   - En la Fase 5 implementaremos el `DataCoverageGate` que activará el modo seguro (fallback) para cualquier centro con menos de 45 días continuos de historial, protegiendo al negocio de errores por arranque en frío (*cold start*).
