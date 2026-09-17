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
    page_title="KROMA Ops | Diagnóstico Empresarial Integral",
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
# 2. MOTOR MATEMÁTICO DETERMINISTA Y CÁLCULO DE ÍNDICES
# ==============================================================================
def ejecutar_motor_diagnostico(d: dict) -> dict:
    # 1. P&L y Tendencia
    v_actual = float(d["ventas_n"])
    v_anterior = max(1.0, float(d["ventas_n1"]))
    crecimiento_ventas = ((v_actual - v_anterior) / v_anterior) * 100.0

    compras = float(d["compras"])
    subcontratas = float(d["subcontratas"])
    coste_personal = float(d["personal"])
    gastos_estructura = float(d["estructura"])
    amortizaciones = float(d["amortizaciones"])
    gastos_financieros = float(d["gastos_financieros"])

    margen_bruto = v_actual - compras - subcontratas
    margen_bruto_pct = (margen_bruto / v_actual * 100.0) if v_actual > 0 else 0.0

    ebitda = margen_bruto - coste_personal - gastos_estructura
    ebitda_pct = (ebitda / v_actual * 100.0) if v_actual > 0 else 0.0

    ebit = ebitda - amortizaciones
    ebt = ebit - gastos_financieros

    # 2. Tesorería y Ciclo de Conversión de Efectivo (CCC)
    saldo_clientes = float(d["saldo_clientes"])
    saldo_proveedores = float(d["saldo_proveedores"])
    stock_medio = float(d["stock_medio"])
    caja_actual = float(d["caja_actual"])
    deuda_bancaria = float(d["deuda_bancaria"])
    cuota_deuda_anual = float(d["cuota_mensual_deuda"]) * 12.0

    dso = (saldo_clientes / v_actual * 365.0) if v_actual > 0 else 0.0
    dpo = (saldo_proveedores / (compras + subcontratas) * 365.0) if (compras + subcontratas) > 0 else 0.0
    coste_mercancias = compras if compras > 0 else (v_actual * 0.4)
    dio = (stock_medio / coste_mercancias * 365.0) if coste_mercancias > 0 else 0.0
    ccc = dio + dso - dpo

    # Caja inmovilizada por DSO > 45 días o stock > 60 días
    ventas_dia = v_actual / 365.0
    caja_atrapada_dso = max(0.0, (dso - 45.0) * ventas_dia)
    caja_atrapada_stock = max(0.0, (dio - 60.0) * (coste_mercancias / 365.0))
    potencial_liberacion_caja = caja_atrapada_dso + caja_atrapada_stock

    # 3. Productividad y Personas
    plantilla = max(1, int(d["plantilla"]))
    coste_hora_medio = (coste_personal / plantilla / 1750.0) if plantilla > 0 else 25.0
    horas_totales_disponibles = plantilla * 1750.0
    horas_improductivas_pct = float(d["pct_horas_improductivas"]) / 100.0
    horas_improductivas = horas_totales_disponibles * horas_improductivas_pct
    coste_horas_improductivas = horas_improductivas * coste_hora_medio

    # 4. Operaciones, Retrabajo e Ineficiencia Administrativa
    num_trabajos = max(1, int(d["num_trabajos_anuales"]))
    pct_retrabajo = float(d["pct_retrabajo"]) / 100.0
    coste_medio_error = float(d["coste_medio_error"])
    coste_retrabajo_anual = num_trabajos * pct_retrabajo * coste_medio_error

    duplicidad_datos = max(1, int(d["duplicidad_datos"]))
    minutos_duplicados_dia = float(d["operaciones_diarias"]) * (duplicidad_datos - 1) * 6.0
    horas_fuga_admin_anual = (minutos_duplicados_dia / 60.0) * 220.0
    fuga_administrativa_euros = horas_fuga_admin_anual * coste_hora_medio

    # 5. Comercial y Concentración
    leads = max(1, int(d["leads_anuales"]))
    ventas_cerradas = max(1, int(d["ventas_cerradas"]))
    tasa_conversion = (ventas_cerradas / leads) * 100.0
    ticket_medio = v_actual / ventas_cerradas if ventas_cerradas > 0 else 0.0
    concentracion_top5 = float(d["concentracion_top5"])

    # 6. Cuantificación de los "€ de Oportunidad" (DR / C / ES / HC)
    dr_retorno_directo = (coste_retrabajo_anual * 0.70) + (potencial_liberacion_caja * 0.15)
    c_capacidad_liberada = (coste_horas_improductivas * 0.50) * (margen_bruto_pct / 100.0)
    es_eficiencia_estructura = fuga_administrativa_euros * 0.85
    hc_headcount_saving = (fuga_administrativa_euros + (coste_horas_improductivas * 0.30)) * 0.40
    total_oportunidad_euros = dr_retorno_directo + c_capacidad_liberada + es_eficiencia_estructura

    # 7. Cálculo de los 8 Índices de Rendimiento (0.0 a 10.0)
    idx_rentabilidad = min(10.0, max(0.0, (ebitda_pct / 18.0) * 10.0))
    idx_productividad = min(10.0, max(0.0, ((1.0 - horas_improductivas_pct) / 0.85) * 10.0))
    idx_liquidez = 10.0 if ccc <= 30 else max(0.0, 10.0 - ((ccc - 30.0) / 12.0))
    idx_comercial = min(10.0, max(0.0, (tasa_conversion / 35.0) * 10.0))
    idx_operaciones = max(0.0, 10.0 - (pct_retrabajo * 80.0))
    
    score_dig = {
        "Baja / Hojas sueltas": 2.0,
        "Parcial / Software no conectado": 4.5,
        "ERP centralizado": 7.5,
        "Automatizado / Conectado": 9.5
    }
    idx_digitalizacion = score_dig.get(d["madurez_digital"], 5.0)

    riesgo_penaliz = 0.0
    if concentracion_top5 > 50: riesgo_penaliz += 3.0
    if d["dependencia_gerente"] == "La empresa se detiene en 48-72h": riesgo_penaliz += 4.0
    if deuda_bancaria > (ebitda * 3.5) and ebitda > 0: riesgo_penaliz += 2.5
    idx_riesgo = max(1.0, 10.0 - riesgo_penaliz)

    cap_extra = float(d["capacidad_adicional_pct"])
    idx_crecimiento = min(10.0, max(1.0, (cap_extra / 40.0) * 10.0))

    return {
        "v_actual": v_actual, "v_anterior": v_anterior, "crecimiento_ventas": crecimiento_ventas,
        "margen_bruto": margen_bruto, "margen_bruto_pct": margen_bruto_pct,
        "ebitda": ebitda, "ebitda_pct": ebitda_pct, "ebit": ebit, "ebt": ebt,
        "dso": dso, "dpo": dpo, "dio": dio, "ccc": ccc,
        "caja_atrapada_dso": caja_atrapada_dso, "potencial_liberacion_caja": potencial_liberacion_caja,
        "coste_retrabajo_anual": coste_retrabajo_anual,
        "fuga_administrativa_euros": fuga_administrativa_euros,
        "coste_horas_improductivas": coste_horas_improductivas,
        "tasa_conversion": tasa_conversion, "ticket_medio": ticket_medio,
        "dr_retorno_directo": dr_retorno_directo,
        "c_capacidad_liberada": c_capacidad_liberada,
        "es_eficiencia_estructura": es_eficiencia_estructura,
        "hc_headcount_saving": hc_headcount_saving,
        "total_oportunidad_euros": total_oportunidad_euros,
        "indices": {
            "Rentabilidad": idx_rentabilidad,
            "Productividad": idx_productividad,
            "Liquidez": idx_liquidez,
            "Comercial": idx_comercial,
            "Operaciones": idx_operaciones,
            "Digitalización": idx_digitalizacion,
            "Autonomía y Riesgo": idx_riesgo,
            "Capacidad de Crecimiento": idx_crecimiento
        }
    }

