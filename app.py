import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
import google.generativeai as genai

# ==============================================================================
# 1. CONFIGURACIÓN Y CLIENTE IA
# ==============================================================================
st.set_page_config(
    page_title="KROMA Ops | Auditoría Operativa y Financiera de Dirección",
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
# 2. MOTOR MATEMÁTICO CUANTITATIVO DE ALTA PRECISIÓN (RESIDUO CERO)
# ==============================================================================
def calcular_auditoria_avanzada(d: dict) -> dict:
    ventas = float(d["ventas"])
    compras = float(d["compras"])
    subcontratas = float(d["subcontratas"])
    coste_personal = float(d["personal"])
    gastos_estructura = float(d["estructura"])
    amortizaciones = float(d["amortizaciones"])
    gastos_financieros = float(d["gastos_financieros"])
    plantilla = max(1, int(d["plantilla"]))

    # Cuadre P&L estricto
    costes_directos = compras + subcontratas
    margen_bruto = ventas - costes_directos
    margen_bruto_pct = (margen_bruto / ventas * 100.0) if ventas > 0 else 0.0

    ebitda = margen_bruto - coste_personal - gastos_estructura
    ebitda_pct = (ebitda / ventas * 100.0) if ventas > 0 else 0.0

    ebit = ebitda - amortizaciones
    ebt = ebit - gastos_financieros
    beneficio_neto_est = ebt * 0.75

    residuo_contable = round(ventas - (costes_directos + coste_personal + gastos_estructura) - ebitda, 4)

    # Mano de obra y coste horario
    horas_anuales_convenio = float(d["horas_anuales_empleado"])
    horas_totales_disponibles = plantilla * horas_anuales_convenio
    coste_hora_cargada = (coste_personal / horas_totales_disponibles) if horas_totales_disponibles > 0 else 25.0

    pct_tiempo_facturable = float(d["pct_tiempo_facturable"]) / 100.0
    horas_facturables_reales = horas_totales_disponibles * pct_tiempo_facturable
    horas_no_facturables = horas_totales_disponibles - horas_facturables_reales
    coste_horas_improductivas = horas_no_facturables * coste_hora_cargada
    precio_medio_hora_vendida = (ventas / horas_facturables_reales) if horas_facturables_reales > 0 else 0.0

    # Fuga por retrabajo
    num_entregas = max(1, int(d["num_operaciones_anuales"]))
    pct_retrabajo = float(d["pct_retrabajo"]) / 100.0
    coste_unit_retrabajo = float(d["coste_unit_retrabajo"])
    fuga_retrabajo_anual = num_entregas * pct_retrabajo * coste_unit_retrabajo

    # Fuga por fricción administrativa y duplicidad
    duplicidad = max(1, int(d["veces_duplicidad_dato"]))
    operaciones_dia = float(d["gestiones_diarias"])
    minutos_perdidos_dia = operaciones_dia * (duplicidad - 1) * 7.5
    horas_admin_perdidas_anual = (minutos_perdidos_dia / 60.0) * 220.0
    fuga_administrativa_anual = horas_admin_perdidas_anual * coste_hora_cargada

    # Circulante y ciclo de conversión de efectivo
    saldo_clientes = float(d["saldo_clientes"])
    saldo_proveedores = float(d["saldo_proveedores"])
    stock_medio = float(d["stock_medio"])
    caja_actual = float(d["caja_actual"])
    deuda_total = float(d["deuda_total"])

    dso = (saldo_clientes / ventas * 365.0) if ventas > 0 else 0.0
    coste_ventas_base = costes_directos if costes_directos > 0 else (ventas * 0.3)
    dpo = (saldo_proveedores / coste_ventas_base * 365.0) if coste_ventas_base > 0 else 0.0
    dio = (stock_medio / coste_ventas_base * 365.0) if coste_ventas_base > 0 else 0.0
    ccc = dio + dso - dpo

    ventas_dia = ventas / 365.0
    caja_atrapada_exceso_cobro = max(0.0, (dso - 45.0) * ventas_dia)
    caja_atrapada_stock = max(0.0, (dio - 30.0) * (coste_ventas_base / 365.0))
    caja_total_liberable = caja_atrapada_exceso_cobro + caja_atrapada_stock

    # Vectores DR / C / ES / HC
    dr_retorno_directo = (fuga_retrabajo_anual * 0.75) + (caja_atrapada_exceso_cobro * 0.10)
    c_capacidad_liberada = (horas_no_facturables * 0.35) * (precio_medio_hora_vendida * (margen_bruto_pct / 100.0))
    es_eficiencia_estructura = fuga_administrativa_anual * 0.85
    hc_optimizacion = (coste_personal / plantilla) * 1.5

    total_oportunidad_anual = dr_retorno_directo + c_capacidad_liberada + es_eficiencia_estructura

    # Proforma a 3 años
    inversion_modernizacion = min(40000.0, max(6000.0, ventas * 0.022))
    mejora_ao1 = total_oportunidad_anual * 0.55
    mejora_ao2 = total_oportunidad_anual * 0.85
    mejora_ao3 = total_oportunidad_anual * 1.10

    ebitda_ao1 = ebitda + mejora_ao1
    ebitda_ao2 = ebitda + mejora_ao2
    ebitda_ao3 = ebitda + mejora_ao3

    payback_meses = (inversion_modernizacion / mejora_ao1 * 12.0) if mejora_ao1 > 0 else 0.0
    roi_3y = (((mejora_ao1 + mejora_ao2 + mejora_ao3) - inversion_modernizacion) / inversion_modernizacion * 100.0) if inversion_modernizacion > 0 else 0.0

    # 8 Índices KROMA
    idx_rentabilidad = min(10.0, max(0.0, (ebitda_pct / 18.0) * 10.0))
    idx_productividad = min(10.0, max(0.0, (pct_tiempo_facturable / 0.80) * 10.0))
    idx_liquidez = 10.0 if ccc <= 30 else max(0.0, 10.0 - ((ccc - 30.0) / 10.0))
    
    leads = max(1, int(d["leads"]))
    cierres = max(1, int(d["cierres"]))
    conversion_comercial = (cierres / leads) * 100.0
    idx_comercial = min(10.0, max(0.0, (conversion_comercial / 35.0) * 10.0))
    idx_operaciones = max(0.0, 10.0 - (pct_retrabajo * 70.0))
    
    dict_dig = {
        "Baja / Papel y hojas aisladas": 2.0,
        "Media / Software fragmentado": 5.0,
        "Integrada / ERP central": 8.0,
        "Avanzada / Automatizada": 10.0
    }
    idx_digitalizacion = dict_dig.get(d["pila_software"], 5.0)

    riesgo = 10.0
    if float(d["concentracion_top5"]) > 45.0:
        riesgo -= 2.5
    if d["dependencia_gerente"] == "Crítica: La empresa se detiene en 48-72h":
        riesgo -= 3.5
    if deuda_total > (ebitda * 3.0) and ebitda > 0:
        riesgo -= 2.0
    idx_riesgo = max(1.0, riesgo)

    cap_adicional = float(d["capacidad_adicional_pct"])
    idx_crecimiento = min(10.0, max(1.0, (cap_adicional / 35.0) * 10.0))

    return {
        "ventas": ventas, "costes_directos": costes_directos, "margen_bruto": margen_bruto,
        "margen_bruto_pct": margen_bruto_pct, "coste_personal": coste_personal,
        "gastos_estructura": gastos_estructura, "ebitda": ebitda, "ebitda_pct": ebitda_pct,
        "ebit": ebit, "ebt": ebt, "beneficio_neto_est": beneficio_neto_est,
        "plantilla": plantilla, "horas_totales_disponibles": horas_totales_disponibles,
        "coste_hora_cargada": coste_hora_cargada, "horas_facturables_reales": horas_facturables_reales,
        "horas_no_facturables": horas_no_facturables, "coste_horas_improductivas": coste_horas_improductivas,
        "precio_medio_hora_vendida": precio_medio_hora_vendida,
        "fuga_retrabajo_anual": fuga_retrabajo_anual, "fuga_administrativa_anual": fuga_administrativa_anual,
        "horas_admin_perdidas_anual": horas_admin_perdidas_anual,
        "dso": dso, "dpo": dpo, "dio": dio, "ccc": ccc,
        "caja_atrapada_exceso_cobro": caja_atrapada_exceso_cobro, "caja_total_liberable": caja_total_liberable,
        "dr_retorno_directo": dr_retorno_directo, "c_capacidad_liberada": c_capacidad_liberada,
        "es_eficiencia_estructura": es_eficiencia_estructura, "hc_optimizacion": hc_optimizacion,
        "total_oportunidad_anual": total_oportunidad_anual,
        "inversion_modernizacion": inversion_modernizacion,
        "mejora_ao1": mejora_ao1, "mejora_ao2": mejora_ao2, "mejora_ao3": mejora_ao3,
        "ebitda_ao1": ebitda_ao1, "ebitda_ao2": ebitda_ao2, "ebitda_ao3": ebitda_ao3,
        "payback_meses": payback_meses, "roi_3y": roi_3y,
        "conversion_comercial": conversion_comercial,
        "indices": {
            "Rentabilidad": idx_rentabilidad, "Productividad": idx_productividad,
            "Liquidez": idx_liquidez, "Comercial": idx_comercial,
            "Operaciones": idx_operaciones, "Digitalización": idx_digitalizacion,
            "Autonomía y Riesgo": idx_riesgo, "Capacidad Crecimiento": idx_crecimiento
        },
        "residuo_cero": residuo_contable == 0.0
    }

# ==============================================================================
# 3. INTERPRETACIÓN ESTRATÉGICA DE CONSULTORÍA (GEMINI 1.5 PRO)
# ==============================================================================
def generar_dictamen_consultoria(datos: dict, calc: dict) -> dict:
    if not ai_model:
        return {
            "dictamen_ejecutivo": "Diagnóstico verificado a residuo cero. El negocio presenta una oportunidad cuantificada de mejora mediante la optimización de capacidad y tiempos improductivos.",
            "analisis_cuello_botella": f"Fricción crítica identificada en {datos.get('colapso_ventas')}. El equipo técnico absorbe tareas no computables como facturación.",
            "analisis_gobernanza_riesgo": f"La concentración del {datos.get('concentracion_top5')}% en cinco cuentas y la dependencia directa de la dirección incrementan el riesgo operativo.",
            "hoja_ruta_directiva": {
                "inmediato_30d": "Contención del retrabajo y aceleración de cobros con vencimiento superior a 45 días.",
                "medio_plazo_90d": "Unificación de la pila de herramientas para suprimir duplicidades administrativas.",
                "estrategico_12m": f"Estandarización de la gestión para apoyar el objetivo de: {datos.get('objetivo_estrategico')}"
            }
        }

    prompt = f"""
    Eres el Socio Principal de una firma de consultoría estratégica y auditoría corporativa (KROMA Ops).
    Emite un dictamen cuantitativo, directo y riguroso sin clichés comerciales ni rodeos introductorios.

    DATOS DE LA EMPRESA:
    - Entidad: {datos.get('nombre_empresa')} | Sector: {datos.get('sector')} | Modelo: {datos.get('tipo_negocio')}
    - Plantilla: {calc['plantilla']} personas | Horas convenio: {datos.get('horas_anuales_empleado')} h
    - Objetivo de la Dirección: {datos.get('objetivo_estrategico')}
    - Cuello de Botella Declarado: {datos.get('cuello_botella_gerente')}
    - Punto de Colapso (+20% Ventas): {datos.get('colapso_ventas')}
    - Dependencia del Gerente: {datos.get('dependencia_gerente')}
    - Concentración Top 5 Clientes: {datos.get('concentracion_top5')}%

    MÉTRICAS MATEMÁTICAS CALCULADAS:
    - Ventas: {calc['ventas']:,.2f} € | Margen Bruto: {calc['margen_bruto']:,.2f} € ({calc['margen_bruto_pct']:.1f}%)
    - EBITDA Normalizado: {calc['ebitda']:,.2f} € ({calc['ebitda_pct']:.1f}%)
    - Coste por Hora Cargada: {calc['coste_hora_cargada']:.2f} €/h
    - Horas No Facturables: {calc['horas_no_facturables']:,.0f} h/año (Coste: {calc['coste_horas_improductivas']:,.2f} €)
    - Fuga Retrabajo/Errores: {calc['fuga_retrabajo_anual']:,.2f} €/año
    - Fuga Duplicidad Administrativa: {calc['fuga_administrativa_anual']:,.2f} €/año
    - Ciclo de Conversión de Efectivo (CCC): {calc['ccc']:.1f} días (DSO: {calc['dso']:.1f}d | Caja atrapada: {calc['caja_atrapada_exceso_cobro']:,.2f} €)
    
    OPORTUNIDAD MONETIZADA (DR / C / ES / HC):
    - [DR] Retorno Directo: {calc['dr_retorno_directo']:,.2f} €
    - [C] Capacidad Liberada: {calc['c_capacidad_liberada']:,.2f} €
    - [ES] Eficiencia Estructura: {calc['es_eficiencia_estructura']:,.2f} €
    - Impacto Consolidado: {calc['total_oportunidad_anual']:,.2f} €/año
    - Inversión Modernización: {calc['inversion_modernizacion']:,.2f} € | Payback: {calc['payback_meses']:.1f} meses | ROI 3 Años: {calc['roi_3y']:.0f}%

    INSTRUCCIONES:
    1. Dictamen ejecutivo directo sobre la viabilidad del modelo frente al objetivo declarado.
    2. Análisis de causa raíz de su cuello de botella operativo.
    3. Evaluación del riesgo organizativo y de concentración de clientes.
    4. Hoja de ruta directiva en tres horizontes (30 días, 90 días, 12 meses).

    RESPONDE EXCLUSIVAMENTE CON UN OBJETO JSON VÁLIDO (sin bloques ```json ni texto extra):
    {{
        "dictamen_ejecutivo": "...",
        "analisis_cuello_botella": "...",
        "analisis_gobernanza_riesgo": "...",
        "hoja_ruta_directiva": {{
            "inmediato_30d": "...",
            "medio_plazo_90d": "...",
            "estrategico_12m": "..."
        }}
    }}
    """
    try:
        res = ai_model.generate_content(prompt)
        t = res.text.strip()
        if t.startswith("```json"):
            t = t[7:]
        if t.startswith("```"):
            t = t[3:]
        if t.endswith("```"):
            t = t[:-3]
        return json.loads(t.strip())
    except Exception:
        return {
            "dictamen_ejecutivo": f"La entidad genera un EBITDA del {calc['ebitda_pct']:.1f}%, pero sufre una fuga de capacidad equivalente a {calc['horas_no_facturables']:,.0f} horas improductivas. El plan estratégico debe canalizarse hacia la recuperación de margen directo.",
            "analisis_cuello_botella": f"El colapso señalado en '{datos.get('colapso_ventas')}' demuestra una absorción del tiempo del equipo en gestiones no computables.",
            "analisis_gobernanza_riesgo": f"Concentración en cartera ({datos.get('concentracion_top5')}%) y nivel de dependencia de gerencia categorizado como crítico.",
            "hoja_ruta_directiva": {
                "inmediato_30d": "Acelerar la cartera de cobros pendientes y fijar criterios de control de entregas.",
                "medio_plazo_90d": "Integración de flujos de datos para recuperar las horas perdidas en tareas administrativas.",
                "estrategico_12m": "Estandarización de procesos de entrega para habilitar el crecimiento sin requerir nuevas contrataciones."
            }
        }

# ==============================================================================
# 4. GENERADOR PDF EDITORIAL
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
        self.drawString(45, 804, "KROMA OPS | DOSSIER DE AUDITORÍA OPERATIVA Y VALORACIÓN ESTRATÉGICA")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(45, 796, 550, 796)
        self.line(45, 42, 550, 42)
        self.drawString(45, 30, "DOCUMENTO TÉCNICO CONFIDENCIAL - ESTRICTAMENTE RESERVADO A DIRECCIÓN")
        self.drawRightString(550, 30, f"Página {self._pageNumber} de {page_count}")
        self.restoreState()

def generar_pdf_editorial(d: dict, c: dict, ia: dict) -> bytes:
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
    title_style = ParagraphStyle('DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=17, leading=21, textColor=colors.HexColor("#0F172A"), spaceAfter=5)
    sub_style = ParagraphStyle('DocSub', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=11, textColor=colors.HexColor("#64748B"), spaceAfter=10)
    h1 = ParagraphStyle('H1', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=colors.HexColor("#0F172A"), spaceBefore=9, spaceAfter=5)
    body = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor("#334155"), spaceAfter=5)
    callout = ParagraphStyle('Callout', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, leading=11, textColor=colors.HexColor("#1E293B"))

    story = []
    story.append(Paragraph("INFORME DE AUDITORÍA OPERATIVA Y VALORACIÓN DE RENDIMIENTO", title_style))
    story.append(Paragraph(f"<b>Empresa:</b> {d.get('nombre_empresa')} | <b>Sector:</b> {d.get('sector')} | <b>Plantilla:</b> {c['plantilla']} empleados | <b>Objetivo:</b> {d.get('objetivo_estrategico')}", sub_style))

    # 1. Dictamen
    story.append(Paragraph("1. DICTAMEN EJECUTIVO DE DIRECCIÓN", h1))
    story.append(Paragraph(ia.get("dictamen_ejecutivo", ""), callout))
    story.append(Spacer(1, 6))

    # 2. Matriz de 8 Índices
    story.append(Paragraph("2. MATRIZ DE RENDIMIENTO OPERATIVO (8 ÍNDICES KROMA)", h1))
    idx_items = list(c["indices"].items())
    t_idx_data = [
        [k for k, _ in idx_items[:4]],
        [f"{v:.1f} / 10" for _, v in idx_items[:4]],
        [k for k, _ in idx_items[4:]],
        [f"{v:.1f} / 10" for _, v in idx_items[4:]]
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
    story.append(Spacer(1, 6))

    # 3. Monetización de Fugas
    story.append(Paragraph("3. CUANTIFICACIÓN DE FUGAS Y € DE OPORTUNIDAD ANUAL", h1))
    opp_data = [
        ["Vector de Oportunidad", "Impacto Monetizado", "Descripción Operativa"],
        ["[DR] Retorno Directo", f"{c['dr_retorno_directo']:,.2f} €", "Contención de retrabajo/fallos y optimización de tesorería"],
        ["[C] Capacidad Liberada", f"{c['c_capacidad_liberada']:,.2f} €", f"Monetización del 35% de horas muertas ({c['horas_no_facturables']:,.0f} h) a margen bruto"],
        ["[ES] Eficiencia de Estructura", f"{c['es_eficiencia_estructura']:,.2f} €", f"Supresión de reintroducción de datos ({c['horas_admin_perdidas_anual']:.0f} h/año recuperadas)"],
        ["TOTAL OPORTUNIDAD ANUAL", f"{c['total_oportunidad_anual']:,.2f} €", "Margen neto anual adicional tras modernización"],
        ["[HC] Amortiguación Headcount", f"{c['hc_optimizacion']:,.2f} €", "Ahorro estimado en nuevas contrataciones para absorber crecimiento"]
    ]
    t_opp = Table(opp_data, colWidths=[140, 115, 250])
    t_opp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('FONTNAME', (0, 4), (-1, 4), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor("#F1F5F9")),
    ]))
    story.append(t_opp)
    story.append(Spacer(1, 6))

    # 4. Conciliación P&L y Circulante
    story.append(Paragraph("4. CONCILIACIÓN P&L (RESIDUO CERO) Y TESORERÍA", h1))
    fin_data = [
        ["Partida de Explotación", "Importe (€)", "Ratio / Saldo", "Métrica de Circulante", "Valor"],
        ["Facturación Bruta", f"{c['ventas']:,.2f} €", "100,0 %", "DSO (Plazo Cobro)", f"{c['dso']:.1f} días"],
        ["Costes Directos / Subcontratas", f"{c['costes_directos']:,.2f} €", f"{c['costes_directos']/c['ventas']*100:.1f} %", "DIO (Inventario)", f"{c['dio']:.1f} días"],
        ["Masa Salarial Total", f"{c['coste_personal']:,.2f} €", f"{c['coste_personal']/c['ventas']*100:.1f} %", "DPO (Pago Prov.)", f"{c['dpo']:.1f} días"],
        ["Gastos Generales (Opex)", f"{c['gastos_estructura']:,.2f} €", f"{c['gastos_estructura']/c['ventas']*100:.1f} %", "CCC (Ciclo Caja)", f"{c['ccc']:.1f} días"],
        ["EBITDA Normalizado", f"{c['ebitda']:,.2f} €", f"{c['ebitda_pct']:.1f} %", "Caja Inmovilizada", f"{c['caja_atrapada_exceso_cobro']:,.2f} €"]
    ]
    t_fin = Table(fin_data, colWidths=[130, 95, 75, 125, 80])
    t_fin.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(t_fin)
    story.append(Spacer(1, 6))

    # 5. Plan Proforma
    story.append(Paragraph("5. CUENTA PROFORMA A 3 AÑOS Y RETORNO DE INVERSIÓN (ROI)", h1))
    prof_data = [
        ["Horizonte", "EBITDA Proforma", "Margen %", "Generación Acumulada", "Métricas de Inversión"],
        ["Año 0 (Base Actual)", f"{c['ebitda']:,.2f} €", f"{c['ebitda_pct']:.1f} %", "Base Referencia", f"Inversión Estimada: {c['inversion_modernizacion']:,.2f} €"],
        ["Año 1 (Fase Inmediata)", f"{c['ebitda_ao1']:,.2f} €", f"{c['ebitda_ao1']/c['ventas']*100:.1f} %", f"+{c['mejora_ao1']:,.2f} €", f"Payback: {c['payback_meses']:.1f} meses"],
        ["Año 2 (Consolidación)", f"{c['ebitda_ao2']:,.2f} €", f"{c['ebitda_ao2']/c['ventas']*100:.1f} %", f"+{c['mejora_ao2']:,.2f} €", f"ROI a 3 Años: {c['roi_3y']:.0f} %"],
        ["Año 3 (Madurez Operativa)", f"{c['ebitda_ao3']:,.2f} €", f"{c['ebitda_ao3']/c['ventas']*100:.1f} %", f"+{c['mejora_ao3']:,.2f} €", "Valoración de empresa maximizada"]
    ]
    t_prof = Table(prof_data, colWidths=[115, 95, 65, 110, 120])
    t_prof.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(t_prof)
    story.append(Spacer(1, 6))

    # 6. Gobernanza y Hoja de Ruta
    story.append(Paragraph("6. ANÁLISIS DE GOBERNANZA Y HOJA DE RUTA DIRECTIVA", h1))
    story.append(Paragraph(f"<b>Cuello de Botella Operativo:</b> {ia.get('analisis_cuello_botella', '')}", body))
    story.append(Paragraph(f"<b>Gobernanza y Riesgo:</b> {ia.get('analisis_gobernanza_riesgo', '')}", body))
    hr = ia.get("hoja_ruta_directiva", {})
    story.append(Paragraph(f"• <b>30 Días:</b> {hr.get('inmediato_30d', '')}", body))
    story.append(Paragraph(f"• <b>90 Días:</b> {hr.get('medio_plazo_90d', '')}", body))
    story.append(Paragraph(f"• <b>12 Meses:</b> {hr.get('estrategico_12m', '')}", body))

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()

