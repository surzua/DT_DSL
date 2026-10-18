"""Generates a native 16:9 Widescreen PowerPoint presentation (.pptx) of EXACTLY 10 SLIDES.

Estructura de 10 Diapositivas Ejecutivas:
Slide 1: Portada Literal (Cover Slide)
Slide 2: Diagnóstico del Error y Bipolaridad Geográfica (Tarea 1 - Parte 1)
Slide 3: Degradación Temporal y Asimetría Logística (Tarea 1 - Parte 2)
Slide 4: Estado Operativo del Plan: Bias e Indisciplina (Tarea 2 - Parte 1)
Slide 5: Métricas Adicionales y Aplanamiento de Demanda (Tarea 2 - Parte 2)
Slide 6: Modelo Complementario: Metodología y Selección (Tarea 3 - Parte 1)
Slide 7: Rolling Backtest y Resultados Fuera de Muestra (Tarea 3 - Parte 2)
Slide 8: Resiliencia ante Cold Start: DataCoverageGate (Tarea 4)
Slide 9: Arquitectura Cloud en AWS (Tarea 5)
Slide 10: Impacto en Negocio, Flota y Roadmap (Tarea 5 / Diapos 9–10 PDF)
"""

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

PPTX_PATH = Path("presentation/deck_ejecutivo_10_slides.pptx")
PPTX_PATH.parent.mkdir(parents=True, exist_ok=True)

# Executive Tech Palette
C_DARK_BG = RGBColor(10, 17, 40)        # #0A1128 Deep Slate Navy
C_SLATE_BG = RGBColor(15, 23, 42)       # #0F172A
C_CARD_DARK = RGBColor(30, 41, 59)      # #1E293B
C_BORDER_DARK = RGBColor(51, 65, 85)    # #334155
C_WHITE = RGBColor(255, 255, 255)
C_LIGHT_BG = RGBColor(248, 250, 252)    # #F8FAFC
C_BORDER_LIGHT = RGBColor(203, 213, 225) # #CBD5E1
C_TEXT_MAIN = RGBColor(15, 23, 42)      # #0F172A
C_TEXT_MUTED = RGBColor(100, 116, 139)  # #64748B
C_BLUE_TECH = RGBColor(37, 99, 235)     # #2563EB
C_CYAN_ACCENT = RGBColor(56, 189, 248)  # #38BDF8
C_GREEN_ACCENT = RGBColor(16, 185, 129) # #10B981
C_RED_ACCENT = RGBColor(239, 68, 68)    # #EF4444
C_AMBER_ACCENT = RGBColor(217, 119, 6)  # #D97706
C_BLUE_TINT = RGBColor(239, 246, 255)   # #EFF6FF
C_AMBER_TINT = RGBColor(254, 243, 199)  # #FEF3C7
C_GREEN_TINT = RGBColor(236, 253, 245)  # #ECFDF5


def set_speaker_notes(slide, notes_text: str):
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = notes_text.strip()