# ==============================================================================
# 3. INTERPRETACIÓN ESTRATÉGICA CONTEXTUAL (GEMINI 1.5 PRO)
# ==============================================================================
def consultar_inteligencia_gemini(datos: dict, c: dict) -> dict:
    if not ai_model:
        return {
            "dictamen_ejecutivo": "Diagnóstico generado mediante motor determinista local. Configure GEMINI_API_KEY para síntesis estratégica avanzada.",
            "analisis_cuello_botella": f"Fricción identificada en {datos.get('colapso_20pct', 'operaciones')} con impacto directo en margen.",
            "analisis_riesgo_gobernanza": "Dependencia organizativa moderada. Requiere estandarizar procesos en puestos clave.",
            "hoja_ruta": {
                "inmediato_30d": "Contención de fugas en retrabajo y aceleración de cobros pendientes.",
                "medio_plazo_90d": "Automatización de duplicidades de datos y eliminación de software obsoleto.",
                "estrategico_12m": f"Alineación organizativa orientada al objetivo directivo: {datos.get('objetivo_estrategico', 'Crecer')}"
            }
        }

    prompt = f"""
    Actúa como Socio Director de Consultoría Estratégica (KROMA Ops). 
    Audita a la siguiente empresa con rigor implacable a partir de sus datos reales e índices calculados:

    EMPRESA Y CONTEXTO:
    - Razón Social: {datos.get('nombre_empresa')} | Sector: {datos.get('sector')} | Submódulo: {datos.get('tipo_negocio')}
    - Objetivo de la Dirección: {datos.get('objetivo_estrategico')} | Problema Crítico Declarado: {datos.get('problema_principal')}
    - Colapso si suben ventas 20%: {datos.get('colapso_20pct')} | Dependencia Gerente: {datos.get('dependencia_gerente')}
    - Datos Específicos del Módulo: {json.dumps(datos.get('datos_sectoriales', {}), ensure_ascii=False)}

    MÉTRICAS ECONÓMICAS Y OPERATIVAS:
    - Ventas: {c['v_actual']:,.2f} € (Variación interanual: {c['crecimiento_ventas']:+.1f}%)
    - Margen Bruto: {c['margen_bruto']:,.2f} € ({c['margen_bruto_pct']:.1f}%) | EBITDA: {c['ebitda']:,.2f} € ({c['ebitda_pct']:.1f}%)
    - Ciclo Conversión Efectivo (CCC): {c['ccc']:.1f} días (DSO: {c['dso']:.1f}d | Stock: {c['dio']:.1f}d | DPO: {c['dpo']:.1f}d)
    - Concentración Top 5 Clientes: {datos.get('concentracion_top5')}%

    OPORTUNIDAD MONETIZADA (TOTAL RECUPERABLE: {c['total_oportunidad_euros']:,.2f} €/año):
    - [DR] Retorno Directo (Retrabajos + Merma): {c['dr_retorno_directo']:,.2f} €
    - [C] Capacidad Liberada (Horas Improductivas): {c['c_capacidad_liberada']:,.2f} €
    - [ES] Eficiencia Estructural (Duplicidad Administrativa): {c['es_eficiencia_estructura']:,.2f} €

    PUNTUACIÓN 8 ÍNDICES KROMA (0-10):
    {json.dumps({k: round(v, 1) for k, v in c['indices'].items()}, ensure_ascii=False)}

    INSTRUCCIONES DIRECTIVAS:
    1. Redacta un DICTAMEN EJECUTIVO directo, sin rodeos, evaluando si el modelo actual soporta el objetivo de "{datos.get('objetivo_estrategico')}".
    2. Analiza la CAUSA RAÍZ de su cuello de botella operativo ({datos.get('colapso_20pct')}).
    3. Evalúa el RIESGO DE GOBERNANZA (dependencia del gerente y concentración de clientes).
    4. Diseña una HOJA DE RUTA en 3 fases (30 días, 90 días, 12 meses) enfocada en capturar los € de oportunidad y blindar la empresa.

    RESPONDE EXCLUSIVAMENTE CON UN OBJETO JSON VÁLIDO (sin markdown, sin comillas triples):
    {{
        "dictamen_ejecutivo": "...",
        "analisis_cuello_botella": "...",
        "analisis_riesgo_gobernanza": "...",
        "hoja_ruta": {{
            "inmediato_30d": "...",
            "medio_plazo_90d": "...",
            "estrategico_12m": "..."
        }}
    }}
    """
    try:
        res = ai_model.generate_content(prompt)
        txt = res.text.strip()
        if txt.startswith("```json"): txt = txt[7:]
        if txt.startswith("```"): txt = txt[3:]
        if txt.endswith("```"): txt = txt[:-3]
        return json.loads(txt.strip())
    except Exception:
        return {
            "dictamen_ejecutivo": f"La estructura económica muestra un EBITDA del {c['ebitda_pct']:.1f}%. El objetivo de '{datos.get('objetivo_estrategico')}' requiere sanear el ciclo de conversión de efectivo ({c['ccc']:.0f} días) y erradicar tareas manuales.",
            "analisis_cuello_botella": f"El colapso señalado en '{datos.get('colapso_20pct')}' evidencia un dimensionamiento rígido que absorbe liquidez.",
            "analisis_riesgo_gobernanza": f"Concentración en principales cuentas ({datos.get('concentracion_top5')}%) y nivel de dependencia directiva clasificado como crítico.",
            "hoja_ruta": {
                "inmediato_30d": "Reclamación activa de cobros vencidos y reducción de retrabajos operativos.",
                "medio_plazo_90d": "Unificación de la pila de software para suprimir la duplicidad de datos.",
                "estrategico_12m": "Estandarización de procesos operativos para desacoplar el crecimiento del tiempo del director general."
            }
        }

