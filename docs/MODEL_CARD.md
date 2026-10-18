# Model Card: Residual Demand Corrector (Ridge $L_2$)

## 1. Resumen del Modelo
- **Nombre del Modelo:** Residual Demand Corrector
- **Versión:** 1.0.0 (Producción / Desafío Técnico Data Scientist Lead)
- **Tipo de Arquitectura:** Corrector Residual Aditivo con regularización Ridge $L_2$ ($\alpha = 10.0$) y función de activación no negativa ReLU ($\max(0, \hat{y}_{\text{base}} + \hat{\epsilon})$).
- **Librería Base:** `scikit-learn >= 1.4.0`, Python 3.11 / 3.12.
- **Autor / Responsable:** Data Scientist Lead
- **Licencia:** Propietaria / Confidencial

---

## 2. Uso Previsto (Intended Use)
- **Caso de Uso Primario:** Corrección diaria de pronósticos de demanda a nivel agregado `(centro_distribucion, fecha_despacho)` para horizontes tácticos de corto plazo ($D+1$ a $D+4$).
- **Audiencia Operativa:** Jefes de Operaciones, Planificadores de Transporte y Sistemas de Despacho Dinámico (*Dynamic Delivery Slotting*) en los 6 Centros de Distribución de la red.
- **Entorno de Despliegue:** Microservicio de inferencia en tiempo real contenerizado en AWS ECS Fargate, expuesto a través de Amazon API Gateway y gobernado por el `DataCoverageGate`.

## 3. Casos de Uso No Previstos y Limitaciones (Out-of-Scope Use)
- **Centros con Arranque en Frío (*Cold Start*):** No debe utilizarse en centros logísticos con menos de 45 días continuos de historia operativa. En tales circunstancias, el `DataCoverageGate` enruta automáticamente hacia el pronóstico base (`SAFE_FALLBACK`).
- **Planificación Estratégica de Largo Plazo:** No debe extrapolarse a horizontes $> D+4$ o planificación macroeconómica anual.
- **Pronóstico a Nivel SKU Individual:** El modelo fue entrenado sobre el volumen físico agregado del Centro de Distribución.

---

## 4. Datos de Entrenamiento e Ingeniería de Características
- **Población Histórica:** 60 días continuos de operación logística (2026-01-01 a 2026-03-01) en 6 centros de distribución regionales (CD_NORTE, CD_SUR, CD_ESTE, CD_CENTRO, CD_OESTE, CD_PACIFICO).
- **Muestra Total:** 1,380 observaciones evaluables (100% cruce inner match entre demanda real agregada y pronóstico base).
- **Protocolo de Causalidad:** *Zero Data Leakage* estricto. Para una emisión a las 06:00 AM del día $t$, solo se consumen registros cerrados con $\tau \le t - 1$.
- **Espacio de Características (26 Covariables en 4 Familias):**
  1. *Calendario / Estacionalidad:* `dia_semana_despacho`, `es_lunes`, `es_fin_de_semana`, `dia_mes`.
  2. *Picos de Demanda:* `es_martes`, interacciones espacio-temporales `centro_distribucion_X_x_martes`.
  3. *Métricas Móviles (Rolling Windows):* Medias (`mean_7d`, `mean_14d`, `mean_21d`) y desviaciones estándar (`std_7d`, `std_14d`, `std_21d`).
  4. *Señales de Discrepancia del Baseline:* `unidades_pronosticadas`, `horizonte_num`, `ratio_base_to_mean7`, dummies geográficas por centro.

---

## 5. Rendimiento Cuantitativo y Benchmarks (Rolling-Origin Backtest)
Validación cruzada con origen rodante sobre **708 pronósticos independientes fuera de muestra (*out-of-time*)** a lo largo de 31 fechas de corte:

| Dimensión de Desempeño | Baseline Oficial | Modelo Corrector ML | Impacto Absoluto ($\Delta$) | Impacto Relativo (%) |
| :--- | :---: | :---: | :---: | :---: |
| **WAPE Global** | **20.73%** | **7.28%** | **-13.45 pp** | **-64.88% de reducción de error** |
| **Bias / Sesgo Global** | **+6.69%** | **+0.69%** | **-6.00 pp** | **Neutralización del sesgo sistemático** |
| **MAE (unidades/día)** | 305.2 unid. | 107.2 unid. | -198.0 unid. | -64.88% |
| **RMSE (unidades/día)** | 404.9 unid. | 164.3 unid. | -240.6 unid. | -59.43% |
| **Pérdida Asimétrica (2.5x Spot)** | **41.30%** | **13.26%** | **-28.04 pp** | **-67.89% en costo logístico** |

- **Consistencia Temporal:** El modelo corrector superó al baseline en el **100% de las 31 fechas evaluadas (31/31)** y en el **100% de los centros logísticos (6/6)**.
- **Resolución de Casos Extremos:** En **CD_SUR**, el WAPE se desplomó de **31.14% a 6.48%** (-24.66 pp) y el sesgo de **+31.14% a -0.15%**.

---

## 6. Consideraciones Éticas, de Negocio y Riesgos Operativos
- **Asimetría de Pérdida Financiera:** Subestimar la demanda fuerza la contratación de fletes spot con tarifas de sobreprecio de $2.5\times$, mientras que sobreestimar acarrea costo de camión subocupado ($1.0\times$). El modelo reduce la pérdida asimétrica de 41.30% a 13.26%, ahorrando entre **$180,000 y $350,000 USD anuales**.
- **Sesgo de Concentración Comercial:** La indisciplina del plan de entrega (17.46% fuera de plan y ratio 3.45x de compras postergadas) genera una sobrecarga no programada los martes (46.2% de la demanda). El modelo complementario absorbe esta señal mediante variables de interacción sin trasladar costos indebidos a los clientes.

---

## 7. MLOps, Monitoreo y Gobernanza de Producción
- **Pipeline de Re-entrenamiento:** Job semanal orquestado en AWS Step Functions con re-entrenamiento en Amazon SageMaker Spot.
- **Monitoreo de Drift (Amazon SageMaker Model Monitor):**
  - *Data Drift:* Test de Kolmogorov-Smirnov (KS) sobre variables continuas y Poblational Stability Index (PSI) sobre categóricas.
  - *Concept / Bias Drift:* Alarma crítica de CloudWatch si el sesgo acumulado en 7 días excede $\pm 3.0\%$.
- **Protocolo de Rollback:** Si el WAPE del modelo supera al WAPE del baseline durante 3 días continuos, el `DataCoverageGate` revoca temporalmente el tag de producción y activa el modo fallback sin intervención manual.