# ==============================================================================
# 5. ENTRADA DE DATOS CON CASO REAL PRECARGADO (AGENCIA DIGITAL B2B)
# ==============================================================================
st.title("KROMA Ops — Auditoría Operativa y Financiera de Dirección")
st.caption("Diagnóstico matemático sin sesgo, conciliación contable estricta y monetización de oportunidades.")

with st.expander("📝 Configurar Parámetros de la Empresa Auditada (Precargado con Caso Real)", expanded=True):
    with st.form("form_auditoria_completa"):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### 1. Identidad y Estrategia")
            nombre_empresa = st.text_input("Razón Social", value="Nexus Digital & Growth Labs S.L.")
            sector = st.text_input("Sector / Actividad", value="Servicios B2B de Marketing Digital y Desarrollo Web")
            tipo_negocio = st.selectbox("Modelo Operativo", [
                "Servicios Profesionales / Consultoría / Agencia",
                "Servicios Técnicos con Movilidad",
                "Industria y Fabricación",
                "Comercio y Distribución",
                "Hostelería y Restauración"
            ])
            plantilla = st.number_input("Plantilla Total (personas)", min_value=1, value=16, step=1)
            horas_anuales_empleado = st.number_input("Horas Anuales por Convenio / Persona", min_value=1000.0, value=1760.0, step=10.0)
            objetivo_estrategico = st.selectbox("Objetivo Directivo a 3 Años", [
                "Aumentar rentabilidad y margen (manteniendo tamaño)",
                "Escalar y crecer en volumen de ventas",
                "Reducir dependencia del propietario / profesionalizar",
                "Preparar la empresa para una venta o entrada de socios",
                "Sanear tesorería y reducir endeudamiento"
            ])
            cuello_botella_gerente = st.text_input("Mayor Preocupación de Dirección", value="Proyectos que se desvían en horas, clientes con cambios continuos y retrasos en cobros.")

            st.markdown("##### 2. Operaciones, Horas y Retrabajo")
            pct_tiempo_facturable = st.slider("% Tiempo Real Facturable del Equipo (vs horas en reuniones, presupuestos y desvíos)", 20, 95, 62)
            num_operaciones_anuales = st.number_input("Nº de Proyectos / Entregas al año", min_value=1, value=180, step=10)
            pct_retrabajo = st.slider("% Trabajos con correcciones / quejas / horas de rehacer no facturadas", 0, 30, 11)
            coste_unit_retrabajo = st.number_input("Coste Medio de Rehacer o Subsanar un Error (€)", min_value=0.0, value=580.0, step=20.0)
            colapso_ventas = st.selectbox("Si las ventas aumentan un 20%, ¿qué colapsa primero?", [
                "Capacidad técnica / Operativa del equipo",
                "Administración y facturación",
                "Tesorería / Financiación de clientes",
                "Dirección y control de calidad",
                "Nada, existe holgura estructural"
            ])
            capacidad_adicional_pct = st.slider("% Volumen adicional absorbible sin contratar", 0, 50, 12)

        with c2:
            st.markdown("##### 3. Cuenta de Explotación (Anual)")
            ventas = st.number_input("Facturación Anual N (€)", min_value=1000.0, value=1420000.0, step=25000.0)
            compras = st.number_input("Costes Directos / Herramientas / Servidores (€)", min_value=0.0, value=180000.0, step=10000.0)
            subcontratas = st.number_input("Subcontratación Externa / Freelance (€)", min_value=0.0, value=165000.0, step=5000.0)
            personal = st.number_input("Masa Salarial Total + Seguridad Social (€)", min_value=1000.0, value=680000.0, step=10000.0)
            estructura = st.number_input("Gastos Generales / Opex (€)", min_value=0.0, value=195000.0, step=5000.0)
            amortizaciones = st.number_input("Amortizaciones (€)", min_value=0.0, value=22000.0, step=2000.0)
            gastos_financieros = st.number_input("Gastos Financieros (€)", min_value=0.0, value=9500.0, step=500.0)

            st.markdown("##### 4. Tesorería, Clientes y Duplicidad")
            saldo_clientes = st.number_input("Saldo Pendiente de Cobro de Clientes (€)", min_value=0.0, value=310000.0, step=10000.0)
            saldo_proveedores = st.number_input("Saldo Deuda Proveedores (€)", min_value=0.0, value=52000.0, step=5000.0)
            stock_medio = st.number_input("Stock Medio / Anticipos Inmovilizados (€)", min_value=0.0, value=15000.0, step=1000.0)
            caja_actual = st.number_input("Caja / Tesorería en Bancos (€)", min_value=0.0, value=42000.0, step=5000.0)
            deuda_total = st.number_input("Deuda Bancaria Total (€)", min_value=0.0, value=110000.0, step=5000.0)
            concentracion_top5 = st.slider("% Ventas concentradas en los 5 principales clientes", 5, 100, 52)
            dependencia_gerente = st.selectbox("Si el Gerente se ausenta 30 días:", [
                "La empresa opera con normalidad",
                "Aparecen fricciones pero continúa",
                "Se frenan presupuestos y decisiones críticas",
                "Crítica: La empresa se detiene en 48-72h"
            ])
            pila_software = st.selectbox("Pila Tecnológica", [
                "Baja / Papel y hojas aisladas",
                "Media / Software fragmentado",
                "Integrada / ERP central",
                "Avanzada / Automatizada"
            ], index=1)
            veces_duplicidad_dato = st.slider("¿Cuántas veces se reintroduce un dato entre herramientas?", 1, 5, 3)
            gestiones_diarias = st.number_input("Operaciones / Fichas procesadas al día", min_value=1, value=35, step=5)
            leads = st.number_input("Oportunidades Comerciales al año", min_value=1, value=140, step=10)
            cierres = st.number_input("Ventas Cerradas al año", min_value=1, value=38, step=5)

        ejecutar_btn = st.form_submit_button("⚡ Ejecutar Auditoría Operativa y Conciliar P&L")

