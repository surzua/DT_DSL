# Reporte de Cierre: Fase 2 - Auditoría del Baseline y Diagnóstico de Error (Tarea 1)

**Fecha de Ejecución:** 2026-10-16  
**Responsable:** Data Scientist Lead  
**Estado:** COMPLETADO CON ÉXITO  

---

## 1. Métricas y Resultados Cuantitativos Clave

El análisis se ejecutó sobre la totalidad de los 1,380 pronósticos emitidos por el modelo base entre el 2026-01-01 y el 2026-02-28, evaluados frente a las 2,011,979 unidades físicas reales despachadas.

### 1.1. Métricas Globales Oficiales (Baseline Frozen)
- **WAPE Global:** **20.84%** (0.2084)
- **Bias Global:** **+6.55%** (+0.0655) $\implies$ Subestimación neta agregada
- **MAE Global:** **303.89** unidades
- **RMSE Global:** **402.19** unidades
- **Pérdida Asimétrica (Penalización $2.5\times$ subestimación vs $1.0\times$ sobreestimación):** **41.39%**

### 1.2. Desempeño por Horizonte de Planificación
A medida que la ventana temporal de predicción se aleja, se evidencia una clara degradación del error:

| Horizonte | WAPE (%) | Bias (%) | MAE (unid.) | RMSE (unid.) | Pérdida Asimétrica | Unidades Reales | Obs. |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **D+1** | **19.77%** | +6.94% | 288.21 | 361.42 | 39.80% | 516,024 | 354 |
| **D+2** | **20.30%** | +7.56% | 295.60 | 384.41 | 41.19% | 506,799 | 348 |
| **D+3** | **20.85%** | +6.40% | 303.69 | 416.51 | 41.28% | 498,206 | 342 |
| **D+4** | **22.53%** | +5.24% | 329.18 | 443.95 | 43.36% | 490,949 | 336 |

### 1.3. Desempeño por Centro de Distribución (CD)
Se detectan patrones bipolares extremos en el sesgo según el territorio geográfico:

| Centro de Distribución | WAPE (%) | Bias (%) | Diagnóstico Estructural | Unidades Reales | % Volumen Total |
| :--- | :---: | :---: | :--- | :---: | :---: |
| **CD_NORTE** | **9.82%** | **+7.47%** | Subestimación moderada pero sistemática | 705,833 | 35.08% |
| **CD_SUR** | **31.56%** | **+31.56%** | **Subestimación severa unidireccional (100% de los días)** | 510,826 | 25.39% |
| **CD_ESTE** | **25.86%** | **+25.30%** | **Subestimación severa casi pura** | 183,209 | 9.11% |
| **CD_CENTRO** | **23.28%** | **-20.21%** | **Sobreestimación crónica** | 346,514 | 17.22% |
| **CD_OESTE** | **23.90%** | **-22.66%** | **Sobreestimación crónica** | 113,037 | 5.62% |
| **CD_PACIFICO** | **22.15%** | **-21.58%** | **Sobreestimación crónica** | 152,560 | 7.58% |

### 1.4. Matrices Cruzadas (Centro $\times$ Horizonte)

#### Matriz WAPE (%)
| Centro / Horizonte | D+1 | D+2 | D+3 | D+4 |
| :--- | :---: | :---: | :---: | :---: |
| **CD_CENTRO** | 19.59% | 19.49% | 26.66% | 27.67% |
| **CD_ESTE** | 24.78% | 24.67% | 25.43% | 28.66% |
| **CD_NORTE** | 8.84% | 10.06% | 8.54% | 11.88% |
| **CD_OESTE** | 25.60% | 24.07% | 21.87% | 24.02% |
| **CD_PACIFICO** | 20.27% | 21.08% | 21.59% | 25.81% |
| **CD_SUR** | 31.73% | 32.33% | 31.85% | 30.27% |

#### Matriz Bias (%)
| Centro / Horizonte | D+1 | D+2 | D+3 | D+4 |
| :--- | :---: | :---: | :---: | :---: |
| **CD_CENTRO** | -19.59% | -17.58% | -20.28% | -23.53% |
| **CD_ESTE** | +24.78% | +24.67% | +24.90% | +26.89% |
| **CD_NORTE** | +8.51% | +8.67% | +6.43% | +6.21% |
| **CD_OESTE** | -25.60% | -24.07% | -20.28% | -20.54% |
| **CD_PACIFICO** | -20.27% | -20.68% | -20.84% | -24.64% |
| **CD_SUR** | +31.73% | +32.33% | +31.85% | +30.27% |

---

## 2. Respuestas Explícitas a la Tarea 1 del Desafío

