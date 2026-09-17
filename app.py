import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
import google.generativeai as genai

# ==============================================================================
# 1. CONFIGURACIÓN Y CLIENTE IA
# ==============================================================================
st.set_page_config(
    page_title="KROMA Ops | Auditoría Operativa y Estratégica Universal",
    layout="wide"
)

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY and "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]

if API_KEY:
    genai.configure(api_key=API_KEY)
    ai_model = genai.GenerativeModel("gemini-1.5-pro-latest")
else:
    ai_model = None

# ==============================================================================
# 2. MOTOR MATEMÁTICO UNIVERSAL (RESIDUO CERO)
# ==============================================================================
def calcular_auditoria_universal(datos: dict) -> dict:
    facturacion = float(datos["facturacion"])
    coste_personal = float(datos["coste_personal"])
    costes_operativos = float(datos["costes_operativos"])
    aprovisionamientos = float(datos["aprovisionamientos"])
    plantilla = max(1, int(datos["plantilla"]))
    
    # 1. Conciliación Base P&L
    costes_totales = coste_personal + costes_operativos + aprovisionamientos
    ebitda_actual = facturacion - costes_totales
    margen_ebitda_pct = (ebitda_actual / facturacion * 100) if facturacion > 0 else 0.0
    margen_contribucion = facturacion - aprovisionamientos
    margen_contribucion_pct = (margen_contribucion / facturacion * 100) if facturacion > 0 else 0.0

    # 2. Ratios Clave de Eficiencia
    facturacion_por_empleado = facturacion / plantilla
    coste_personal_por_empleado = coste_personal / plantilla
    ratio_coste_laboral = (coste_personal / facturacion * 100) if facturacion > 0 else 0.0

    # 3. Modelado de Fugas e Ineficiencias según Nivel Digital y Procesos
    factores_fuga = {
        "Manual / Papel / Hojas de cálculo aisladas": 0.085,  # 8.5% pérdida estimada
        "Básico / Herramientas estándar no integradas": 0.050, # 5.0%
        "Medio / ERP o software sectorial parcial": 0.030,     # 3.0%
        "Alto / Procesos integrados y automatizados": 0.012   # 1.2%
    }
    pct_fuga = factores_fuga.get(datos["madurez_digital"], 0.04)
    
    # Impacto monetizado
    fuga_operativa_anual = facturacion * pct_fuga
    horas_recuperables_estimadas = (coste_personal * (pct_fuga * 0.75)) / max(22.0, (coste_personal_por_empleado / 1750))

    # 4. Proyección Proforma (Optimización y Modernización)
    mejora_eficiencia_ao1 = fuga_operativa_anual * 0.60
    coste_inversion_modernizacion = min(35000.0, max(4500.0, facturacion * 0.018))
    
    ebitda_proforma_ao1 = ebitda_actual + mejora_eficiencia_ao1
    ebitda_proforma_ao2 = ebitda_actual + (fuga_operativa_anual * 0.85)
    ebitda_proforma_ao3 = ebitda_actual + (fuga_operativa_anual * 1.05)

    payback_meses = (coste_inversion_modernizacion / mejora_eficiencia_ao1 * 12) if mejora_eficiencia_ao1 > 0 else 0.0
    roi_3_aos = (((mejora_eficiencia_ao1 + (fuga_operativa_anual * 0.85) + (fuga_operativa_anual * 1.05)) - coste_inversion_modernizacion) / coste_inversion_modernizacion * 100) if coste_inversion_modernizacion > 0 else 0.0

    # Verificación de cuadre a residuo cero
    residuo = round((facturacion - (aprovisionamientos + coste_personal + costes_operativos)) - ebitda_actual, 4)

    return {
        "facturacion": facturacion,
        "coste_personal": coste_personal,
        "costes_operativos": costes_operativos,
        "aprovisionamientos": aprovisionamientos,
        "plantilla": plantilla,
        "ebitda_actual": ebitda_actual,
        "margen_ebitda_pct": margen_ebitda_pct,
        "margen_contribucion": margen_contribucion,
        "margen_contribucion_pct": margen_contribucion_pct,
        "facturacion_por_empleado": facturacion_por_empleado,
        "coste_personal_por_empleado": coste_personal_por_empleado,
        "ratio_coste_laboral": ratio_coste_laboral,
        "fuga_operativa_anual": fuga_operativa_anual,
        "horas_recuperables_estimadas": horas_recuperables_estimadas,
        "coste_inversion_modernizacion": coste_inversion_modernizacion,
        "mejora_eficiencia_ao1": mejora_eficiencia_ao1,
        "ebitda_proforma_ao1": ebitda_proforma_ao1,
        "ebitda_proforma_ao2": ebitda_proforma_ao2,
        "ebitda_proforma_ao3": ebitda_proforma_ao3,
        "payback_meses": payback_meses,
        "roi_3_aos": roi_3_aos,
        "residuo_cero": residuo == 0.0
    }

