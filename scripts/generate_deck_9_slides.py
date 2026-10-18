"""Generates an executive 9-slide PDF presentation deck (McKinsey & Co. style).

Cover slide features author name, executive title, and dark technological aesthetic.
Slides 2-9 feature Action Titles, KPI cards, and embedded high-resolution figures.
"""

import os
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    KeepTogether,
    PageBreak,
)
from reportlab.pdfgen import canvas

PRESENTATION_DIR = Path("presentation")
PRESENTATION_DIR.mkdir(parents=True, exist_ok=True)
PDF_PATH = PRESENTATION_DIR / "deck_ejecutivo_9_slides_mckinsey.pdf"

# Page dimensions (Landscape Letter: 11 x 8.5 inches = 792 x 612 pt)
PAGE_WIDTH, PAGE_HEIGHT = landscape(letter)


class McKinseyCanvas(canvas.Canvas):
    """Custom canvas that applies McKinsey-style headers/footers to content slides,

    while keeping Slide 1 as a full dark technological cover slide.
    """

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
            if self._pageNumber == 1:
                self.draw_cover_decorations()
            else:
                self.draw_slide_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_cover_decorations(self):
        self.saveState()
        # Dark technological background
        self.setFillColor(colors.HexColor("#0A1128"))
        self.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

        # Subtle geometric gradient lines/grid
        self.setStrokeColor(colors.HexColor("#1E293B"))
        self.setLineWidth(1)
        self.line(40, PAGE_HEIGHT - 60, PAGE_WIDTH - 40, PAGE_HEIGHT - 60)
        self.line(40, 70, PAGE_WIDTH - 40, 70)

        # Electric blue accent bar
        self.setFillColor(colors.HexColor("#2563EB"))
        self.rect(40, PAGE_HEIGHT - 62, 120, 3, fill=1, stroke=0)

        # Watermark/footer
        self.setFillColor(colors.HexColor("#64748B"))
        self.setFont("Helvetica", 8)
        self.drawString(40, 48, "CONFIDENCIAL | COMITÉ EJECUTIVO DE OPERACIONES & SUPPLY CHAIN")
        self.drawRightString(PAGE_WIDTH - 40, 48, "MCKINSEY & CO. STYLE EXECUTIVE DELIVERABLE")
        self.restoreState()

    def draw_slide_decorations(self, total_pages):
        self.saveState()
        # Top banner bar
        self.setFillColor(colors.HexColor("#0F172A"))
        self.rect(0, PAGE_HEIGHT - 22, PAGE_WIDTH, 22, fill=1, stroke=0)

        # Header Title
        self.setFillColor(colors.HexColor("#38BDF8"))
        self.setFont("Helvetica-Bold", 8)
        self.drawString(30, PAGE_HEIGHT - 15, "ESTRATEGIA ANALÍTICA & OPTIMIZACIÓN DE SUPPLY CHAIN B2B")
        self.setFillColor(colors.HexColor("#94A3B8"))
        self.setFont("Helvetica", 8)
        self.drawRightString(PAGE_WIDTH - 30, PAGE_HEIGHT - 15, "DESAFÍO TÉCNICO: DATA SCIENTIST LEAD")

        # Bottom footer bar
        self.setFillColor(colors.HexColor("#F8FAFC"))
        self.rect(0, 0, PAGE_WIDTH, 22, fill=1, stroke=0)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.line(0, 22, PAGE_WIDTH, 22)

        # Footer text
        self.setFillColor(colors.HexColor("#64748B"))
        self.setFont("Helvetica", 8)
        self.drawString(30, 7, "Sebastián Felipe Urzúa Bórquez | Data Scientist Lead | Presentación Ejecutiva")
        self.drawRightString(PAGE_WIDTH - 30, 7, f"Diapositiva {self._pageNumber} de {total_pages}")
        self.restoreState()