# ==============================================================================
# 4. GENERADOR PDF EDITORIAL DE ALTA DENSIDAD
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
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#475569"))
        self.drawString(45, 804, "KROMA OPS | AUDITORÍA INTEGRAL Y DICTAMEN ESTRATÉGICO")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(45, 796, 550, 796)
        self.line(45, 42, 550, 42)
        self.drawString(45, 30, "DOCUMENTO TÉCNICO CONFIDENCIAL - ESTRICTAMENTE RESERVADO A DIRECCIÓN")
        self.drawRightString(550, 30, f"Página {self._pageNumber} de {page_count}")
        self.restoreState()

def generar_pdf_dossier(d: dict, c: dict, ia: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=45,
        rightMargin=45,
        topMargin=55,
        bottomMargin=55
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=colors.HexColor("#0F172A"), spaceAfter=6)
    sub_style = ParagraphStyle('DocSub', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=11, textColor=colors.HexColor("#64748B"), spaceAfter=12)
    h1 = ParagraphStyle('H1', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10.5, leading=14, textColor=colors.HexColor("#0F172A"), spaceBefore=10, spaceAfter=5)
    body = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor("#334155"), spaceAfter=6)
    callout = ParagraphStyle('Callout', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, leading=11, textColor=colors.HexColor("#1E293B"))

    story = []
    story.append(Paragraph(f"INFORME DE AUDITORÍA OPERATIVA Y VALORACIÓN DE EFICIENCIA", title_style))
    story.append(Paragraph(f"<b>Entidad:</b> {d.get('nombre_empresa')} | <b>Sector:</b> {d.get('sector')} | <b>Modelo:</b> {d.get('tipo_negocio')} | <b>Objetivo Declarado:</b> {d.get('objetivo_estrategico')}", sub_style))

    # Bloque 1: Dictamen Ejecutivo
    story.append(Paragraph("1. DICTAMEN ESTRATÉGICO DE DIRECCIÓN", h1))
    story.append(Paragraph(ia.get("dictamen_ejecutivo", ""), callout))
    story.append(Spacer(1, 6))

    # Bloque 2: Matriz de los 8 Índices KROMA
    story.append(Paragraph("2. MATRIZ CUANTITATIVA DE 8 ÍNDICES DE RENDIMIENTO", h1))
    idx_items = list(c["indices"].items())
    row1_names = [k for k, _ in idx_items[:4]]
    row1_vals = [f"{v:.1f} / 10" for _, v in idx_items[:4]]
    row2_names = [k for k, _ in idx_items[4:]]
    row2_vals = [f"{v:.1f} / 10" for _, v in idx_items[4:]]
    
    t_idx_data = [
        row1_names,
        row1_vals,
        row2_names,
        row2_vals
    ]
    t_idx = Table(t_idx_data, colWidths=[126, 126, 126, 127])
    t_idx.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor("#F8FAFC")),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor("#1E293B")),
        ('TEXTCOLOR', (0, 2), (-1, 2), colors.white),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor("#F8FAFC")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_idx)
    story.append(Spacer(1, 8))

    # Bloque 3: € de Oportunidad (DR / C / ES / HC)
    story.append(Paragraph("3. CUANTIFICACIÓN DEL IMPACTO RECUPERABLE (€ DE OPORTUNIDAD)", h1))
    opp_data = [
        ["Vector de Impacto", "Monetización (€/año)", "Origen de la Fuga / Acción Requerida"],
        ["[DR] Retorno Directo", f"{c['dr_retorno_directo']:,.2f} €", "Contención de retrabajo, costes de errores y liquidación de mermas"],
        ["[C] Capacidad Liberada", f"{c['c_capacidad_liberada']:,.2f} €", "Margen bruto recuperable al reconvertir horas improductivas en facturación"],
        ["[ES] Eficiencia de Estructura", f"{c['es_eficiencia_estructura']:,.2f} €", "Supresión de duplicidad de captura de datos y horas manuales de oficina"],
        ["[HC] Optimización de Crecimiento", f"{c['hc_headcount_saving']:,.2f} €", "Capacidad de absorber mayor volumen sin incremento proporcional de personal"],
        ["TOTAL IMPACTO ACCIONABLE", f"{c['total_oportunidad_euros']:,.2f} €", "Margen neto anual consolidado al culminar la modernización"]
    ]
    t_opp = Table(opp_data, colWidths=[145, 110, 250])
    t_opp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.HexColor("#0F172A")),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#F1F5F9")),
    ]))
    story.append(t_opp)
    story.append(Spacer(1, 8))

    # Bloque 4: Cuenta de Explotación y Tesorería
    story.append(Paragraph("4. RADIOGRAFÍA FINANCIERA Y CICLO DE CONVERSIÓN DE EFECTIVO", h1))
    fin_data = [
        ["Métrica Financiera", "Valor Calculado", "Métrica de Tesorería y Balance", "Valor Calculado"],
        ["Facturación Anual N", f"{c['v_actual']:,.2f} €", "DSO (Plazo Medio Cobro)", f"{c['dso']:.1f} días"],
        ["Crecimiento vs N-1", f"{c['crecimiento_ventas']:+.1f} %", "DIO (Permanencia de Stock)", f"{c['dio']:.1f} días"],
        ["Margen Bruto", f"{c['margen_bruto']:,.2f} € ({c['margen_bruto_pct']:.1f}%)", "DPO (Plazo Pago Proveedor)", f"{c['dpo']:.1f} días"],
        ["EBITDA Normalizado", f"{c['ebitda']:,.2f} € ({c['ebitda_pct']:.1f}%)", "CCC (Ciclo Conversión Caja)", f"{c['ccc']:.1f} días"],
        ["EBIT (Resultado Operativo)", f"{c['ebit']:,.2f} €", "Caja Atrapada Excesiva", f"{c['potencial_liberacion_caja']:,.2f} €"]
    ]
    t_fin = Table(fin_data, colWidths=[135, 117, 135, 118])
    t_fin.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(t_fin)
    story.append(Spacer(1, 8))

    # Bloque 5: Análisis de Cuellos de Botella y Riesgo
    story.append(Paragraph("5. EVALUACIÓN DE VULNERABILIDAD, PROCESOS Y GOBERNANZA", h1))
    story.append(Paragraph(f"<b>Causa Raíz Operativa ({d.get('colapso_20pct')}):</b> {ia.get('analisis_cuello_botella')}", body))
    story.append(Paragraph(f"<b>Riesgo Estructural y Concentración:</b> {ia.get('analisis_riesgo_gobernanza')}", body))
    story.append(Spacer(1, 6))

    # Bloque 6: Hoja de Ruta Ejecutiva
    story.append(Paragraph("6. PLAN DIRECTIVO DE ACCIÓN Y MODERNIZACIÓN", h1))
    hr = ia.get("hoja_ruta", {})
    story.append(Paragraph(f"• <b>Fase 1 (Inmediato - 30 días):</b> {hr.get('inmediato_30d', '')}", body))
    story.append(Paragraph(f"• <b>Fase 2 (Consolidación - 90 días):</b> {hr.get('medio_plazo_90d', '')}", body))
    story.append(Paragraph(f"• <b>Fase 3 (Estratégico - 12 meses):</b> {hr.get('estrategico_12m', '')}", body))

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()