### Pregunta 1: ¿Qué centros subestiman de manera consistente la demanda real y cuáles la sobreestiman?
**Respuesta:**
- **Centros que SUBESTIMAN de manera consistente (Bias $>0$):**
  1. **CD_SUR:** Presenta un **Bias de +31.56%** (idéntico a su WAPE de 31.56%), lo que demuestra matemáticamente que el pronóstico estuvo por debajo de la realidad en prácticamente el 100% de los despachos evaluados.
  2. **CD_ESTE:** Presenta un **Bias de +25.30%** (frente a un WAPE de 25.86%), con una subestimación estructural casi absoluta.
  3. **CD_NORTE:** Presenta un **Bias de +7.47%** (WAPE de 9.82%). Si bien su error relativo es el más bajo del sistema, su sesgo positivo es crítico por ser el centro de mayor volumen operativo (35.08% de la demanda total).
- **Centros que SOBREESTIMAN de manera consistente (Bias $<0$):**
  1. **CD_OESTE:** Presenta un **Bias de -22.66%** (WAPE de 23.90%). Pronostica persistentemente más volumen del que el mercado demanda.
  2. **CD_PACIFICO:** Presenta un **Bias de -21.58%** (WAPE de 22.15%).
  3. **CD_CENTRO:** Presenta un **Bias de -20.21%** (WAPE de 23.28%).

### Pregunta 2: ¿Cómo se degrada la precisión del pronóstico (WAPE) a medida que la ventana temporal se extiende de D+1 a D+4?
**Respuesta:**
- El WAPE global sufre una **degradación monótona creciente**:
  - Pasa de **19.77% en D+1** a **20.30% en D+2**, **20.85% en D+3**, y alcanza **22.53% en D+4**.
  - Esto representa un deterioro absoluto de **+2.76 puntos porcentuales**, equivalente a un **aumento relativo del error del +13.93%**.
- La degradación es especialmente aguda en **CD_CENTRO** (pasa de 19.59% en D+1 a 27.67% en D+4, $+8.08$ pp de pérdida de precisión) y en **CD_PACIFICO** (de 20.27% en D+1 a 25.81% en D+4, $+5.54$ pp).
- La causa operativa subyacente es la falta de visibilidad de las órdenes de compra de último momento que ingresan entre D-2 y D-1, afectando con mayor severidad a los horizontes lejanos.

---

## 3. Insights de Negocio y Criterio Lead: Asimetría de Costo

En operaciones logísticas B2B de consumo masivo, **el error no es simétrico**:
1. **Subestimar (Bias $>0$):** Genera quiebres de inventario en picking, incapacidad de carga en los camiones contratados en contrato marco y fuerza a la operación a salir al mercado a contratar **fletes spot de última hora con sobrecostos del 150% al 300%**, arriesgando además penalizaciones por SLA de entrega (OTIF).
2. **Sobreestimar (Bias $<0$):** Conlleva capacidad de bodega reservada no utilizada y camiones despachados con factor de ocupación subóptimo, con un costo unitario significativamente menor que un flete de emergencia.
3. **Peligro Crítico en el Baseline Actual:**
   - Los centros que subestiman (CD_NORTE, CD_SUR y CD_ESTE) representan el **69.58% del volumen total de carga de la compañía**.
   - Por esta razón, la **Pérdida Asimétrica Operativa calculada asciende a 41.39%**, duplicando el WAPE nominal de 20.84%.

---

## 4. Artefactos Persistidos y Suite de Pruebas

- **Métrica Serializada:** `data/processed/baseline_metrics_summary.csv` (35 filas cubriendo niveles global, centro, horizonte y cruces).
- **Figuras Diagnósticas:**
  - `reports/figures/fase_02/heatmap_wape_centro_horizonte.png`
  - `reports/figures/fase_02/heatmap_bias_centro_horizonte.png`
  - `reports/figures/fase_02/degradacion_temporal_wape.png`
  - `reports/figures/fase_02/distribucion_errores_por_centro.png`
- **Tests Unitarios:** 4 pruebas en `tests/test_metrics.py` (cálculos matemáticos, asimetría de pérdida, integridad del baseline) ejecutadas con éxito en 0.85s.

---

## 5. Directrices e Inputs para las Fases Siguientes

1. **Para Fase 3 (Plan de Entrega y Capacidad):**
   - Evaluar si la sobreestimación en CD_CENTRO, CD_OESTE y CD_PACIFICO proviene de clientes con planes inflados que luego cancelan o reducen pedidos.
   - Contrastar los picos de demanda en CD_SUR y CD_NORTE contra la capacidad máxima diaria para medir cuántas veces se desbordó la capacidad.
2. **Para Fase 4 (Modelo Corrector ML):**
   - El baseline WAPE a batir queda fijado en **20.84% global** (D+1: 19.77%, D+2: 20.30%, D+3: 20.85%, D+4: 22.53%).
   - Se debe incorporar un sesgo correctivo diferenciado: correcciones aditivas positivas para CD_SUR/CD_ESTE/CD_NORTE y negativas para CD_CENTRO/CD_OESTE/CD_PACIFICO.
   - La función objetivo del modelo de corrección debe calibrarse con penalización asimétrica o MAE/Huber para mitigar el sesgo positivo.