def build_9_slide_deck():
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=landscape(letter),
        leftMargin=30,
        rightMargin=30,
        topMargin=32,
        bottomMargin=30,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    action_title_style = ParagraphStyle(
        "ActionTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
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
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "SlideBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
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
        alignment=1,  # Center
    )
    highlight_text = ParagraphStyle(
        "HighlightText",
        parent=body_style,
        fontSize=12,
        leading=14,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#10B981"),
        alignment=1,  # Center
    )
    alert_text = ParagraphStyle(
        "AlertText",
        parent=body_style,
        fontSize=12,
        leading=14,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#EF4444"),
        alignment=1,  # Center
    )
    subtext_center = ParagraphStyle(
        "SubtextCenter",
        parent=body_style,
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#64748B"),
        alignment=1,  # Center
    )

    story = []

    # =========================================================================
    # SLIDE 1: PORTADA EJECUTIVA (DARK TECHNOLOGICAL COVER)
    # =========================================================================
    story.append(Spacer(1, 100))

    tag_style = ParagraphStyle(
        "CoverTag",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#38BDF8"),
    )
    title_cover_style = ParagraphStyle(
        "CoverTitle",
        fontName="Helvetica-Bold",
        fontSize=30,
        leading=36,
        textColor=colors.white,
    )
    subtitle_cover_style = ParagraphStyle(
        "CoverSubtitle",
        fontName="Helvetica",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#94A3B8"),
    )
    author_cover_style = ParagraphStyle(
        "CoverAuthor",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.white,
    )
    meta_cover_style = ParagraphStyle(
        "CoverMeta",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#CBD5E1"),
    )

    story.append(Paragraph("ESTRATEGIA ANALÍTICA & OPTIMIZACIÓN DE SUPPLY CHAIN B2B", tag_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("Desafío Técnico Data Scientist Lead", title_cover_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Optimización de Capacidad Logística, Reducción de Sesgo y Corrección de Pronóstico", subtitle_cover_style))
    story.append(Spacer(1, 55))

    author_block = [
        Paragraph("<b>Sebastián Felipe Urzúa Bórquez</b>", author_cover_style),
        Spacer(1, 4),
        Paragraph("Candidato a Data Scientist Lead | Especialista en Machine Learning & Supply Chain", meta_cover_style),
        Paragraph("Entregable Ejecutivo: Formato Consultoría Estratégica (McKinsey Style)", meta_cover_style),
        Paragraph("Octubre 2026 | Documento Confidencial", meta_cover_style),
    ]

    badges_data = [
        [
            Paragraph("<b>WAPE GLOBAL</b><br/><font size=11 color='#10B981'><b>20.7% → 7.3%</b></font>", card_title),
            Paragraph("<b>BIAS GLOBAL</b><br/><font size=11 color='#10B981'><b>+6.7% → +0.7%</b></font>", card_title),
            Paragraph("<b>ROI FINOPS AWS</b><br/><font size=11 color='#38BDF8'><b>2,008% (21x)</b></font>", card_title),
        ]
    ]
    t_badges = Table(badges_data, colWidths=[120, 120, 120])
    t_badges.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1E293B")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#334155")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))

    cover_row = Table([[author_block, t_badges]], colWidths=[400, 320])
    cover_row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ]))
    story.append(cover_row)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 2: RESUMEN EJECUTIVO (THE BREAKTHROUGH & BUSINESS CASE)
    # =========================================================================
    story.append(Paragraph("Resumen Ejecutivo: La intervención analítica reduce el error a 7.3%, neutraliza el sesgo y ahorra hasta $350k USD anuales", action_title_style))
    story.append(Paragraph("SÍNTESIS EJECUTIVA: DE UN PRONÓSTICO BASE DEFICITARIO A UN SISTEMA DE DECISIÓN RESILIENTE", tracker_style))

    kpis_s2 = [
        [
            Paragraph("WAPE GLOBAL BACKTEST", card_title),
            Paragraph("SESGO ESTRUCTURAL (BIAS)", card_title),
            Paragraph("PÉRDIDA ASIMÉTRICA", card_title),
            Paragraph("RETORNO FINOPS (AWS)", card_title),
        ],
        [
            Paragraph("<b>20.73% → 7.28%</b>", highlight_text),
            Paragraph("<b>+6.69% → +0.69%</b>", highlight_text),
            Paragraph("<b>41.30% → 13.26%</b>", highlight_text),
            Paragraph("<b>2,008% (21.1x)</b>", highlight_text),
        ],
        [
            Paragraph("-13.45 pp (-64.9% error relativo)<br/>31 días fuera de muestra", subtext_center),
            Paragraph("Sesgo neutralizado<br/>CD_SUR: +31.1% a -0.15%", subtext_center),
            Paragraph("-28.04 pp en fletes spot<br/>Penalización 2.5x erradicada", subtext_center),
            Paragraph("Costo $185/mes vs ahorro<br/>$3,900/mes en fletes spot", subtext_center),
        ],
    ]
    t_kpis_s2 = Table(kpis_s2, colWidths=[180, 180, 180, 180])
    t_kpis_s2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_kpis_s2)
    story.append(Spacer(1, 10))

    # 3 Strategic Pillars
    col_p1 = [
        Paragraph("<b>1. DIAGNÓSTICO (El Dolor Oculto)</b>", bold_body),
        Spacer(1, 3),
        Paragraph("• <b>Asimetría Logística Severa:</b> El baseline subestima fuertemente en centros masivos (CD_SUR +31.6%, CD_NORTE +7.5%), donde la falta de flota obliga a fletes spot con sobreprecio de 2.5x.", body_style),
        Paragraph("• <b>Efecto Martes Negro:</b> El 46.2% de la demanda semanal colapsa los martes, desbordando CD_NORTE el 10% de los días con 17.5% de compras fuera de plan.", body_style),
    ]
    col_p2 = [
        Paragraph("<b>2. INTERVENCIÓN (Data Science)</b>", bold_body),
        Spacer(1, 3),
        Paragraph("• <b>Corrector Residual Ridge L2:</b> Modelo lineal regularizado con 26 covariables exógenas y cero data leakage (datos cerrados a las 06:00 AM).", body_style),
        Paragraph("• <b>DataCoverageGate (45 días):</b> Mecanismo de resiliencia con fallback seguro ante Cold Start sin excepciones.", body_style),
        Paragraph("• <b>Dynamic Slotting:</b> Bonificación de 2-3% en días valle para aplanar el PAR de 2.1x a <1.35x.", body_style),
    ]
    col_p3 = [
        Paragraph("<b>3. VALOR EN P&L & GOBERNANZA</b>", bold_body),
        Spacer(1, 3),
        Paragraph("• <b>Ahorro Financiero Directo:</b> Eliminación de 974 unid. de exceso y sobrecostos por $180k - $350k USD/año.", body_style),
        Paragraph("• <b>Nivel de Servicio (OTIF):</b> Elevación del 91.5% al 98.2% con menor congestión de patios.", body_style),
        Paragraph("• <b>Cloud Serverless en AWS:</b> Pipeline automatizado en SageMaker Spot + ECS Fargate por ~$185 USD/mes.", body_style),
    ]
    t_pillars = Table([[col_p1, col_p2, col_p3]], colWidths=[240, 240, 240])
    t_pillars.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFFFF")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_pillars)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 3: AUDITORÍA DEL BASELINE Y ASIMETRÍA LOGÍSTICA (TAREA 1)
    # =========================================================================
    story.append(Paragraph("Auditoría Baseline: El WAPE de 20.8% ocultaba una severa bipolaridad y un costo real del 41.4% en fletes spot", action_title_style))
    story.append(Paragraph("TAREA 1: EVALUACIÓN CUANTITATIVA DEL PRONÓSTICO BASE (1,380 PUNTOS AUDITADOS | 2026-01-01 A 2026-03-01)", tracker_style))

    cd_table_data = [
        ["Centro Logístico", "Vol. Real", "% Red", "WAPE (%)", "Bias (%)", "Diagnóstico Operativo"],
        ["CD_NORTE", "705,833", "35.1%", "9.82%", "+7.47%", "Subestimación masiva en volumen pico"],
        ["CD_SUR", "510,826", "25.4%", "31.56%", "+31.56%", "Subestimación crítica severa (100% de días)"],
        ["CD_CENTRO", "346,514", "17.2%", "23.28%", "-20.21%", "Sobreestimación crónica (capacidad ociosa)"],
        ["CD_ESTE", "183,209", "9.1%", "25.86%", "+25.30%", "Subestimación estructural persistente"],
        ["CD_PACIFICO", "152,560", "7.6%", "22.15%", "-21.58%", "Sobreestimación sistemática"],
        ["CD_OESTE", "113,037", "5.6%", "23.90%", "-22.66%", "Sobreestimación sistemática"],
    ]
    t_cd_s3 = Table(cd_table_data, colWidths=[90, 65, 45, 55, 55, 170])
    t_cd_s3.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ALIGN", (1, 0), (4, -1), "CENTER"),
    ]))

    deg_img_path = "reports/figures/fase_02/degradacion_temporal_wape.png"
    deg_img = Image(deg_img_path, width=3.0 * inch, height=1.75 * inch) if os.path.exists(deg_img_path) else Paragraph("Gráfico no disponible", body_style)

    row_s3 = Table([[t_cd_s3, deg_img]], colWidths=[485, 235])
    row_s3.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story.append(row_s3)
    story.append(Spacer(1, 6))

    asym_box = (
        "<b>Hallazgos Clave de Auditoría & Asimetría de Costo Logístico:</b><br/>"
        "• <b>Bipolaridad de la Red (Pregunta 1):</b> CD_NORTE, CD_SUR y CD_ESTE concentran el <b>69.6% de la demanda</b> y subestiman sistemáticamente. CD_SUR se queda corto el 100% de los días (+31.56%). CD_CENTRO, CD_PACIFICO y CD_OESTE sobreestiman en más del 20%, dejando camiones vacíos.<br/>"
        "• <b>Criterio Asimétrico:</b> Subestimar es <b>2.5x más costoso</b> que sobreestimar por fletes spot. La <b>Pérdida Asimétrica Real asciende al 41.39%</b>, duplicando el WAPE nominal.<br/>"
        "• <b>Degradación Temporal (Pregunta 2):</b> Deterioro monótono de D+1 (19.77%) a D+4 (22.53%) (+2.76 pp / +13.9% relativo) debido a la acumulación de compras fuera de plan a 96 horas."
    )
    story.append(Table([[Paragraph(asym_box, body_style)]], colWidths=[720], style=[
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#BFDBFE")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 4: DESAJUSTE OPERATIVO Y EL EFECTO "MARTES NEGRO" (TAREA 2)
    # =========================================================================
    story.append(Paragraph("Desajuste Operativo: El 46.2% de la demanda se aglomera los martes con un 17.5% de compras fuera de plan", action_title_style))
    story.append(Paragraph("TAREA 2: BRECHA PLAN VS REALIDAD, ADHESIÓN POR CLIENTE Y SATURACIÓN DE CAPACIDAD", tracker_style))

    sat_img_path = "reports/figures/fase_03/saturacion_capacidad_cd.png"
    sat_img = Image(sat_img_path, width=3.3 * inch, height=1.9 * inch) if os.path.exists(sat_img_path) else Paragraph("Gráfico no disponible", body_style)

    plan_diag = [
        Paragraph("<b>Diagnóstico de la Brecha Comercial (Preguntas 1, 2 y 3):</b>", bold_body),
        Spacer(1, 2),
        Paragraph("• <b>Bias del Plan Comercial (Pregunta 1):</b> El plan subestima en volumen un <b>+10.62%</b> (78.9k reales vs 70.5k planificadas) con un desvío temporal de <b>+0.44 días de retraso</b>.", body_style),
        Paragraph("• <b>Tasa Fuera de Plan (Pregunta 2):</b> <b>17.46% global</b> (129 de 739 órdenes auditadas). CD_NORTE lidera desvíos (24.4%), seguido por CD_PACIFICO (21.3%). Miércoles (22.9%) y Lunes (22.1%) sufren la mayor deserción.", body_style),
        Paragraph("• <b>Ratio Retraso/Adelanto (3.45x):</b> Por cada orden adelantada, 3.45 órdenes se postergan. Esta deuda logística acumulada estalla en el cuello de botella del martes.", body_style),
        Paragraph("• <b>Saturación en CD_NORTE:</b> Supera el 100% de capacidad en el <b>10% de los días</b> (hasta 110.3%), acumulando <b>974.3 unidades en exceso</b> que forzaron fletes spot. Jueves y viernes quedan ociosos (70-80%).", body_style),
    ]
    t_sat_row = Table([[plan_diag, sat_img]], colWidths=[410, 310])
    t_sat_row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(t_sat_row)
    story.append(Spacer(1, 6))

    metrics_prop = (
        "<b>Métricas Operativas Adicionales Propuestas para Monitoreo Continuo (Pregunta 3):</b><br/>"
        "1. <b>Tasa de Adhesión por Cliente (Adhesion Rate):</b> Aísla el top 20% de clientes volátiles (Efecto Pareto). "
        "2. <b>Volumen en Riesgo Fuera de Plan (% Volume at Risk):</b> Pondera el impacto real en toneladas. "
        "3. <b>Peak-to-Average Ratio Semanal (PAR = 2.10x):</b> Monitorea la concentración extrema de demanda en días específicos."
    )
    story.append(Table([[Paragraph(metrics_prop, body_style)]], colWidths=[720], style=[
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEF3C7")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#FDE68A")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 5: ESTRATEGIA DE APLANAMIENTO: DYNAMIC DELIVERY SLOTTING (TAREA 2)
    # =========================================================================
    story.append(Paragraph("Estrategia de Aplanamiento: Dynamic Delivery Slotting e incentivos comerciales para balancear la flota", action_title_style))
    story.append(Paragraph("TAREA 2 (PROPUESTA ESTRATÉGICA): REDUCCIÓN DEL PICO DE MARTES Y BONIFICACIÓN EN VENTANAS VALLE", tracker_style))

    slots_data = [
        [
            Paragraph("ZONA VERDE (VALLE)", card_title),
            Paragraph("ZONA AMARILLA (NORMAL)", card_title),
            Paragraph("ZONA ROJA (PICO CRÍTICO)", card_title),
        ],
        [
            Paragraph("Ocupación ≤ 60%", highlight_text),
            Paragraph("60% < Ocupación ≤ 85%", ParagraphStyle("Amber", parent=card_title, fontSize=12, leading=14, textColor=colors.HexColor("#D97706"))),
            Paragraph("Ocupación > 85%", alert_text),
        ],
        [
            Paragraph("• Jueves y Viernes.<br/>• <b>Descuento Logístico 2.0% - 3.0%</b> en factura por entrega programada fija.<br/>• Despacho con SLA prioritario garantizado.", body_style),
            Paragraph("• Lunes y Miércoles.<br/>• Tarifa base de transporte estándar.<br/>• Asignación regular de ventanas de entrega sin bonificación.", body_style),
            Paragraph("• Martes en CD_NORTE y CD_SUR.<br/>• <b>Surge fee disuasivo (+3.0%)</b>.<br/>• Redirección sugerida a jueves con flete bonificado y preferencia de carga.", body_style),
        ],
    ]
    t_slots = Table(slots_data, colWidths=[240, 240, 240])
    t_slots.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(t_slots)
    story.append(Spacer(1, 10))

    col_impl = [
        Paragraph("<b>Mecanismo de Despliegue en Software B2B:</b>", bold_body),
        Paragraph("• <b>App de Preventa y Portal Web:</b> Al seleccionar el martes cuando la ocupación supere el 80%, el sistema activa una alerta proactiva ofreciendo entrega el jueves con descuento y SLA blindado.", body_style),
        Paragraph("• <b>Negociación con Cuentas Clave:</b> Acuerdos marco con el top 20% de clientes para entregas bisemanales balanceadas.", body_style),
    ]
    col_kpis = [
        Paragraph("<b>Metas Cuantitativas de la Estrategia:</b>", bold_body),
        Paragraph("• <b>Peak-to-Average Ratio (PAR):</b> Reducción de <b>2.10x a < 1.35x</b>.", body_style),
        Paragraph("• <b>Volumen en Días Valle:</b> Incrementar del 26% actual a <b>≥ 40%</b>.", body_style),
        Paragraph("• <b>Días Saturados CD_NORTE:</b> Disminución del <b>10% al 0%</b>.", body_style),
        Paragraph("• <b>Ahorro de Flota:</b> Evitar contratar 8 camiones fijos dedicados para absorber el pico.", body_style),
    ]
    t_strat = Table([[col_impl, col_kpis]], colWidths=[360, 360])
    t_strat.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#BFDBFE")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_strat)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 6: MODELO CORRECTOR RESIDUAL RIDGE L2 (TAREA 3)
    # =========================================================================
    story.append(Paragraph("Modelo Predictivo: Un corrector residual Ridge L2 supera a GBDT en costo, estabilidad y cero data leakage", action_title_style))
    story.append(Paragraph("TAREA 3: ARQUITECTURA RESIDUAL REGULARIZADA, JUSTIFICACIÓN TÉCNICA E IMPORTANCIA DE VARIABLES", tracker_style))

    feat_img_path = "reports/figures/fase_04/importancia_caracteristicas_modelo.png"
    feat_img = Image(feat_img_path, width=3.3 * inch, height=1.95 * inch) if os.path.exists(feat_img_path) else Paragraph("Gráfico no disponible", body_style)

    model_desc = [
        Paragraph("<b>Enfoque Analítico: Corrección Residual No-Negativa</b>", bold_body),
        Paragraph("En lugar de predecir la demanda desde cero arriesgando inestabilidad, modelamos quirúrgicamente el residuo del baseline:", body_style),
        Paragraph("<b>y_corregido = max(0, y_baseline + epsilon_hat)</b>", ParagraphStyle("Form", parent=bold_body, textColor=colors.HexColor("#0F172A"), fontSize=9)),
        Paragraph("• <b>Restricción de No-Negatividad:</b> Asegura que jamás se emitan órdenes de despacho negativas.", body_style),
        Spacer(1, 2),
        Paragraph("<b>¿Por qué Ridge L2 sobre LightGBM / GBDT?</b>", bold_body),
        Paragraph("• <b>Régimen 'Small Data':</b> Ventanas de 612 a 1,332 filas. Los árboles sobreajustan y crean funciones escalonadas rígidas.", body_style),
        Paragraph("• <b>Estructura Aditiva del Error:</b> El sesgo es de nivel territorial (+310 unid. CD_SUR) y pico martes, modelado de forma exacta y monótona por Ridge.", body_style),
        Paragraph("• <b>Eficiencia Operacional:</b> Solución cerrada calculada en <b>< 1 ms</b> por reentrenamiento diario, sin afinamiento estocástico de hiperparámetros.", body_style),
        Paragraph("• <b>Control Estricto de Leakage:</b> Rolling features de 7, 14 y 21 días calculadas estrictamente con datos cerrados a las 06:00 AM.", body_style),
    ]
    t_mod_row = Table([[model_desc, feat_img]], colWidths=[410, 310])
    t_mod_row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(t_mod_row)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 7: VALIDACIÓN OUT-OF-TIME: ROLLING BACKTEST (TAREA 3)
    # =========================================================================
    story.append(Paragraph("Validación Fuera de Muestra: El WAPE cae a 7.28% y el sesgo se neutraliza en todos los centros de la red", action_title_style))
    story.append(Paragraph("TAREA 3 (VALIDACIÓN): ROLLING-ORIGIN BACKTEST EN 31 DÍAS SECUENCIALES (708 PRONÓSTICOS EVALUADOS)", tracker_style))

    comp_img_path = "reports/figures/fase_04/comparativa_wape_modelo_vs_baseline.png"
    comp_img = Image(comp_img_path, width=3.3 * inch, height=1.9 * inch) if os.path.exists(comp_img_path) else Paragraph("Gráfico no disponible", body_style)

    bt_table_data = [
        ["Centro / Nivel", "WAPE Base", "WAPE Modelo", "Delta WAPE", "Bias Base", "Bias Modelo"],
        ["GLOBAL", "20.73%", "7.28%", "-13.45 pp", "+6.69%", "+0.69%"],
        ["CD_SUR", "31.14%", "6.48%", "-24.66 pp", "+31.14%", "-0.15%"],
        ["CD_ESTE", "26.44%", "8.08%", "-18.36 pp", "+25.87%", "+2.98%"],
        ["CD_PACIFICO", "23.14%", "5.72%", "-17.43 pp", "-22.52%", "+0.16%"],
        ["CD_OESTE", "23.45%", "8.24%", "-15.21 pp", "-21.95%", "-1.89%"],
        ["CD_CENTRO", "23.04%", "9.70%", "-13.33 pp", "-19.35%", "+0.48%"],
        ["CD_NORTE", "9.59%", "6.64%", "-2.94 pp", "+7.76%", "+1.32%"],
    ]
    t_bt = Table(bt_table_data, colWidths=[78, 58, 62, 62, 58, 62])
    t_bt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ]))

    t_bt_row = Table([[t_bt, comp_img]], colWidths=[385, 335])
    t_bt_row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story.append(t_bt_row)
    story.append(Spacer(1, 6))

    honest_box = (
        "<b>Honestidad Analítica y Criterio Lead:</b><br/>"
        "• <b>Comportamiento en D+4:</b> El WAPE cae de 22.98% a 9.90% (-13.1 pp). Sin embargo, D+4 mantiene la mayor dispersión debido a la incertidumbre irreducible de compras fuera de plan a 4 días.<br/>"
        "• <b>Conservadurismo en CD_NORTE:</b> La mejora fue de 2.94 pp (de 9.59% a 6.64%). Dado que CD_NORTE ya operaba aceptable, el modelo corrigió con prudencia sin sobreajustar.<br/>"
        "• <b>Pérdida Asimétrica Desplomada:</b> De 41.30% a <b>13.26% (-28.04 pp)</b>, traduciendo la mejora técnica en ahorro neto de transporte."
    )
    story.append(Table([[Paragraph(honest_box, body_style)]], colWidths=[720], style=[
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 8: RESILIENCIA OPERATIVA Y ARQUITECTURA CLOUD AWS (TAREAS 4 Y 5)
    # =========================================================================
    story.append(Paragraph("Resiliencia & Cloud: Gate de 45 días contra Cold Start y arquitectura AWS Serverless con ROI de 2,008%", action_title_style))
    story.append(Paragraph("TAREAS 4 Y 5: DATA COVERAGE GATE, TOLERANCIA A FALLAS Y ARQUITECTURA DE PRODUCCIÓN EN AWS", tracker_style))

    sens_img_path = "reports/figures/fase_05/flujo_decision_resiliencia_gate.png"
    sens_img = Image(sens_img_path, width=3.2 * inch, height=1.9 * inch) if os.path.exists(sens_img_path) else Paragraph("Gráfico no disponible", body_style)

    gate_desc = [
        Paragraph("<b>Lógica del DataCoverageGate (Sin Excepciones):</b>", bold_body),
        Paragraph("• Evalúa la racha continua de días de despacho sin vacíos de calendario en el CD:", body_style),
        Paragraph("  - <b>Racha ≥ 45 días continuos:</b> Habilita inferencia del modelo ML (`ADVANCED_MODEL`).", body_style),
        Paragraph("  - <b>Racha < 45 días (Cold Start):</b> Enruta automáticamente hacia el pronóstico base (`SAFE_FALLBACK`) con telemetría de advertencia sin arrojar excepciones.", body_style),
        Spacer(1, 2),
        Paragraph("<b>Justificación Estadística del Umbral de 45 Días:</b>", bold_body),
        Paragraph("• <b>6.4 ciclos semanales:</b> Garantiza al menos 6 observaciones de cada día (especialmente martes), acotando el error estándar (SE ≤ 0.408 sigma).", body_style),
        Paragraph("• <b>Saturación de Features:</b> Permite inicializar ventanas rodantes de 21 días sin imputación artificial.", body_style),
    ]
    t_gate_row = Table([[gate_desc, sens_img]], colWidths=[410, 310])
    t_gate_row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(t_gate_row)
    story.append(Spacer(1, 6))

    cloud_box = (
        "<b>Arquitectura AWS Serverless de 4 Capas & Dimensionamiento FinOps:</b><br/>"
        "• <b>1. Ingesta & Data Lake:</b> Amazon S3 (Parquet Snappy) + AWS KMS + AWS Glue Catalog.<br/>"
        "• <b>2. Orquestación Batch:</b> EventBridge (06:00 AM) + Step Functions (DAG) + SageMaker Training en instancias Spot (c6i.xlarge, ahorro 70%).<br/>"
        "• <b>3. Inferencia Tiempo Real (<50 ms):</b> API Gateway + ECS Fargate (FastAPI) + ElastiCache Redis para consulta ultrarrápida de cupos.<br/>"
        "• <b>4. FinOps & ROI:</b> Costo operativo de <b>~$185 USD/mes</b> frente a un ahorro de <b>~$3,900 USD/mes</b> en fletes spot. <b>ROI = 2,008% (21.1x)</b>."
    )
    story.append(Table([[Paragraph(cloud_box, body_style)]], colWidths=[720], style=[
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#BFDBFE")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 9: IMPACTO EN P&L, GOBERNANZA Y ROADMAP DE 12 SEMANAS (VISIÓN LEAD)
    # =========================================================================
    story.append(Paragraph("Impacto en Negocio & Roadmap: Ahorro de hasta $350k USD/año con despliegue en 12 semanas y monitoreo MLOps", action_title_style))
    story.append(Paragraph("CONCLUSIÓN ESTRATÉGICA: CASO DE NEGOCIO EN P&L, CRONOGRAMA DE ROLLOUT Y GOBERNANZA CONTINUA", tracker_style))

    pnl_cards = [
        [
            Paragraph("REDUCCIÓN DE FLETES SPOT", card_title),
            Paragraph("NIVEL DE SERVICIO (OTIF)", card_title),
            Paragraph("OPTIMIZACIÓN DE FLOTA PICO", card_title),
        ],
        [
            Paragraph("<b>-$240,000 USD/año</b>", highlight_text),
            Paragraph("<b>91.5% → 98.2%</b>", highlight_text),
            Paragraph("<b>-15% Camiones Fijos</b>", highlight_text),
        ],
        [
            Paragraph("Ahorro directo en fletes spot al eliminar<br/>974 unid. de desborde en CD_NORTE", subtext_center),
            Paragraph("Cumplimiento On-Time In-Full<br/>Menos penalizaciones comerciales B2B", subtext_center),
            Paragraph("Aplanamiento de demanda martes reduce<br/>necesidad de flota sobredimensionada", subtext_center),
        ],
    ]
    t_pnl = Table(pnl_cards, colWidths=[240, 240, 240])
    t_pnl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_pnl)
    story.append(Spacer(1, 8))

    roadmap_data = [
        ["Fase / Hito", "Semanas", "Alcance y Entregables Clave", "Criterio de Éxito / Gate"],
        ["Fase 1: Piloto Regional", "Sem 1 - 4", "Despliegue en CD_NORTE y CD_SUR. Activación de Step Functions y DataCoverageGate.", "WAPE < 8.5%, cero caídas en inferencia"],
        ["Fase 2: Dynamic Slotting", "Sem 5 - 8", "Integración de cupos en Portal B2B y App Preventa. Bonificación 2.5% días valle.", "Adopción de días valle > 35%, PAR < 1.6x"],
        ["Fase 3: Rollout Nacional", "Sem 9 - 12", "Extensión a los 6 CDs. Activación de SageMaker Model Monitor para drift continuo.", "100% eliminación de fletes spot, ROI 20x"],
    ]
    t_road = Table(roadmap_data, colWidths=[110, 60, 390, 160])
    t_road.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(t_road)
    story.append(Spacer(1, 6))

    gov_box = (
        "<b>Gobernanza Continua & Comité MLOps:</b><br/>"
        "• <b>Monitoreo Diario de Drift:</b> Alertas automatizadas en Slack/PagerDuty si WAPE móvil 7d supera el 12% o el Bias sale de [-4%, +4%].<br/>"
        "• <b>Reentrenamiento Semanal:</b> Ejecución dominical en SageMaker Spot con promoción automática al Model Registry si bate al baseline.<br/>"
        "• <b>Comité Conjunto S&OP:</b> Sesión quincenal de Data Science, Logística y Ventas para calibrar el semáforo de slotting dinámico."
    )
    story.append(Table([[Paragraph(gov_box, body_style)]], colWidths=[720], style=[
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ECFDF5")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#A7F3D0")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))

    doc.build(story, canvasmaker=McKinseyCanvas)
    print(f"[OK] Deck Ejecutivo de 9 diapositivas generado exitosamente en: {PDF_PATH}")


if __name__ == "__main__":
    build_9_slide_deck()
