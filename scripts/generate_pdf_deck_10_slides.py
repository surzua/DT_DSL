"""Generates an executive 10-slide PDF presentation deck for the Data Scientist Lead technical defense.

Calibrated to fill the entire 16:9 / Landscape Letter page (560 pt usable height)
without empty bottom halves, text overflows, or missing backgrounds.
Includes high-resolution diagram embedding and automated PNG slide previews.
"""

from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
)
from reportlab.pdfgen import canvas
import fitz  # PyMuPDF for slide rendering

PRESENTATION_DIR = Path("presentation")
PRESENTATION_DIR.mkdir(parents=True, exist_ok=True)
PDF_PATH = PRESENTATION_DIR / "deck_ejecutivo_10_slides.pdf"
PREVIEW_DIR = PRESENTATION_DIR / "slides_preview"
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

# Landscape Letter: 11 x 8.5 inches = 792 x 612 pt
PAGE_WIDTH, PAGE_HEIGHT = landscape(letter)


def draw_cover_bg(canvas_obj, doc_obj):
    """Draws full dark technological background on cover slide before flowables."""
    canvas_obj.saveState()
    # Dark Navy Base (#0A1128)
    canvas_obj.setFillColor(colors.HexColor("#0A1128"))
    canvas_obj.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

    # Subtle geometric grid / accent lines
    canvas_obj.setStrokeColor(colors.HexColor("#1E293B"))
    canvas_obj.setLineWidth(1)
    canvas_obj.line(40, PAGE_HEIGHT - 45, PAGE_WIDTH - 40, PAGE_HEIGHT - 45)
    canvas_obj.line(40, 50, PAGE_WIDTH - 40, 50)

    # Electric blue accent bar at the top
    canvas_obj.setFillColor(colors.HexColor("#2563EB"))
    canvas_obj.rect(40, PAGE_HEIGHT - 47, 160, 3, fill=1, stroke=0)

    # Watermark/footer on cover
    canvas_obj.setFillColor(colors.HexColor("#64748B"))
    canvas_obj.setFont("Helvetica-Bold", 8)
    canvas_obj.drawString(40, 32, "CONFIDENCIAL | COMITÉ EJECUTIVO DE OPERACIONES & LOGÍSTICA")
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.drawRightString(PAGE_WIDTH - 40, 32, "ENTREGABLE TÉCNICO OFICIAL | PROCESO DE SELECCIÓN")
    canvas_obj.restoreState()


def draw_content_bg(canvas_obj, doc_obj):
    """Draws subtle header/footer background bars on content slides before flowables."""
    canvas_obj.saveState()
    # Top banner bar
    canvas_obj.setFillColor(colors.HexColor("#0F172A"))
    canvas_obj.rect(0, PAGE_HEIGHT - 22, PAGE_WIDTH, 22, fill=1, stroke=0)

    # Bottom footer bar
    canvas_obj.setFillColor(colors.HexColor("#F8FAFC"))
    canvas_obj.rect(0, 0, PAGE_WIDTH, 22, fill=1, stroke=0)
    canvas_obj.setStrokeColor(colors.HexColor("#E2E8F0"))
    canvas_obj.line(0, 22, PAGE_WIDTH, 22)
    canvas_obj.restoreState()