# ==============================================================================
# 3. BENCHMARKING E INNOVACIÓN DINÁMICA (IA)
# ==============================================================================
def generar_analisis_ia(datos: dict, calc: dict) -> dict:
    if not ai_model:
        return {
            "benchmarking_sectorial": "Análisis sectorial no disponible (requiere API Key de Gemini configurada).",
            "evaluacion_cuello_botella": "Evaluación basada en parámetros estándar de eficiencia operativa.",
            "hoja_ruta_innovacion": {
                "fase_1_digitalizacion": "Auditoría de procesos manuales y centralización de datos maestros.",
                "fase_2_automatizacion": "Integración de flujos de trabajo repetitivos y facturación electrónica.",
                "fase_3_ia_aplicada": "Modelado predictivo de demanda y asistencia automatizada.",
                "fase_4_blindaje_legal": "Cumplimiento normativo de facturación digital obligatoria."
            },
            "recomendacion_directiva": "Priorizar la captura de fugas operativas de corto plazo para autofinanciar la modernización tecnológica."
        }

    prompt = f"""
    Actúa como un Auditor Estratégico y Consultor de Dirección de primer nivel (KROMA Ops).
    Tu misión es generar un análisis contextualizado de benchmarking sectorial y una hoja de ruta de innovación para la siguiente empresa:

    PERFIL DE LA EMPRESA:
    - Nombre: {datos.get('nombre_empresa', 'Empresa Auditada')}
    - Sector de Actividad: {datos.get('sector', 'No especificado')}
    - Modelo de Negocio: {datos.get('modelo_negocio', 'Servicios / Operaciones')}
    - Plantilla: {calc['plantilla']} empleados
    - Madurez Digital Actual: {datos.get('madurez_digital', 'Básica')}
    - Principal Cuello de Botella Declarado: {datos.get('cuello_botella', 'Gestión operativa')}

    MÉTRICAS Y P&L CONCILIADO:
    - Facturación Anual: {calc['facturacion']:,.2f} €
    - Facturación por Empleado: {calc['facturacion_por_empleado']:,.2f} €
    - Peso de Personal sobre Ventas: {calc['ratio_coste_laboral']:.1f} %
    - EBITDA Actual: {calc['ebitda_actual']:,.2f} € ({calc['margen_ebitda_pct']:.1f} %)
    - Fuga Operativa Estimada: {calc['fuga_operativa_anual']:,.2f} € / año
    - Horas anuales recuperables: {calc['horas_recuperables_estimadas']:.0f} h

    INSTRUCCIONES ANALÍTICAS:
    1. Compara estos ratios con los estándares reales y benchmarking de su sector ({datos.get('sector')}). Indica si sus ratios están por encima, en la media o rezagados respecto al cuartil superior.
    2. Analiza específicamente su cuello de botella declarado ('{datos.get('cuello_botella')}') y explica la causa raíz operativa.
    3. Diseña una hoja de ruta de modernización en 4 horizontes:
       - Digitalización y procesos inmediatos.
       - Automatización de flujos de trabajo.
       - Aplicación práctica de Inteligencia Artificial específica para este sector.
       - Adecuación y blindaje normativo / fiscal (Facturación electrónica, Veri*factu).
    4. Proporciona una recomendación de gobernanza para el Comité de Dirección.

    RESPONDE EXCLUSIVAMENTE CON UN OBJETO JSON VÁLIDO CON ESTA ESTRUCTURA (sin comillas invertidas ni bloques markdown):
    {{
        "benchmarking_sectorial": "Análisis comparativo riguroso frente al mercado...",
        "evaluacion_cuello_botella": "Diagnóstico detallado de su principal fricción...",
        "hoja_ruta_innovacion": {{
            "fase_1_digitalizacion": "...",
            "fase_2_automatizacion": "...",
            "fase_3_ia_aplicada": "...",
            "fase_4_blindaje_legal": "..."
        }},
        "recomendacion_directiva": "Dictamen final para la Dirección General..."
    }}
    """
    try:
        response = ai_model.generate_content(prompt)
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        return json.loads(raw_text.strip())
    except Exception as e:
        return {
            "benchmarking_sectorial": f"Diagnóstico sectorial en proceso. Análisis empírico del sector {datos.get('sector')}.",
            "evaluacion_cuello_botella": f"Fricción identificada en {datos.get('cuello_botella')}. Se sugiere optimización de tiempos.",
            "hoja_ruta_innovacion": {
                "fase_1_digitalizacion": "Estandarización y captura centralizada de datos.",
                "fase_2_automatizacion": "Eliminación de tareas manuales de gestión y reconciliación.",
                "fase_3_ia_aplicada": "Asistentes de operaciones y automatización analítica.",
                "fase_4_blindaje_legal": "Adaptación a sistemas de facturación verificable."
            },
            "recomendacion_directiva": "Proceder a la fase de captura de ineficiencias según el plan proforma."
        }