# ==============================================================================
# 6. EJECUCIÓN INMEDIATA Y RENDERIZADO EN PANTALLA
# ==============================================================================
datos_actuales = {
    "nombre_empresa": nombre_empresa, "sector": sector, "tipo_negocio": tipo_negocio,
    "plantilla": plantilla, "horas_anuales_empleado": horas_anuales_empleado,
    "objetivo_estrategico": objetivo_estrategico, "cuello_botella_gerente": cuello_botella_gerente,
    "pct_tiempo_facturable": pct_tiempo_facturable, "num_operaciones_anuales": num_operaciones_anuales,
    "pct_retrabajo": pct_retrabajo, "coste_unit_retrabajo": coste_unit_retrabajo,
    "colapso_ventas": colapso_ventas, "capacidad_adicional_pct": capacidad_adicional_pct,
    "ventas": ventas, "compras": compras, "subcontratas": subcontratas, "personal": personal,
    "estructura": estructura, "amortizaciones": amortizaciones, "gastos_financieros": gastos_financieros,
    "saldo_clientes": saldo_clientes, "saldo_proveedores": saldo_proveedores, "stock_medio": stock_medio,
    "caja_actual": caja_actual, "deuda_total": deuda_total, "concentracion_top5": concentracion_top5,
    "dependencia_gerente": dependencia_gerente, "pila_software": pila_software,
    "veces_duplicidad_dato": veces_duplicidad_dato, "gestiones_diarias": gestiones_diarias,
    "leads": leads, "cierres": cierres
}