class ExecutiveDeckCanvas(canvas.Canvas):
    """Canvas that computes total pages and prints header/footer labels in save()."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            if self._pageNumber > 1:
                self.saveState()
                # Top header texts
                self.setFillColor(colors.HexColor("#38BDF8"))
                self.setFont("Helvetica-Bold", 8)
                self.drawString(30, PAGE_HEIGHT - 15, "ESTRATEGIA ANALÍTICA & OPTIMIZACIÓN DE SUPPLY CHAIN B2B")
                self.setFillColor(colors.HexColor("#94A3B8"))
                self.setFont("Helvetica", 8)
                self.drawRightString(PAGE_WIDTH - 30, PAGE_HEIGHT - 15, "DESAFÍO TÉCNICO: DATA SCIENTIST LEAD")

                # Bottom footer texts
                self.setFillColor(colors.HexColor("#64748B"))
                self.setFont("Helvetica", 8)
                self.drawString(30, 7, "Sebastián Felipe Urzúa Bórquez | Postulación Data Scientist Lead | Presentación Técnica Oficial")
                self.drawRightString(PAGE_WIDTH - 30, 7, f"Diapositiva {self._pageNumber} de {num_pages}")
                self.restoreState()
            super().showPage()
        super().save()


def build_10_slide_deck():
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=landscape(letter),
        leftMargin=30,
        rightMargin=30,
        topMargin=26,
        bottomMargin=26,
    )

    styles = getSampleStyleSheet()

    # Typography & Styles
    action_title_style = ParagraphStyle(
        "ActionTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=13.5,
        leading=17,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=2,
    )
    tracker_style = ParagraphStyle(
        "TrackerSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#2563EB"),
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "SlideBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor("#334155"),
    )
    bold_body = ParagraphStyle(
        "SlideBoldBody",
        parent=body_style,
        fontName="Helvetica-Bold",
    )
    card_title = ParagraphStyle(
        "CardTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0F172A"),
        alignment=1,
    )
    highlight_text = ParagraphStyle(
        "HighlightText",
        parent=body_style,
        fontSize=16,
        leading=19,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#10B981"),
        alignment=1,
    )
    alert_text = ParagraphStyle(
        "AlertText",
        parent=body_style,
        fontSize=16,
        leading=19,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#EF4444"),
        alignment=1,
    )
    cyan_text = ParagraphStyle(
        "CyanText",
        parent=body_style,
        fontSize=16,
        leading=19,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#38BDF8"),
        alignment=1,
    )
    subtext_center = ParagraphStyle(
        "SubtextCenter",
        parent=body_style,
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#64748B"),
        alignment=1,
    )
    cell_text = ParagraphStyle(
        "CellText",
        parent=body_style,
        fontSize=8,
        leading=10.5,
    )
    cell_header = ParagraphStyle(
        "CellHeader",
        parent=body_style,
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.5,
        textColor=colors.white,
        alignment=1,
    )

    story = []

    # =========================================================================
    # SLIDE 1: PORTADA LITERAL (COVER SLIDE - DARK THEME)
    # =========================================================================
    story.append(Spacer(1, 28))

    cover_tag_style = ParagraphStyle(
        "CoverTag",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#38BDF8"),
    )
    story.append(Paragraph("PROCESO DE SELECCIÓN DATA SCIENTIST LEAD  |  EVALUACIÓN TÉCNICA", cover_tag_style))
    story.append(Spacer(1, 12))

    cover_h1_style = ParagraphStyle(
        "CoverH1",
        fontName="Helvetica-Bold",
        fontSize=32,
        leading=38,
        textColor=colors.white,
    )
    story.append(Paragraph("Desafío Técnico: Data Scientist Lead", cover_h1_style))
    story.append(Spacer(1, 8))

    cover_sub_style = ParagraphStyle(
        "CoverSub",
        fontName="Helvetica",
        fontSize=14,
        leading=19,
        textColor=colors.HexColor("#94A3B8"),
    )
    story.append(Paragraph("Auditoría de Demanda, Corrección Analítica de Pronóstico, Resiliencia Operativa y Arquitectura Cloud en AWS", cover_sub_style))
    story.append(Spacer(1, 24))

    # Author Card (Left) + 4 Metrics (Right)
    author_p = Paragraph(
        "<font size=16 color='#FFFFFF'><b>Sebastián Felipe Urzúa Bórquez</b></font><br/><br/>"
        "<font size=9.5 color='#CBD5E1'>"
        "• <b>Cargo al que postula:</b> Data Scientist Lead<br/>"
        "• <b>Entregable:</b> Executive Deck & Technical Defense (10 Diapositivas)<br/>"
        "• <b>Entorno Evaluado:</b> Red Logística B2B | 6 Centros de Distribución Regionales<br/>"
        "• <b>Horizonte de Análisis:</b> 60 Días Operativos (1,380 puntos auditados)<br/>"
        "• <b>Fecha de Presentación:</b> Octubre 2026"
        "</font>",
        body_style,
    )

    kpi_card_1 = [
        Paragraph("PRECISIÓN GLOBAL (WAPE)", ParagraphStyle("C1", parent=card_title, textColor=colors.HexColor("#94A3B8"))),
        Paragraph("20.7% → 7.3%", cyan_text),
        Paragraph("-65% error relativo (Backtest)", subtext_center),
    ]
    kpi_card_2 = [
        Paragraph("SESGO ESTRUCTURAL", ParagraphStyle("C2", parent=card_title, textColor=colors.HexColor("#94A3B8"))),
        Paragraph("+6.7% → +0.7%", highlight_text),
        Paragraph("Sesgo neutralizado en la red", subtext_center),
    ]
    kpi_card_3 = [
        Paragraph("PÉRDIDA ASIMÉTRICA", ParagraphStyle("C3", parent=card_title, textColor=colors.HexColor("#94A3B8"))),
        Paragraph("41.3% → 13.3%", highlight_text),
        Paragraph("-28 pp fletes spot (2.5x)", subtext_center),
    ]
    kpi_card_4 = [
        Paragraph("RETORNO FINOPS AWS", ParagraphStyle("C4", parent=card_title, textColor=colors.HexColor("#94A3B8"))),
        Paragraph("$185 USD/mes", cyan_text),
        Paragraph("ROI > 2,000% (Payback < 1 flete)", subtext_center),
    ]

    t_kpis_grid = Table([
        [kpi_card_1, kpi_card_2],
        [kpi_card_3, kpi_card_4],
    ], colWidths=[175, 175])
    t_kpis_grid.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1E293B")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#334155")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#334155")),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))

    t_mid_cover = Table([[author_p, t_kpis_grid]], colWidths=[360, 360])
    t_mid_cover.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#1E293B")),
        ("BOX", (0, 0), (0, 0), 1, colors.HexColor("#334155")),
        ("TOPPADDING", (0, 0), (0, 0), 16),
        ("BOTTOMPADDING", (0, 0), (0, 0), 16),
        ("LEFTPADDING", (0, 0), (0, 0), 18),
        ("RIGHTPADDING", (0, 0), (0, 0), 18),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(t_mid_cover)
    story.append(Spacer(1, 16))

    # Bottom Pill Badges
    pills_text = (
        "<b>[ WAPE: 20.7% → 7.3% ]</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
        "<b>[ Sesgo: +6.7% → +0.7% ]</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
        "<b>[ Resiliencia: Gate 45 Días ]</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
        "<b>[ Cloud: AWS Serverless ]</b>"
    )
    p_pills = Paragraph(pills_text, ParagraphStyle("Pills", fontName="Helvetica-Bold", fontSize=9.5, leading=13, textColor=colors.HexColor("#38BDF8"), alignment=1))
    t_pills = Table([[p_pills]], colWidths=[720])
    t_pills.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0F172A")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#1E293B")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_pills)
    story.append(Spacer(1, 14))

    # Synthesis Banner on Cover
    summary_banner = (
        "<font size=9.5 color='#38BDF8'><b>SÍNTESIS DE LA DEFENSA TÉCNICA:</b></font>&nbsp;&nbsp;"
        "<font size=8.5 color='#CBD5E1'>"
        "Auditoría exhaustiva de 1,380 puntos con diagnóstico de sesgo asimétrico territorial; mecanismo de "
        "nivelación de demanda con Dynamic Delivery Slotting; formulación de corrector residual Ridge L2 con validación rodante out-of-time "
        "de 31 días; DataCoverageGate de 45 días contra fallas de arranque en frío; y arquitectura cloud en AWS Serverless "
        "con latencia &lt;50ms y costo mensual de $185 USD (ROI superior a 2,000%)."
        "</font>"
    )
    t_summary_banner = Table([[Paragraph(summary_banner, body_style)]], colWidths=[720], style=[
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1E293B")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#334155")),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
    ])
    story.append(t_summary_banner)

    story.append(PageBreak())

    # =========================================================================
    # SLIDE 2: DIAGNÓSTICO DEL ERROR Y BIPOLARIDAD GEOGRÁFICA (TAREA 1 - PARTE 1)
    # =========================================================================
    story.append(Paragraph("La auditoría del pronóstico base revela una red bipolar: el 70% del volumen sufre subestimación severa (CD_SUR +31.6%), forzando fletes de urgencia.", action_title_style))
    story.append(Paragraph("TAREA 1: EVALUACIÓN CUANTITATIVA DE WAPE Y BIAS POR CENTRO DE DISTRIBUCIÓN (1,380 PUNTOS AUDITADOS)", tracker_style))
    story.append(Spacer(1, 12))

    # Left: Table of 6 CDs (fixed column widths to prevent text wrapping on CD names)
    headers_cd_p = [Paragraph(h, cell_header) for h in ["Centro Logístico", "Vol. Real", "% Red", "WAPE", "Bias Base", "Diagnóstico Operativo Crítico"]]
    raw_cd_data = [
        ["CD_SUR", "510,826", "25.4%", "31.56%", "+31.56%", "Subestimación Crítica: Déficit el 100% de los días evaluados"],
        ["CD_ESTE", "183,209", "9.1%", "25.86%", "+25.30%", "Subestimación Estructural: Capacidad de transporte superada"],
        ["CD_NORTE", "705,833", "35.1%", "9.82%", "+7.47%", "Subestimación en Picos: Satura andenes en martes (volumen masivo)"],
        ["CD_CENTRO", "346,514", "17.2%", "23.28%", "-20.21%", "Sobreestimación Crónica: Camiones con capacidad ociosa"],
        ["CD_PACIFICO", "152,560", "7.6%", "22.15%", "-21.58%", "Sobreestimación Sistemática: Costo financiero de sobrestock"],
        ["CD_OESTE", "113,037", "5.6%", "23.90%", "-22.66%", "Sobreestimación Sistemática: Flota sobredimensionada"],
    ]
    tbl_cd_rows = [headers_cd_p]
    for r in raw_cd_data:
        is_under = "+" in r[4]
        b_color = "#EF4444" if is_under else "#2563EB"
        row_p = [
            Paragraph(f"<b>{r[0]}</b>", cell_text),
            Paragraph(r[1], cell_text),
            Paragraph(r[2], cell_text),
            Paragraph(f"<b>{r[3]}</b>", cell_text),
            Paragraph(f"<font color='{b_color}'><b>{r[4]}</b></font>", cell_text),
            Paragraph(f"<font size=7>{r[5]}</font>", cell_text),
        ]
        tbl_cd_rows.append(row_p)

    t_cd = Table(tbl_cd_rows, colWidths=[74, 52, 40, 48, 52, 134])
    t_cd.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6.5),
        ("TOPPADDING", (0, 0), (-1, -1), 6.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    # Right: Heatmap Image
    img_heatmap = Image("reports/figures/fase_02/heatmap_bias_centro_horizonte.png", width=315, height=210)

    t_s2_mid = Table([[t_cd, img_heatmap]], colWidths=[405, 315])
    t_s2_mid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(t_s2_mid)
    story.append(Spacer(1, 16))

    # Bottom Callout Box
    callout_s2_text = (
        "<font size=10 color='#1E40AF'><b>HALLAZGO ESTRUCTURAL DE RED LOGÍSTICA (RESPUESTA A PREGUNTA 1 DEL PDF):</b></font><br/>"
        "• <b>Bloque Deficitario (Subestimación Crítica / Bias > 0):</b> CD_NORTE, CD_SUR y CD_ESTE concentran el <b>69.6% de toda la demanda física</b> "
        "(1.40 millones de unidades). La falta sistemática de proyección obliga a contratar transporte spot a última hora bajo tarifas de urgencia.<br/>"
        "• <b>Bloque Excedentario (Sobreestimación Sistemática / Bias < 0):</b> CD_CENTRO, CD_PACIFICO y CD_OESTE representan el 30.4% restante "
        "y proyectan un 20% por encima de la realidad, inmovilizando inventario, ocupando espacio en andenes y encareciendo el costo de almacenaje.<br/>"
        "• <b>Diagnóstico Lead:</b> El error no es ruido blanco aleatorio; es una fractura territorial estructural que exige un modelo corrector aditivo."
    )
    story.append(Table([[Paragraph(callout_s2_text, body_style)]], colWidths=[720], style=[
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#93C5FD")),
        ("TOPPADDING", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
    ]))

    story.append(PageBreak())

    # =========================================================================
    # SLIDE 3: DEGRADACIÓN TEMPORAL Y ASIMETRÍA LOGÍSTICA (TAREA 1 - PARTE 2)
    # =========================================================================
    story.append(Paragraph("El WAPE se degrada en +2.76 pp hacia D+4, amplificando una Pérdida Asimétrica real del 41.4% por penalización de fletes spot.", action_title_style))
    story.append(Paragraph("TAREA 1: DEGRADACIÓN POR HORIZONTE TEMPORAL Y FORMULACIÓN DE PÉRDIDA ASIMÉTRICA", tracker_style))
    story.append(Spacer(1, 12))

    # Left: Horizon Table & Root Cause
    headers_h_p = [Paragraph(h, cell_header) for h in ["Horizonte de Anticipación", "WAPE Base", "Bias Base", "Delta vs D+1", "Deterioro Relativo"]]
    raw_h_data = [
        ["D+1 (24 horas)", "19.77%", "+6.69%", "Baseline", "Máxima precisión del sistema"],
        ["D+2 (48 horas)", "20.30%", "+6.70%", "+0.53 pp", "Deterioro inicial de preventa"],
        ["D+3 (72 horas)", "20.85%", "+6.70%", "+1.08 pp", "Pérdida de visibilidad de pedidos"],
        ["D+4 (96 horas)", "22.53%", "+6.69%", "+2.76 pp", "+14.0% de deterioro relativo"],
    ]
    tbl_h_rows = [headers_h_p]
    for r in raw_h_data:
        row_p = [
            Paragraph(f"<b>{r[0]}</b>", cell_text),
            Paragraph(f"<b>{r[1]}</b>", cell_text),
            Paragraph(r[2], cell_text),
            Paragraph(r[3], cell_text),
            Paragraph(f"<font size=7>{r[4]}</font>", cell_text),
        ]
        tbl_h_rows.append(row_p)

    t_h = Table(tbl_h_rows, colWidths=[90, 55, 50, 65, 135])
    t_h.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    box_causa = (
        "<font size=9 color='#0F172A'><b>Causa Raíz Operativa a 96 horas:</b></font><br/>"
        "La degradación no es un defecto del algoritmo, sino del comportamiento del cliente B2B: a 4 días de anticipación "
        "el sistema carece de visibilidad sobre reprogramaciones y compras erráticas fuera de plan."
    )
    t_left_s3 = Table([[t_h], [Spacer(1, 10)], [Table([[Paragraph(box_causa, body_style)]], colWidths=[395], style=[
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("PADDING", (0, 0), (-1, -1), 10),
    ])]], colWidths=[395])
    t_left_s3.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))

    # Right: Degradación temporal chart
    img_deg = Image("reports/figures/fase_02/degradacion_temporal_wape.png", width=320, height=215)

    t_s3_mid = Table([[t_left_s3, img_deg]], colWidths=[400, 320])
    t_s3_mid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(t_s3_mid)
    story.append(Spacer(1, 16))

    # Bottom: Pérdida Asimétrica Box (clean ascii without special glyph boxes)
    asym_text = (
        "<font size=10 color='#B45309'><b>FORMULACIÓN DE PÉRDIDA ASIMÉTRICA EN SUPPLY CHAIN (PENALIZACIÓN 2.5x EN FLETES SPOT):</b></font><br/>"
        "• <b>Desbalance de Costos Logísticos:</b> En distribución de consumo masivo, quedarse corto (subestimar) detona quiebre de servicio y fletes spot "
        "con sobreprecios abusivos de mercado (<i>c</i><sub>under</sub> = 2.5x), mientras que sobreestimar sólo genera costo financiero de almacenaje (<i>c</i><sub>over</sub> = 1.0x).<br/>"
        "• <b>Ecuación de Pérdida Asimétrica:</b> Loss<sub>asym</sub> = Σ [ 2.5 · max(0, y - y_pronóstico) + 1.0 · max(0, y_pronóstico - y) ] / Σ |y|<br/>"
        "• <b>Consecuencia en el Negocio:</b> La <b>Pérdida Asimétrica Real del baseline alcanza el 41.39%</b>, duplicando el WAPE nominal de 20.8%. "
        "Optimizar únicamente con métricas simétricas cuadráticas (MSE/RMSE) subestima gravemente el dolor financiero de la compañía."
    )
    story.append(Table([[Paragraph(asym_text, body_style)]], colWidths=[720], style=[
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEF3C7")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#FCD34D")),
        ("TOPPADDING", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
    ]))

    story.append(PageBreak())

    # =========================================================================
    # SLIDE 4: ESTADO OPERATIVO DEL PLAN: BIAS E INDISCIPLINA (TAREA 2 - PARTE 1)
    # =========================================================================
    story.append(Paragraph("El plan comercial presenta un sesgo de +10.6% en unidades y un 17.5% de compras fuera de plan, concentradas en CD_NORTE (24.4%).", action_title_style))
    story.append(Paragraph("TAREA 2: AUDITORÍA DEL PLAN DE ENTREGA DE CLIENTES (90 CLIENTES AUDITADOS, 739 COMPRAS)", tracker_style))
    story.append(Spacer(1, 12))

    # Top KPI cards row
    kpi_plan_1 = [
        Paragraph("BIAS EN VOLUMEN DEL PLAN", card_title),
        Paragraph("+10.62%", alert_text),
        Paragraph("70,550 pactadas vs 78,930 reales (+8.3k déficit)", subtext_center),
    ]
    kpi_plan_2 = [
        Paragraph("COMPRAS FUERA DE PLAN", card_title),
        Paragraph("17.46%", alert_text),
        Paragraph("129 de 739 compras en fechas distintas a la acordada", subtext_center),
    ]
    kpi_plan_3 = [
        Paragraph("BIAS EN FECHAS COMPROMETIDAS", card_title),
        Paragraph("+0.44 días", alert_text),
        Paragraph("Tendencia neta de clientes a postergar pedidos", subtext_center),
    ]
    t_kpis_plan = Table([[kpi_plan_1, kpi_plan_2, kpi_plan_3]], colWidths=[238, 238, 238])
    t_kpis_plan.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEF2F2")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#FECACA")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#FCA5A5")),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    story.append(t_kpis_plan)
    story.append(Spacer(1, 14))

    # Middle: Table (CD & Day breakdown) vs Chart
    headers_plan_p = [Paragraph(h, cell_header) for h in ["Centro Logístico", "% Fuera Plan", "Día Planificado", "% Fuera Plan"]]
    raw_plan_data = [
        ["CD_NORTE (Mayor volumen)", "24.39%", "Miércoles (Mayor deserción)", "22.86%"],
        ["CD_SUR (Mayor déficit)", "18.70%", "Lunes (Volatilidad inicial)", "22.09%"],
        ["CD_PACIFICO", "18.03%", "Martes (Día pico)", "17.16%"],
        ["CD_ESTE", "15.60%", "Jueves (Día valle)", "14.86%"],
        ["CD_CENTRO", "14.17%", "Viernes (Mayor disciplina)", "10.34%"],
        ["CD_OESTE", "13.93%", "Total Red Logística", "17.46%"],
    ]
    tbl_plan_rows = [headers_plan_p]
    for r in raw_plan_data:
        row_p = [
            Paragraph(f"<b>{r[0]}</b>", cell_text),
            Paragraph(f"<font color='#EF4444'><b>{r[1]}</b></font>", cell_text),
            Paragraph(f"<b>{r[2]}</b>", cell_text),
            Paragraph(f"<b>{r[3]}</b>", cell_text),
        ]
        tbl_plan_rows.append(row_p)

    t_plan = Table(tbl_plan_rows, colWidths=[120, 75, 120, 75])
    t_plan.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5.5),
        ("TOPPADDING", (0, 0), (-1, -1), 5.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    img_fuera_plan = Image("reports/figures/fase_03/compras_fuera_plan_por_dia_semana.png", width=315, height=185)

    t_s4_mid = Table([[t_plan, img_fuera_plan]], colWidths=[400, 320])
    t_s4_mid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(t_s4_mid)
    story.append(Spacer(1, 14))

    # Bottom Box: Operational Finding
    hallazgo_plan = (
        "<font size=10 color='#1E40AF'><b>CONCENTRACIÓN CRÍTICA EN CD_NORTE Y DIAGNÓSTICO OPERATIVO (PREGUNTAS 1 Y 2):</b></font><br/>"
        "• <b>Concentración Territorial de Indisciplina:</b> CD_NORTE combina el 35% de toda la carga física de la compañía con la peor tasa de indisciplina comercial "
        "(1 de cada 4 pedidos se compra fuera de fecha). Los miércoles y lunes registran >22% de fuga, desestabilizando "
        "el dimensionamiento de andenes y la programación de rutas de transporte.<br/>"
        "• <b>Impacto en Capacidad:</b> La deserción comercial provoca que el 17.5% de los despachos se concentren en días pico no programados, "
        "imposibilitando la optimización de flota fija."
    )
    story.append(Table([[Paragraph(hallazgo_plan, body_style)]], colWidths=[720], style=[
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#93C5FD")),
        ("TOPPADDING", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
    ]))

    story.append(PageBreak())

    # =========================================================================
    # SLIDE 5: MÉTRICAS ADICIONALES Y APLANAMIENTO DE DEMANDA (TAREA 2 - PARTE 2)
    # =========================================================================
    story.append(Paragraph("Con un Late-to-Early Ratio de 3.45x y 46% de carga los martes, proponemos 'Dynamic Delivery Slotting' para abatir el PAR de 2.10x a <1.35x.", action_title_style))
    story.append(Paragraph("TAREA 2: MÉTRICAS COMPLEMENTARIAS Y ESTRATEGIA DE APLANAMIENTO DE CURVA (PREGUNTAS 3 Y 4)", tracker_style))
    story.append(Spacer(1, 12))

    # Left: 3 Stacked Cards for Metrics
    c_m1 = [
        Paragraph("MÉTRICA 1: LATE-TO-EARLY RATIO = 3.45x", card_title),
        Paragraph("100 Retrasos vs 29 Adelantos (3.45 a 1)", alert_text),
        Paragraph("Demuestra postergación deliberada de inventario por parte del cliente B2B", subtext_center),
    ]
    c_m2 = [
        Paragraph("MÉTRICA 2: PEAK-TO-AVERAGE RATIO (PAR) = 2.10x", card_title),
        Paragraph("36,468 Unidades los Martes (46.2% semanal)", alert_text),
        Paragraph("Duplica la media diaria semanal, colapsando la capacidad de carga de camiones", subtext_center),
    ]
    c_m3 = [
        Paragraph("MÉTRICA 3: TASA DE SATURACIÓN DE FLOTA (CD_NORTE)", card_title),
        Paragraph("10% de Días > 100% de Capacidad (Pico 110.3%)", alert_text),
        Paragraph("974 unidades de desborde que exigen fletes spot. Jueves y viernes al 70%", subtext_center),
    ]
    t_3m = Table([[c_m1], [Spacer(1, 8)], [c_m2], [Spacer(1, 8)], [c_m3]], colWidths=[395])
    t_3m.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#FEF2F2")),
        ("BACKGROUND", (0, 2), (0, 2), colors.HexColor("#FEF2F2")),
        ("BACKGROUND", (0, 4), (0, 4), colors.HexColor("#FEF2F2")),
        ("BOX", (0, 0), (0, 0), 1, colors.HexColor("#FECACA")),
        ("BOX", (0, 2), (0, 2), 1, colors.HexColor("#FECACA")),
        ("BOX", (0, 4), (0, 4), 1, colors.HexColor("#FECACA")),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))

    # Right: Chart of Saturation
    img_sat = Image("reports/figures/fase_03/saturacion_capacidad_cd.png", width=315, height=225)

    t_s5_mid = Table([[t_3m, img_sat]], colWidths=[400, 320])
    t_s5_mid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(t_s5_mid)
    story.append(Spacer(1, 16))

    # Bottom: Strategy Dynamic Delivery Slotting
    slot_text = (
        "<font size=10 color='#065F46'><b>ESTRATEGIA OPERATIVA DE APLANAMIENTO: DYNAMIC DELIVERY SLOTTING (PREGUNTA 4 DEL PDF):</b></font><br/>"
        "• <b>Mecanismo Semáforo de Capacidad en Portal B2B:</b><br/>"
        "  - <i>Zona Verde (Ocupación ≤ 60%, Jueves/Viernes):</i> <b>Descuento logístico de 2.0% a 3.0%</b> en factura por entrega en día valle programado.<br/>"
        "  - <i>Zona Amarilla (60% < Ocupación ≤ 85%, Lunes/Miércoles):</i> Tarifa logística estándar de operación.<br/>"
        "  - <i>Zona Roja (Ocupación > 85%, Martes Pico):</i> Cierre dinámico de cupos preferentes o recargo disuasivo por congestión de andenes (+3%).<br/>"
        "• <b>Metas Cuantitativas de Control:</b> Reducir el PAR de 2.10x a <b>< 1.35x</b>; elevar la cuota de días valle de 26% a <b>≥ 40%</b>; y erradicar al <b>0%</b> los días con saturación >100% en CD_NORTE."
    )
    story.append(Table([[Paragraph(slot_text, body_style)]], colWidths=[720], style=[
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ECFDF5")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#A7F3D0")),
        ("TOPPADDING", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
    ]))

    story.append(PageBreak())

    # =========================================================================
    # SLIDE 6: MODELO COMPLEMENTARIO: METODOLOGÍA Y SELECCIÓN (TAREA 3 - PARTE 1)
    # =========================================================================
    story.append(Paragraph("El Corrector Residual Ridge L2 supera a modelos de árboles en 'Small Data', garantizando estabilidad matricial, interpretabilidad y cero fuga de datos.", action_title_style))
    story.append(Paragraph("TAREA 3: FORMULACIÓN ANALÍTICA, INGENIERÍA DE CARACTERÍSTICAS Y CRITERIO DE SELECCIÓN", tracker_style))
    story.append(Spacer(1, 12))

    # Left: Formulation, Features & Selection (clean ASCII)
    box_m6 = (
        "<font size=9.5 color='#1E40AF'><b>1. Formulación Residual con Barrera No-Negativa:</b></font><br/>"
        "El modelo complementario predice el error aditivo residual con cota inferior física de no-negatividad:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>y_corregido = max(0, y_base + epsilon_residual)</b>, donde epsilon_residual = Ridge_L2(X, α=10.0)<br/>"
        "Garantiza matemáticamente que jamás se emita una orden de despacho con unidades físicas negativas.<br/><br/>"
        "<font size=9.5 color='#1E40AF'><b>2. Ingeniería de Características & Protocolo Zero-Leakage:</b></font><br/>"
        "• Dummies de calendario (<i>es_martes</i>, <i>es_lunes</i>) para capturar la estacionalidad intra-semanal.<br/>"
        "• Interacciones territoriales cruzadas (<i>CD_NORTE_x_martes</i> = +139 unid., <i>CD_SUR_x_martes</i> = +212 unid.).<br/>"
        "• Rolling Features: medias móviles de 7, 14 y 21 días (<i>rolling_mean_21d</i>), desviaciones y ratio de señal base.<br/>"
        "• Blindaje Zero-Leakage: Despachos cerrados estrictamente antes de 06:00 AM (τ ≤ t - 1). Cero fuga de futuro.<br/><br/>"
        "<font size=9.5 color='#1E40AF'><b>3. Criterio de Selección: ¿Por qué Ridge L2 sobre Árboles (LightGBM/XGBoost)?:</b></font><br/>"
        "• <b>Régimen de 'Small Data' (612 a 1,332 filas en ventanas rodantes):</b> Los árboles sobreajustan y generan escalones discontinuos.<br/>"
        "• <b>Sesgo Aditivo Territorial:</b> Offsets continuos (+310 CD_SUR, -220 CD_PACIFICO) capturados de forma óptima por Ridge (α=10.0).<br/>"
        "• <b>Velocidad e Interpretabilidad:</b> Solución analítica matricial cerrada en <b>< 1 ms</b> (vs 450 ms GBDT) y betas 100% auditables."
    )
    t_box_m6 = Table([[Paragraph(box_m6, body_style)]], colWidths=[400], style=[
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ("PADDING", (0, 0), (-1, -1), 10),
    ])

    # Right: Feature Importance Chart
    img_feat = Image("reports/figures/fase_04/importancia_caracteristicas_modelo.png", width=315, height=265)

    t_s6_mid = Table([[t_box_m6, img_feat]], colWidths=[405, 315])
    t_s6_mid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(t_s6_mid)
    story.append(Spacer(1, 16))

    # Bottom Callout: Operational Robustness
    rob_text = (
        "<font size=10 color='#065F46'><b>AUDITORÍA DE COEFICIENTES Y ESTABILIDAD MATRICIAL:</b></font><br/>"
        "La regularización L2 previene la explosión de coeficientes ante colinealidad territorial. Los betas reflejan exactamente "
        "la estructura del negocio: penalización correctiva en CD_SUR y CD_ESTE para abastecer andenes, y atenuación en CD_CENTRO y CD_PACIFICO. "
        "El modelo provee una función de ajuste continua, suave y predecible para el área de compras y abastecimiento."
    )
    story.append(Table([[Paragraph(rob_text, body_style)]], colWidths=[720], style=[
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ECFDF5")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#A7F3D0")),
        ("TOPPADDING", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
    ]))

    story.append(PageBreak())

    # =========================================================================
    # SLIDE 7: ROLLING BACKTEST Y RESULTADOS FUERA DE MUESTRA (TAREA 3 - PARTE 2)
    # =========================================================================
    story.append(Paragraph("El rolling backtest en 31 días secuenciales demuestra que el modelo reduce el WAPE a 7.28% y neutraliza el sesgo a +0.69%.", action_title_style))
    story.append(Paragraph("TAREA 3: VALIDACIÓN CRUZADA CON ORIGEN RODANTE (ROLLING-ORIGIN BACKTEST, 708 PRONÓSTICOS EVALUADOS)", tracker_style))
    story.append(Spacer(1, 12))

    # Left: Rolling Backtest Table
    headers_bt_p = [Paragraph(h, cell_header) for h in ["Centro / Nivel", "WAPE Base", "WAPE Mod", "Delta WAPE", "Bias Base", "Bias Mod", "Estado"]]
    raw_bt_data = [
        ["GLOBAL", "20.73%", "7.28%", "-13.45 pp (-65%)", "+6.69%", "+0.69%", "Meta Cumplida (<10%)"],
        ["CD_SUR", "31.14%", "6.48%", "-24.66 pp (-79%)", "+31.14%", "-0.15%", "Sesgo Neutralizado"],
        ["CD_ESTE", "26.44%", "8.08%", "-18.36 pp (-69%)", "+25.87%", "+2.98%", "Subestimación eliminada"],
        ["CD_PACIFICO", "23.14%", "5.72%", "-17.43 pp (-75%)", "-22.52%", "+0.16%", "Corregido a meta"],
        ["CD_OESTE", "23.45%", "8.24%", "-15.21 pp (-65%)", "-21.95%", "-1.89%", "Corregido a meta"],
        ["CD_CENTRO", "23.04%", "9.70%", "-13.33 pp (-58%)", "-19.35%", "+0.48%", "Corregido a meta"],
        ["CD_NORTE", "9.59%", "6.64%", "-2.94 pp (-31%)", "+7.76%", "+1.32%", "Optimizado prudente"],
    ]
    tbl_bt_rows = [headers_bt_p]
    for i, r in enumerate(raw_bt_data):
        is_global = i == 0
        row_p = [
            Paragraph(f"<b>{r[0]}</b>" if is_global else r[0], cell_text),
            Paragraph(f"<b>{r[1]}</b>" if is_global else r[1], cell_text),
            Paragraph(f"<font color='#10B981'><b>{r[2]}</b></font>", cell_text),
            Paragraph(f"<font color='#10B981'><b>{r[3]}</b></font>", cell_text),
            Paragraph(r[4], cell_text),
            Paragraph(f"<b>{r[5]}</b>", cell_text),
            Paragraph(f"<font size=7>{r[6]}</font>", cell_text),
        ]
        tbl_bt_rows.append(row_p)

    t_bt = Table(tbl_bt_rows, colWidths=[70, 52, 52, 85, 52, 48, 61])
    t_bt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#F1F5F9")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 2), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    # Right: 2 Stacked Comparison Charts
    img_wape = Image("reports/figures/fase_04/comparativa_wape_modelo_vs_baseline.png", width=290, height=125)
    img_bias = Image("reports/figures/fase_04/comparativa_bias_modelo_vs_baseline.png", width=290, height=125)
    t_stacked_charts = Table([[img_wape], [Spacer(1, 4)], [img_bias]], colWidths=[290])
    t_stacked_charts.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    t_s7_mid = Table([[t_bt, t_stacked_charts]], colWidths=[425, 295])
    t_s7_mid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(t_s7_mid)
    story.append(Spacer(1, 16))

    # Bottom: Honestidad Analítica & Asimetría
    hon_text = (
        "<font size=10 color='#065F46'><b>HONESTIDAD ANALÍTICA Y PÉRDIDA ASIMÉTRICA EN OUT-OF-SAMPLE:</b></font><br/>"
        "• <b>Evolución por Horizonte:</b> D+1 cae a <b>5.76%</b>; D+2 a <b>6.16%</b>; D+3 a <b>7.32%</b>; y D+4 se sitúa en <b>9.90%</b>.<br/>"
        "• <b>Criterio de Honestidad Técnica (Requerimiento PDF):</b> En D+4 el WAPE se mantiene en 9.90%, reflejando la dispersión natural "
        "irreducible provocada por el 17.5% de clientes fuera de plan. El modelo no inventa certidumbre donde no hay trazabilidad.<br/>"
        "• <b>Impacto en Pérdida Asimétrica (Penalización 2.5x):</b> Se desploma del <b>41.30% al 13.26% (-28.04 pp / -67.9% relativo)</b>, "
        "erradicando los sobrecostos de fletes de emergencia."
    )
    story.append(Table([[Paragraph(hon_text, body_style)]], colWidths=[720], style=[
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ECFDF5")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#A7F3D0")),
        ("TOPPADDING", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
    ]))

    story.append(PageBreak())

    # =========================================================================
    # SLIDE 8: RESILIENCIA ANTE COLD START: DATACOVERAGEGATE (TAREA 4)
    # =========================================================================
    story.append(Paragraph("El DataCoverageGate con umbral de 45 días previene excepciones ante 'Cold Start' y minimiza el error estándar en un 16.8%.", action_title_style))
    story.append(Paragraph("TAREA 4: REGLA DE CONTROL OPERATIVO (GATE), COBERTURA HISTÓRICA MÍNIMA Y FALLBACK SEGURO", tracker_style))
    story.append(Spacer(1, 12))

    # Left: Rule Logic, Statistics & Sensitivity
    box_s8 = (
        "<font size=9.5 color='#1E40AF'><b>1. Lógica del Mecanismo de Control (Gate):</b></font><br/>"
        "Inspecciona diariamente la racha continua de días de despacho disponibles sin huecos temporales para cada CD:<br/>"
        "• <b>Si Racha ≥ 45 días:</b> Habilita el reentrenamiento e inferencia del modelo complementario (<i>ADVANCED_CORRECTOR</i>).<br/>"
        "• <b>Si Racha < 45 días (Centro Nuevo o Interrupción):</b> Conmuta suavemente a pronóstico base oficial (<i>SAFE_FALLBACK</i>) "
        "registrando advertencias en logs estructurados. Cero caídas en producción.<br/><br/>"
        "<font size=9.5 color='#1E40AF'><b>2. Fundamentación Estadística del Umbral de 45 Días:</b></font><br/>"
        "• <b>6.4 Ciclos Semanales Completos:</b> Asegura observar al menos 6 ocurrencias de cada día (especialmente el pico crítico del martes).<br/>"
        "• <b>Saturación de Rolling Features:</b> Permite computar medias móviles de 21 días (<i>rolling_mean_21d</i>) sin imputaciones sesgadas.<br/>"
        "• <b>Reducción del Error Estándar:</b> Reduce el error estándar en un <b>16.8%</b> respecto a 15 días (SE = σ / √45 ≈ 0.149σ).<br/><br/>"
        "<font size=9.5 color='#1E40AF'><b>3. Análisis de Riesgos y Sensibilidad (Requerimiento PDF):</b></font><br/>"
        "• <i>Riesgo Reducir Umbral (<45 días, ej. 15-30d):</i> Varianza muestral excesiva; WAPE salta a >12.5% por sobreajuste en picos atípicos.<br/>"
        "• <i>Riesgo Aumentar Umbral (>45 días, ej. 60-90d):</i> Costo de oportunidad; priva innecesariamente 3 meses de capturar el 65% de ahorro.<br/>"
        "• <b>Conclusión Lead:</b> 45 días es el punto óptimo (sweet spot) entre estabilidad matemática y velocidad de despliegue."
    )
    t_box_s8 = Table([[Paragraph(box_s8, body_style)]], colWidths=[400], style=[
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ("PADDING", (0, 0), (-1, -1), 10),
    ])

    # Right: 2 Stacked Images (Flow + Sensitivity)
    img_flow = Image("reports/figures/fase_05/flujo_decision_resiliencia_gate.png", width=300, height=130)
    img_sens = Image("reports/figures/fase_05/sensibilidad_umbral_dias_wape.png", width=300, height=130)
    t_stacked_gate = Table([[img_flow], [Spacer(1, 4)], [img_sens]], colWidths=[300])
    t_stacked_gate.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    t_s8_mid = Table([[t_box_s8, t_stacked_gate]], colWidths=[415, 305])
    t_s8_mid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(t_s8_mid)
    story.append(Spacer(1, 16))

    # Bottom Callout: Resiliencia en Producción
    callout_gate = (
        "<font size=10 color='#065F46'><b>TOLERANCIA A FALLAS Y TELEMETRÍA EN PRODUCCIÓN:</b></font><br/>"
        "El middleware DataCoverageGate opera en memoria dentro del microservicio FastAPI con latencia < 1 ms. Emite alertas en CloudWatch "
        "si la tasa de fallback de la red supera el 5%, permitiendo a Data Science diagnosticar fallas en origen sin impactar la operación diaria."
    )
    story.append(Table([[Paragraph(callout_gate, body_style)]], colWidths=[720], style=[
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ECFDF5")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#A7F3D0")),
        ("TOPPADDING", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
    ]))

    story.append(PageBreak())

    # =========================================================================
    # SLIDE 9: ARQUITECTURA CLOUD EN AWS (TAREA 5)
    # =========================================================================
    story.append(Paragraph("La arquitectura AWS Serverless desacopla batch e inferencia en tiempo real (<50ms) con alta disponibilidad y costo de $185 USD/mes.", action_title_style))
    story.append(Paragraph("TAREA 5: DISEÑO CONCEPTUAL DE ARQUITECTURA CLOUD, MLOPS Y PERSISTENCIA EN AWS", tracker_style))
    story.append(Spacer(1, 10))

    # Top: High-Resolution AWS Architecture Diagram (300 DPI)
    img_aws = Image("reports/figures/fase_05/diagrama_arquitectura_aws.png", width=720, height=245)
    story.append(img_aws)
    story.append(Spacer(1, 14))

    # Bottom: 4 Architecture Component Cards
    c_aws_1 = [
        Paragraph("1. BATCH / RE-TRAINING", ParagraphStyle("A1", parent=card_title, textColor=colors.HexColor("#2563EB"))),
        Paragraph(
            "• <b>EventBridge:</b> Disparo dominical 23:00 UTC o por drift.<br/>"
            "• <b>Step Functions:</b> DAG serverless (Pydantic → Features → Train).<br/>"
            "• <b>SageMaker Spot:</b> Instancias c6i.xlarge (70% ahorro cómputo).<br/>"
            "• <b>Model Registry:</b> Versión con tag 'Approved'.",
            ParagraphStyle("B1", parent=body_style, fontSize=7.8, leading=11)
        ),
    ]
    c_aws_2 = [
        Paragraph("2. INFERENCIA REAL-TIME", ParagraphStyle("A2", parent=card_title, textColor=colors.HexColor("#2563EB"))),
        Paragraph(
            "• <b>API Gateway:</b> Endpoints REST /v1/forecast/correct.<br/>"
            "• <b>ECS Fargate:</b> Microservicio FastAPI autoescalable Multi-AZ.<br/>"
            "• <b>DataCoverageGate:</b> Middleware en memoria (<1 ms).<br/>"
            "• <b>ElastiCache Redis:</b> Semáforo de slots verde/amarillo/rojo.",
            ParagraphStyle("B2", parent=body_style, fontSize=7.8, leading=11)
        ),
    ]
    c_aws_3 = [
        Paragraph("3. PERSISTENCIA & DATA LAKE", ParagraphStyle("A3", parent=card_title, textColor=colors.HexColor("#2563EB"))),
        Paragraph(
            "• <b>S3 Data Lake:</b> Zonas Raw y Curated (Parquet Snappy).<br/>"
            "• <b>Aurora Serverless v2:</b> Transaccional ACID para planes y cupos.<br/>"
            "• <b>AWS KMS:</b> Encriptación en reposo y en tránsito.<br/>"
            "• <b>AWS Glue Catalog:</b> Gobernanza y linaje de datos.",
            ParagraphStyle("B3", parent=body_style, fontSize=7.8, leading=11)
        ),
    ]
    c_aws_4 = [
        Paragraph("4. MLOPS & FINOPS", ParagraphStyle("A4", parent=card_title, textColor=colors.HexColor("#2563EB"))),
        Paragraph(
            "• <b>CloudWatch:</b> Métricas latencia p95 y tasa fallback.<br/>"
            "• <b>Model Monitor:</b> Alerta Slack si WAPE 7d > 12% o drift sesgo.<br/>"
            "• <b>Presupuesto FinOps:</b> ~$140 a $230 USD/mes (Media: <b>$185 USD/mes</b>).<br/>"
            "• <b>ROI Infraestructura:</b> > 2,000% (Payback en < 1 flete).",
            ParagraphStyle("B4", parent=body_style, fontSize=7.8, leading=11)
        ),
    ]

    t_aws_cards = Table([[c_aws_1, c_aws_2, c_aws_3, c_aws_4]], colWidths=[177, 177, 177, 177])
    t_aws_cards.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_aws_cards)

    story.append(PageBreak())

    # =========================================================================
    # SLIDE 10: IMPACTO EN NEGOCIO, FLOTA Y ROADMAP (TAREA 5 / DIAPOS 9–10 PDF)
    # =========================================================================
    story.append(Paragraph("La solución elimina el 100% de la sobrecapacidad en CD_NORTE, proyecta ahorros de hasta $350k USD y eleva el OTIF a >98%.", action_title_style))
    story.append(Paragraph("IMPACTO EN NEGOCIO: OPTIMIZACIÓN DE FLOTA, FLETES SPOT, NIVEL DE SERVICIO Y ROADMAP (PDF SLIDES 9-10)", tracker_style))
    story.append(Spacer(1, 12))

    # Top 3 Business Impact KPI Cards
    kpi_biz_1 = [
        Paragraph("OPTIMIZACIÓN DE FLOTA Y CAPACIDAD", card_title),
        Paragraph("974 Unid. Desborde Eliminadas", highlight_text),
        Paragraph("Reduce 15% flota pico de martes en CD_NORTE, eliminando saturación > 100%", subtext_center),
    ]
    kpi_biz_2 = [
        Paragraph("EVALUACIÓN FLETES DE EMERGENCIA", card_title),
        Paragraph("$180k - $350k USD / año", highlight_text),
        Paragraph("Ahorro paramétrico. Costo cloud ($185/mes) rinde ROI > 2,000%", subtext_center),
    ]
    kpi_biz_3 = [
        Paragraph("NIVEL DE SERVICIO AL CLIENTE (OTIF)", card_title),
        Paragraph("91.5% → ≥ 98.0%", highlight_text),
        Paragraph("Cumplimiento On-Time In-Full, mitigando multas y quiebres de stock", subtext_center),
    ]
    t_biz = Table([[kpi_biz_1, kpi_biz_2, kpi_biz_3]], colWidths=[238, 238, 238])
    t_biz.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ECFDF5")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#A7F3D0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#6EE7B7")),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    story.append(t_biz)
    story.append(Spacer(1, 14))

    # Middle: Roadmap 12 Semanas
    headers_road_p = [Paragraph(h, cell_header) for h in ["Fase / Hito", "Semanas", "Alcance Operativo y Entregables Clave", "Gate de Control / Criterio de Éxito"]]
    raw_road = [
        ["Fase 1: Piloto Regional", "Sem 1 - 4", "Despliegue CD_NORTE y CD_SUR en sombra. Activación Step Functions y DataCoverageGate.", "WAPE < 8.0% real, 0 interrupciones operativas."],
        ["Fase 2: Dynamic Slotting", "Sem 5 - 8", "Integración de cupos en Portal B2B y app preventa. Activación bono comercial 2.5% en días valle.", "Adopción de días valle > 35%, PAR < 1.6x."],
        ["Fase 3: Rollout Nacional", "Sem 9 - 12", "Extensión a 6 CDs. Activación SageMaker Model Monitor y entrega formal a S&OP Transporte.", "100% fletes spot eliminados, ROI auditado."],
    ]
    tbl_road_rows = [headers_road_p]
    for r in raw_road:
        row_p = [
            Paragraph(f"<b>{r[0]}</b>", cell_text),
            Paragraph(f"<b>{r[1]}</b>", cell_text),
            Paragraph(r[2], cell_text),
            Paragraph(f"<font size=7.5>{r[3]}</font>", cell_text),
        ]
        tbl_road_rows.append(row_p)

    t_road = Table(tbl_road_rows, colWidths=[110, 60, 370, 180])
    t_road.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6.5),
        ("TOPPADDING", (0, 0), (-1, -1), 6.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(t_road)
    story.append(Spacer(1, 14))

    # Bottom: Split (Aclaración Fletes + Gobernanza S&OP)
    aclaracion_text = (
        "<font size=9 color='#1E40AF'><b>Aclaración Metodológica Lead (Evaluación de Fletes):</b></font><br/>"
        "El dataset original no contiene variables monetarias directas. La evaluación económica se aborda con total rigor técnico "
        "como un <b>Modelo Paramétrico de Caso de Negocio</b>: se valoriza la eliminación de 974 unidades de desborde y la reducción "
        "del 67.9% en pérdida asimétrica bajo supuestos de mercado ($15-$25 USD/unid. en flete spot de urgencia / $450 por viaje de camión no planificado). "
        "El ahorro neto estimado es de <b>$180k a $350k USD anuales</b>."
    )
    t_aclaracion = Table([[Paragraph(aclaracion_text, body_style)]], colWidths=[375], style=[
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#93C5FD")),
        ("PADDING", (0, 0), (-1, -1), 10),
    ])

    gov_text = (
        "<font size=9 color='#065F46'><b>Gobernanza Continua & MLOps:</b></font><br/>"
        "• <b>Monitoreo Diario de Drift:</b> Alertas Slack si WAPE 7d > 12% o Bias fuera de [-4%, +4%].<br/>"
        "• <b>Reentrenamiento Semanal:</b> Cómputo dominical en SageMaker Spot con promoción automática.<br/>"
        "• <b>Comité Conjunto S&OP:</b> Sesión quincenal (DS + Transporte + Ventas) para calibrar el semáforo.<br/>"
        "• <b>Auditoría Continua:</b> Conciliación mensual de ahorro en fletes contra balance financiero."
    )
    t_gov = Table([[Paragraph(gov_text, body_style)]], colWidths=[335], style=[
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ECFDF5")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#A7F3D0")),
        ("PADDING", (0, 0), (-1, -1), 10),
    ])

    t_s10_bottom = Table([[t_aclaracion, t_gov]], colWidths=[380, 340])
    t_s10_bottom.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(t_s10_bottom)

    # Build the PDF
    doc.build(
        story,
        canvasmaker=ExecutiveDeckCanvas,
        onFirstPage=draw_cover_bg,
        onLaterPages=draw_content_bg,
    )
    print(f"[OK] Deck Ejecutivo de 10 diapositivas generado exitosamente en: {PDF_PATH}")

    # Render PNG slide previews using PyMuPDF (fitz)
    doc_fitz = fitz.open(str(PDF_PATH))
    print(f"[INFO] Renderizando {len(doc_fitz)} diapositivas a PNG de alta resolución (150 DPI)...")
    for page_idx in range(len(doc_fitz)):
        page = doc_fitz[page_idx]
        pix = page.get_pixmap(dpi=150)
        out_png = PREVIEW_DIR / f"slide_{page_idx + 1:02d}.png"
        pix.save(str(out_png))
        print(f"  -> {out_png} generado ({pix.width}x{pix.height})")
    doc_fitz.close()
    print("[OK] Todas las diapositivas renderizadas exitosamente a PNG.")


if __name__ == "__main__":
    build_10_slide_deck()