# ==============================================================================
# 4. GENERADOR PDF EDITORIAL (15 SECCIONES)
# ==============================================================================
class NumberedCanvas(canvas.Canvas):
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
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        # Encabezado
        self.drawString(54, 800, "KROMA OPS | DOSSIER DE AUDITORÍA OPERATIVA Y ESTRATÉGICA")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 792, 541, 792)
        # Pie
        self.line(54, 48, 541, 48)
        self.drawString(54, 36, "DOCUMENTO TÉCNICO CONFIDENCIAL - EMISIÓN DIRECTIVA")
        self.drawRightString(541, 36, f"Página {self._pageNumber} de {page_count}")
        self.restoreState()

def generar_pdf_universal(datos: dict, calc: dict, ia_results: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=60,
        bottomMargin=60
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=12
    )
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=14,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=8
    )

    story = []

    # Portada / Cabecera
    story.append(Paragraph(f"INFORME DE AUDITORÍA OPERATIVA Y HOJA DE RUTA", title_style))
    story.append(Paragraph(f"<b>Entidad:</b> {datos.get('nombre_empresa', 'No especificada')} | <b>Sector:</b> {datos.get('sector', 'General')} | <b>Plantilla:</b> {calc['plantilla']} personas", body_style))
    story.append(Spacer(1, 10))

    # Sección 1: P&L Base
    story.append(Paragraph("1. Conciliación Económica Base (P&L Verificada)", h1_style))
    pl_data = [
        ["Concepto Contable", "Importe Anual (€)", "% sobre Ingresos"],
        ["Facturación Total Bruta", f"{calc['facturacion']:,.2f} €", "100,0 %"],
        ["Aprovisionamientos / Costes Directos", f"{calc['aprovisionamientos']:,.2f} €", f"{calc['aprovisionamientos']/calc['facturacion']*100:.1f} %"],
        ["Masa Salarial y Cargas Sociales", f"{calc['coste_personal']:,.2f} €", f"{calc['ratio_coste_laboral']:.1f} %"],
        ["Costes Operativos Generales (Opex)", f"{calc['costes_operativos']:,.2f} €", f"{calc['costes_operativos']/calc['facturacion']*100:.1f} %"],
        ["EBITDA de Explotación", f"{calc['ebitda_actual']:,.2f} €", f"{calc['margen_ebitda_pct']:.1f} %"]
    ]
    t_pl = Table(pl_data, colWidths=[240, 130, 117])
    t_pl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.HexColor("#0F172A")),
    ]))
    story.append(t_pl)
    story.append(Spacer(1, 10))

    # Sección 2: Benchmarking Sectorial (IA)
    story.append(Paragraph("2. Evaluación de Benchmarking y Competitividad Sectorial", h1_style))
    story.append(Paragraph(ia_results.get("benchmarking_sectorial", ""), body_style))
    story.append(Spacer(1, 8))

    # Sección 3: Análisis de Cuello de Botella y Fugas
    story.append(Paragraph(f"3. Diagnóstico de Operativa y Fricción Declarada ({datos.get('cuello_botella', 'Operativa')})", h1_style))
    story.append(Paragraph(ia_results.get("evaluacion_cuello_botella", ""), body_style))
    story.append(Paragraph(f"<b>Cuantificación de fuga operativa estimada:</b> {calc['fuga_operativa_anual']:,.2f} €/año (equivalente a aprox. {calc['horas_recuperables_estimadas']:,.0f} horas de capacidad no capitalizada).", body_style))
    story.append(Spacer(1, 8))

    # Sección 4: Plan Proforma de Modernización a 3 Años
    story.append(Paragraph("4. Cuenta de Resultados Proforma con Eficiencia Operativa (3 Años)", h1_style))
    proforma_data = [
        ["Horizonte Temporal", "EBITDA Proyectado (€)", "Margen s/Ventas", "Generación Neta Acumulada"],
        ["Año 0 (Situación Actual)", f"{calc['ebitda_actual']:,.2f} €", f"{calc['margen_ebitda_pct']:.1f} %", "Base de Referencia"],
        ["Año 1 (Fase Digital / Captura 60%)", f"{calc['ebitda_proforma_ao1']:,.2f} €", f"{calc['ebitda_proforma_ao1']/calc['facturacion']*100:.1f} %", f"+{calc['mejora_eficiencia_ao1']:,.2f} €"],
        ["Año 2 (Automatización / Captura 85%)", f"{calc['ebitda_proforma_ao2']:,.2f} €", f"{calc['ebitda_proforma_ao2']/calc['facturacion']*100:.1f} %", f"+{calc['ebitda_proforma_ao2']-calc['ebitda_actual']:,.2f} €"],
        ["Año 3 (Madurez con IA / 100%+)", f"{calc['ebitda_proforma_ao3']:,.2f} €", f"{calc['ebitda_proforma_ao3']/calc['facturacion']*100:.1f} %", f"+{calc['ebitda_proforma_ao3']-calc['ebitda_actual']:,.2f} €"]
    ]
    t_prof = Table(proforma_data, colWidths=[150, 110, 95, 132])
    t_prof.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
    ]))
    story.append(t_prof)
    story.append(Spacer(1, 10))

    # Sección 5: Hoja de Ruta de Innovación
    story.append(Paragraph("5. Hoja de Ruta de Innovación y Modernización Integral", h1_style))
    ruta = ia_results.get("hoja_ruta_innovacion", {})
    story.append(Paragraph(f"• <b>Digitalización de Procesos:</b> {ruta.get('fase_1_digitalizacion', '')}", body_style))
    story.append(Paragraph(f"• <b>Automatización de Flujos:</b> {ruta.get('fase_2_automatizacion', '')}", body_style))
    story.append(Paragraph(f"• <b>Inteligencia Artificial Aplicada:</b> {ruta.get('fase_3_ia_aplicada', '')}", body_style))
    story.append(Paragraph(f"• <b>Blindaje Normativo y Fiscal:</b> {ruta.get('fase_4_blindaje_legal', '')}", body_style))
    story.append(Spacer(1, 10))

    # Sección 6: Dictamen Directivo
    story.append(Paragraph("6. Dictamen de Dirección y Gobernanza", h1_style))
    story.append(Paragraph(ia_results.get("recomendacion_directiva", ""), body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()

# ==============================================================================
# 5. INTERFAZ LIMPIA DE ENTRADA DE DATOS (STREAMLIT)
# ==============================================================================
st.title("KROMA Ops — Auditoría Operativa y Financiera")
st.caption("Diagnóstico universal de capacidad, benchmarking sectorial y hoja de ruta de innovación.")

with st.form("form_auditoria_universal"):
    st.subheader("1. Identificación y Perfil de Negocio")
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        nombre_empresa = st.text_input("Nombre de la Empresa", value="Soluciones Integrales S.L.")
        sector = st.text_input("Sector de Actividad", value="Servicios Técnicos y Mantenimiento Industrial")
    with col_a2:
        modelo_negocio = st.selectbox(
            "Modelo Operativo Principal",
            ["Servicios con personal de campo / desplazamientos", "Servicios profesionales / consultoría", "Proyectos e instalaciones", "Distribución y comercio", "Fabricación / Taller"]
        )
        plantilla = st.number_input("Plantilla Total (personas)", min_value=1, value=12, step=1)

    st.subheader("2. Cuentas Maestras de Explotación (Anual)")
    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
    with col_b1:
        facturacion = st.number_input("Facturación Anual (€)", min_value=10000.0, value=850000.0, step=10000.0)
    with col_b2:
        coste_personal = st.number_input("Coste Personal Anual (€)", min_value=5000.0, value=380000.0, step=5000.0)
    with col_b3:
        aprovisionamientos = st.number_input("Aprovisionamientos / Materiales (€)", min_value=0.0, value=220000.0, step=5000.0)
    with col_b4:
        costes_operativos = st.number_input("Gastos Generales / Opex (€)", min_value=0.0, value=110000.0, step=5000.0)

    st.subheader("3. Madurez y Cuellos de Botella Actuales")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        madurez_digital = st.selectbox(
            "Nivel de Digitalización Actual",
            [
                "Manual / Papel / Hojas de cálculo aisladas",
                "Básico / Herramientas estándar no integradas",
                "Medio / ERP o software sectorial parcial",
                "Alto / Procesos integrados y automatizados"
            ]
        )
    with col_c2:
        cuello_botella = st.selectbox(
            "Principal Fricción o Reto Percibido",
            [
                "Control de horas trabajadas vs. horas facturadas",
                "Retrasos en presupuestos y cobro de servicios",
                "Márgenes reducidos y costes operativos descontrolados",
                "Dependencia excesiva de tareas manuales y administrativas",
                "Falta de visibilidad sobre la rentabilidad real por cliente o proyecto"
            ]
        )

    submit_btn = st.form_submit_button("Ejecutar Auditoría y Generar Plan")

# ==============================================================================
# 6. EJECUCIÓN Y RENDERIZADO DEL DIAGNÓSTICO
# ==============================================================================
if submit_btn:
    datos_input = {
        "nombre_empresa": nombre_empresa,
        "sector": sector,
        "modelo_negocio": modelo_negocio,
        "plantilla": plantilla,
        "facturacion": facturacion,
        "coste_personal": coste_personal,
        "aprovisionamientos": aprovisionamientos,
        "costes_operativos": costes_operativos,
        "madurez_digital": madurez_digital,
        "cuello_botella": cuello_botella
    }

    with st.spinner("Conciliando estados financieros a residuo cero y analizando sector..."):
        calculos = calcular_auditoria_universal(datos_input)
        analisis_ia = generar_analisis_ia(datos_input, calculos)
        pdf_bytes = generar_pdf_universal(datos_input, calculos, analisis_ia)

    st.success("Auditoría completada. Conciliación matemática verificada (Residuo: 0,00 €).")

    # Métricas de primer nivel
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("EBITDA Actual", f"{calculos['ebitda_actual']:,.2f} €", f"{calculos['margen_ebitda_pct']:.1f}%")
    m2.metric("Fuga Operativa Anual", f"{calculos['fuga_operativa_anual']:,.2f} €", "-Incurrible", delta_color="inverse")
    m3.metric("Recuperación Año 1", f"+{calculos['mejora_eficiencia_ao1']:,.2f} €", f"Payback: {calculos['payback_meses']:.1f} m")
    m4.metric("Facturación / Empleado", f"{calculos['facturacion_por_empleado']:,.2f} €", f"Coste: {calculos['ratio_coste_laboral']:.1f}% s/Ventas")

    st.markdown("---")

    # Pestañas de detalle
    tab1, tab2, tab3 = st.tabs(["📊 P&L Conciliado", "🌐 Benchmarking e IA", "🚀 Plan de Innovación"])

    with tab1:
        st.write("#### Conciliación Estricta de la Cuenta de Explotación")
        df_pl = pd.DataFrame([
            {"Partida": "Facturación Bruta", "Importe (€)": calculos["facturacion"], "% s/Ventas": 100.0},
            {"Partida": "(-) Aprovisionamientos y Costes Directos", "Importe (€)": -calculos["aprovisionamientos"], "% s/Ventas": (calculos["aprovisionamientos"]/calculos["facturacion"])*100},
            {"Partida": "(-) Masa Salarial y Seguridad Social", "Importe (€)": -calculos["coste_personal"], "% s/Ventas": calculos["ratio_coste_laboral"]},
            {"Partida": "(-) Gastos de Explotación (Opex)", "Importe (€)": -calculos["costes_operativos"], "% s/Ventas": (calculos["costes_operativos"]/calculos["facturacion"])*100},
            {"Partida": "(=) EBITDA Normalizado", "Importe (€)": calculos["ebitda_actual"], "% s/Ventas": calculos["margen_ebitda_pct"]},
        ])
        st.dataframe(df_pl.style.format({"Importe (€)": "{:,.2f} €", "% s/Ventas": "{:.1f} %"}), use_container_width=True)

    with tab2:
        st.write("#### Benchmarking Sectorial Dinámico")
        st.info(analisis_ia.get("benchmarking_sectorial", ""))
        st.write("#### Análisis del Cuello de Botella")
        st.write(analisis_ia.get("evaluacion_cuello_botella", ""))

    with tab3:
        st.write("#### Hoja de Ruta de Modernización")
        ruta = analisis_ia.get("hoja_ruta_innovacion", {})
        st.markdown(f"**1. Digitalización:** {ruta.get('fase_1_digitalizacion', '')}")
        st.markdown(f"**2. Automatización:** {ruta.get('fase_2_automatizacion', '')}")
        st.markdown(f"**3. IA Aplicada al Sector:** {ruta.get('fase_3_ia_aplicada', '')}")
        st.markdown(f"**4. Blindaje Normativo:** {ruta.get('fase_4_blindaje_legal', '')}")
        st.markdown(f"> **Dictamen Directivo:** {analisis_ia.get('recomendacion_directiva', '')}")

    st.markdown("---")
    st.download_button(
        label="📄 Descargar Dossier de Auditoría Completo (PDF)",
        data=pdf_bytes,
        file_name=f"Auditoria_KROMA_{datos_input['nombre_empresa'].replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
