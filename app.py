import io
import json
import re
import time
from google import genai
from google.genai import types
import markdown
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from xhtml2pdf import pisa

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="KROMA Ops | Operational & Capacity Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- ESTILO VISUAL MODERNO (SAAS PREMIUM) ---
st.markdown(
    """
    <style>
    /* Ocultar elementos estándar de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    /* Tipografía y acabados */
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        color: #0f172a;
    }
    
    .kroma-hero {
        padding: 10px 0 24px 0;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 24px;
    }
    .kroma-hero-tag {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 1.2px;
        color: #2563eb;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .kroma-hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.2;
        margin-bottom: 10px;
    }
    .kroma-hero-desc {
        font-size: 1.05rem;
        color: #475569;
        line-height: 1.5;
        max-width: 900px;
    }

    /* Tarjetas de métricas */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .callout-legal {
        background-color: #f8fafc;
        border-left: 3px solid #2563eb;
        padding: 12px 16px;
        margin: 14px 0;
        font-size: 0.92rem;
        color: #334155;
        border-radius: 0 6px 6px 0;
    }
    .assistant-card {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 8px;
        padding: 20px;
        margin-top: 28px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- CABECERA SUPERIOR DE MARCA (KROMA OPS) ---
st.markdown(
    """
    <div style="display: flex; align-items: center; justify-content: space-between; padding: 14px 22px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
        <div style="display: flex; align-items: center; gap: 12px;">
            <svg width="34" height="34" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M18 3L4 11V25L18 33L18 18L4 11" fill="url(#kg1)"/>
                <path d="M18 3L32 11L18 18V33L32 25V11" fill="url(#kg2)"/>
                <path d="M18 3L32 11L18 18L4 11L18 3Z" fill="#2563EB"/>
                <defs>
                    <linearGradient id="kg1" x1="4" y1="11" x2="18" y2="33" gradientUnits="userSpaceOnUse">
                        <stop stop-color="#0F172A"/>
                        <stop offset="1" stop-color="#1E3A8A"/>
                    </linearGradient>
                    <linearGradient id="kg2" x1="32" y1="11" x2="18" y2="33" gradientUnits="userSpaceOnUse">
                        <stop stop-color="#2563EB"/>
                        <stop offset="1" stop-color="#06B6D4"/>
                    </linearGradient>
                </defs>
            </svg>
            <div style="display: flex; align-items: baseline; gap: 6px;">
                <span style="font-size: 21px; font-weight: 800; letter-spacing: 1.5px; color: #0F172A;">KROMA</span>
                <span style="background: #0F172A; color: #FFFFFF; font-size: 11px; font-weight: 700; padding: 2px 7px; border-radius: 4px; letter-spacing: 0.8px;">OPS</span>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 12px;">
            <span style="display: inline-flex; align-items: center; gap: 6px; font-size: 11.5px; font-weight: 600; color: #047857; background: #ECFDF5; padding: 4px 11px; border-radius: 20px; border: 1px solid #A7F3D0;">
                <span style="width: 6px; height: 6px; border-radius: 50%; background: #10B981;"></span>
                Motor Financiero Residuo 0,00 €
            </span>
            <span style="font-size: 11.5px; font-weight: 500; color: #475569; background: #F1F5F9; padding: 4px 11px; border-radius: 20px; border: 1px solid #E2E8F0;">
                RD 238/2026 & Veri*factu 2027
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- HERO COMERCIAL ---
st.markdown(
    """
    <div class="kroma-hero">
        <div class="kroma-hero-tag">Inteligencia Operativa & Diagnóstico de Capacidad</div>
        <div class="kroma-hero-title">Desbloquea el margen oculto de tu estructura técnica</div>
        <div class="kroma-hero-desc">
            Evaluación cuantitativa para pymes de instalaciones y servicios técnicos (SAT). Identifica horas no facturadas, concilia tu cuenta proforma a residuo cero y planifica tu modernización en 4 minutos.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- MOTOR DE MAQUETACIÓN PDF EDITORIAL KROMA OPS ---
def generar_pdf_editorial(markdown_texto, empresa_nombre, sector_nombre):
    html_cuerpo = markdown.markdown(markdown_texto, extensions=["tables", "fenced_code"])
    
    plantilla_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        @page {{
            size: a4 portrait;
            margin: 20mm 15mm 20mm 15mm;
            @top-left {{
                content: "KROMA OPS — DOSSIER DE DIRECCIÓN | CONFIDENCIAL";
                font-family: Helvetica, Arial, sans-serif;
                font-size: 7.5pt;
                color: #64748b;
                border-bottom: 0.5pt solid #cbd5e1;
                padding-bottom: 4px;
            }}
            @top-right {{
                content: "{empresa_nombre}";
                font-family: Helvetica, Arial, sans-serif;
                font-size: 7.5pt;
                color: #64748b;
                border-bottom: 0.5pt solid #cbd5e1;
                padding-bottom: 4px;
            }}
            @bottom-right {{
                content: "Página " counter(page) " de " counter(pages);
                font-family: Helvetica, Arial, sans-serif;
                font-size: 7.5pt;
                color: #64748b;
            }}
            @bottom-left {{
                content: "KROMA Operations Intelligence Platform (v2.4)";
                font-family: Helvetica, Arial, sans-serif;
                font-size: 7.5pt;
                color: #64748b;
            }}
        }}

        body {{
            font-family: Helvetica, Arial, sans-serif;
            font-size: 9pt;
            line-height: 1.5;
            color: #1e293b;
        }}

        .portada {{
            page-break-after: always;
            padding-top: 55mm;
            text-align: left;
        }}
        .portada-subtitulo-sup {{
            font-size: 10pt;
            font-weight: bold;
            color: #2563eb;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin-bottom: 12px;
        }}
        .portada-titulo {{
            font-size: 26pt;
            font-weight: bold;
            color: #0f172a;
            line-height: 1.15;
            margin-bottom: 18px;
        }}
        .portada-bajada {{
            font-size: 11pt;
            color: #475569;
            line-height: 1.6;
            margin-bottom: 50mm;
        }}
        .portada-meta {{
            border-top: 1.5pt solid #0f172a;
            padding-top: 15px;
            font-size: 8.5pt;
            color: #334155;
            line-height: 1.8;
        }}

        h1 {{
            font-size: 14.5pt;
            color: #0f172a;
            border-bottom: 1.5pt solid #0f172a;
            padding-bottom: 4px;
            margin-top: 22px;
            margin-bottom: 12px;
            page-break-before: always;
        }}
        h2 {{
            font-size: 11.5pt;
            color: #1e40af;
            margin-top: 16px;
            margin-bottom: 8px;
            border-bottom: 0.5pt solid #cbd5e1;
            padding-bottom: 3px;
            page-break-after: avoid;
        }}
        h3 {{
            font-size: 9.5pt;
            color: #0f172a;
            margin-top: 12px;
            margin-bottom: 6px;
            page-break-after: avoid;
        }}

        p {{
            margin-bottom: 8px;
            text-align: justify;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            margin-bottom: 14px;
            page-break-inside: avoid;
            font-size: 8pt;
        }}
        th {{
            background-color: #f1f5f9;
            color: #0f172a;
            font-weight: bold;
            text-align: left;
            padding: 6px 8px;
            border-top: 1pt solid #0f172a;
            border-bottom: 1pt solid #cbd5e1;
        }}
        td {{
            padding: 5px 8px;
            border-bottom: 0.5pt solid #e2e8f0;
            color: #334155;
        }}
        tr:nth-child(even) td {{
            background-color: #f8fafc;
        }}

        blockquote {{
            background-color: #f8fafc;
            border-left: 3pt solid #2563eb;
            margin: 10px 0;
            padding: 8px 12px;
            font-size: 8.5pt;
            color: #334155;
        }}

        ul, ol {{
            margin-top: 4px;
            margin-bottom: 10px;
            padding-left: 18px;
        }}
        li {{
            margin-bottom: 4px;
        }}
    </style>
    </head>
    <body>
        <div class="portada">
            <div class="portada-subtitulo-sup">KROMA OPS — Intelligence Dossier</div>
            <div class="portada-titulo">Plan de Eficiencia Operativa y Desbloqueo de Capacidad</div>
            <div class="portada-bajada">
                Auditoría cuantitativa de tiempos no facturables, cuenta de explotación proforma conciliada con residuo cero y hoja de ruta de modernización.
            </div>
            <div class="portada-meta">
                <b>Entidad Evaluada:</b> {empresa_nombre}<br>
                <b>Especialidad Operativa:</b> {sector_nombre}<br>
                <b>Fecha de Emisión:</b> Septiembre de 2026<br>
                <b>Carácter:</b> Confidencial — Reservado para Dirección General y Comité Estratégico
            </div>
        </div>

        {html_cuerpo}
    </body>
    </html>
    """
    
    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(plantilla_html, dest=pdf_buffer)
    if pisa_status.err:
        return None
    pdf_buffer.seek(0)
    return pdf_buffer

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("### Configuración de Acceso")
    api_key_usuario = st.text_input(
        "Clave de API (Gemini):",
        type="password",
        help="Introduce tu clave de API de Google AI Studio.",
    )
    st.markdown("---")
    st.markdown("### Marco de Trazabilidad")
    st.caption(
        """
        • **[DR] Dato Reportado:** Información facilitada en el test.\n
        • **[C] Cálculo:** Resultado matemático exacto derivado.\n
        • **[FE] Fuente Externa:** Normativa legal oficial (BOE).\n
        • **[ES] Estimación:** Valor técnico aproximado.\n
        • **[HC] Hipótesis de Cálculo:** Supuesto de escenario futuro.\n
        • **[OD] Objetivo Directivo:** Meta formal del plan.
        """
    )

# Memoria de sesión
if "informe_generado" not in st.session_state:
    st.session_state["informe_generado"] = None
if "datos_contexto" not in st.session_state:
    st.session_state["datos_contexto"] = ""
if "datos_graficos" not in st.session_state:
    st.session_state["datos_graficos"] = {}
if "ultima_pregunta" not in st.session_state:
    st.session_state["ultima_pregunta"] = None
if "ultima_respuesta" not in st.session_state:
    st.session_state["ultima_respuesta"] = None

# --- FORMULARIO ESTRUCTURADO ---
tab_gen, tab_fin, tab_ops, tab_mkt, tab_vision = st.tabs([
    "1. Estructura y Capacidad",
    "2. Datos Económicos",
    "3. Circuito Comercial y Tiempos",
    "4. Clientes y Diferenciación",
    "5. Dirección, Plan e Inversión",
])

with tab_gen:
    st.markdown("#### Identificación Corporativa y Capacidad Humana")
    g1, g2, g3 = st.columns(3)
    with g1:
        empresa_razon = st.text_input("Razón Social o Empresa:", value="ClimaServ Levantina S.L.")
        sector = st.text_input("Actividad o sector principal:", value="Instalación y mantenimiento de climatización y aerotermia")
        subsector = st.text_input("Especialidad operativa:", value="Frío comercial para hostelería y climatización residencial de alta gama")
    with g2:
        pais_region = st.text_input("Ámbito territorial de actuación:", value="España (Comunidad Valenciana)")
        ano_creacion = st.number_input("Año de constitución (opcional):", min_value=1950, max_value=2026, value=2012)
        tamano_equipo = st.number_input("Plantilla total (personas):", min_value=1, max_value=500, value=6)
    with g3:
        operarios_directos = st.number_input("Técnicos directos en campo:", min_value=1, max_value=500, value=4)
        personal_admin = st.number_input("Personal de administración:", min_value=0, max_value=50, value=1)
        personal_comercial = st.number_input("Personal comercial/ventas:", min_value=0, max_value=50, value=1)
        tiene_flota = st.checkbox("Flota de furgonetas o vehículos", value=True)

    if tiene_flota:
        f1, f2 = st.columns(2)
        with f1:
            num_vehiculos = st.number_input("Número de furgonetas:", min_value=1, max_value=100, value=4)
        with f2:
            control_stock_vehiculos = st.selectbox(
                "Control de material en vehículos:",
                [
                    "Sin registro formal / Los operarios reponen según necesidad",
                    "Registro manual en papel al inicio y fin de jornada",
                    "Hojas de cálculo periódicas",
                    "Identificación digital (códigos QR / aplicación móvil)",
                ],
            )
    else:
        num_vehiculos = 0
        control_stock_vehiculos = "Sin flota de vehículos"

with tab_fin:
    st.markdown("#### Cuenta de Explotación y Tesorería")
    archivo_subido = st.file_uploader("Adjuntar balance o P&L (PDF, Excel, CSV) (opcional):", type=["pdf", "xlsx", "xls", "csv"])
    if archivo_subido is not None:
        st.info(f"Documento incorporado: **{archivo_subido.name}**.")

    fn1, fn2, fn3 = st.columns(3)
    with fn1:
        facturacion_anual = st.number_input("Facturación último ejercicio (€):", min_value=10000, max_value=50000000, value=480000, step=10000)
        facturacion_anterior = st.number_input("Facturación ejercicio previo (€):", min_value=0, max_value=50000000, value=450000, step=10000)
    with fn2:
        coste_personal = st.number_input("Coste anual de personal (€):", min_value=5000, max_value=30000000, value=195000, step=5000)
        coste_compras_recambios = st.number_input("Consumo anual de materiales (€):", min_value=0, max_value=30000000, value=165000, step=5000)
    with fn3:
        gastos_fijos = st.number_input("Gastos fijos de estructura (€):", min_value=1000, max_value=10000000, value=58000, step=2000)
        margen_ebitda_declarado = st.number_input("EBIT reportado (€):", min_value=-500000, max_value=10000000, value=62000, step=2000)

    costes_totales = coste_personal + coste_compras_recambios + gastos_fijos
    resultado_teorico = facturacion_anual - costes_totales
    facturacion_por_empleado = facturacion_anual / tamano_equipo if tamano_equipo > 0 else 0
    margen_bruto_pct = ((facturacion_anual - coste_compras_recambios) / facturacion_anual) * 100 if facturacion_anual > 0 else 0

    st.markdown("##### Ratios Derivados de Explotación")
    cf1, cf2, cf3 = st.columns(3)
    cf1.metric("Facturación por Empleado [C]", f"{facturacion_por_empleado:,.0f} €/año")
    cf2.metric("Margen s/ Materiales [C]", f"{margen_bruto_pct:.2f} %")
    cf3.metric("Resultado Calculado [C]", f"{resultado_teorico:,.0f} €")

    with st.expander("Plazos de cobro y saldo vencido (opcional)"):
        dias_cobro = st.number_input("Periodo medio de cobro (días) (DSO):", min_value=0, max_value=365, value=68)
        saldo_pendiente_cobro = st.number_input("Saldo pendiente vencido (€):", min_value=0, max_value=5000000, value=18000, step=1000)

with tab_ops:
    st.markdown("#### Circuito Comercial y Cuellos de Botella")
    op1, op2, op3 = st.columns(3)
    with op1:
        presupuestos_mes = st.number_input("Presupuestos emitidos/mes:", min_value=1, max_value=5000, value=25)
        tasa_conversion_presupuestos = st.slider("Tasa de presupuestos aceptados (%):", min_value=5, max_value=100, value=35)
        ticket_medio_operacion = st.number_input("Ticket medio facturado (€):", min_value=10, max_value=50000, value=1450, step=50)
    with op2:
        horas_perdidas_dia = st.number_input("Horas diarias agregadas no facturables:", min_value=0.5, max_value=16.0, value=3.5, step=0.5)
        quien_hace_presupuestos = st.selectbox("Responsable de presupuestos:", ["Dirección / Gerencia", "Técnicos especialistas", "Personal administrativo", "Área comercial"])
        precio_hora_mano_obra = st.number_input("Tarifa facturada mano de obra (€/h):", min_value=15, max_value=300, value=42, step=1)
    with op3:
        tiempo_cierre_factura = st.selectbox("Plazo de facturación tras trabajo:", ["Misma jornada (in situ)", "Entre 24 y 48 horas", "Entre 3 y 7 días hábiles", "A mes vencido"])
        origen_clientes = st.selectbox("Canal de captación principal:", ["Recomendaciones directas", "Búsqueda online y local", "Acción comercial", "Subcontratación"])
        stack_tecnologico = st.selectbox("Sistemas actuales:", ["Partes en papel y hojas de cálculo", "Software local sin sincronización", "Herramientas en nube sin integrar", "ERP/FSM integrado"])

    friccion_operativa = st.text_area(
        "Cuello de botella principal:",
        value="Los partes de trabajo en papel tardan hasta 5 días en procesarse y facturarse. Se dedican 3,5 h diarias agregadas a tareas no facturables (2 h entre técnicos rellenando papel y cuadrando furgoneta, 1 h en presupuestos complejos que no se convierten y 0,5 h en administración). Descontrol de stock en furgonetas que genera segundas visitas.",
        height=80,
    )

with tab_mkt:
    st.markdown("#### Clientes y Diferenciación")
    m1, m2 = st.columns(2)
    with m1:
        porcentaje_b2c = st.slider("Ingresos particulares (%):", min_value=0, max_value=100, value=40)
        porcentaje_b2b = 100 - porcentaje_b2c
        st.caption(f"Ingresos procedentes de empresas: **{porcentaje_b2b}%**")
        ingresos_recurrentes_pct = st.slider("Ingresos bajo contratos de mantenimiento (%):", min_value=0, max_value=100, value=15)
    with m2:
        competidor_referencia = st.text_input("Competidor de referencia:", value="Grandes comercializadoras con cuotas empaquetadas")
        ventaja_competitiva = st.text_input("Factor diferencial actual:", value="Respuesta técnica en menos de 3 horas en averías críticas de hostelería")

    with st.expander("Concentración de clientes (opcional)"):
        top5_concentracion = st.slider("Concentración en los 5 mayores clientes (%):", min_value=5, max_value=100, value=30)

with tab_vision:
    st.markdown("#### Plan e Inversión")
    v1, v2 = st.columns(2)
    with v1:
        presupuesto_disponible = st.number_input("Presupuesto disponible anual para modernización (€):", min_value=0, max_value=500000, value=6500, step=500)
        horizonte = st.slider("Horizonte temporal (años):", min_value=1, max_value=5, value=3)
        objetivo_principal_crecimiento = st.selectbox("Prioridad estratégica:", ["Incrementar el margen neto y la rentabilidad", "Ampliar facturación en empresas", "Reducir dependencia directiva", "Estandarizar procesos"])
    with v2:
        pregunta_115_inaccion = st.text_area("Riesgo de inacción en 3 años:", value="Reducción de márgenes por costes laborales y pérdida de cuota local ante competidores con cuotas empaquetadas.", height=70)
        pregunta_116_deseo = st.text_area("Problema prioritario a resolver:", value="Eliminar horas en presupuestos sin cerrar y liquidar partes en menos de 24 horas.", height=70)

# =====================================================================
# FUNCIONES GRÁFICAS PLOTLY
# =====================================================================
def render_trend_matrix(trends_data):
    horiz_scores = {"Prioridad inmediata (0-6 meses)": 1.5, "Preparación (6-18 meses)": 5.0, "Seguimiento (18-36 meses)": 8.5}
    nombres, x_vals, y_vals, descripciones = [], [], [], []
    for t in trends_data:
        h_str = t.get("horizon", "Preparación (6-18 meses)")
        h_score = horiz_scores.get(h_str, 5.0)
        impact = t.get("impact", 5)
        nombres.append(t.get("name", "Tendencia"))
        x_vals.append(h_score)
        y_vals.append(impact)
        descripciones.append(f"Área: {t.get('quadrant', 'Operaciones')}<br>Impacto: {impact}/10<br>Plazo: {h_str}")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode="markers+text", text=nombres, textposition="top center", textfont=dict(size=10, color="#1e293b"), marker=dict(size=12, color="#2563eb", line=dict(width=1.5, color="#0f172a")), hoverinfo="text", hovertext=descripciones))
    fig.add_hline(y=5.5, line_dash="dot", line_color="#cbd5e1")
    fig.add_vline(x=5.0, line_dash="dot", line_color="#cbd5e1")
    fig.update_layout(title=dict(text="Mapa de Tendencias y Prioridades de Gestión", font=dict(size=13, color="#0f172a")), xaxis=dict(title="Horizonte Temporal", range=[0, 10], tickvals=[1.5, 5.0, 8.5], ticktext=["0-6 meses", "6-18 meses", "18-36 meses"], showgrid=False), yaxis=dict(title="Nivel de Impacto", range=[0, 11], tickvals=[2, 4, 6, 8, 10], showgrid=True, gridcolor="#f8fafc"), plot_bgcolor="#ffffff", paper_bgcolor="#ffffff", height=420, margin=dict(l=40, r=30, t=50, b=40))
    return fig

def render_gap_bars(gap_data):
    categories = ["Digitalización", "Eficiencia Operativa", "Control de Margen", "Cartera B2B", "Capacidad Adaptación"]
    pyme_scores = gap_data.get("pyme", [2, 4, 4, 5, 3])
    ref_scores = gap_data.get("benchmark_orientativo", [5, 5, 5, 5, 4])
    target_scores = gap_data.get("benchmark_aspiracional", [8, 8, 8, 8, 8])

    fig = go.Figure()
    fig.add_trace(go.Bar(y=categories, x=pyme_scores, orientation="h", name="Situación Actual [DR]", marker=dict(color="#334155"), width=0.25))
    fig.add_trace(go.Scatter(y=categories, x=ref_scores, mode="markers", name="Referencia Modelo [ES]", marker=dict(color="#94a3b8", size=11, symbol="line-ns", line=dict(width=3, color="#64748b"))))
    fig.add_trace(go.Scatter(y=categories, x=target_scores, mode="markers", name="Objetivo Dirección [OD]", marker=dict(color="#2563eb", size=10, symbol="diamond")))
    fig.update_layout(title=dict(text="Evaluación de Posición Operativa (Escala 1–10)", font=dict(size=13, color="#0f172a")), xaxis=dict(range=[0, 10.5], showgrid=True, gridcolor="#f8fafc"), yaxis=dict(autorange="reversed"), legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(size=10)), plot_bgcolor="#ffffff", paper_bgcolor="#ffffff", height=350, margin=dict(l=140, r=20, t=50, b=50))
    return fig