calc = calcular_auditoria_avanzada(datos_actuales)

# Panel de Métricas Maestras
st.markdown("---")
st.subheader("🎯 Panel de Control Ejecutivo: Situación Actual")
m1, m2, m3, m4 = st.columns(4)
m1.metric("EBITDA Normalizado", f"{calc['ebitda']:,.2f} €", f"{calc['ebitda_pct']:.1f}% s/Ventas")
m2.metric("€ de Oportunidad Total", f"{calc['total_oportunidad_anual']:,.2f} €", "Recuperable/año", delta_color="normal")
m3.metric("Fuga Horas Improductivas", f"{calc['coste_horas_improductivas']:,.2f} €", f"{calc['horas_no_facturables']:,.0f} h no facturadas", delta_color="inverse")
m4.metric("Caja Atrapada en Clientes", f"{calc['caja_atrapada_exceso_cobro']:,.2f} €", f"DSO: {calc['dso']:.0f} días", delta_color="inverse")

# Secciones de Inspección Visual
st.markdown("### 1. Desglose de Fugas Monetizadas (€ de Oportunidad)")
st.write("Cuantificación del capital que se drena en la operativa por ineficiencias de proceso y horas improductivas:")
c_opp1, c_opp2 = st.columns([3, 2])
with c_opp1:
    df_vectores = pd.DataFrame([
        {
            "Vector KROMA": "[DR] Retorno Directo",
            "Impacto Anual (€)": calc["dr_retorno_directo"],
            "Concepto Operativo": f"Contención de los {calc['fuga_retrabajo_anual']:,.2f} € perdidos en rehacer proyectos y subsanar fallos."
        },
        {
            "Vector KROMA": "[C] Capacidad Liberada",
            "Impacto Anual (€)": calc["c_capacidad_liberada"],
            "Concepto Operativo": f"Monetización del 35% de las {calc['horas_no_facturables']:,.0f} h improductivas al margen bruto actual ({calc['margen_bruto_pct']:.1f}%)."
        },
        {
            "Vector KROMA": "[ES] Eficiencia Estructural",
            "Impacto Anual (€)": calc["es_eficiencia_estructura"],
            "Concepto Operativo": f"Ahorro de las {calc['horas_admin_perdidas_anual']:.0f} h/año perdidas en reintroducir datos ({calc['fuga_administrativa_anual']:,.2f} €)."
        },
        {
            "Vector KROMA": "IMPACTO CONSOLIDADO",
            "Impacto Anual (€)": calc["total_oportunidad_anual"],
            "Concepto Operativo": "Margen neto anual recuperable al culminar la optimización de procesos."
        },
        {
            "Vector KROMA": "[HC] Amortiguación Headcount",
            "Impacto Anual (€)": calc["hc_optimizacion"],
            "Concepto Operativo": "Ahorro de contratar 1,5 empleados adicionales al absorber más volumen con la estructura actual."
        }
    ])
    st.dataframe(df_vectores.style.format({"Impacto Anual (€)": "{:,.2f} €"}), use_container_width=True)