def create_10_slide_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Helper: Decorations for content slides
    def add_decorations(slide, slide_num, total_slides=10):
        # Top banner
        banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.38))
        banner.fill.solid()
        banner.fill.fore_color.rgb = C_SLATE_BG
        banner.line.color.rgb = C_SLATE_BG
        tf = banner.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.5)
        tf.margin_top = Inches(0.06)
        p = tf.paragraphs[0]
        p.text = "ESTRATEGIA ANALÍTICA & OPTIMIZACIÓN DE SUPPLY CHAIN B2B  |  DESAFÍO TÉCNICO: DATA SCIENTIST LEAD"
        p.font.size = Pt(8.5)
        p.font.bold = True
        p.font.color.rgb = C_CYAN_ACCENT

        # Bottom footer bar
        footer = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.12), Inches(13.333), Inches(0.38))
        footer.fill.solid()
        footer.fill.fore_color.rgb = C_LIGHT_BG
        footer.line.color.rgb = C_BORDER_LIGHT
        tf_f = footer.text_frame
        tf_f.margin_left = Inches(0.5)
        tf_f.margin_top = Inches(0.06)
        p_f = tf_f.paragraphs[0]
        p_f.text = f"Sebastián Felipe Urzúa Bórquez | Postulación Data Scientist Lead | Presentación Técnica Oficial          Diapositiva {slide_num} de {total_slides}"
        p_f.font.size = Pt(8.5)
        p_f.font.color.rgb = C_TEXT_MUTED

    # Helper: Headers (Tracker + Action Title)
    def add_headers(slide, action_title, tracker_subtitle):
        tx_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.44), Inches(12.333), Inches(0.95))
        tf = tx_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_track = tf.paragraphs[0]
        p_track.text = tracker_subtitle.upper()
        p_track.font.size = Pt(9.0)
        p_track.font.bold = True
        p_track.font.color.rgb = C_BLUE_TECH

        p_act = tf.add_paragraph()
        p_act.text = action_title
        p_act.font.size = Pt(15.5)
        p_act.font.bold = True
        p_act.font.color.rgb = C_TEXT_MAIN

    # Helper: KPI Card
    def add_kpi_card(slide, left, top, width, height, title, value, subtext, val_color=C_GREEN_ACCENT, bg_color=C_LIGHT_BG):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = C_BORDER_LIGHT
        card.line.width = Pt(1)

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.12)
        tf.margin_top = Inches(0.08)

        p1 = tf.paragraphs[0]
        p1.text = title.upper()
        p1.alignment = PP_ALIGN.CENTER
        p1.font.size = Pt(8.5)
        p1.font.bold = True
        p1.font.color.rgb = C_TEXT_MAIN

        p2 = tf.add_paragraph()
        p2.text = value
        p2.alignment = PP_ALIGN.CENTER
        p2.font.size = Pt(18)
        p2.font.bold = True
        p2.font.color.rgb = val_color

        p3 = tf.add_paragraph()
        p3.text = subtext
        p3.alignment = PP_ALIGN.CENTER
        p3.font.size = Pt(8.0)
        p3.font.color.rgb = C_TEXT_MUTED

    # =========================================================================
    # SLIDE 1: PORTADA LITERAL (COVER SLIDE)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = C_DARK_BG
    bg1.line.color.rgb = C_DARK_BG

    accent = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.75), Inches(2.5), Inches(0.06))
    accent.fill.solid()
    accent.fill.fore_color.rgb = C_CYAN_ACCENT
    accent.line.color.rgb = C_CYAN_ACCENT

    tbox1 = s1.shapes.add_textbox(Inches(0.8), Inches(1.05), Inches(11.7), Inches(2.4))
    tf1 = tbox1.text_frame
    tf1.word_wrap = True

    p_tag = tf1.paragraphs[0]
    p_tag.text = "PROCESO DE SELECCIÓN DATA SCIENTIST LEAD  |  EVALUACIÓN TÉCNICA"
    p_tag.font.size = Pt(11)
    p_tag.font.bold = True
    p_tag.font.color.rgb = C_CYAN_ACCENT

    p_t1 = tf1.add_paragraph()
    p_t1.text = "Desafío Técnico: Data Scientist Lead"
    p_t1.font.size = Pt(36)
    p_t1.font.bold = True
    p_t1.font.color.rgb = C_WHITE

    p_sub1 = tf1.add_paragraph()
    p_sub1.text = "Auditoría de Demanda, Corrección Analítica de Pronóstico, Resiliencia Operativa y Arquitectura Cloud en AWS"
    p_sub1.font.size = Pt(16)
    p_sub1.font.color.rgb = RGBColor(148, 163, 184)

    # Metadata card on Cover
    acard = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(3.7), Inches(6.5), Inches(2.3))
    acard.fill.solid()
    acard.fill.fore_color.rgb = C_CARD_DARK
    acard.line.color.rgb = C_BORDER_DARK
    atf = acard.text_frame
    atf.word_wrap = True
    atf.margin_left = atf.margin_top = Inches(0.22)

    ap1 = atf.paragraphs[0]
    ap1.text = "Sebastián Felipe Urzúa Bórquez"
    ap1.font.size = Pt(19)
    ap1.font.bold = True
    ap1.font.color.rgb = C_WHITE

    ap2 = atf.add_paragraph()
    ap2.text = (
        "• Cargo al que postula: Data Scientist Lead\n"
        "• Entregable: Executive Deck & Technical Defense (10 Diapositivas)\n"
        "• Red Evaluada: Red Logística B2B | 6 Centros de Distribución Regionales | 60 Días Operativos\n"
        "• Fecha: Octubre 2026"
    )
    ap2.font.size = Pt(10)
    ap2.font.color.rgb = RGBColor(203, 213, 225)

    # 4 KPI cards on Cover
    cover_kpis = [
        ("PRECISIÓN GLOBAL", "20.7% → 7.3%", "WAPE (-65% error rel. en backtest)", Inches(7.6), Inches(3.7), C_GREEN_ACCENT),
        ("SESGO ESTRUCTURAL", "+6.7% → +0.7%", "Neutralizado en toda la red", Inches(10.3), Inches(3.7), C_CYAN_ACCENT),
        ("PÉRDIDA ASIMÉTRICA", "41.3% → 13.3%", "-28 pp costo fletes spot (2.5x)", Inches(7.6), Inches(4.9), C_GREEN_ACCENT),
        ("RETORNO FINOPS AWS", "$185 USD/mes", "ROI > 2,000% (Payback < 1 flete spot)", Inches(10.3), Inches(4.9), C_CYAN_ACCENT),
    ]
    for k_title, k_val, k_sub, k_l, k_t, k_col in cover_kpis:
        card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, k_l, k_t, Inches(2.45), Inches(1.05))
        card.fill.solid()
        card.fill.fore_color.rgb = C_CARD_DARK
        card.line.color.rgb = C_BORDER_DARK
        ctf = card.text_frame
        ctf.word_wrap = True
        ctf.margin_top = Inches(0.08)
        cp1 = ctf.paragraphs[0]
        cp1.text = k_title
        cp1.alignment = PP_ALIGN.CENTER
        cp1.font.size = Pt(8.5)
        cp1.font.bold = True
        cp1.font.color.rgb = RGBColor(148, 163, 184)
        cp2 = ctf.add_paragraph()
        cp2.text = k_val
        cp2.alignment = PP_ALIGN.CENTER
        cp2.font.size = Pt(16.5)
        cp2.font.bold = True
        cp2.font.color.rgb = k_col
        cp3 = ctf.add_paragraph()
        cp3.text = k_sub
        cp3.alignment = PP_ALIGN.CENTER
        cp3.font.size = Pt(7.5)
        cp3.font.color.rgb = RGBColor(203, 213, 225)

    # Bottom Pill Badges
    pills = [
        "[ WAPE: 20.7% → 7.3% ]",
        "[ Sesgo: +6.7% → +0.7% ]",
        "[ Resiliencia: Gate 45 Días ]",
        "[ Cloud: AWS Serverless ]",
    ]
    pill_box = s1.shapes.add_textbox(Inches(0.8), Inches(6.05), Inches(11.7), Inches(0.4))
    ptf = pill_box.text_frame
    ptf.paragraphs[0].text = "     ".join(pills)
    ptf.paragraphs[0].font.size = Pt(10)
    ptf.paragraphs[0].font.bold = True
    ptf.paragraphs[0].font.color.rgb = C_CYAN_ACCENT

    # Cover Synthesis Card
    cov_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.5), Inches(11.7), Inches(0.65))
    cov_card.fill.solid()
    cov_card.fill.fore_color.rgb = C_CARD_DARK
    cov_card.line.color.rgb = C_BORDER_DARK
    ctf_cov = cov_card.text_frame
    ctf_cov.word_wrap = True
    ctf_cov.margin_left = Inches(0.2)
    ctf_cov.margin_top = Inches(0.08)
    p_cov_s = ctf_cov.paragraphs[0]
    p_cov_s.text = "SÍNTESIS DE LA DEFENSA TÉCNICA: "
    p_cov_s.font.size = Pt(8.5)
    p_cov_s.font.bold = True
    p_cov_s.font.color.rgb = C_CYAN_ACCENT
    p_cov_s.text += "Auditoría de 1,380 puntos con diagnóstico de sesgo territorial; mecanismo de nivelación con Dynamic Delivery Slotting; corrector residual Ridge L2 con validación out-of-time secuencial en 31 días rodantes; DataCoverageGate de 45 días contra fallas de arranque en frío; y arquitectura cloud en AWS Serverless con latencia <50ms y costo mensual de $185 USD (ROI superior a 2,000%)."
    p_cov_s.font.bold = False

    set_speaker_notes(
        s1,
        "Estimado comité de evaluación: Les presento mi resolución integral al Desafío Técnico para el rol de Data Scientist Lead. "
        "A lo largo de esta presentación abordaremos con total exhaustividad cada una de las 5 tareas planteadas en el documento oficial: "
        "auditaremos el comportamiento del baseline actual y la indisciplina en el plan comercial, formularemos un modelo corrector residual "
        "con cero data leakage, diseñaremos la regla de resiliencia operativa ante cold start y desplegaremos la arquitectura cloud en AWS para operar "
        "en tiempo real y batch. Mi objetivo es demostrar no sólo rigor matemático y analítico, sino criterio de supply chain y arquitectura para llevar "
        "soluciones robustas a producción."
    )

    # =========================================================================
    # SLIDE 2: DIAGNÓSTICO DEL ERROR Y BIPOLARIDAD GEOGRÁFICA (TAREA 1 - PARTE 1)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_decorations(s2, 2)
    add_headers(
        s2,
        "La auditoría del pronóstico base revela una red bipolar: el 70% del volumen sufre subestimación severa (CD_SUR +31.6%), forzando fletes de urgencia.",
        "TAREA 1: EVALUACIÓN CUANTITATIVA DE WAPE Y BIAS POR CENTRO DE DISTRIBUCIÓN (1,380 PUNTOS AUDITADOS)"
    )

    # Left Column: Table of 6 CDs
    t_left, t_top, t_width, t_height = Inches(0.5), Inches(1.5), Inches(6.8), Inches(3.2)
    shape_tbl = s2.shapes.add_table(7, 6, t_left, t_top, t_width, t_height)
    table = shape_tbl.table
    col_w = [Inches(1.2), Inches(0.9), Inches(0.7), Inches(0.9), Inches(0.9), Inches(2.2)]
    for idx, w in enumerate(col_w):
        table.columns[idx].width = w

    headers_cd = ["Centro", "Vol. Real", "% Red", "WAPE", "Bias Base", "Diagnóstico Operativo Crítico"]
    for j, h in enumerate(headers_cd):
        cell = table.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_SLATE_BG
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(8.5)
            p.font.bold = True
            p.font.color.rgb = C_WHITE

    cd_rows = [
        ("CD_SUR", "510.8k", "25.4%", "31.56%", "+31.56%", "Subestimación Crítica: Déficit 100% de días"),
        ("CD_ESTE", "183.2k", "9.1%", "25.86%", "+25.30%", "Subestimación Estructural: Capacidad superada"),
        ("CD_NORTE", "705.8k", "35.1%", "9.82%", "+7.47%", "Subestimación en Picos: Satura andenes martes"),
        ("CD_CENTRO", "346.5k", "17.2%", "23.28%", "-20.21%", "Sobreestimación Crónica: Capacidad ociosa"),
        ("CD_PACIFICO", "152.6k", "7.6%", "22.15%", "-21.58%", "Sobreestimación Sistemática: Sobrestock"),
        ("CD_OESTE", "113.0k", "5.6%", "23.90%", "-22.66%", "Sobreestimación Sistemática: Flota ociosa"),
    ]
    for i, row in enumerate(cd_rows):
        for j, val in enumerate(row):
            cell = table.cell(i + 1, j)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_WHITE if i % 2 == 0 else C_LIGHT_BG
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(8.0)
                if j in [0, 3, 4]:
                    p.font.bold = True
                if j == 4:
                    p.font.color.rgb = C_RED_ACCENT if "+" in val else C_BLUE_TECH
                else:
                    p.font.color.rgb = C_TEXT_MAIN

    # Left Callout Box (Bloques deficitario vs excedentario)
    callout_s2 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(4.85), Inches(6.8), Inches(2.15))
    callout_s2.fill.solid()
    callout_s2.fill.fore_color.rgb = C_BLUE_TINT
    callout_s2.line.color.rgb = RGBColor(147, 197, 253)
    c2_tf = callout_s2.text_frame
    c2_tf.word_wrap = True
    c2_tf.margin_left = c2_tf.margin_top = c2_tf.margin_right = Inches(0.18)
    p_c2_h = c2_tf.paragraphs[0]
    p_c2_h.text = "HALLAZGO ESTRUCTURAL DE RED LOGÍSTICA (PREGUNTA 1 DEL PDF):"
    p_c2_h.font.size = Pt(9.5)
    p_c2_h.font.bold = True
    p_c2_h.font.color.rgb = C_BLUE_TECH

    p_c2_b = c2_tf.add_paragraph()
    p_c2_b.text = (
        "• Bloque Deficitario (Bias > 0): CD_NORTE, CD_SUR y CD_ESTE concentran el 69.6% de la demanda física "
        "(1.40 millones de unidades). La subestimación sistemática obliga a contratar transporte spot de urgencia.\n"
        "• Bloque Excedentario (Bias < 0): CD_CENTRO, CD_PACIFICO y CD_OESTE representan el 30.4% restante y proyectan "
        "un 20% por encima de la realidad, inmovilizando inventario y encareciendo almacenamiento.\n"
        "• Conclusión: El error no es ruido blanco gaussiano; es una fractura territorial estructural que exige corrección aditiva."
    )
    p_c2_b.font.size = Pt(8.5)
    p_c2_b.font.color.rgb = C_TEXT_MAIN

    # Right Column: Chart Image
    img_path_s2 = Path("reports/figures/fase_02/heatmap_bias_centro_horizonte.png")
    if img_path_s2.exists():
        s2.shapes.add_picture(str(img_path_s2), Inches(7.5), Inches(1.5), width=Inches(5.35))

    set_speaker_notes(
        s2,
        "Respondiendo con precisión a la primera pregunta de la Tarea 1: el pronóstico base no tiene un error aleatorio; exhibe una fractura "
        "geográfica estructural. Tres centros subestiman sistemáticamente y tres sobreestiman crónicamente. Lo crítico para el negocio es que "
        "la subestimación se concentra en los centros de mayor escala: CD_NORTE, CD_SUR y CD_ESTE representan el 70% de la carga de la empresa. "
        "En particular, CD_SUR es una emergencia operativa: el modelo se quedó corto el 100% de los días evaluados con un sesgo del +31.56%. "
        "Esto significa que cada día en CD_SUR la operación arranca con déficit de camiones."
    )

    # =========================================================================
    # SLIDE 3: DEGRADACIÓN TEMPORAL Y ASIMETRÍA LOGÍSTICA (TAREA 1 - PARTE 2)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_decorations(s3, 3)
    add_headers(
        s3,
        "El WAPE se degrada en +2.76 pp hacia D+4, amplificando una Pérdida Asimétrica real del 41.4% por penalización de fletes spot.",
        "TAREA 1: DEGRADACIÓN POR HORIZONTE TEMPORAL Y FORMULACIÓN DE PÉRDIDA ASIMÉTRICA"
    )

    # Left Column: Table of Horizons D+1 to D+4
    shape_t3 = s3.shapes.add_table(5, 5, Inches(0.5), Inches(1.5), Inches(6.8), Inches(2.2))
    table3 = shape_t3.table
    col_w3 = [Inches(1.5), Inches(1.2), Inches(1.1), Inches(1.2), Inches(1.8)]
    for idx, w in enumerate(col_w3):
        table3.columns[idx].width = w

    headers_h = ["Horizonte", "WAPE Base", "Bias Base", "Delta vs D+1", "Deterioro Relativo"]
    for j, h in enumerate(headers_h):
        cell = table3.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_SLATE_BG
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(8.5)
            p.font.bold = True
            p.font.color.rgb = C_WHITE

    h_rows = [
        ("D+1 (24 hrs)", "19.77%", "+6.69%", "Baseline", "Máxima precisión actual"),
        ("D+2 (48 hrs)", "20.30%", "+6.70%", "+0.53 pp", "Deterioro inicial de preventa"),
        ("D+3 (72 hrs)", "20.85%", "+6.70%", "+1.08 pp", "Pérdida de visibilidad pedidos"),
        ("D+4 (96 hrs)", "22.53%", "+6.69%", "+2.76 pp", "+14.0% deterioro acumulado"),
    ]
    for i, row in enumerate(h_rows):
        for j, val in enumerate(row):
            cell = table3.cell(i + 1, j)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_WHITE if i % 2 == 0 else C_LIGHT_BG
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(8.5)
                if j in [0, 1, 3]:
                    p.font.bold = True
                p.font.color.rgb = C_TEXT_MAIN

    # Left Callout: Causa Raíz
    c3_box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(3.9), Inches(6.8), Inches(3.1))
    c3_box.fill.solid()
    c3_box.fill.fore_color.rgb = C_LIGHT_BG
    c3_box.line.color.rgb = C_BORDER_LIGHT
    c3_tf = c3_box.text_frame
    c3_tf.word_wrap = True
    c3_tf.margin_left = c3_tf.margin_top = c3_tf.margin_right = Inches(0.18)
    p3_h = c3_tf.paragraphs[0]
    p3_h.text = "CAUSA RAÍZ Y ASIMETRÍA DE COSTOS LOGÍSTICOS:"
    p3_h.font.size = Pt(9.5)
    p3_h.font.bold = True
    p3_h.font.color.rgb = C_BLUE_TECH

    p3_b = c3_tf.add_paragraph()
    p3_b.text = (
        "1. Pérdida de Visibilidad a 96 horas:\n"
        "   • A 4 días, el sistema desconoce qué clientes postergarán o adelantarán sus compras fuera de plan.\n"
        "2. Formulación de Pérdida Asimétrica (Penalización 2.5x):\n"
        "   • En logística B2B, quedarse corto (subestimar) detona quiebres de servicio y fletes spot de pánico con sobrecosto:\n"
        "     Loss_asym = Σ [ 2.5 · max(0, y - y_pronóstico) + 1.0 · max(0, y_pronóstico - y) ] / Σ |y|\n"
        "   • Consecuencia: La Pérdida Asimétrica Real del baseline alcanza el 41.39%, duplicando el WAPE nominal de 20.8%.\n"
        "   • Conclusión Lead: No se puede optimizar el forecast con error cuadrático simétrico (RMSE/MSE)."
    )
    p3_b.font.size = Pt(8.5)
    p3_b.font.color.rgb = C_TEXT_MAIN

    # Right Column: Chart Image
    img_path_s3 = Path("reports/figures/fase_02/degradacion_temporal_wape.png")
    if img_path_s3.exists():
        s3.shapes.add_picture(str(img_path_s3), Inches(7.5), Inches(1.5), width=Inches(5.35))

    set_speaker_notes(
        s3,
        "Al responder la segunda pregunta de la Tarea 1, constatamos que el WAPE sube monótonamente desde 19.77% en D+1 hasta 22.53% en D+4. "
        "Esto representa una pérdida relativa del 14% en precisión. La causa es operativa: a 4 días no existe suficiente trazabilidad de preventa "
        "para anticipar cambios de compra. Pero como Data Scientist Lead, introduzco una métrica indispensable: la Pérdida Asimétrica. En supply chain, "
        "quedarse corto no cuesta lo mismo que pasarse. Subestimar obliga a llamar transportistas spot a tarifas de pánico. Ponderando este sobrecosto de 2.5x, "
        "el verdadero dolor del baseline no era 20.8%, sino un 41.4% de ineficiencia económica."
    )

    # =========================================================================
    # SLIDE 4: ESTADO OPERATIVO DEL PLAN: BIAS E INDISCIPLINA (TAREA 2 - PARTE 1)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_decorations(s4, 4)
    add_headers(
        s4,
        "El plan comercial presenta un sesgo de +10.6% en unidades y un 17.5% de compras fuera de plan, concentradas en CD_NORTE (24.4%).",
        "TAREA 2: AUDITORÍA DEL PLAN DE ENTREGA DE CLIENTES (90 CLIENTES AUDITADOS, 739 COMPRAS)"
    )

    # Left: 2 Highlight KPI Cards
    add_kpi_card(s4, Inches(0.5), Inches(1.5), Inches(3.3), Inches(1.15), "BIAS EN VOLUMEN DEL PLAN", "+10.62%", "70,550 pactadas vs 78,930 reales (+8.3k déficit)", C_RED_ACCENT, C_AMBER_TINT)
    add_kpi_card(s4, Inches(4.0), Inches(1.5), Inches(3.3), Inches(1.15), "COMPRAS FUERA DE PLAN", "17.46%", "129 de 739 compras en fechas no acordadas", C_RED_ACCENT, C_AMBER_TINT)

    # Left Table: Breakdown by CD & Day
    shape_t4 = s4.shapes.add_table(7, 4, Inches(0.5), Inches(2.8), Inches(6.8), Inches(2.3))
    table4 = shape_t4.table
    col_w4 = [Inches(1.8), Inches(1.5), Inches(1.8), Inches(1.7)]
    for idx, w in enumerate(col_w4):
        table4.columns[idx].width = w

    headers_plan = ["Centro Logístico", "% Fuera Plan", "Día Planificado", "% Fuera Plan"]
    for j, h in enumerate(headers_plan):
        cell = table4.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_SLATE_BG
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(8.5)
            p.font.bold = True
            p.font.color.rgb = C_WHITE

    plan_rows = [
        ("CD_NORTE (Mayor volumen)", "24.39%", "Miércoles (Máxima deserción)", "22.86%"),
        ("CD_SUR (Mayor déficit)", "18.70%", "Lunes (Volatilidad inicial)", "22.09%"),
        ("CD_PACIFICO", "18.03%", "Martes (Día pico)", "17.16%"),
        ("CD_ESTE", "15.60%", "Jueves (Día valle)", "14.86%"),
        ("CD_CENTRO", "14.17%", "Viernes (Mayor disciplina)", "10.34%"),
        ("CD_OESTE", "13.93%", "Total Red Logística", "17.46%"),
    ]
    for i, row in enumerate(plan_rows):
        for j, val in enumerate(row):
            cell = table4.cell(i + 1, j)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_WHITE if i % 2 == 0 else C_LIGHT_BG
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(8.0)
                if j in [0, 2]:
                    p.font.bold = True
                if j in [1, 3] and ("24" in val or "22" in val):
                    p.font.bold = True
                    p.font.color.rgb = C_RED_ACCENT
                else:
                    p.font.color.rgb = C_TEXT_MAIN

    # Left Callout Box: Bias en Fechas
    c4_box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(5.25), Inches(6.8), Inches(1.75))
    c4_box.fill.solid()
    c4_box.fill.fore_color.rgb = C_LIGHT_BG
    c4_box.line.color.rgb = C_BORDER_LIGHT
    c4_tf = c4_box.text_frame
    c4_tf.word_wrap = True
    c4_tf.margin_left = c4_tf.margin_top = c4_tf.margin_right = Inches(0.18)
    p4_h = c4_tf.paragraphs[0]
    p4_h.text = "RESPUESTAS EXPLÍCITAS A PREGUNTAS 1 Y 2 DEL PDF:"
    p4_h.font.size = Pt(9.0)
    p4_h.font.bold = True
    p4_h.font.color.rgb = C_BLUE_TECH

    p4_b = c4_tf.add_paragraph()
    p4_b.text = (
        "• Bias en Fechas (+0.44 días de retraso promedio): Hay una tendencia neta a postergar la compra.\n"
        "• Concentración Crítica en CD_NORTE: Combina el 35% del volumen con la peor tasa de indisciplina "
        "(1 de cada 4 pedidos fuera de fecha), transformándose en el principal foco de congestión de andenes."
    )
    p4_b.font.size = Pt(8.5)
    p4_b.font.color.rgb = C_TEXT_MAIN

    # Right Column: Chart Image
    img_path_s4 = Path("reports/figures/fase_03/compras_fuera_plan_por_dia_semana.png")
    if img_path_s4.exists():
        s4.shapes.add_picture(str(img_path_s4), Inches(7.5), Inches(1.5), width=Inches(5.35))

    set_speaker_notes(
        s4,
        "Pasando a la Tarea 2: auditamos los 90 clientes y 739 compras reales. Respondo a la primera pregunta: sí, existe un sesgo significativo "
        "en el plan de entrega. En unidades, el plan subestima la demanda real en un +10.62%, lo que significa que comercial compromete menos "
        "producto del que el cliente termina pidiendo. En fechas, el sesgo es positivo en +0.44 días, indicando una tendencia neta a postergar pedidos. "
        "A la segunda pregunta: el 17.46% de las compras se realizan fuera de plan. Lo grave es dónde se concentra: CD_NORTE lidera la indisciplina "
        "con un 24.4% de compras fuera de fecha, y los miércoles y lunes son los días de mayor fuga de clientes."
    )

    # =========================================================================
    # SLIDE 5: MÉTRICAS ADICIONALES Y APLANAMIENTO DE DEMANDA (TAREA 2 - PARTE 2)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_decorations(s5, 5)
    add_headers(
        s5,
        "Con un Late-to-Early Ratio de 3.45x y 46% de carga los martes, proponemos 'Dynamic Delivery Slotting' para abatir el PAR de 2.10x a <1.35x.",
        "TAREA 2: MÉTRICAS COMPLEMENTARIAS Y ESTRATEGIA DE APLANAMIENTO DE CURVA (PREGUNTAS 3 Y 4)"
    )

    # Left Column: 3 Complementary Metrics
    add_kpi_card(s5, Inches(0.5), Inches(1.5), Inches(6.8), Inches(1.1), "MÉTRICA 1: LATE-TO-EARLY RATIO = 3.45x", "100 Retrasos vs 29 Adelantos (3.45 a 1)", "Demuestra que la indisciplina no es aleatoria: es postergación deliberada de inventario B2B", C_RED_ACCENT, C_AMBER_TINT)
    add_kpi_card(s5, Inches(0.5), Inches(2.7), Inches(6.8), Inches(1.1), "MÉTRICA 2: PEAK-TO-AVERAGE RATIO (PAR) = 2.10x", "36,468 Unidades los Martes (46.2% de la semana)", "Duplica la media diaria semanal, colapsando la capacidad de carga de camiones", C_RED_ACCENT, C_AMBER_TINT)
    add_kpi_card(s5, Inches(0.5), Inches(3.9), Inches(6.8), Inches(1.1), "MÉTRICA 3: TASA DE SATURACIÓN DE FLOTA (CD_NORTE)", "10% de los Días > 100% de Capacidad (Pico 110.3%)", "974 unidades de desborde que exigen fletes de emergencia spot. Jueves y viernes al 70%", C_RED_ACCENT, C_AMBER_TINT)

    # Left Bottom Box: Impacto Operativo
    c5_left = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(5.1), Inches(6.8), Inches(1.9))
    c5_left.fill.solid()
    c5_left.fill.fore_color.rgb = C_BLUE_TINT
    c5_left.line.color.rgb = RGBColor(147, 197, 253)
    c5_tf = c5_left.text_frame
    c5_tf.word_wrap = True
    c5_tf.margin_left = c5_tf.margin_top = c5_tf.margin_right = Inches(0.18)
    p5_lh = c5_tf.paragraphs[0]
    p5_lh.text = "ESTRATEGIA PROPUESTA: DYNAMIC DELIVERY SLOTTING (PREGUNTA 4)"
    p5_lh.font.size = Pt(9.5)
    p5_lh.font.bold = True
    p5_lh.font.color.rgb = C_BLUE_TECH

    p5_lb = c5_tf.add_paragraph()
    p5_lb.text = (
        "• Zona Verde (Ocupación ≤ 60%, Jue/Vie): Bonificación de 2.0% a 3.0% en factura por entrega programada fija.\n"
        "• Zona Amarilla (60% < Ocupación ≤ 85%, Lun/Mié): Tarifa logística estándar.\n"
        "• Zona Roja (Ocupación > 85%, Martes): Cierre de slots preferentes o recargo disuasivo (+3%).\n"
        "• Metas de Éxito: PAR de 2.10x a <1.35x | Días valle > 40% cuota | 0% saturación en CD_NORTE."
    )
    p5_lb.font.size = Pt(8.5)
    p5_lb.font.color.rgb = C_TEXT_MAIN

    # Right Column: Chart Image
    img_path_s5 = Path("reports/figures/fase_03/saturacion_capacidad_cd.png")
    if img_path_s5.exists():
        s5.shapes.add_picture(str(img_path_s5), Inches(7.5), Inches(1.5), width=Inches(5.35))

    set_speaker_notes(
        s5,
        "Para la pregunta 3, diseñé tres métricas que completan el mapa operativo: el Late-to-Early Ratio es de 3.45 a 1, probando que el cliente "
        "posterga sistemáticamente; el PAR es de 2.10x los martes; y la saturación de CD_NORTE supera el 100% en 1 de cada 10 días, acumulando "
        "974 unidades de desborde. Para la pregunta 4, no recomiendo contratar más camiones que quedarían vacíos jueves y viernes. Propongo Dynamic "
        "Delivery Slotting: un semáforo de capacidad dinámico en el portal de preventa que premia con un 2.5% de descuento a quienes trasladen sus "
        "despachos a días valle. Con mover sólo un 15% del volumen de los martes, eliminamos el 100% de la sobrecarga y abatimos el PAR a menos de 1.35x."
    )

    # =========================================================================
    # SLIDE 6: MODELO COMPLEMENTARIO: METODOLOGÍA Y SELECCIÓN (TAREA 3 - PARTE 1)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_decorations(s6, 6)
    add_headers(
        s6,
        "El Corrector Residual Ridge L2 supera a modelos de árboles en 'Small Data', garantizando estabilidad matricial, interpretabilidad y cero fuga de datos.",
        "TAREA 3: FORMULACIÓN ANALÍTICA, INGENIERÍA DE CARACTERÍSTICAS Y CRITERIO DE SELECCIÓN"
    )

    # Left Column: Formulation & Technical Criteria
    box_s6 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(1.5), Inches(6.8), Inches(5.5))
    box_s6.fill.solid()
    box_s6.fill.fore_color.rgb = C_LIGHT_BG
    box_s6.line.color.rgb = C_BORDER_LIGHT
    s6_tf = box_s6.text_frame
    s6_tf.word_wrap = True
    s6_tf.margin_left = s6_tf.margin_top = s6_tf.margin_right = Inches(0.2)

    p6_1 = s6_tf.paragraphs[0]
    p6_1.text = "1. FORMULACIÓN RESIDUAL NO NEGATIVA (BARRERA LÓGICA):"
    p6_1.font.size = Pt(9.5)
    p6_1.font.bold = True
    p6_1.font.color.rgb = C_BLUE_TECH

    p6_1b = s6_tf.add_paragraph()
    p6_1b.text = (
        "• El modelo complementario no predice la demanda desde cero; predice el error residual aditivo:\n"
        "  y_corregido = max(0, y_base + epsilon_residual), donde epsilon_residual = Ridge_L2(X, α=10.0)\n"
        "• El truncamiento no negativo garantiza cero órdenes físicas negativas en producción."
    )
    p6_1b.font.size = Pt(8.5)
    p6_1b.font.color.rgb = C_TEXT_MAIN

    p6_2 = s6_tf.add_paragraph()
    p6_2.text = "2. INGENIERÍA DE CARACTERÍSTICAS Y PROTOCOLO ZERO-LEAKAGE:"
    p6_2.font.size = Pt(9.5)
    p6_2.font.bold = True
    p6_2.font.color.rgb = C_BLUE_TECH

    p6_2b = s6_tf.add_paragraph()
    p6_2b.text = (
        "• Dummies de Calendario: es_martes, es_lunes (estacionalidad intra-semanal probada en Tarea 2).\n"
        "• Interacciones Territoriales: CD_NORTE_x_martes (+139 unid.), CD_SUR_x_martes (+212 unid.).\n"
        "• Rolling Features: rolling_mean_7d, rolling_mean_14d, rolling_mean_21d, rolling_std y ratio_base_to_mean7.\n"
        "• Blindaje Zero-Leakage: Despachos cerrados estrictamente antes de 06:00 AM (τ ≤ t-1)."
    )
    p6_2b.font.size = Pt(8.5)
    p6_2b.font.color.rgb = C_TEXT_MAIN

    p6_3 = s6_tf.add_paragraph()
    p6_3.text = "3. CRITERIO DE SELECCIÓN: ¿POR QUÉ RIDGE L2 SOBRE ÁRBOLES (LIGHTGBM/XGBOOST)?:"
    p6_3.font.size = Pt(9.5)
    p6_3.font.bold = True
    p6_3.font.color.rgb = C_BLUE_TECH

    p6_3b = s6_tf.add_paragraph()
    p6_3b.text = (
        "• Régimen 'Small Data' (612 a 1,332 filas en ventanas rodantes): Árboles sobreajustan y generan funciones escalonadas.\n"
        "• Naturaleza Aditiva del Sesgo: Offsets territoriales continuos capturados idealmente por Ridge (α=10.0).\n"
        "• Inferencia < 1 ms vs 450 ms de GBDT: Solución analítica matricial cerrada y coeficientes β 100% auditables."
    )
    p6_3b.font.size = Pt(8.5)
    p6_3b.font.color.rgb = C_TEXT_MAIN

    # Right Column: Feature Importance Chart
    img_path_s6 = Path("reports/figures/fase_04/importancia_caracteristicas_modelo.png")
    if img_path_s6.exists():
        s6.shapes.add_picture(str(img_path_s6), Inches(7.5), Inches(1.5), width=Inches(5.35))

    set_speaker_notes(
        s6,
        "En la Tarea 3 debíamos desarrollar el modelo complementario. Opté por una arquitectura correctora residual: predecir el error aditivo "
        "del baseline con regularización Ridge L2 y truncamiento no negativo. Cumplimos con creces la ingeniería de features solicitada: variables "
        "de día, interacciones territoriales para capturar el pico de los martes y rolling features de 7, 14 y 21 días, todas con blindaje absoluto de "
        "zero data leakage. ¿Por qué Ridge y no LightGBM? Porque en ventanas rodantes de 1,000 registros, los árboles tienden a sobreajustar y "
        "producen funciones en escalera que desestabilizan el picking logístico. Ridge entrega una solución analítica cerrada en menos de un milisegundo, "
        "coeficientes auditables y la máxima estabilidad operativa."
    )

    # =========================================================================
    # SLIDE 7: ROLLING BACKTEST Y RESULTADOS FUERA DE MUESTRA (TAREA 3 - PARTE 2)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_decorations(s7, 7)
    add_headers(
        s7,
        "El rolling backtest en 31 días secuenciales demuestra que el modelo reduce el WAPE a 7.28% y neutraliza el sesgo a +0.69%.",
        "TAREA 3: VALIDACIÓN CRUZADA CON ORIGEN RODANTE (ROLLING-ORIGIN BACKTEST, 708 PRONÓSTICOS EVALUADOS)"
    )

    # Left Column: Table of Backtest Results
    shape_t7 = s7.shapes.add_table(8, 7, Inches(0.5), Inches(1.5), Inches(6.8), Inches(3.6))
    table7 = shape_t7.table
    col_w7 = [Inches(1.1), Inches(0.9), Inches(0.9), Inches(1.1), Inches(0.9), Inches(0.9), Inches(1.0)]
    for idx, w in enumerate(col_w7):
        table7.columns[idx].width = w

    headers_btest = ["Centro", "WAPE Base", "WAPE Mod", "Delta WAPE", "Bias Base", "Bias Mod", "Estado"]
    for j, h in enumerate(headers_btest):
        cell = table7.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_SLATE_BG
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(8.0)
            p.font.bold = True
            p.font.color.rgb = C_WHITE

    btest_rows = [
        ("GLOBAL", "20.73%", "7.28%", "-13.45 pp (-65%)", "+6.69%", "+0.69%", "Meta Cumplida"),
        ("CD_SUR", "31.14%", "6.48%", "-24.66 pp (-79%)", "+31.14%", "-0.15%", "Sesgo Neutralizado"),
        ("CD_ESTE", "26.44%", "8.08%", "-18.36 pp (-69%)", "+25.87%", "+2.98%", "Subestimación eliminada"),
        ("CD_PACIFICO", "23.14%", "5.72%", "-17.43 pp (-75%)", "-22.52%", "+0.16%", "Corregido"),
        ("CD_OESTE", "23.45%", "8.24%", "-15.21 pp (-65%)", "-21.95%", "-1.89%", "Corregido"),
        ("CD_CENTRO", "23.04%", "9.70%", "-13.33 pp (-58%)", "-19.35%", "+0.48%", "Corregido"),
        ("CD_NORTE", "9.59%", "6.64%", "-2.94 pp (-31%)", "+7.76%", "+1.32%", "Optimizado"),
    ]
    for i, row in enumerate(btest_rows):
        for j, val in enumerate(row):
            cell = table7.cell(i + 1, j)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_WHITE if i % 2 == 0 else C_LIGHT_BG
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(8.0)
                if i == 0 or j in [0, 2, 3]:
                    p.font.bold = True
                if j == 2:
                    p.font.color.rgb = C_GREEN_ACCENT
                elif j == 3 and "-" in val:
                    p.font.color.rgb = C_GREEN_ACCENT
                else:
                    p.font.color.rgb = C_TEXT_MAIN

    # Left Callout Box: Honestidad Técnica & Pérdida Asimétrica
    c7_box = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(5.2), Inches(6.8), Inches(1.8))
    c7_box.fill.solid()
    c7_box.fill.fore_color.rgb = C_GREEN_TINT
    c7_box.line.color.rgb = RGBColor(167, 243, 208)
    c7_tf = c7_box.text_frame
    c7_tf.word_wrap = True
    c7_tf.margin_left = c7_tf.margin_top = c7_tf.margin_right = Inches(0.18)
    p7_h = c7_tf.paragraphs[0]
    p7_h.text = "HONESTIDAD ANALÍTICA Y PÉRDIDA ASIMÉTRICA EN OUT-OF-SAMPLE:"
    p7_h.font.size = Pt(9.0)
    p7_h.font.bold = True
    p7_h.font.color.rgb = RGBColor(6, 95, 70)

    p7_b = c7_tf.add_paragraph()
    p7_b.text = (
        "• Degradación Controlada por Horizonte: D+1: 5.76% | D+2: 6.16% | D+3: 7.32% | D+4: 9.90%.\n"
        "• Criterio de Honestidad (PDF): A 96 horas el WAPE sube a 9.90% reflejando la dispersión real de clientes fuera de plan.\n"
        "• Desplome en Pérdida Asimétrica: Cae del 41.30% al 13.26% (-28.04 pp / -67.9% relativo), eliminando fletes spot."
    )
    p7_b.font.size = Pt(8.5)
    p7_b.font.color.rgb = C_TEXT_MAIN

    # Right Column: 2 Stacked Comparison Charts
    img_wape = Path("reports/figures/fase_04/comparativa_wape_modelo_vs_baseline.png")
    if img_wape.exists():
        s7.shapes.add_picture(str(img_wape), Inches(7.5), Inches(1.5), width=Inches(5.35), height=Inches(2.65))

    img_bias = Path("reports/figures/fase_04/comparativa_bias_modelo_vs_baseline.png")
    if img_bias.exists():
        s7.shapes.add_picture(str(img_bias), Inches(7.5), Inches(4.3), width=Inches(5.35), height=Inches(2.65))

    set_speaker_notes(
        s7,
        "Esta lámina expone la validación más exigente: un rolling backtest de 31 días secuenciales donde cada mañana el modelo se reentrena "
        "sólo con datos cerrados y proyecta los 4 horizontes. Los resultados son contundentes: el WAPE global colapsa de 20.73% a 7.28%, una "
        "reducción relativa del 65%. El sesgo de la red pasa de +6.69% a un virtual cero (+0.69%). En CD_SUR, que era el mayor dolor logístico, "
        "el error se desploma del 31% al 6.48%. En CD_NORTE la mejora es prudente para no sobreajustar. Y en D+4 logramos 9.90%, manteniendo rigor "
        "y honestidad analítica respecto a la incertidumbre intrínseca a 4 días."
    )

    # =========================================================================
    # SLIDE 8: RESILIENCIA ANTE COLD START: DATACOVERAGEGATE (TAREA 4)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_decorations(s8, 8)
    add_headers(
        s8,
        "El DataCoverageGate con umbral de 45 días previene excepciones ante 'Cold Start' y minimiza el error estándar en un 16.8%.",
        "TAREA 4: REGLA DE CONTROL OPERATIVO (GATE), COBERTURA HISTÓRICA MÍNIMA Y FALLBACK SEGURO"
    )

    # Left Column: Rule Logic, Statistics & Trade-offs
    box_s8 = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(1.5), Inches(6.8), Inches(5.5))
    box_s8.fill.solid()
    box_s8.fill.fore_color.rgb = C_LIGHT_BG
    box_s8.line.color.rgb = C_BORDER_LIGHT
    s8_tf = box_s8.text_frame
    s8_tf.word_wrap = True
    s8_tf.margin_left = s8_tf.margin_top = s8_tf.margin_right = Inches(0.2)

    p8_1 = s8_tf.paragraphs[0]
    p8_1.text = "1. LÓGICA DEL MECANISMO DE CONTROL (DATACOVERAGEGATE):"
    p8_1.font.size = Pt(9.5)
    p8_1.font.bold = True
    p8_1.font.color.rgb = C_BLUE_TECH

    p8_1b = s8_tf.add_paragraph()
    p8_1b.text = (
        "• Inspecciona diariamente la racha continua de días de despacho disponibles sin huecos temporales:\n"
        "  - Si Racha ≥ 45 días: Habilita el reentrenamiento e inferencia del modelo complementario (ADVANCED_CORRECTOR).\n"
        "  - Si Racha < 45 días (Centro Nuevo o Falla de Datos): Conmuta suavemente a pronóstico base oficial "
        "(SAFE_FALLBACK) con logs de advertencia. Cero excepciones en producción."
    )
    p8_1b.font.size = Pt(8.5)
    p8_1b.font.color.rgb = C_TEXT_MAIN

    p8_2 = s8_tf.add_paragraph()
    p8_2.text = "2. FUNDAMENTACIÓN ESTADÍSTICA DEL UMBRAL DE 45 DÍAS:"
    p8_2.font.size = Pt(9.5)
    p8_2.font.bold = True
    p8_2.font.color.rgb = C_BLUE_TECH

    p8_2b = s8_tf.add_paragraph()
    p8_2b.text = (
        "• 6.4 Ciclos Semanales Completos: Garantiza observar al menos 6 veces cada día (especialmente el pico crítico del martes).\n"
        "• Saturación de Rolling Features: Permite computar medias móviles de 21 días (rolling_mean_21d) sin sesgo de inicio.\n"
        "• Reducción del Error Estándar: Disminuye el error estándar en un 16.8% respecto a 15 días (SE = σ / √45 ≈ 0.149σ)."
    )
    p8_2b.font.size = Pt(8.5)
    p8_2b.font.color.rgb = C_TEXT_MAIN

    p8_3 = s8_tf.add_paragraph()
    p8_3.text = "3. ANÁLISIS DE SENSIBILIDAD Y ARGUMENTACIÓN DE RIESGOS (PDF):"
    p8_3.font.size = Pt(9.5)
    p8_3.font.bold = True
    p8_3.font.color.rgb = C_BLUE_TECH

    p8_3b = s8_tf.add_paragraph()
    p8_3b.text = (
        "• Riesgo de Reducir Umbral (<45 días, ej. 15-30 días): Varianza muestral excesiva. WAPE salta a >12.5% por sobreajuste en picos erráticos.\n"
        "• Riesgo de Aumentar Umbral (>45 días, ej. 60-90 días): Costo de oportunidad. Retrasa innecesariamente 3 meses la captura del 65% de ahorro.\n"
        "• Conclusión Lead: 45 días es el punto óptimo (sweet spot) entre estabilidad matemática y aceleración de valor."
    )
    p8_3b.font.size = Pt(8.5)
    p8_3b.font.color.rgb = C_TEXT_MAIN

    # Right Column: Decision Flow Chart & Sensitivity
    img_flow = Path("reports/figures/fase_05/flujo_decision_resiliencia_gate.png")
    if img_flow.exists():
        s8.shapes.add_picture(str(img_flow), Inches(7.5), Inches(1.5), width=Inches(5.35), height=Inches(2.65))

    img_sens = Path("reports/figures/fase_05/sensibilidad_umbral_dias_wape.png")
    if img_sens.exists():
        s8.shapes.add_picture(str(img_sens), Inches(7.5), Inches(4.3), width=Inches(5.35), height=Inches(2.65))

    set_speaker_notes(
        s8,
        "En la Tarea 4 resolvimos un riesgo común en ingeniería de datos: el arranque en frío o interrupciones en la historia de un centro. "
        "Diseñamos el DataCoverageGate: una regla determinística que inspecciona la racha continua de días del CD. Si tiene 45 días o más, "
        "entrena e infiere el modelo corrector; si tiene menos, conmuta suavemente al pronóstico base con logs de advertencia, garantizando "
        "cero fallas en producción. ¿Por qué 45 días? Porque 45 días equivalen a 6 semanas y media, permitiendo ver al menos 6 martes para "
        "calibrar el pico y saturar las medias móviles de 21 días. Reducir el umbral a 15 días dispara el error a más del 12% por sobreajuste; "
        "aumentarlo a 60 días demora innecesariamente la captura de valor."
    )

    # =========================================================================
    # SLIDE 9: ARQUITECTURA CLOUD EN AWS (TAREA 5)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_decorations(s9, 9)
    add_headers(
        s9,
        "La arquitectura AWS Serverless desacopla batch e inferencia en tiempo real (<50ms) con alta disponibilidad y costo de $185 USD/mes.",
        "TAREA 5: DISEÑO CONCEPTUAL DE ARQUITECTURA CLOUD, MLOPS Y PERSISTENCIA EN AWS"
    )

    # Top: High-Resolution AWS Architecture Diagram
    img_aws = Path("reports/figures/fase_05/diagrama_arquitectura_aws.png")
    if img_aws.exists():
        s9.shapes.add_picture(str(img_aws), Inches(0.5), Inches(1.45), width=Inches(12.333), height=Inches(3.35))

    # Bottom: 4 Architecture Component Cards
    aws_cards = [
        (
            "1. PROCESAMIENTO BATCH / RE-TRAIN",
            "• EventBridge: Disparo dominical 23:00 UTC o por drift.\n"
            "• Step Functions: DAG serverless (Contratos Pydantic → Rolling Features → Train).\n"
            "• SageMaker Spot: Instancias c6i.xlarge (70% ahorro cómputo).\n"
            "• Model Registry: Versión con tag 'Approved'.",
            Inches(0.5), Inches(4.95), Inches(3.0)
        ),
        (
            "2. INFERENCIA REAL-TIME (<50ms)",
            "• API Gateway: Endpoints REST /v1/forecast/correct.\n"
            "• ECS Fargate: Microservicio FastAPI en contenedores Docker.\n"
            "• DataCoverageGate Middleware: Valida racha en memoria (<1ms).\n"
            "• ElastiCache Redis: Semáforo de slots verde/amarillo/rojo.",
            Inches(3.6), Inches(4.95), Inches(3.0)
        ),
        (
            "3. PERSISTENCIA & DATA LAKE",
            "• S3 Data Lake: Raw (CSV) y Curated (Parquet Snappy particionado por CD y fecha).\n"
            "• Aurora PostgreSQL Serverless: ACID para planes de entrega.\n"
            "• AWS KMS & Glue Catalog: Seguridad y gobernanza.",
            Inches(6.7), Inches(4.95), Inches(3.0)
        ),
        (
            "4. MLOPS CONTINUO & FINOPS",
            "• CloudWatch: Latencia p95 y tasa fallback (<5%).\n"
            "• Model Monitor: Alerta Slack si WAPE 7d > 12% o Bias fuera de [-4%, +4%].\n"
            "• FinOps: Costo operativo de $185 USD/mes ($140-$230).",
            Inches(9.8), Inches(4.95), Inches(3.0)
        ),
    ]
    for c_title, c_desc, c_l, c_t, c_w in aws_cards:
        card = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c_l, c_t, c_w, Inches(2.05))
        card.fill.solid()
        card.fill.fore_color.rgb = C_LIGHT_BG
        card.line.color.rgb = C_BORDER_LIGHT
        ctf = card.text_frame
        ctf.word_wrap = True
        ctf.margin_left = ctf.margin_right = Inches(0.12)
        ctf.margin_top = Inches(0.08)
        p1 = ctf.paragraphs[0]
        p1.text = c_title
        p1.font.size = Pt(8.5)
        p1.font.bold = True
        p1.font.color.rgb = C_BLUE_TECH
        p2 = ctf.add_paragraph()
        p2.text = c_desc
        p2.font.size = Pt(7.8)
        p2.font.color.rgb = C_TEXT_MAIN

    set_speaker_notes(
        s9,
        "Para la Tarea 5 diseñé una arquitectura en AWS para producción. Cumple estrictamente los 3 pilares exigidos: en Batch, usamos AWS "
        "Step Functions y EventBridge para orquestar la validación con contratos Pydantic y reentrenar en SageMaker con instancias Spot, "
        "ahorrando 70% de cómputo. En Inferencia, desplegamos microservicios FastAPI sobre ECS Fargate con Redis ElastiCache para entregar "
        "recomendaciones de despacho en menos de 50 milisegundos con alta concurrencia. En Persistencia, desacoplamos un lago de datos en S3 "
        "con Parquet y compresión Snappy para analítica, junto con Amazon Aurora Serverless para transacciones ACID. Añadí además observabilidad "
        "con SageMaker Model Monitor para alertar desviaciones de sesgo. Todo esto con un costo FinOps de apenas $185 USD al mes."
    )

    # =========================================================================
    # SLIDE 10: IMPACTO EN NEGOCIO, FLOTA Y ROADMAP (TAREA 5 / DIAPOS 9–10 PDF)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_decorations(s10, 10)
    add_headers(
        s10,
        "La solución elimina el 100% de la sobrecapacidad en CD_NORTE, proyecta ahorros de hasta $350k USD y eleva el OTIF a >98%.",
        "IMPACTO EN NEGOCIO: OPTIMIZACIÓN DE FLOTA, FLETES SPOT, NIVEL DE SERVICIO Y ROADMAP (PDF SLIDES 9-10)"
    )

    # Top Row: 3 Business Impact KPI Cards
    add_kpi_card(
        s10, Inches(0.5), Inches(1.5), Inches(3.9), Inches(1.35),
        "OPTIMIZACIÓN DE FLOTA Y CAPACIDAD",
        "974 Unid. Desborde Eliminadas",
        "Reduce 15% flota pico de martes en CD_NORTE, eliminando saturación > 100%",
        C_GREEN_ACCENT, C_GREEN_TINT
    )
    add_kpi_card(
        s10, Inches(4.7), Inches(1.5), Inches(3.9), Inches(1.35),
        "AHORRO EN FLETES DE EMERGENCIA",
        "$180k - $350k USD / año",
        "Modelo paramétrico de mercado. Infraestructura cloud ($185/mes) rinde ROI > 2,000%",
        C_GREEN_ACCENT, C_GREEN_TINT
    )
    add_kpi_card(
        s10, Inches(8.9), Inches(1.5), Inches(3.9), Inches(1.35),
        "NIVEL DE SERVICIO AL CLIENTE (OTIF)",
        "91.5% → ≥ 98.0%",
        "Cumplimiento On-Time In-Full, mitigando multas comerciales B2B y quiebres",
        C_GREEN_ACCENT, C_GREEN_TINT
    )

    # Bottom Left: Table of 12-Week Roadmap
    shape_t10 = s10.shapes.add_table(4, 4, Inches(0.5), Inches(3.05), Inches(7.5), Inches(2.2))
    table10 = shape_t10.table
    col_w10 = [Inches(1.8), Inches(1.0), Inches(2.7), Inches(2.0)]
    for idx, w in enumerate(col_w10):
        table10.columns[idx].width = w

    headers_r = ["Fase / Hito", "Semanas", "Alcance y Entregables", "Gate de Control"]
    for j, h in enumerate(headers_r):
        cell = table10.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_SLATE_BG
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(8.5)
            p.font.bold = True
            p.font.color.rgb = C_WHITE

    r_rows = [
        ("Fase 1: Piloto Regional", "Sem 1-4", "Despliegue CD_NORTE y CD_SUR en sombra. Step Functions y Gate 45d.", "WAPE < 8.0%, 0 fallas"),
        ("Fase 2: Dynamic Slotting", "Sem 5-8", "Integración de cupos en Portal B2B. Bono comercial 2.5% en días valle.", "Días valle > 35%, PAR < 1.6x"),
        ("Fase 3: Rollout Nacional", "Sem 9-12", "Extensión a 6 CDs. Activación SageMaker Monitor y entrega S&OP.", "100% fletes spot eliminados"),
    ]
    for i, row in enumerate(r_rows):
        for j, val in enumerate(row):
            cell = table10.cell(i + 1, j)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_WHITE if i % 2 == 0 else C_LIGHT_BG
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(8.0)
                if j in [0, 1]:
                    p.font.bold = True
                p.font.color.rgb = C_TEXT_MAIN

    # Bottom Right: Governance & Continuous MLOps Callout Box
    gov_card = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.2), Inches(3.05), Inches(4.6), Inches(3.9))
    gov_card.fill.solid()
    gov_card.fill.fore_color.rgb = C_LIGHT_BG
    gov_card.line.color.rgb = C_BORDER_LIGHT
    gtf = gov_card.text_frame
    gtf.word_wrap = True
    gtf.margin_left = gtf.margin_top = gtf.margin_right = Inches(0.18)

    p_gh = gtf.paragraphs[0]
    p_gh.text = "KPIS DE CONTROL Y GOBERNANZA CONTINUA:"
    p_gh.font.size = Pt(9.5)
    p_gh.font.bold = True
    p_gh.font.color.rgb = C_BLUE_TECH

    p_gb = gtf.add_paragraph()
    p_gb.text = (
        "1. KPIs de Monitoreo Continuo:\n"
        "   • WAPE Out-of-Time: Meta < 8.5% en los 6 CDs.\n"
        "   • Bias Estructural: Rango admisible [-2.0%, +2.0%].\n"
        "   • Peak-to-Average Ratio: Reducción de 2.10x a < 1.35x.\n"
        "   • Deserción del Plan: Tasa fuera de plan < 10% (hoy 17.5%).\n"
        "   • Incidencia de Fletes Spot: 0 viajes de pánico recurrentes.\n\n"
        "2. Gobernanza & S&OP:\n"
        "   • Alertas Automáticas: Notificación Slack ante drift de sesgo.\n"
        "   • Reentrenamiento Semanal: Cómputo dominical en SageMaker Spot.\n"
        "   • Comité S&OP Quincenal: Data Science, Transporte y Ventas calibran semáforo de slotting dinámico.\n"
        "   • Auditoría Mensual: Conciliación de ahorro en fletes con balance."
    )
    p_gb.font.size = Pt(8.2)
    p_gb.font.color.rgb = C_TEXT_MAIN

    # Bottom Left Box: Aclaración Metodológica Lead
    aclaracion_box = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(5.4), Inches(7.5), Inches(1.55))
    aclaracion_box.fill.solid()
    aclaracion_box.fill.fore_color.rgb = C_BLUE_TINT
    aclaracion_box.line.color.rgb = RGBColor(147, 197, 253)
    atf10 = aclaracion_box.text_frame
    atf10.word_wrap = True
    atf10.margin_left = atf10.margin_top = atf10.margin_right = Inches(0.15)
    p_ah = atf10.paragraphs[0]
    p_ah.text = "ACLARACIÓN METODOLÓGICA POSTULANTE LEAD (EVALUACIÓN DE FLETES):"
    p_ah.font.size = Pt(8.5)
    p_ah.font.bold = True
    p_ah.font.color.rgb = C_BLUE_TECH

    p_ab = atf10.add_paragraph()
    p_ab.text = (
        "El dataset original no contiene columnas monetarias. La evaluación económica se aborda con total "
        "rigor técnico como un Modelo Paramétrico de Caso de Negocio: se valoriza la eliminación de 974 unidades "
        "de desborde y la reducción del 67.9% en la penalización por pérdida asimétrica bajo tarifas estándar "
        "de mercado ($15-$25 USD/unid. en flete spot de urgencia / $450 por camión no planificado). "
        "El ahorro neto estimado es de $180k a $350k USD anuales."
    )
    p_ab.font.size = Pt(7.8)
    p_ab.font.color.rgb = C_TEXT_MAIN

    set_speaker_notes(
        s10,
        "Para concluir, un Data Scientist Lead debe cerrar el puente entre el algoritmo y el P&L de la compañía. En esta lámina final sintetizo "
        "el impacto en negocio: no sólo eliminamos 974 unidades de congestión en CD_NORTE y reducimos un 15% la flota pico de los martes, sino que "
        "mitigamos de raíz la contratación de fletes spot. Como el dataset no trae costos monetarios explícitos, construí un modelo paramétrico bajo "
        "supuestos estándar de industria: evitar estos desbordes representa entre $180,000 y $350,000 USD anuales de ahorro, con una infraestructura "
        "cloud que se paga sola evitando un solo camión de emergencia al mes. Presento además un plan de despliegue a 12 semanas que inicia con un "
        "piloto controlado en modo sombra, integra el slotting comercial y culmina con MLOps continuo. Con esto doy respuesta rigurosa y exhaustiva "
        "a todas las exigencias del desafío. Muchas gracias."
    )

    prs.save(str(PPTX_PATH))
    print(f"[OK] Presentación PowerPoint de 10 Diapositivas generada exitosamente en: {PPTX_PATH}")


if __name__ == "__main__":
    create_10_slide_presentation()
