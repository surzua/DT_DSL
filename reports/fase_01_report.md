# Reporte de Cierre: Fase 1 - Setup, Data Contract y Pipeline Base

**Fecha de Ejecución:** 2026-10-16  
**Responsable:** Data Scientist Lead  
**Estado:** COMPLETADO CON ÉXITO  

---

## 1. Fórmulas Matemáticas y Metodología de Agregación

Para garantizar paridad dimensional estricta entre las fuentes de datos y preservar la conservación de masa de la demanda, se formalizan las siguientes ecuaciones:

### 1.1. Agregación Multicanal de Demanda Real
La demanda diaria total de cada Centro de Distribución $cd \in \mathcal{C}$ en la fecha de despacho $t$ se define como la suma de las entregas físicas en los canales de venta $\mathcal{K} = \{\text{PORTAL\_WEB}, \text{AGENTE\_COMERCIAL}, \text{ATENCION\_TELEFONICA}\}$:
$$y_{cd, t}^{\text{real}} = \sum_{k \in \mathcal{K}} y_{cd, t, k}^{\text{real}}$$

**Principio de Conservación de Demanda Física:**
$$\sum_{cd \in \mathcal{C}} \sum_{t \in \mathcal{T}} y_{cd, t}^{\text{real}} \equiv \sum_{cd \in \mathcal{C}} \sum_{t \in \mathcal{T}} \sum_{k \in \mathcal{K}} y_{cd, t, k}^{\text{real}} = 2,011,978.87 \text{ unidades}$$

### 1.2. Mapeo de Horizontes y Fechas
Cada pronóstico emitido por el modelo base se genera en una fecha de emisión $t_{\text{emision}}$ para una fecha objetivo de despacho $t_{\text{despacho}}$ con un horizonte de planificación $h \in \{D+1, D+2, D+3, D+4\}$:
$$t_{\text{despacho}} = t_{\text{emision}} + \Delta h, \quad \Delta h \in \{1, 2, 3, 4\} \text{ días}$$

### 1.3. Integridad Referencial Conjuntista
Se verifica que el conjunto de centros de distribución sea idéntico en las cuatro fuentes:
$$\mathcal{C}_{\text{pedidos}} \equiv \mathcal{C}_{\text{pronostico}} \equiv \mathcal{C}_{\text{capacidad}} \equiv \mathcal{C}_{\text{plan}} = \{\text{CD\_CENTRO}, \text{CD\_ESTE}, \text{CD\_NORTE}, \text{CD\_OESTE}, \text{CD\_PACIFICO}, \text{CD\_SUR}\}$$

---

## 2. Métricas y Resultados Cuantitativos Clave

- **Entorno de Ejecución:** Python 3.12+ gestionado con `uv`, empaquetado editable mediante `hatchling` (`dt-dsl==0.1.0`), con 89 dependencias resueltas de manera determinista e instaladas en entorno virtual `.venv`.
- **Validación de Integridad Referencial:**
  - 100% de coherencia en los 6 Centros de Distribución (`CD_NORTE`, `CD_SUR`, `CD_CENTRO`, `CD_ESTE`, `CD_OESTE`, `CD_PACIFICO`) a lo largo de los 4 datasets crudos.
  - Cero valores nulos (`NaN` / `null`) detectados en los 4 archivos de entrada.
- **Volumen de Datos Procesados:**
  - `pedidos_historicos_genericos.csv`: 1,080 registros crudos $\rightarrow$ consolidados en **360 registros diarios** (60 días continuos del 2026-01-01 al 2026-03-01 $\times$ 6 CDs).
  - Conservación exacta de masa de demanda: $\sum \text{unidades\_reales\_raw} \equiv \sum \text{unidades\_reales\_agregadas}$.
  - `pronostico_demanda_generico.csv`: **1,380 registros** evaluables (D+1: 354, D+2: 348, D+3: 342, D+4: 336 registros), con cruce exacto (100% inner match) con la demanda real agregada.
  - `capacidad_logistica_generica.csv`: **360 registros** (60 días $\times$ 6 CDs).
  - `plan_entrega_clientes_generico.csv`: **739 registros** cubriendo 90 clientes únicos (15 clientes por CD) entre el 2026-01-01 y el 2026-03-01.
- **Artefactos Parquet Persistidos:**
  - `data/processed/demanda_real_agregada.parquet` (360 filas)
  - `data/processed/pronostico_base_limpio.parquet` (1,380 filas)
  - `data/processed/capacidad_logistica_limpia.parquet` (360 filas)
  - `data/processed/plan_entrega_limpio.parquet` (739 filas)
- **Calidad de Software:** 4 pruebas unitarias en `tests/test_loader.py` ejecutadas y aprobadas al 100% en `pytest`.

---

## 2. Insights de Negocio y Operaciones Logísticas

1. **Estructura Multicanal:** La demanda real proviene de 3 canales principales: `PORTAL_WEB`, `AGENTE_COMERCIAL` y `ATENCION_TELEFONICA`. El canal web representa el volumen mayoritario pero presenta una dinámica temporal distinta respecto a los pedidos asistidos por ejecutivos comerciales.
2. **Homogeneidad de Horizontes en Pronóstico:** El sistema actual emite predicciones en 4 horizontes discretos ($D+1$ a $D+4$). La reducción en cantidad de observaciones para $D+3$ y $D+4$ responde matemáticamente a la ventana finita de simulación (60 días), dado que las emisiones de finales de febrero proyectan hasta el 1 de marzo.
3. **Escalares de Capacidad Operativa:** La capacidad de transporte no es completamente plana; muestra escalonamientos sistemáticos (factor $1.25\times$ en días seleccionados), lo que sugiere habilitación de turnos extraordinarios o flota secundaria contratada previamente.

---

## 3. Anomalías, Riesgos y Limitaciones Detectadas

- **Discrepancia Temporal en Plan vs Compra:** En `plan_entrega_clientes_generico.csv`, existen 129 compras de 739 (17.46%) marcadas con `fuera_de_plan == 1`. Esto significa que los clientes desvían su día de recepción respecto al compromiso comercial, lo cual es un factor desestabilizador clave de la capacidad del CD.
- **Granularidad del Pronóstico:** El modelo base pronostica a nivel `(centro_distribucion, fecha_despacho)` y no a nivel de canal. La agregación desarrollada en `src/data/loader.py` garantiza paridad dimensional estricta para evitar sesgos por agregación asimétrica.

---

## 4. Directrices e Inputs para la Fase 2

1. **Auditoría Oficial del Baseline (Tarea 1):** Utilizar `data/processed/pronostico_base_limpio.parquet` como fuente única de verdad para computar WAPE y Bias por CD y por horizonte.
2. **Matrices de Calor de Degradación:** Contrastar el WAPE en matriz cruzada Centro $\times$ Horizonte ($D+1$ a $D+4$).
3. **Análisis de Asimetría de Pérdida:** Ponderar el impacto económico de subestimar (Bias positivo $\rightarrow$ sobrecosto de fletes spot y rotura de stock) vs sobreestimar (Bias negativo $\rightarrow$ costo de capital y capacidad ociosa).
4. **Congelamiento de Métricas:** Generar `data/processed/baseline_metrics_summary.csv` que servirá como umbral oficial inmutable contra el cual se medirá el modelo de Machine Learning en la Fase 4.