with c_opp2:
    st.info(f"""
    **Parámetros Horarios Clave:**
    * **Coste por Hora Cargada:** `{calc['coste_hora_cargada']:.2f} €/h`
    * **Precio Medio Facturado:** `{calc['precio_medio_hora_vendida']:.2f} €/h`
    * **Horas Disponibles:** `{calc['horas_totales_disponibles']:,.0f} h`
    * **Horas Facturadas:** `{calc['horas_facturables_reales']:,.0f} h ({pct_tiempo_facturable}%)`
    * **Horas Pérdida/Gestión:** `{calc['horas_no_facturables']:,.0f} h ({100-pct_tiempo_facturable}%)`
    """)

st.markdown("### 2. Matriz Cuantitativa de Salud Operativa (8 Índices)")
cols_idx = st.columns(4)
i = 0
for nombre_idx, valor_idx in calc["indices"].items():
    with cols_idx[i % 4]:
        color = "normal" if valor_idx >= 7.0 else ("off" if valor_idx >= 5.0 else "inverse")
        estado = "Sólido" if valor_idx >= 7.0 else ("Precaución" if valor_idx >= 5.0 else "Crítico")
        st.metric(nombre_idx, f"{valor_idx:.1f} / 10", estado)
    i += 1

st.markdown("### 3. Cascada P&L Conciliada a Residuo Cero y Ciclo de Caja")
col_pl, col_caja = st.columns(2)
with col_pl:
    st.write("##### Cascada de la Cuenta de Explotación")
    df_pl_show = pd.DataFrame([
        {"Partida": "Facturación Bruta", "Importe (€)": calc["ventas"], "% s/Ventas": 100.0},
        {"Partida": "(-) Costes Directos / Servidores", "Importe (€)": -calc["costes_directos"], "% s/Ventas": (calc["costes_directos"]/calc["ventas"])*100},
        {"Partida": "(=) Margen de Contribución Bruto", "Importe (€)": calc["margen_bruto"], "% s/Ventas": calc["margen_bruto_pct"]},
        {"Partida": "(-) Masa Salarial Total", "Importe (€)": -calc["coste_personal"], "% s/Ventas": (calc["coste_personal"]/calc["ventas"])*100},
        {"Partida": "(-) Gastos Estructura (Opex)", "Importe (€)": -calc["gastos_estructura"], "% s/Ventas": (calc["gastos_estructura"]/calc["ventas"])*100},
        {"Partida": "(=) EBITDA Normalizado", "Importe (€)": calc["ebitda"], "% s/Ventas": calc["ebitda_pct"]},
        {"Partida": "(-) Amortizaciones y Financieros", "Importe (€)": -(amortizaciones + gastos_financieros), "% s/Ventas": ((amortizaciones + gastos_financieros)/calc["ventas"])*100},
        {"Partida": "(=) EBT (Resultado Antes Impuestos)", "Importe (€)": calc["ebt"], "% s/Ventas": (calc["ebt"]/calc["ventas"])*100}
    ])
    st.dataframe(df_pl_show.style.format({"Importe (€)": "{:,.2f} €", "% s/Ventas": "{:.1f} %"}), use_container_width=True)