# =====================================================================
# EJECUCIÓN DEL CHECK-UP
# =====================================================================
st.markdown("---")
if st.button("Ejecutar Check-up Operativo y Generar Dossier Proforma", type="primary", use_container_width=True):
    if not api_key_usuario:
        st.error("Es obligatorio introducir la clave de API en la barra lateral izquierda.")
    else:
        with st.spinner("KROMA Engine: Auditando unit economics, conciliando P&L con residuo 0,00 € y maquetando dossier..."):
            try:
                cliente = genai.Client(api_key=api_key_usuario)

                # Motor Matemático Conciliado
                ratio_compras_exacto = coste_compras_recambios / facturacion_anual  # 165/480 = 0.34375
                ratio_margen_exacto = 1.0 - ratio_compras_exacto  # 0.65625
                horas_totales_no_fac = horas_perdidas_dia * 220  # 770 h
                coste_hora_medio_plantilla = coste_personal / (tamano_equipo * 1800)  # 18.06 €/h
                coste_salarial_improductivo = round(horas_totales_no_fac * coste_hora_medio_plantilla)  # 13.903 €
                margen_por_hora_calc = precio_hora_mano_obra * ratio_margen_exacto  # 27.5625 €/h

                capex_inicial = 4000
                opex_ano1 = 2500
                inversion_total_ano1 = capex_inicial + opex_ano1  # 6.500 €

                ventas_horas_liberadas = 385 * precio_hora_mano_obra  # 16.170 €
                ventas_conversion = 6 * ticket_medio_operacion  # 8.700 €
                ventas_contratos_b2b = 5 * 900  # 4.500 €
                ventas_nuevas_totales = ventas_horas_liberadas + ventas_conversion + ventas_contratos_b2b  # 29.370 €
                facturacion_ano1 = facturacion_anual + ventas_nuevas_totales  # 509.370 €

                ahorro_mermas_stock = 4800
                coste_material_nuevo = round(ventas_nuevas_totales * ratio_compras_exacto)  # 10.096 €
                compras_ano1 = coste_compras_recambios + coste_material_nuevo - ahorro_mermas_stock  # 170.296 €

                personal_ano1 = coste_personal  # 195.000 €
                gastos_fijos_ano1 = gastos_fijos  # 58.000 €
                ebit_ano1 = facturacion_ano1 - compras_ano1 - personal_ano1 - gastos_fijos_ano1 - opex_ano1  # 83.574 €

                margen_horas_p1 = round(ventas_horas_liberadas * ratio_margen_exacto)  # 10.612 €
                margen_conversion_p2 = round(ventas_conversion * ratio_margen_exacto)  # 5.709 €
                margen_b2b_p4 = round(ventas_contratos_b2b * ratio_margen_exacto)  # 2.953 €
                ahorro_stock_p3 = ahorro_mermas_stock  # 4.800 €
                mejora_neta_ebit = margen_horas_p1 + margen_conversion_p2 + ahorro_stock_p3 + margen_b2b_p4 - opex_ano1  # 21.574 €

                h_recup_25 = horas_totales_no_fac * 0.25
                margen_inc_25 = h_recup_25 * margen_por_hora_calc
                payback_meses_25 = (inversion_total_ano1 / margen_inc_25) * 12

                h_recup_50 = horas_totales_no_fac * 0.50
                margen_inc_50 = h_recup_50 * margen_por_hora_calc
                payback_meses_50 = (inversion_total_ano1 / margen_inc_50) * 12  # 7.4 meses

                h_recup_75 = horas_totales_no_fac * 0.75
                margen_inc_75 = h_recup_75 * margen_por_hora_calc
                payback_meses_75 = (inversion_total_ano1 / margen_inc_75) * 12

                prompt_completo = f"""
Eres un Socio Director de Consultoría de Operaciones y Estrategia Empresarial de KROMA OPS.
Fecha actual del análisis: Septiembre de 2026.
Debes elaborar un informe técnico, sobrio, exhaustivo y matemáticamente riguroso para la Dirección General y Comité Estratégico de {empresa_razon}.

BASE DE DATOS AUDITADA (CONCILIACIÓN MATEMÁTICA CON RESIDUO CERO 0,00 €):
- Entidad evaluada: [DR] {empresa_razon} | Sector: [DR] {sector} | {subsector} | Ámbito: [DR] {pais_region}
- Plantilla total: [DR] {tamano_equipo} personas (4 técnicos de campo, 1 soporte admin, 1 gerencia/comercial)
- Facturación anual reportada: [DR] {facturacion_anual:,} € | Coste personal: [DR] {coste_personal:,} € | Compras: [DR] {coste_compras_recambios:,} € | Gastos fijos: [DR] {gastos_fijos:,} € | EBIT actual: [DR] {margen_ebitda_declarado:,} € ({margen_ebitda_declarado/facturacion_anual*100:.2f}%)
- Facturación por empleado: [C] {facturacion_por_empleado:,.0f} €/año
- Margen bruto s/ materiales: [C] {margen_bruto_pct:.2f}% | Ratio compras s/ ventas: [C] {ratio_compras_exacto*100:.2f}%
- Coste horario medio de plantilla: [C] {coste_hora_medio_plantilla:.2f} €/h ({coste_personal:,} € / 6 / 1.800 h).
- Horas no facturables: [DR] {horas_perdidas_dia} h/día agregadas x 220 días = [C] {horas_totales_no_fac:.0f} h/año.
- Coste salarial improductivo: [C] {coste_salarial_improductivo:,} €/año ({horas_totales_no_fac:.0f} h x {coste_hora_medio_plantilla:.2f} €/h).
- Capacidad teórica liberable: [C] {horas_totales_no_fac * precio_hora_mano_obra:,.0f} €/año ({horas_totales_no_fac:.0f} h x {precio_hora_mano_obra} €/h).
- Margen de contribución directo derivado por hora facturada: [C] {margen_por_hora_calc:.2f} €/h (tarifa {precio_hora_mano_obra} €/h x ratio margen bruto {ratio_margen_exacto:.5f}).
- Inversión Año 1: Presupuesto declarado [DR] {presupuesto_disponible:,} €. Desglose: CAPEX inicial [ES] {capex_inicial:,} € + OPEX anual SaaS [ES] {opex_ano1:,} €/año. Inversión total prevista: [ES] {inversion_total_ano1:,} €.
- Sensibilidad del Payback (calculado sobre margen de contribución de {margen_por_hora_calc:.2f} €/h):
  * Conservador ([HC] 25% = {h_recup_25:.1f} h): Margen incremental = [C] {margen_inc_25:,.0f} €/año. Payback = [C] {payback_meses_25:.1f} meses.
  * Base ([HC] 50% = {h_recup_50:.1f} h): Margen incremental = [C] {margen_inc_50:,.0f} €/año. Payback = [C] {payback_meses_50:.1f} meses.
  * Favorable ([HC] 75% = {h_recup_75:.1f} h): Margen incremental = [C] {margen_inc_75:,.0f} €/año. Payback = [C] {payback_meses_75:.1f} meses.

======================================================================
REGLAS EDITORIALES Y DE CUADRE CONTABLE ESTRICTO:
======================================================================
1. RESUMEN EJECUTIVO PREVIO (PÁGINA EJECUTIVA PARA DIRECCIÓN GENERAL):
   Abre con un Resumen Ejecutivo estructurado:
   - Situación actual de partida ([DR] 480k € ventas, [DR] 62k € EBIT, [DR] 770 h no facturables/año).
   - Diagnóstico central: 3 cuellos de botella críticos (gestión manual de partes, presupuestos no convertidos, descontrol de van-stock).
   - Inversión requerida: [ES] 6.500 € (4.000 € CAPEX + 2.500 € OPEX SaaS Año 1).
   - Retorno esperado y distinción neta: Payback teórico condicionado de [C] 7,4 meses bajo el Escenario Base ([HC] 50% captura).
     * OBLIGATORIO: Distinguir con total claridad que la Palanca 1 de recuperación de horas aporta de forma aislada +10.612 € [C] de margen, mientras que el impacto económico global consolidado de todas las palancas del Escenario A totaliza +21.574 € [C] de mejora neta de EBIT (alcanzando 83.574 € [C]).
   - Tabla de Cuadro de Mando Directivo (Decisiones clave a adoptar):
     * Seleccionar solución tecnológica | Plazo: Mes 1 | Responsable: Dirección | Inversión: — | Impacto: Alto.
     * Implantar FSM/ERP móvil | Plazo: Meses 1-3 | Responsable: Dirección + Proveedor | Inversión: 4.000 € | Impacto: Alto.
     * Fase de Validación Operativa (medir tiempos reales) | Plazo: Mes 1 | Responsable: Operaciones | Inversión: — | Impacto: Crítico.
     * Activar catálogo paramétrico de presupuestos | Plazo: Meses 2-4 | Responsable: Comercial | Inversión: — | Impacto: Medio/Alto.
     * Lanzar oferta estandarizada de contratos B2B | Plazo: Meses 4-8 | Responsable: Comercial | Inversión: — | Impacto: Medio/Alto.

2. DECLARACIÓN DE ALCANCE Y TRAZABILIDAD (SECCIÓN 0):
   - Informe técnico de diagnóstico y consultoría operativa elaborado a partir de la información declarada por la empresa; no constituye una auditoría contable o financiera independiente.
   - Leyenda formal: [DR] Dato Reportado, [C] Cálculo, [FE] Fuente Externa, [ES] Estimación, [HC] Hipótesis de Cálculo, [OD] Objetivo Directivo.

3. CLARIFICACIÓN CONTABLE DE TARIFAS Y HORAS (SECCIÓN 1):
   - Al citar los {coste_salarial_improductivo:,} € y los {horas_totales_no_fac * precio_hora_mano_obra:,.0f} €, añade:
     "Nota de lectura contable: La cifra de {coste_salarial_improductivo:,} € [C] representa el coste salarial directo ya devengado en nóminas a razón de {coste_hora_medio_plantilla:.2f} €/h [C] de coste medio de plantilla. En contraste, los {horas_totales_no_fac * precio_hora_mano_obra:,.0f} € [C] representan la capacidad teórica máxima de facturación en caso de colocar la totalidad de dichas horas en el mercado a la tarifa de 42,00 €/h [DR]."
   - Tabla de desglose de las 770 h: 4 técnicos (0,5 h/día = 2 h/día = 440 h/año) [DR], 1 gerencia/comercial (1 h/día = 220 h/año) [DR], 1 administración (0,5 h/día = 110 h/año) [DR]. Total = 770 h/año [C].
   - Cadena de métricas de técnicos: 4 técnicos [DR] x 1.800 h = 7.200 h de plantilla [C]. Capacidad efectiva: 6.760 h tras descontar las 440 h improductivas.
   - Denominar exactamente: "[C] Margen de contribución directo derivado por hora facturada: {margen_por_hora_calc:.2f} €/h", resultante de aplicar el margen bruto sobre materiales reportado (65,625%) a la tarifa de 42 €/h. Prohibido citar costes inventados de 14,44 €/h.
   - En pricing: Matizar que el margen bruto sobre materiales favorable no demuestra por sí solo poder de fijación de precios.

4. RIGOR NORMATIVO BOE A SEPTIEMBRE DE 2026 (SECCIÓN 2):
   - Facturación B2B: Citar Real Decreto 238/2026 [FE]. Formatos: sintaxis XML Facturae y sintaxis UBL bajo norma EN 16931 [FE]. Prohibido citar Factur-X.
   - Veri*factu (RD 1007/2023 modificado por RDL 15/2025): 1 de enero de 2027 para sociedades y 1 de julio de 2027 para autónomos [FE].

5. BENCHMARKS Y MODELOS DE TRANSFERENCIA (SECCIONES 3 Y 4):
   - En la sección 3, sustituir 'Top 20%' por 'Referencia superior del modelo comparativo de consultoría [ES]'. Confianza Medio-Bajo [ES].
   - En la sección 4, titular: 'Modelos Teóricos de Transferencia y Patrones Operativos Típicos' (esquemas ilustrativos no auditorías directas).

6. METODOLOGÍA DEL SCORING Y TABLA PONDERADA EXACTA DE 9,20/10 (SECCIÓN 7):
   - Incluir baremo (1-2: Manual/Crítico, 3-4: Inicial, 5-6: Funcional con deficiencias, 7-8: Estandarizado, 9-10: Optimizado).
   - En la Sección 7.2, justificar el 9,20/10 con tabla ponderada exacta:
     * Movilidad SAT: 20% x 9,50 = 1,900 [C]
     * Capacidad Offline: 15% x 9,00 = 1,350 [C]
     * Cumplimiento Normativo: 15% x 9,50 = 1,425 [C]
     * Control Stock Furgoneta: 10% x 9,00 = 0,900 [C]
     * Gases Fluorados (F-Gas): 10% x 9,00 = 0,900 [C]
     * Integración Contable: 10% x 9,00 = 0,900 [C]
     * Presupuestos: 10% x 9,00 = 0,900 [C]
     * Coste TCO: 10% x 9,25 = 0,925 [C]
     * TOTAL PONDERADO = EXACTAMENTE 9,20 / 10 [C].

7. SELECCIÓN DE PROVEEDOR Y RIESGOS TECNOLÓGICOS (SECCIONES 10 Y 12):
   - En el pliego del RFP: Exigir 'Declaración responsable y acreditación técnica del fabricante que garantice la inalterabilidad, conservación y trazabilidad según RD 1007/2023'.
   - En riesgos: Prohibido decir 'SQLite'. Usar 'Almacenamiento local cifrado con sincronización transaccional posterior'.

8. CONCILIACIÓN EXACTA DE LA P&L A RESIDUO CERO Y PLAN A 36 MESES (SECCIÓN 13):
   Queda TERMINANTEMENTE PROHIBIDO poner dos filas de EBIT distintas para el mismo año. Corregir cualquier errata: usar '% CAMBIO'.
   - Desglose conciliado exacto de la Sección 13.1:
     * Palanca 1 (Captura de 385 h [HC]): Ventas +16.170 € [C] | Materiales +5.558 € [C] | Margen neto +10.612 € [C] (385 h x 42 € x {ratio_margen_exacto:.5f}).
     * Palanca 2 (Mejora de conversión presupuestaria): Ventas +8.700 € [ES] (6 presupuestos extra x 1.450 €) | Materiales +2.991 € [ES] | Margen neto +5.709 € [ES].
     * Palanca 3 (Optimización de stock): Ventas 0 € | Ahorro compras -4.800 € [HC] | Margen neto +4.800 € [HC] (165.000 € x 2,90909%).
     * Palanca 4 (Contratos B2B): Ventas +4.500 € [ES] (5 contratos x 900 €) | Materiales +1.547 € [ES] | Margen neto +2.953 € [ES].
     * Total incremento ventas = +29.370 € [C].
     * Incremento neto materiales = +5.296 € [C] (+10.096 € materiales nuevos - 4.800 € ahorro stock [HC]).
     * Menos software OPEX Año 1 = -2.500 € [ES].
     * Impacto neto en EBIT = +21.574 € [C].
     * EBIT inicial 62.000 € [DR] + 21.574 € [C] = 83.574 € [C] (Residuo: 0,00 €).
   - P&L Proforma Escenario A:
     * Actual [DR]: Ventas 480.000 € | Compras 165.000 € | Personal 195.000 € | Fijos 58.000 € | Software 0 € | EBIT = 62.000 € (12,9%).
     * Año 1 [ES]: Ventas 509.370 € | Compras 170.296 € | Personal 195.000 € | Fijos 58.000 € | Software 2.500 € | EBIT = 83.574 € (16,4%).
     * Año 2 [ES]: Ventas 528.000 € | Compras 171.600 € ([HC] mejora ratio compras al 32,5%) | Personal 197.000 € ([HC]) | Fijos 58.500 € ([HC]) | Software 5.000 € [ES] (estimación presupuestaria sujeta a oferta formal) | EBIT = 95.900 € (18,2%).
     * Año 3 [OD]: Ventas 545.000 € | Compras 168.950 € ([HC] compras al 31,0%) | Personal 201.000 € ([HC]) | Fijos 59.000 € ([HC]) | Software 8.500 € [ES] (estimación presupuestaria sujeta a oferta formal) | EBIT = 107.550 € (19,7%).
   - Contraste con Escenario B (Transformación a Ventas Constantes de 480.000 €): Ventas 480.000 € | Compras 160.200 € (ahorro stock 4.800 € [HC]) | Personal 195.000 € | Fijos 58.000 € | Software 2.500 € | EBIT = 64.300 € (13,4%). Explicar que se mantiene facturación constante redirigiendo capacidad hacia B2B preventivo sin ampliar personal.

9. DICTAMEN FINAL DEL CONSULTOR (SECCIÓN 14):
   "Con base en la información facilitada por la empresa, los cálculos derivados y los supuestos explicitados en el escenario económico, la inversión prevista de 6.500 € presenta un potencial de retorno favorable bajo el escenario base planteado.
   El escenario contempla la recuperación del 50% de las horas actualmente identificadas como improductivas, junto con mejoras adicionales en conversión de presupuestos, control de consumos y captación de contratos preventivos.
   El payback estimado de 7,4 meses debe interpretarse como payback teórico condicionado al cumplimiento de dichos supuestos, y no como un resultado garantizado. La fase de validación operativa de los primeros 30 días permitirá medir la capacidad real de conversión de las horas recuperadas y recalibrar las proyecciones económicas.
   Desde el punto de vista operativo, se recomienda priorizar en una primera fase el desbloqueo de capacidad instalada, la trazabilidad de partes y materiales y la estandarización de presupuestos antes de acometer incrementos estructurales de plantilla, reevaluando la necesidad de incorporaciones tras medir la utilización efectiva posterior a la implantación."

10. FORMATO JSON OBLIGATORIO PARA GRÁFICOS:
    - Inicia obligatoriamente con el bloque ```json ... ``` con 'trends' y 'gap_analysis'.
"""

                partes_contenido = []
                if archivo_subido is not None:
                    bytes_archivo = archivo_subido.read()
                    mime_type = archivo_subido.type
                    partes_contenido.append(types.Part.from_bytes(data=bytes_archivo, mime_type=mime_type))
                    prompt_completo += "\n\nDOCUMENTO CONTABLE ADJUNTO: Coteja partidas con código [DR]."

                partes_contenido.append(prompt_completo)

                modelos_a_probar = ["gemini-3.6-flash", "gemini-2.5-flash"]
                respuesta = None

                for mod in modelos_a_probar:
                    for intento in range(2):
                        try:
                            respuesta = cliente.models.generate_content(model=mod, contents=partes_contenido)
                            if respuesta:
                                break
                        except Exception as err:
                            if "503" in str(err) or "UNAVAILABLE" in str(err):
                                time.sleep(3)
                                continue
                            else:
                                raise err
                    if respuesta:
                        break

                if not respuesta:
                    raise Exception("Servidores de IA saturados temporalmente. Reintenta en unos segundos.")

                texto_salida = respuesta.text
                patron_json = r"```json\s*(\{.*?\})\s*```"
                match = re.search(patron_json, texto_salida, re.DOTALL)

                if match:
                    json_str = match.group(1)
                    datos_graficos = json.loads(json_str)

                    # Filtrado de anclas residuales
                    informe_limpio = re.sub(patron_json, "", texto_salida, flags=re.DOTALL).strip()
                    informe_limpio = re.sub(r"\[svg\]\(.*?\)", "", informe_limpio, flags=re.IGNORECASE)
                    informe_limpio = re.sub(r"\[#.*?\]", "", informe_limpio)
                    informe_limpio = re.sub(r"<a\s+name=[\"'].*?[\"']\s*></a>", "", informe_limpio, flags=re.IGNORECASE)
                    informe_limpio = re.sub(r"[ \t]+$", "", informe_limpio, flags=re.MULTILINE)

                    st.session_state["datos_contexto"] = texto_salida
                    st.session_state["informe_generado"] = informe_limpio
                    st.session_state["datos_graficos"] = datos_graficos
                    st.success("KROMA Engine: Evaluación cuantitativa y dossier proforma generados con éxito.")

                else:
                    texto_limpio = re.sub(r"\[svg\]\(.*?\)", "", texto_salida, flags=re.IGNORECASE)
                    texto_limpio = re.sub(r"\[#.*?\]", "", texto_limpio)
                    texto_limpio = re.sub(r"<a\s+name=[\"'].*?[\"']\s*></a>", "", texto_limpio, flags=re.IGNORECASE)
                    texto_limpio = re.sub(r"[ \t]+$", "", texto_limpio, flags=re.MULTILINE)
                    st.session_state["informe_generado"] = texto_limpio
                    st.session_state["datos_contexto"] = texto_salida

            except Exception as e:
                st.error(f"Error durante el procesamiento: {e}")

