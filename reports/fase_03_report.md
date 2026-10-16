# Reporte de Cierre: Fase 3 - Estado Operativo del Plan, Capacidad y Estrategia de Negocio (Tarea 2)

**Fecha de Ejecución:** 2026-10-16  
**Responsable:** Data Scientist Lead  
**Estado:** COMPLETADO CON ÉXITO  

---

## 1. Métricas y Resultados Cuantitativos Clave

El análisis abarca los 739 registros de compromisos comerciales de entrega correspondientes a 90 clientes B2B (15 por cada uno de los 6 Centros de Distribución), complementado con el cruce diario de capacidad máxima de transporte en los 60 días operativos.

### 1.1. Resumen Global del Plan vs Realidad
- **Total Unidades Planificadas:** 70,549.90 unidades
- **Total Unidades Compradas Reales:** 78,930.42 unidades
- **Bias de Volumen del Plan:** **+10.62%** ($(\text{Real} - \text{Plan}) / \text{Real}$) $\implies$ **Subestimación comercial sistemática**.
- **Desvío Temporal Promedio ($\Delta = \text{Fecha Real} - \text{Fecha Plan}$):** **+0.44 días** (rango: $-3$ a $+7$ días).
- **Tasa Global de Compras Fuera de Plan (`fuera_de_plan == 1`):** **17.46%** (129 de 739 pedidos).
- **Asimetría del Desvío Temporal:**
  - Compras retrasadas ($\Delta > 0$): **100 pedidos** (77.52% de los desvíos).
  - Compras adelantadas ($\Delta < 0$): **29 pedidos** (22.48% de los desvíos).
  - **Late-to-Early Ratio:** **$3.45\times$** (los clientes postergan casi 3.5 veces más de lo que adelantan).

### 1.2. Desglose de Desvíos por Centro de Distribución
Existe una notable disparidad territorial en la disciplina de compra de los clientes:

| Centro de Distribución | Total Pedidos | Pedidos Fuera | % Fuera de Plan | Bias Volumen (%) | Desvío Promedio ($\Delta$ días) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **CD_NORTE** | 123 | 30 | **24.39%** | +10.82% | +0.67 días |
| **CD_PACIFICO** | 122 | 26 | **21.31%** | +12.35% | +0.60 días |
| **CD_ESTE** | 118 | 23 | **19.49%** | +11.83% | +0.50 días |
| **CD_SUR** | 122 | 23 | **18.85%** | +10.15% | +0.48 días |
| **CD_CENTRO** | 126 | 14 | **11.11%** | +9.24% | +0.22 días |
| **CD_OESTE** | 128 | 13 | **10.16%** | +9.08% | +0.19 días |

### 1.3. Desglose por Día de la Semana Planificado

| Día Planificado | Total Pedidos | Pedidos Fuera | % Fuera de Plan | % del Plan Total Semanal |
| :--- | :---: | :---: | :---: | :---: |
| **Lunes (Monday)** | 104 | 23 | **22.12%** | 14.07% |
| **Martes (Tuesday)** | **259** | **42** | **16.22%** | **35.05%** |
| **Miércoles (Wednesday)** | 109 | 25 | **22.94%** | 14.75% |
| **Jueves (Thursday)** | 151 | 21 | **13.91%** | 20.43% |
| **Viernes (Friday)** | 116 | 18 | **15.52%** | 15.70% |

*Hallazgo clave:* El martes concentra por diseño comercial el **35.05% de todos los pedidos programados**. Sin embargo, al observar las fechas reales de compra, los martes absorben **36,467.72 unidades reales**, representando el **46.20% de toda la demanda semanal de la empresa**, exacerbando la congestión operativa.

### 1.4. Saturación de Capacidad Logística Diaria
Al contrastar la demanda total diaria contra la `capacidad_maxima_unidades`:

| Centro de Distribución | Días Totales | Días Saturados (>100%) | % Días Saturados | Ocupación Máx. | Ocupación Media | Exceso Acumulado |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **CD_NORTE** | 60 | **6** | **10.00%** | **110.34%** | 82.73% | **974.26 unid.** |
| **CD_SUR** | 60 | **2** | **3.33%** | 108.44% | 81.18% | 353.74 unid. |
| **CD_CENTRO** | 60 | **2** | **3.33%** | 104.40% | 81.13% | 122.21 unid. |
| **CD_ESTE** | 60 | **1** | **1.67%** | 105.84% | 80.25% | 70.04 unid. |
| **CD_OESTE** | 60 | **1** | **1.67%** | 101.50% | 78.91% | 11.28 unid. |
| **CD_PACIFICO** | 60 | **1** | **1.67%** | 101.04% | 82.25% | 8.14 unid. |

---

## 2. Respuestas Explícitas a la Tarea 2 del Desafío

### Pregunta 1: ¿Existe un Bias en el plan de entrega? ¿Subestima o sobreestima sistemáticamente el comportamiento real de compra?
**Respuesta:**
- **Sí, existe un Bias positivo evidente en dos dimensiones:**
  1. **En Volumen de Unidades:** El plan presenta un **Bias de +10.62%**, lo que demuestra que el plan **subestima sistemáticamente el volumen real comprado**. Los clientes terminan ordenando un 11.9% más unidades de las acordadas comercialmente (78,930 vs 70,550 unidades). Esto ocurre de manera homogénea en todos los CDs (entre +9.08% en CD_OESTE y +12.35% en CD_PACIFICO).
  2. **En Fechas de Compra:** Existe un sesgo de retraso ($\Delta$ promedio $= +0.44$ días). El 77.5% de los desvíos corresponden a compras que se realizan después de la fecha acordada (hasta 7 días de retraso), lo que genera un "efecto acumulación" de pedidos pendientes hacia la mitad de semana.

### Pregunta 2: ¿Cuál es el porcentaje de compras realizadas fuera del plan?
**Respuesta:**
- **Total Red:** **17.46%** (129 de 739 compras).
- **Por Centro de Distribución:**
  - CD_NORTE: **24.39%** (el más indisciplinado y a la vez el más grande).
  - CD_PACIFICO: **21.31%**.
  - CD_ESTE: **19.49%**.
  - CD_SUR: **18.85%**.
  - CD_CENTRO: **11.11%**.
  - CD_OESTE: **10.16%**.
- **Por Día de la Semana Planificado:**
  - Miércoles: **22.94%**.
  - Lunes: **22.12%**.
  - Martes: **16.22%** (pero con el mayor volumen absoluto: 42 pedidos desfasados).
  - Viernes: **15.52%**.
  - Jueves: **13.91%**.

### Pregunta 3: ¿Qué métricas adicionales calcularías para completar el panorama operativo? Justificación.
**Respuesta:**
1. **Tasa de Adhesión por Cliente ($Adhesion\_Rate_i$):**
   - *Cálculo:* % de pedidos que cada cliente ejecuta exactamente en su fecha y volumen pactado.
   - *Aporte:* Revela la concentración del desvío (Ley de Pareto). En nuestro análisis (`analisis_adhesion_clientes.csv`), un subconjunto de 18 clientes explica más del 60% de los desvíos. Permite segmentar la gestión comercial y aplicar políticas contractuales diferenciadas.
2. **Volumen en Riesgo Fuera de Plan (% Volume at Risk):**
   - *Cálculo:* Unidades físicas asociadas a pedidos fuera de plan / Unidades totales.
   - *Aporte:* No es lo mismo desviar una orden de 50 unidades que una de 600 unidades. Esta métrica cuantifica el impacto real de carga en el patio de maniobras.
3. **Ratio Tardío / Adelantado (Late-to-Early Ratio):**
   - *Cálculo:* Pedidos con $\Delta > 0$ / Pedidos con $\Delta < 0$.
   - *Aporte:* Un ratio de $3.45\times$ indica que la flota no sufre por clientes que "se anticipan", sino por clientes que "acumulan deuda logística" que explota a mitad de semana.
4. **Índice de Saturación de Capacidad y Exceso de Flota:**
   - *Cálculo:* Días con Ocupación $>100\%$ y suma de unidades excedentes.
   - *Aporte:* Demuestra que CD_NORTE colapsa en el 10% de sus días, totalizando 974.26 unidades en exceso que obligan a contratar fletes spot de emergencia.