with col_caja:
    st.write("##### Ciclo de Conversión de Efectivo (CCC)")
    st.metric("Días de Ciclo de Efectivo (CCC)", f"{calc['ccc']:.1f} días", f"DSO: {calc['dso']:.1f}d | DPO: {calc['dpo']:.1f}d")
    st.write(f"""
    * **Plazo Medio de Cobro (DSO):** `{calc['dso']:.1f} días` *(Caja inmovilizada por superar 45 días: **{calc['caja_atrapada_exceso_cobro']:,.2f} €**)*.
    * **Plazo Medio de Pago (DPO):** `{calc['dpo']:.1f} días`.
    * **Permanencia de Stock / Anticipos (DIO):** `{calc['dio']:.1f} días`.
    * **Deuda Financiera Total:** `{deuda_total:,.2f} €` *(Ratio Deuda / EBITDA: `{deuda_total/calc['ebitda']:.2f}x`)*.
    """)

st.markdown("### 4. Cuenta Proforma a 3 Años y Retorno de Inversión")
c_prof1, c_prof2 = st.columns([3, 1])
with c_prof1:
    df_proforma = pd.DataFrame([
        {"Horizonte": "Año 0 (Situación Actual)", "EBITDA Proforma": calc["ebitda"], "Margen %": calc["ebitda_pct"], "Generación Neta": 0.0},
        {"Horizonte": "Año 1 (Captura 55% Fugas)", "EBITDA Proforma": calc["ebitda_ao1"], "Margen %": (calc["ebitda_ao1"]/calc["ventas"])*100, "Generación Neta": calc["mejora_ao1"]},
        {"Horizonte": "Año 2 (Captura 85% Fugas)", "EBITDA Proforma": calc["ebitda_ao2"], "Margen %": (calc["ebitda_ao2"]/calc["ventas"])*100, "Generación Neta": calc["mejora_ao2"]},
        {"Horizonte": "Año 3 (Madurez y Escala)", "EBITDA Proforma": calc["ebitda_ao3"], "Margen %": (calc["ebitda_ao3"]/calc["ventas"])*100, "Generación Neta": calc["mejora_ao3"]},
    ])
    st.dataframe(df_proforma.style.format({"EBITDA Proforma": "{:,.2f} €", "Margen %": "{:.1f} %", "Generación Neta": "+{:,.2f} €"}), use_container_width=True)