# ==============================================================================
# 5. FORMULARIO MODULAR MULTI-BLOQUE (STREAMLIT)
# ==============================================================================
st.title("KROMA Ops — Auditoría Empresarial y Diagnóstico Integral")
st.caption("Motor determinista universal de rendimiento operativo, rentabilidad, tesorería y gobernanza.")

# --- SELECTOR DE MÓDULO REACTIVO (FUERA DEL FORMULARIO) ---
tipo_negocio = st.selectbox(
    "Selecciona la tipología de empresa para activar su módulo sectorial específico:",
    [
        "Servicios Técnicos / Instalaciones",
        "Industria / Fabricación",
        "Comercio / Retail / Distribución",
        "Hostelería / Restauración",
        "Servicios Profesionales / Consultoría"
    ]
)

with st.form("form_auditoria_completa"):
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "1. Identidad y Estrategia",
        "2. P&L y Rentabilidad",
        "3. Tesorería y Balance",
        "4. Productividad y Personas",
        "5. Comercial y Clientes",
        "6. Procesos y Datos",
        "7. Módulo Sectorial"
    ])

    with tab1:
        st.subheader("Identificación de la Empresa y Visión Estratégica")
        c1, c2 = st.columns(2)
        with c1:
            nombre_empresa = st.text_input("Nombre de la Empresa", value="Técnicas y Montajes Industriales S.L.")
            sector = st.text_input("Sector de Actividad Detallado", value="Ingeniería y Servicios Técnicos")
            plantilla = st.number_input("Nº Empleados Totales", min_value=1, value=14, step=1)
        with c2:
            objetivo_estrategico = st.selectbox("Objetivo de la Dirección a 3 Años", [
                "Aumentar rentabilidad y margen (manteniendo tamaño)",
                "Escalar y crecer en volumen de ventas",
                "Reducir dependencia del propietario / profesionalizar",
                "Preparar la empresa para una venta o entrada de socios",
                "Sanear tesorería y reducir endeudamiento"
            ])
            problema_principal = st.text_input("Mayor Problema que Quita el Sueño a la Dirección", value="Falta de control de horas en proyectos y retrasos en cobros.")

    with tab2:
        st.subheader("Cuenta de Explotación (Mini P&L Anual)")
        c3, c4, c5 = st.columns(3)
        with c3:
            ventas_n = st.number_input("Facturación Año Actual (€)", min_value=1000.0, value=1250000.0, step=25000.0)
            ventas_n1 = st.number_input("Facturación Año Anterior (€)", min_value=1000.0, value=1100000.0, step=25000.0)
        with c4:
            compras = st.number_input("Aprovisionamientos / Materiales (€)", min_value=0.0, value=350000.0, step=10000.0)
            subcontratas = st.number_input("Subcontratación Directa (€)", min_value=0.0, value=90000.0, step=5000.0)
        with c5:
            personal = st.number_input("Masa Salarial Total + SS (€)", min_value=1000.0, value=480000.0, step=10000.0)
            estructura = st.number_input("Gastos Generales / Opex (€)", min_value=0.0, value=160000.0, step=5000.0)
            amortizaciones = st.number_input("Amortizaciones (€)", min_value=0.0, value=25000.0, step=2000.0)
            gastos_financieros = st.number_input("Gastos Financieros (€)", min_value=0.0, value=12000.0, step=1000.0)

    with tab3:
        st.subheader("Balance Operativo y Circulante (Tesorería)")
        c6, c7 = st.columns(2)
        with c6:
            saldo_clientes = st.number_input("Saldo Pendiente de Clientes (€)", min_value=0.0, value=260000.0, step=10000.0)
            saldo_proveedores = st.number_input("Saldo Deuda a Proveedores (€)", min_value=0.0, value=85000.0, step=5000.0)
            stock_medio = st.number_input("Valor de Stock / Inventario Medio (€)", min_value=0.0, value=75000.0, step=5000.0)
        with c7:
            caja_actual = st.number_input("Caja / Tesorería Disponible (€)", min_value=0.0, value=45000.0, step=5000.0)
            deuda_bancaria = st.number_input("Deuda Bancaria Total (€)", min_value=0.0, value=180000.0, step=10000.0)
            cuota_mensual_deuda = st.number_input("Cuota Mensual Financiación (€/mes)", min_value=0.0, value=3200.0, step=200.0)

    with tab4:
        st.subheader("Capacidad, Productividad y Personas")
        c8, c9 = st.columns(2)
        with c8:
            pct_horas_improductivas = st.slider("% Horas no facturables / improductivas (desplazamientos, gestiones)", 0, 60, 22)
            num_trabajos_anuales = st.number_input("Nº Total de Trabajos / Proyectos / Pedidos al año", min_value=1, value=650, step=25)
            pct_retrabajo = st.slider("% Trabajos con fallos / repeticiones / retrabajo", 0, 30, 6)
            coste_medio_error = st.number_input("Coste Medio de Subsanar un Error / Retrabajo (€)", min_value=0.0, value=350.0, step=25.0)
        with c9:
            dependencia_gerente = st.selectbox("Si el Gerente desaparece 30 días:", [
                "La empresa opera con normalidad",
                "Aparecen fricciones pero continúa",
                "Se frenan decisiones críticas y presupuestos",
                "La empresa se detiene en 48-72h"
            ])
            colapso_20pct = st.selectbox("Si las ventas suben un 20% mañana, ¿qué colapsa primero?", [
                "Capacidad técnica / Operarios de campo",
                "Administración y facturación",
                "Tesorería / Financiación del circulante",
                "Capacidad de almacenaje y logística",
                "Nada, tenemos holgura operativa"
            ])
            capacidad_adicional_pct = st.slider("% Volumen adicional absorbible sin contratar", 0, 50, 15)

    with tab5:
        st.subheader("Comercial, Cartera y Dependencia")
        c10, c11 = st.columns(2)
        with c10:
            leads_anuales = st.number_input("Nº Oportunidades / Presupuestos emitidos al año", min_value=1, value=220, step=10)
            ventas_cerradas = st.number_input("Nº Presupuestos Ganados / Clientes cerrados", min_value=1, value=85, step=5)
        with c11:
            concentracion_top5 = st.slider("% Ventas en los 5 Mayores Clientes", 5, 100, 48)
            churn_pct = st.slider("% Clientes perdidos al año (Tasa de Churn)", 0, 50, 8)

    with tab6:
        st.subheader("Digitalización, Procesos y Duplicidades")
        c12, c13 = st.columns(2)
        with c12:
            madurez_digital = st.selectbox("Pila de Software Principal", [
                "Baja / Hojas sueltas",
                "Parcial / Software no conectado",
                "ERP centralizado",
                "Automatizado / Conectado"
            ])
            duplicidad_datos = st.slider("¿Cuántas veces se teclea el mismo dato? (WhatsApp -> Excel -> ERP -> Factura)", 1, 5, 3)
        with c13:
            operaciones_diarias = st.number_input("Nº Documentos / Órdenes gestionadas al día", min_value=1, value=25, step=5)
            seguridad_backup = st.selectbox("Copias de Seguridad y Ciberseguridad", [
                "Backups automáticos y MFA activado",
                "Copias periódicas manuales",
                "Sin protocolo formalizado de respaldo"
            ])

    with tab7:
        st.subheader(f"Módulo Sectorial Específico: {tipo_negocio}")
        datos_sectoriales = {}
        if tipo_negocio == "Servicios Técnicos / Instalaciones":
            s1, s2 = st.columns(2)
            datos_sectoriales["horas_desplazamiento_pct"] = s1.slider("% Tiempo en desplazamientos / furgoneta", 0, 50, 25)
            datos_sectoriales["partes_en_papel_pct"] = s2.slider("% Albaranes / Partes aún en papel", 0, 100, 40)
        elif tipo_negocio == "Industria / Fabricación":
            s1, s2 = st.columns(2)
            datos_sectoriales["oee_estimado"] = s1.slider("OEE Estimado de Planta (%)", 30, 95, 68)
            datos_sectoriales["scrap_pct"] = s2.slider("% Merma / Desecho de Material", 0, 20, 4)
        elif tipo_negocio == "Comercio / Retail / Distribución":
            s1, s2 = st.columns(2)
            datos_sectoriales["rotacion_stock"] = s1.number_input("Rotaciones de Stock al Año", min_value=1.0, value=4.5, step=0.5)
            datos_sectoriales["ventas_m2"] = s2.number_input("Ventas por m² (€/año)", min_value=100.0, value=2800.0, step=100.0)
        elif tipo_negocio == "Hostelería / Restauración":
            s1, s2 = st.columns(2)
            datos_sectoriales["food_cost_pct"] = s1.slider("Food & Beverage Cost (%)", 15, 55, 31)
            datos_sectoriales["rotacion_mesas"] = s2.number_input("Rotación de Mesas en Servicio Punta", min_value=0.5, value=1.8, step=0.1)
        else: # Servicios Profesionales / Consultoría
            s1, s2 = st.columns(2)
            datos_sectoriales["utilizacion_teorica"] = s1.slider("Ratio de Ocupación Facturable (%)", 30, 95, 65)
            datos_sectoriales["desviacion_horas_proyectos"] = s2.slider("% Proyectos con horas no facturadas", 0, 60, 20)

    st.markdown("---")
    ejecutar_btn = st.form_submit_button("⚡ Ejecutar Auditoría Operativa y Generar Dossier")