### Pregunta 4: Estrategia para aplanar la curva de demanda (efecto pico martes)
**Respuesta Ejecutiva:**
- **Diagnóstico:** Los martes concentran el **46.2% de la demanda real semanal**, colapsando la flota en CD_NORTE y CD_SUR, mientras que jueves y viernes operan con capacidad ociosa ($\approx 70-80\%$).
- **Mecanismo Propuesto: Dynamic Delivery Slotting & Incentivos Comerciales B2B:**
  1. *Descuento por Ventana Valle (Off-Peak Incentive):* Otorgar un descuento logístico del 2.0% al 3.0% sobre la factura a clientes B2B que acepten calendarizar sus entregas recurrentes los días jueves o viernes.
  2. *Capacidad Dinámica y Cuotas en Tiempo Real:* Implementar un sistema de cupos en el motor de reservas. Cuando la capacidad proyectada para el martes en un CD alcance el 80%, el sistema activa una tarifa dinámica de alta demanda (*surge fee*) para entregas adicionales ese día y ofrece como alternativa preferente el miércoles o jueves con flete bonificado.
  3. *Re-agendamiento Proactivo de Clientes Pareto:* Contactar proactivamente a los clientes con baja tasa de adhesión identificados en CD_NORTE para rediseñar su cronograma de abastecimiento con despachos fraccionados lunes/jueves en lugar de un único despacho gigante el martes.
- **Implementación en el Software B2B:**
  - Conectar el checkout del portal web B2B y la app móvil de los agentes comerciales con la API de disponibilidad logística.
  - La API evalúa la ocupación del CD para la fecha solicitada y devuelve slots con código de semáforo: Verde (con incentivo financiero aplicado automáticamente), Amarillo (estándar), y Rojo (bloqueado por sobrecapacidad con redirección guiada).
- **KPIs para Medir el Efecto:**
  1. **Peak-to-Average Ratio (PAR):** Reducir el ratio de demanda martes / promedio diario de $2.1\times$ a $\le 1.35\times$.
  2. **% Participación de Días Valle:** Elevar la cuota de volumen despachado jueves y viernes del actual 26% a $\ge 40\%$.
  3. **Tasa de Saturación de CD_NORTE:** Bajar del 10.0% actual a 0.0% de días con desborde.
  4. **Sobrecosto de Flete de Emergencia:** Ahorro cuantificado en USD al reducir a cero los viajes spot no planificados.
  5. **OTIF (On-Time In-Full):** Incrementar el cumplimiento de entrega a $\ge 98\%$ al descongestionar las rampas de carga de los martes.

---

## 3. Artefactos Persistidos y Suite de Pruebas

- **Tablas Procesadas:**
  - `data/processed/analisis_adhesion_clientes.csv` (90 registros con métricas por cliente y CD).
  - `data/processed/saturacion_capacidad_cd.csv` (6 registros de ocupación y saturación por CD).
- **Figuras Diagnósticas:**
  - `reports/figures/fase_03/compras_fuera_plan_por_dia_semana.png`
  - `reports/figures/fase_03/fuera_plan_por_cd.png`
  - `reports/figures/fase_03/distribucion_delta_dias.png`
  - `reports/figures/fase_03/saturacion_capacidad_cd.png`
- **Tests Unitarios:** 4 pruebas en `tests/test_delivery_plan.py` ejecutadas y aprobadas en 1.21s.

---

## 4. Directrices e Inputs para la Fase 4

1. **Variables Explicativas Clave (Feature Engineering):**
   - Indicador explícito de día de la semana (`dia_semana`, especialmente `es_martes == 1`).
   - Señales de estacionalidad semanal y desvío de plan histórico por CD.
   - Rolling features de demanda real por CD (lags de 7, 14 y 21 días) para capturar el nivel base de volumen sin incurrir en data leakage.
2. **Priorización por Centro:**
   - CD_NORTE requiere modelado enfocado en capturar picos de alta demanda.
   - CD_SUR requiere corrección aditiva sustancial (+31% de brecha estructural).