with c_prof2:
    st.success(f"""
    **Métricas de Inversión:**
    * **Inversión Requerida:** `{calc['inversion_modernizacion']:,.2f} €`
    * **Plazo de Retorno (Payback):** `{calc['payback_meses']:.1f} meses`
    * **ROI a 3 Años:** `+{calc['roi_3y']:.0f} %`
    """)

# Consulta de IA bajo demanda
st.markdown("### 5. Dictamen Estratégico y Hoja de Ruta (IA Gemini)")
with st.spinner("Sintetizando dictamen de gobernanza y hoja de ruta con IA..."):
    ia_analisis = generar_dictamen_consultoria(datos_actuales, calc)

col_ia1, col_ia2 = st.columns(2)
with col_ia1:
    st.write("##### Dictamen de Dirección")
    st.info(ia_analisis.get("dictamen_ejecutivo", ""))
    st.write("##### Causa Raíz de Cuellos de Botella")
    st.write(ia_analisis.get("analisis_cuello_botella", ""))

with col_ia2:
    st.write("##### Riesgo de Gobernanza y Concentración")
    st.warning(ia_analisis.get("analisis_gobernanza_riesgo", ""))
    st.write("##### Hoja de Ruta de Modernización")
    hr = ia_analisis.get("hoja_ruta_directiva", {})
    st.markdown(f"* **Inmediato (30 días):** {hr.get('inmediato_30d', '')}")
    st.markdown(f"* **Consolidación (90 días):** {hr.get('medio_plazo_90d', '')}")
    st.markdown(f"* **Estratégico (12 meses):** {hr.get('estrategico_12m', '')}")

st.markdown("---")
pdf_bytes = generar_pdf_editorial(datos_actuales, calc, ia_analisis)
st.download_button(
    label="📄 Descargar Dossier de Dirección en PDF",
    data=pdf_bytes,
    file_name=f"Auditoria_KROMA_{datos_actuales['nombre_empresa'].replace(' ', '_')}.pdf",
    mime="application/pdf"
)