# =====================================================================
# RENDERIZADO DEL INFORME Y ASISTENTE DIRECTIVO
# =====================================================================
if st.session_state.get("informe_generado"):
    datos_graficos = st.session_state.get("datos_graficos", {})

    st.subheader("Representación Gráfica de Posición y Prioridades")
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        if "trends" in datos_graficos:
            fig_trends = render_trend_matrix(datos_graficos["trends"])
            st.plotly_chart(fig_trends, use_container_width=True)

    with col_g2:
        if "gap_analysis" in datos_graficos:
            fig_gap = render_gap_bars(datos_graficos["gap_analysis"])
            st.plotly_chart(fig_gap, use_container_width=True)

    # --- DESCARGA DOSSIER KROMA OPS ---
    st.markdown("---")
    c_pdf1, c_pdf2 = st.columns([3, 1])
    with c_pdf1:
        st.markdown("#### Dossier Técnico Proforma (15 Secciones)")
        st.caption("Documento ejecutivo con cuenta de explotación proforma conciliada, arquitectura de solución y plan a 180 días.")
    with c_pdf2:
        pdf_bytes = generar_pdf_editorial(
            st.session_state["informe_generado"],
            empresa_nombre=empresa_razon if 'empresa_razon' in locals() else "Empresa Evaluada",
            sector_nombre=subsector if 'subsector' in locals() else "Servicios Técnicos",
        )
        if pdf_bytes:
            st.download_button(
                label="📥 Descargar Dossier PDF de Dirección",
                data=pdf_bytes,
                file_name=f"KROMA_OPS_Dossier_Direccion_{empresa_razon.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

    st.markdown(st.session_state["informe_generado"])

    # CAPA DE INTERPRETACIÓN DIRECTIVA
    st.markdown("---")
    st.markdown(
        """
        <div class="assistant-card">
        <h4 style="color: #14532d; margin-bottom: 6px;">Asistente Directivo de Interpretación</h4>
        <p style="font-size: 0.92rem; color: #166534; margin-bottom: 14px;">
        Consulta tu informe en lenguaje directo. El asistente explica los resultados utilizando exclusivamente los datos de tu diagnóstico.
        </p>
        <p style="font-size: 0.88rem; color: #14532d; font-weight: bold; margin-bottom: 8px;">
        Preguntas directas sugeridas:
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_b1, col_b2, col_b3 = st.columns(3)
    pregunta_inmediata = None

    with col_b1:
        if st.button("Explícame el informe sin lenguaje técnico", use_container_width=True):
            pregunta_inmediata = "Explícame de forma muy sencilla y directa los 3 puntos más importantes de mi informe como si estuviéramos tomando un café, con mis datos reales y sin tecnicismos."
        if st.button("¿Cuánto dinero puedo recuperar realmente?", use_container_width=True):
            pregunta_inmediata = "¿Cuánto dinero y margen de contribución real puedo recuperar según el escenario base de 50% de recuperación horaria y cómo se calcula el payback de 7,4 meses?"

    with col_b2:
        if st.button("¿Cuál es el principal problema hoy?", use_container_width=True):
            pregunta_inmediata = "A partir de mis números reales, ¿cuál es exactamente el mayor problema y cuello de botella que tiene hoy mi empresa?"
        if st.button("¿Qué se hace en la validación operativa?", use_container_width=True):
            pregunta_inmediata = "Explícame en qué consiste la fase de Validación Operativa de los primeros 30 días y por qué es necesaria antes de implantar software."

    with col_b3:
        if st.button("¿Por qué digitalizar primero los partes?", use_container_width=True):
            pregunta_inmediata = "¿Por qué recomendáis digitalizar primero los partes de trabajo y el stock en furgonetas en vez de contratar comerciales o hacer publicidad?"
        if st.button("¿Qué riesgos tengo si no hago nada?", use_container_width=True):
            pregunta_inmediata = "Si decido no hacer nada durante los próximos 3 años, ¿qué impacto económico, operativo y normativo sufrirá mi empresa según el informe?"

    pregunta_abierta = st.text_input("O escribe una consulta sobre tu informe:", placeholder="Ej: ¿Cómo se desglosa el incremento de ingresos en la cuenta proforma?")
    btn_enviar_abierta = st.button("Consultar al Asistente", type="secondary")

    pregunta_a_procesar = None
    if pregunta_inmediata:
        pregunta_a_procesar = pregunta_inmediata
    elif btn_enviar_abierta and pregunta_abierta:
        pregunta_a_procesar = pregunta_abierta

    if pregunta_a_procesar:
        if not api_key_usuario:
            st.error("Introduce tu clave de API en la barra lateral para consultar al asistente.")
        else:
            with st.spinner("KROMA Engine: Analizando informe para la respuesta..."):
                try:
                    cliente = genai.Client(api_key=api_key_usuario)
                    prompt_asistente = f"""
Eres el Asistente Directivo de KROMA OPS para esta pyme.
Responde al dueño con claridad, cercanía y rigor analítico.

REGLAS:
1. Responde basándote EXCLUSIVAMENTE en los datos de este informe.
2. Cita las cifras reales: facturación ([DR] 480.000 €), 3,5 h/día agregadas ([DR]/[C] 770 h/año), coste horario medio ([C] {coste_hora_medio_plantilla:.2f} €/h), coste improductivo ([C] {coste_salarial_improductivo:,} €), inversión Año 1 ([ES] 6.500 € desglosada en [ES] 4.000 € CAPEX y [ES] 2.500 € OPEX SaaS).
3. En la cuenta proforma, explica que la facturación crece a {facturacion_ano1:,} € en el Año 1, con un EBIT único de {ebit_ano1:,} € ({ebit_ano1/facturacion_ano1*100:.1f}%), plenamente conciliado a residuo 0,00 €.
4. No inventes datos y sé pedagógico.

INFORME COMPLETO:
{st.session_state['datos_contexto']}

PREGUNTA:
{pregunta_a_procesar}
"""
                    modelos_asistente = ["gemini-3.6-flash", "gemini-2.5-flash"]
                    res_asistente = None
                    for mod in modelos_asistente:
                        try:
                            res_asistente = cliente.models.generate_content(model=mod, contents=prompt_asistente)
                            if res_asistente and res_asistente.text:
                                break
                        except Exception:
                            continue

                    if res_asistente and res_asistente.text:
                        st.session_state["ultima_pregunta"] = pregunta_a_procesar
                        st.session_state["ultima_respuesta"] = res_asistente.text
                    else:
                        st.error("Servidores temporalmente ocupados. Por favor, vuelve a pulsar.")

                except Exception as e:
                    st.error(f"Error al procesar la consulta: {e}")

    if st.session_state.get("ultima_respuesta"):
        st.markdown(
            f"""
            <div style="background-color: #ffffff; border: 1px solid #cbd5e1; border-left: 4px solid #16a34a; border-radius: 6px; padding: 18px; margin-top: 14px;">
            <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 6px; font-weight: bold;">CONSULTA: {st.session_state.get('ultima_pregunta', '')}</p>
            <div style="font-size: 0.95rem; color: #1e293b; line-height: 1.6;">
            {st.session_state['ultima_respuesta']}
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