# ==============================================================================
# 6. EJECUCIÓN, VISUALIZACIÓN DE ÍNDICES Y DESCARGA
# ==============================================================================
if ejecutar_btn:
    payload = {
        "nombre_empresa": nombre_empresa, "sector": sector, "tipo_negocio": tipo_negocio,
        "objetivo_estrategico": objetivo_estrategico, "problema_principal": problema_principal,
        "plantilla": plantilla, "ventas_n": ventas_n, "ventas_n1": ventas_n1,
        "compras": compras, "subcontratas": subcontratas, "personal": personal,
        "estructura": estructura, "amortizaciones": amortizaciones, "gastos_financieros": gastos_financieros,
        "saldo_clientes": saldo_clientes, "saldo_proveedores": saldo_proveedores, "stock_medio": stock_medio,
        "caja_actual": caja_actual, "deuda_bancaria": deuda_bancaria, "cuota_mensual_deuda": cuota_mensual_deuda,
        "pct_horas_improductivas": pct_horas_improductivas, "num_trabajos_anuales": num_trabajos_anuales,
        "pct_retrabajo": pct_retrabajo, "coste_medio_error": coste_medio_error,
        "dependencia_gerente": dependencia_gerente, "colapso_20pct": colapso_20pct,
        "capacidad_adicional_pct": capacidad_adicional_pct,
        "leads_anuales": leads_anuales, "ventas_cerradas": ventas_cerradas,
        "concentracion_top5": concentracion_top5, "churn_pct": churn_pct,
        "madurez_digital": madurez_digital, "duplicidad_datos": duplicidad_datos,
        "operaciones_diarias": operaciones_diarias, "seguridad_backup": seguridad_backup,
        "datos_sectoriales": datos_sectoriales
    }

    with st.spinner("Calculando conciliación estricta, ciclo de caja e interpretando con IA..."):
        calc = ejecutar_motor_diagnostico(payload)
        ia_resp = consultar_inteligencia_gemini(payload, calc)
        pdf_bytes = generar_pdf_dossier(payload, calc, ia_resp)

    st.success("Diagnóstico Cuantitativo Finalizado con Éxito.")

    # Tarjetas de Impacto
    c_m1, c_m2, c_m3, c_m4 = st.columns(4)
    c_m1.metric("EBITDA Normalizado", f"{calc['ebitda']:,.2f} €", f"{calc['ebitda_pct']:.1f}% s/Ventas")
    c_m2.metric("€ de Oportunidad Anual", f"{calc['total_oportunidad_euros']:,.2f} €", "Recuperable", delta_color="normal")
    c_m3.metric("Ciclo Efectivo (CCC)", f"{calc['ccc']:.0f} días", f"DSO: {calc['dso']:.0f}d | Stock: {calc['dio']:.0f}d", delta_color="inverse")
    c_m4.metric("Caja Ociosa / Atrapada", f"{calc['potencial_liberacion_caja']:,.2f} €", "Optimización DSO")

    st.markdown("---")

    # Pestañas de Resultados
    r_tab1, r_tab2, r_tab3, r_tab4 = st.tabs([
        "🎯 Matriz de 8 Índices",
        "💰 € de Oportunidad (DR / C / ES / HC)",
        "📊 Finanzas y Tesorería",
        "🧭 Dictamen y Plan de Dirección"
    ])

    with r_tab1:
        st.subheader("Matriz de Salud y Rendimiento Operativo (0 a 10)")
        df_indices = pd.DataFrame([
            {"Índice Operativo": k, "Puntuación": f"{v:.1f} / 10", "Estado": "Óptimo" if v >= 7.5 else ("Alerta" if v >= 5.0 else "Crítico")}
            for k, v in calc["indices"].items()
        ])
        st.dataframe(df_indices, use_container_width=True)

    with r_tab2:
        st.subheader("Desglose Analítico de los € de Oportunidad")
        df_opp = pd.DataFrame([
            {"Vector": "[DR] Retorno Directo", "Importe Anual": calc["dr_retorno_directo"], "Concepto": "Contención de retrabajo, costes de errores y mermas"},
            {"Vector": "[C] Capacidad Liberada", "Importe Anual": calc["c_capacidad_liberada"], "Concepto": "Margen recuperable convirtiendo horas improductivas en facturación"},
            {"Vector": "[ES] Eficiencia Estructural", "Importe Anual": calc["es_eficiencia_estructura"], "Concepto": "Ahorro de horas en duplicidad y reintroducción manual"},
            {"Vector": "[HC] Capacidad de Absorción", "Importe Anual": calc["hc_headcount_saving"], "Concepto": "Ahorro al absorber crecimiento sin requerir nuevas contrataciones"},
            {"Vector": "TOTAL MONETIZADO", "Importe Anual": calc["total_oportunidad_euros"], "Concepto": "Impacto consolidado anual"}
        ])
        st.dataframe(df_opp.style.format({"Importe Anual": "{:,.2f} €"}), use_container_width=True)

    with r_tab3:
        st.subheader("P&L y Ciclo de Conversión de Efectivo (CCC)")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.write("##### Cascada de Resultados")
            df_pl = pd.DataFrame([
                {"Partida": "Facturación Anual N", "Importe": calc["v_actual"], "% s/Ventas": 100.0},
                {"Partida": "(-) Compras Directas", "Importe": -payload["compras"], "% s/Ventas": (payload["compras"]/calc["v_actual"])*100},
                {"Partida": "(-) Subcontratación", "Importe": -payload["subcontratas"], "% s/Ventas": (payload["subcontratas"]/calc["v_actual"])*100},
                {"Partida": "(=) Margen Bruto", "Importe": calc["margen_bruto"], "% s/Ventas": calc["margen_bruto_pct"]},
                {"Partida": "(-) Masa Salarial", "Importe": -payload["personal"], "% s/Ventas": (payload["personal"]/calc["v_actual"])*100},
                {"Partida": "(-) Gastos Estructura", "Importe": -payload["estructura"], "% s/Ventas": (payload["estructura"]/calc["v_actual"])*100},
                {"Partida": "(=) EBITDA", "Importe": calc["ebitda"], "% s/Ventas": calc["ebitda_pct"]},
                {"Partida": "(=) EBIT", "Importe": calc["ebit"], "% s/Ventas": (calc["ebit"]/calc["v_actual"])*100}
            ])
            st.dataframe(df_pl.style.format({"Importe": "{:,.2f} €", "% s/Ventas": "{:.1f} %"}), use_container_width=True)
        with col_f2:
            st.write("##### Ciclo de Conversión de Efectivo (CCC)")
            st.info(f"**CCC Actual:** {calc['ccc']:.1f} días  \n*Cálculo:* {calc['dio']:.1f}d (Stock) + {calc['dso']:.1f}d (Cobro) - {calc['dpo']:.1f}d (Pago)")
            st.warning(f"**Caja Atrapada en Retraso de Cobros:** {calc['caja_atrapada_dso']:,.2f} € (Exceso sobre 45 días estándar).")

    with r_tab4:
        st.subheader("Dictamen Ejecutivo y Hoja de Ruta (IA)")
        st.write(f"**Dictamen de Dirección:**")
        st.markdown(f"> *{ia_resp.get('dictamen_ejecutivo')}*")
        st.write(f"**Causa Raíz Operativa:** {ia_resp.get('analisis_cuello_botella')}")
        st.write(f"**Riesgo Organizativo:** {ia_resp.get('analisis_riesgo_gobernanza')}")
        st.write("##### Hoja de Ruta Directiva")
        hr_ui = ia_resp.get("hoja_ruta", {})
        st.markdown(f"- **30 Días:** {hr_ui.get('inmediato_30d')}")
        st.markdown(f"- **90 Días:** {hr_ui.get('medio_plazo_90d')}")
        st.markdown(f"- **12 Meses:** {hr_ui.get('estrategico_12m')}")

    st.markdown("---")
    st.download_button(
        label="📄 Descargar Dossier Ejecutivo Completo (PDF)",
        data=pdf_bytes,
        file_name=f"Auditoria_KROMA_{payload['nombre_empresa'].replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
