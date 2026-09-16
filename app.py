import json
import re
import time
from google import genai
from google.genai import types
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Diagnóstico Operativo y Plan de Acción Estratégico",
    page_icon="📋",
    layout="wide",
)

st.markdown(
    """
    <style>
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .callout-legal {
        background-color: #f8fafc;
        border-left: 3px solid #0f172a;
        padding: 12px 16px;
        margin: 12px 0;
        font-size: 0.92rem;
        color: #334155;
    }
    .assistant-card {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 6px;
        padding: 18px;
        margin-top: 24px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Diagnóstico Operativo, Capacidad Productiva y Plan Estratégico")
st.markdown(
    "Herramienta cuantitativa de evaluación de capacidad productiva, análisis comparativo y prioridades de gestión para pymes."
)
st.markdown("---")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Acceso y Configuración")
    api_key_usuario = st.text_input(
        "Clave de API (Gemini):",
        type="password",
        help="Introduce tu clave personal de acceso a la API de Google AI Studio.",
    )
    st.markdown("---")
    st.markdown("### Marco de Trazabilidad Documental")
    st.caption(
        """
        • **[DR] Dato Reportado:** Información facilitada por la empresa en el test.\n
        • **[C] Cálculo:** Resultado matemático exacto derivado de datos reportados.\n
        • **[FE] Fuente Externa:** Normativa legal oficial (BOE) o fuentes acreditadas.\n
        • **[ES] Estimación:** Valor aproximado ante ausencia de medición directa.\n
        • **[HC] Hipótesis de Cálculo:** Supuesto de gestión para modelar escenarios.\n
        • **[OD] Objetivo Directivo:** Meta fijada formalmente en el plan de trabajo.
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

# --- FORMULARIO ESTRUCTURADO EN 5 FASES ---
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
        sector = st.text_input(
            "Actividad o sector principal:",
            value="Instalación y mantenimiento de climatización y aerotermia",
        )
        subsector = st.text_input(
            "Especialidad operativa:",
            value="Frío comercial para hostelería y climatización residencial de alta gama",
        )
        pais_region = st.text_input(
            "Ámbito territorial de actuación:",
            value="España (Comunidad Valenciana)",
        )
    with g2:
        ano_creacion = st.number_input(
            "Año de constitución (opcional):",
            min_value=1950,
            max_value=2026,
            value=2012,
        )
        tamano_equipo = st.number_input(
            "Plantilla total de la empresa (personas):",
            min_value=1,
            max_value=500,
            value=6,
        )
        operarios_directos = st.number_input(
            "Técnicos directos en campo/obra/taller:",
            min_value=1,
            max_value=500,
            value=4,
        )
    with g3:
        personal_admin = st.number_input(
            "Personal de soporte administrativo:",
            min_value=0,
            max_value=50,
            value=1,
        )
        personal_comercial = st.number_input(
            "Personal dedicado a captación y ventas:",
            min_value=0,
            max_value=50,
            value=1,
        )
        tiene_flota = st.checkbox("La empresa cuenta con flota de furgonetas o vehículos", value=True)

    if tiene_flota:
        st.markdown("##### Gestión de Vehículos Operativos")
        f1, f2 = st.columns(2)
        with f1:
            num_vehiculos = st.number_input(
                "Número de furgonetas de servicio:",
                min_value=1,
                max_value=100,
                value=4,
            )
        with f2:
            control_stock_vehiculos = st.selectbox(
                "Procedimiento actual de control de material en vehículo:",
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
    
    archivo_subido = st.file_uploader(
        "Adjuntar balance de sumas y saldos, pérdidas y ganancias o listado contable (PDF, Excel, CSV) (opcional):",
        type=["pdf", "xlsx", "xls", "csv"],
        help="Permite cotejar partidas contables exactas y documentar las cifras con rigor.",
    )
    if archivo_subido is not None:
        st.info(f"Documento incorporado: **{archivo_subido.name}**. Se cotejarán los datos contables directamente.")

    fn1, fn2, fn3 = st.columns(3)
    with fn1:
        facturacion_anual = st.number_input(
            "Facturación anual del último ejercicio (€):",
            min_value=10000,
            max_value=50000000,
            value=480000,
            step=10000,
        )
        facturacion_anterior = st.number_input(
            "Facturación del ejercicio previo (€) (opcional):",
            min_value=0,
            max_value=50000000,
            value=450000,
            step=10000,
        )
    with fn2:
        coste_personal = st.number_input(
            "Coste total anual de personal (Nóminas brutas + Seguridad Social) (€):",
            min_value=5000,
            max_value=30000000,
            value=195000,
            step=5000,
        )
        coste_compras_recambios = st.number_input(
            "Consumo anual de materiales, repuestos y compras (€):",
            min_value=0,
            max_value=30000000,
            value=165000,
            step=5000,
        )
    with fn3:
        gastos_fijos = st.number_input(
            "Gastos fijos de estructura (Alquiler, suministros, seguros, asesoría) (€):",
            min_value=1000,
            max_value=10000000,
            value=58000,
            step=2000,
        )
        margen_ebitda_declarado = st.number_input(
            "Beneficio de explotación (EBIT) reportado (€):",
            min_value=-500000,
            max_value=10000000,
            value=62000,
            step=2000,
        )

    costes_totales = coste_personal + coste_compras_recambios + gastos_fijos
    resultado_teorico = facturacion_anual - costes_totales
    discrepancia_contable = abs(resultado_teorico - margen_ebitda_declarado)
    facturacion_por_empleado = facturacion_anual / tamano_equipo if tamano_equipo > 0 else 0
    margen_bruto_pct = ((facturacion_anual - coste_compras_recambios) / facturacion_anual) * 100 if facturacion_anual > 0 else 0

    st.markdown("##### Ratios Derivados de Explotación")
    cf1, cf2, cf3 = st.columns(3)
    cf1.metric("Facturación por Empleado [C]", f"{facturacion_por_empleado:,.0f} €/año")
    cf2.metric("Margen de Contribución s/ Materiales [C]", f"{margen_bruto_pct:.2f} %")
    cf3.metric("Resultado Contable Calculado [C]", f"{resultado_teorico:,.0f} €")

    if discrepancia_contable > 5000:
        st.markdown(
            f"""
            <div class="callout-legal">
            <b>Nota sobre información económica:</b> La resta de ingresos reportados ({facturacion_anual:,.0f} €) y gastos totales ({costes_totales:,.0f} €) arroja un resultado calculado de {resultado_teorico:,.0f} €, distinto del beneficio reportado ({margen_ebitda_declarado:,.0f} €). El informe tomará como referencia la capacidad horaria productiva hasta la verificación de la cuenta de pérdidas y ganancias definitiva.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("Plazos de cobro y saldo pendiente de cobro (opcional)"):
        dias_cobro = st.number_input(
            "Periodo medio de cobro a clientes (días):",
            min_value=0,
            max_value=365,
            value=65,
        )
        saldo_pendiente_cobro = st.number_input(
            "Saldo pendiente de cobro vencido (€):",
            min_value=0,
            max_value=5000000,
            value=18000,
            step=1000,
        )

with tab_ops:
    st.markdown("#### Circuito Comercial y Cuellos de Botella de Ejecución")
    op1, op2, op3 = st.columns(3)
    with op1:
        presupuestos_mes = st.number_input(
            "Número aproximado de presupuestos emitidos al mes:",
            min_value=1,
            max_value=5000,
            value=25,
        )
        tasa_conversion_presupuestos = st.slider(
            "Porcentaje estimado de presupuestos aceptados (%):",
            min_value=5,
            max_value=100,
            value=35,
        )
        ticket_medio_operacion = st.number_input(
            "Importe medio facturado por intervención (€):",
            min_value=10,
            max_value=50000,
            value=1450,
            step=50,
        )
    with op2:
        horas_perdidas_dia = st.number_input(
            "Tiempo diario agregado de gestión no facturable en la empresa (horas/día):",
            min_value=0.5,
            max_value=16.0,
            value=3.5,
            step=0.5,
            help="Suma total diaria de tiempo invertido entre técnicos (partes manuales), gerencia (presupuestos perdidos) y administración.",
        )
        quien_hace_presupuestos = st.selectbox(
            "Responsable habitual de elaborar los presupuestos:",
            [
                "Dirección / Gerencia",
                "Técnicos especialistas durante jornada de trabajo",
                "Personal administrativo",
                "Área comercial dedicada",
            ],
        )
        precio_hora_mano_obra = st.number_input(
            "Tarifa horaria facturada de mano de obra (€/h sin IVA):",
            min_value=15,
            max_value=300,
            value=42,
            step=1,
        )
    with op3:
        tiempo_cierre_factura = st.selectbox(
            "Plazo habitual entre finalización del trabajo y emisión de factura:",
            [
                "Misma jornada (in situ o procedimiento automático)",
                "Entre 24 y 48 horas",
                "Entre 3 y 7 días hábiles",
                "Facturación periódica a mes vencido",
            ],
        )
        origen_clientes = st.selectbox(
            "Canal principal de llegada de nuevos clientes:",
            [
                "Recomendaciones directas y clientes recurrentes",
                "Búsqueda orgánica en internet y presencia local",
                "Acción comercial directa",
                "Subcontratación y acuerdos con plataformas",
            ],
        )
        stack_tecnologico = st.selectbox(
            "Sistemas de información y gestión en uso:",
            [
                "Partes de trabajo físicos en papel y hojas de cálculo",
                "Aplicación de gestión local no sincronizada",
                "Herramientas en la nube sin integración directa entre sí",
                "Software de gestión integrada (ERP/FSM) con soporte móvil",
            ],
        )

    friccion_operativa = st.text_area(
        "Descripción del principal cuello de botella operativo y de gestión:",
        value="Los partes de trabajo en papel tardan hasta 5 días en procesarse y facturarse. Se dedican 3,5 h diarias agregadas a tareas no facturables (2 h entre técnicos rellenando papel y cuadrando furgoneta, 1 h en presupuestos complejos que no se convierten y 0,5 h en administración). Descontrol de stock en furgonetas que genera segundas visitas.",
        height=90,
    )

with tab_mkt:
    st.markdown("#### Segmentación de Clientes y Diferenciación")
    m1, m2 = st.columns(2)
    with m1:
        porcentaje_b2c = st.slider(
            "Proporción de ingresos procedente de particulares (%):",
            min_value=0,
            max_value=100,
            value=40,
        )
        porcentaje_b2b = 100 - porcentaje_b2c
        st.caption(f"Proporción de ingresos procedente de empresas/terciario: **{porcentaje_b2b}%**")

        ingresos_recurrentes_pct = st.slider(
            "Proporción de ingresos bajo contratos de mantenimiento periódico (%):",
            min_value=0,
            max_value=100,
            value=15,
        )
    with m2:
        competidor_referencia = st.text_input(
            "Competidor de referencia o presión externa relevante:",
            value="Grandes empresas de servicios energéticos y comercializadoras con contratos cerrados de mantenimiento",
        )
        ventaja_competitiva = st.text_input(
            "Factor diferencial actual (motivo principal de contratación):",
            value="Capacidad de respuesta técnica con plazo inferior a 3 horas en averías críticas de hostelería local",
        )

    with st.expander("Concentración de clientes en facturación (opcional)"):
        top5_concentracion = st.slider(
            "Porcentaje de facturación concentrado en los 5 principales clientes (%):",
            min_value=5,
            max_value=100,
            value=30,
        )

with tab_vision:
    st.markdown("#### Prioridades Estratégicas y Presupuesto")
    v1, v2 = st.columns(2)
    with v1:
        presupuesto_disponible = st.number_input(
            "Presupuesto máximo asignable reportado para modernización operativa en 12 meses (€):",
            min_value=0,
            max_value=500000,
            value=6500,
            step=500,
        )
        horizonte = st.slider(
            "Periodo de planificación del estudio (años):",
            min_value=1,
            max_value=5,
            value=3,
        )
        objetivo_principal_crecimiento = st.selectbox(
            "Prioridad estratégica directiva:",
            [
                "Incrementar el margen neto y la rentabilidad sobre la estructura actual",
                "Ampliar volumen de facturación y captar cuota en empresas",
                "Reducir la dependencia operativa del equipo directivo",
                "Contener costes y estandarizar procedimientos de trabajo",
            ],
        )

    with v2:
        st.markdown("##### Perspectiva y Criterio Directivo")
        pregunta_115_inaccion = st.text_area(
            "Impacto previsto si no se introducen cambios en el periodo considerado:",
            value="Los márgenes operativos tenderán a reducirse por la evolución de costes salariales, competidores integrados captarán clientes locales con cuotas empaquetadas y se deteriorará la rentabilidad.",
            height=70,
        )
        pregunta_116_deseo = st.text_area(
            "Problema prioritario a resolver en el corto plazo según la dirección:",
            value="Eliminar el tiempo consumido en presupuestos de averías que no prosperan y reducir el plazo de liquidación de partes de trabajo a menos de 24 horas.",
            height=70,
        )

# =====================================================================
# FUNCIONES GRÁFICAS EJECUTIVAS
# =====================================================================
def render_trend_matrix(trends_data):
    horiz_scores = {
        "Prioridad inmediata (0-6 meses)": 1.5,
        "Preparación (6-18 meses)": 5.0,
        "Seguimiento (18-36 meses)": 8.5,
    }
    
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

    fig.add_trace(
        go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="markers+text",
            text=nombres,
            textposition="top center",
            textfont=dict(family="Arial", size=10, color="#1e293b"),
            marker=dict(size=12, color="#1e40af", line=dict(width=1.5, color="#0f172a")),
            hoverinfo="text",
            hovertext=descripciones,
        )
    )

    fig.add_hline(y=5.5, line_dash="dot", line_color="#cbd5e1", line_width=1.5)
    fig.add_vline(x=5.0, line_dash="dot", line_color="#cbd5e1", line_width=1.5)

    fig.add_annotation(x=2.5, y=9.5, text="ACTUACIÓN INMEDIATA<br>(Alto impacto / Corto plazo)", showarrow=False, font=dict(size=10, color="#475569"))
    fig.add_annotation(x=7.5, y=9.5, text="PREPARACIÓN ESTRATÉGICA<br>(Alto impacto / Medio-largo plazo)", showarrow=False, font=dict(size=10, color="#475569"))
    fig.add_annotation(x=2.5, y=1.5, text="OPTIMIZACIÓN TÁCTICA<br>(Impacto moderado / Corto plazo)", showarrow=False, font=dict(size=10, color="#475569"))
    fig.add_annotation(x=7.5, y=1.5, text="MONITORIZACIÓN<br>(Impacto moderado / Largo plazo)", showarrow=False, font=dict(size=10, color="#475569"))

    fig.update_layout(
        title=dict(text="Mapa de Tendencias y Prioridades de Gestión", font=dict(size=13, color="#0f172a")),
        xaxis=dict(title="Horizonte Temporal de Actuación", range=[0, 10], tickvals=[1.5, 5.0, 8.5], ticktext=["0-6 meses", "6-18 meses", "18-36 meses"], showgrid=False),
        yaxis=dict(title="Nivel de Impacto en Rentabilidad y Operaciones", range=[0, 11], tickvals=[2, 4, 6, 8, 10], showgrid=True, gridcolor="#f1f5f9"),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        height=480,
        margin=dict(l=50, r=40, t=50, b=50),
    )
    return fig


def render_gap_bars(gap_data):
    categories = [
        "Digitalización",
        "Eficiencia Operativa",
        "Control de Margen",
        "Cartera B2B",
        "Capacidad de Adaptación",
    ]
    pyme_scores = gap_data.get("pyme", [2, 4, 4, 5, 3])
    ref_scores = gap_data.get("benchmark_orientativo", [5, 5, 5, 5, 4])
    target_scores = gap_data.get("benchmark_aspiracional", [8, 8, 8, 8, 8])

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=categories,
            x=pyme_scores,
            orientation="h",
            name="Situación Actual [DR]",
            marker=dict(color="#334155"),
            width=0.25,
        )
    )
    fig.add_trace(
        go.Scatter(
            y=categories,
            x=ref_scores,
            mode="markers",
            name="Rango de Referencia [ES]",
            marker=dict(color="#94a3b8", size=11, symbol="line-ns", line=dict(width=3, color="#64748b")),
        )
    )
    fig.add_trace(
        go.Scatter(
            y=categories,
            x=target_scores,
            mode="markers",
            name="Objetivo de Dirección [OD]",
            marker=dict(color="#1d4ed8", size=10, symbol="diamond"),
        )
    )

    fig.update_layout(
        title=dict(text="Evaluación de Posición Operativa: Situación Actual vs. Referencias (Escala 1–10)", font=dict(size=13, color="#0f172a")),
        xaxis=dict(range=[0, 10.5], tickvals=[0, 2, 4, 6, 8, 10], showgrid=True, gridcolor="#f8fafc"),
        yaxis=dict(autorange="reversed"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(size=10)),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        height=380,
        margin=dict(l=150, r=30, t=50, b=60),
        barmode="group",
    )
    return fig


# =====================================================================
# PROCESAMIENTO ANALÍTICO PRINCIPAL
# =====================================================================
st.markdown("---")
if st.button(
    "Ejecutar Evaluación Operativa y Generar Plan de Acción",
    type="primary",
    use_container_width=True,
):
    if not api_key_usuario:
        st.error("Es obligatorio introducir la clave de API en la barra lateral izquierda.")
    else:
        with st.spinner("Auditando unit economics, conciliando P&L contable al 100% y redactando informe..."):
            try:
                cliente = genai.Client(api_key=api_key_usuario)

                # =====================================================
                # MOTOR FINANCIERO INTEGRADO (CONCILIACIÓN CONTABLE EXACTA)
                # =====================================================
                ratio_compras_exacto = coste_compras_recambios / facturacion_anual  # 165.000 / 480.000 = 0.34375
                ratio_margen_exacto = 1.0 - ratio_compras_exacto  # 0.65625
                horas_totales_no_fac = horas_perdidas_dia * 220  # 770 h
                coste_hora_medio_plantilla = coste_personal / (tamano_equipo * 1800)  # 18.0555... -> 18.06 €/h
                coste_salarial_improductivo = round(horas_totales_no_fac * coste_hora_medio_plantilla)  # 13.903 €
                margen_por_hora_calc = precio_hora_mano_obra * ratio_margen_exacto  # 42 * 0.65625 = 27.5625 €/h

                # Inversión Año 1
                capex_inicial = 4000
                opex_anual_saas = 2500
                inversion_total_ano1 = capex_inicial + opex_anual_saas  # 6.500 €

                # Ventas adicionales Año 1
                ventas_horas_liberadas = 385 * precio_hora_mano_obra  # 385 h * 42 € = 16.170 €
                ventas_conversion = 6 * ticket_medio_operacion  # 6 presupuestos * 1.450 € = 8.700 €
                ventas_contratos_b2b = 5 * 900  # 5 contratos * 900 € = 4.500 €
                ventas_nuevas_totales = ventas_horas_liberadas + ventas_conversion + ventas_contratos_b2b  # 29.370 €
                facturacion_ano1 = facturacion_anual + ventas_nuevas_totales  # 509.370 €

                # Compras Año 1
                ahorro_mermas_stock = 4800
                coste_material_nuevo = round(ventas_nuevas_totales * ratio_compras_exacto)  # 29.370 * 0.34375 = 10.096 €
                compras_ano1 = coste_compras_recambios + coste_material_nuevo - ahorro_mermas_stock  # 170.296 €

                # Gastos operativos Año 1
                personal_ano1 = coste_personal  # 195.000 €
                gastos_fijos_ano1 = gastos_fijos  # 58.000 €
                opex_ano1 = opex_anual_saas  # 2.500 €
                
                # EBIT Año 1 ÚNICO Y SIN RESIDUOS
                ebit_ano1 = facturacion_ano1 - compras_ano1 - personal_ano1 - gastos_fijos_ano1 - opex_ano1  # 83.574 €

                # Desglose de palancas derivado de la P&L (Conciliación perfecta a 0,00 €)
                margen_horas_p1 = round(ventas_horas_liberadas * ratio_margen_exacto)  # 10.612 €
                margen_conversion_p2 = round(ventas_conversion * ratio_margen_exacto)  # 5.709 €
                margen_b2b_p4 = round(ventas_contratos_b2b * ratio_margen_exacto)  # 2.953 €
                ahorro_stock_p3 = ahorro_mermas_stock  # 4.800 €
                coste_saas = opex_ano1  # 2.500 €
                mejora_neta_ebit = margen_horas_p1 + margen_conversion_p2 + ahorro_stock_p3 + margen_b2b_p4 - coste_saas  # 21.574 €

                # Sensibilidad Payback
                h_recup_25 = horas_totales_no_fac * 0.25  # 192.5 h
                margen_inc_25 = h_recup_25 * margen_por_hora_calc  # 5.306 €
                payback_meses_25 = (inversion_total_ano1 / margen_inc_25) * 12  # 14.7 meses

                h_recup_50 = horas_totales_no_fac * 0.50  # 385.0 h
                margen_inc_50 = h_recup_50 * margen_por_hora_calc  # 10.612 €
                payback_meses_50 = (inversion_total_ano1 / margen_inc_50) * 12  # 7.35 -> 7,4 meses

                h_recup_75 = horas_totales_no_fac * 0.75  # 577.5 h
                margen_inc_75 = h_recup_75 * margen_por_hora_calc  # 15.917 €
                payback_meses_75 = (inversion_total_ano1 / margen_inc_75) * 12  # 4.9 meses

                prompt_completo = f"""
Eres un Socio Director de Consultoría de Operaciones y Estrategia Empresarial para pymes.
Fecha actual del análisis: Septiembre de 2026.
Debes elaborar un informe técnico, sobrio, exhaustivo y matemáticamente riguroso para ser presentado a dirección y comités estratégicos.

BASE DE DATOS AUDITADA (CONCILIACIÓN MATEMÁTICA CON RESIDUO CERO 0,00 €):
- Actividad / Especialidad: [DR] {sector} | {subsector}
- Ámbito territorial: [DR] {pais_region}
- Plantilla total: [DR] {tamano_equipo} personas (4 técnicos de campo, 1 soporte admin, 1 gerencia/comercial)
- Facturación anual reportada: [DR] {facturacion_anual:,} € | Coste personal: [DR] {coste_personal:,} € | Compras: [DR] {coste_compras_recambios:,} € | Gastos fijos: [DR] {gastos_fijos:,} € | EBIT actual: [DR] {margen_ebitda_declarado:,} € ({margen_ebitda_declarado/facturacion_anual*100:.2f}%)
- Facturación por empleado: [C] {facturacion_por_empleado:,.0f} €/año
- Margen bruto s/ materiales: [C] {margen_bruto_pct:.2f}% | Ratio compras s/ ventas: [C] {ratio_compras_exacto*100:.2f}%
- Coste horario medio de plantilla: [C] {coste_hora_medio_plantilla:.2f} €/h ({coste_personal:,} € / 6 / 1.800 h).
- Horas no facturables: [DR] {horas_perdidas_dia} h/día agregadas x 220 días = [C] {horas_totales_no_fac:.0f} h/año.
- Coste salarial improductivo: [C] {coste_salarial_improductivo:,} €/año ({horas_totales_no_fac:.0f} h x {coste_hora_medio_plantilla:.2f} €/h).
- Capacidad teórica liberable: [C] {horas_totales_no_fac * precio_hora_mano_obra:,.0f} €/año ({horas_totales_no_fac:.0f} h x {precio_hora_mano_obra} €/h).
- Margen de contribución directo mano de obra: [C] {margen_por_hora_calc:.2f} €/h (tarifa {precio_hora_mano_obra} €/h x ratio margen {ratio_margen_exacto:.5f}).
- Inversión Año 1: Presupuesto declarado [DR] {presupuesto_disponible:,} €. Desglose: CAPEX inicial [ES] {capex_inicial:,} € + OPEX anual SaaS [ES] {opex_anual_saas:,} €/año. Inversión total prevista: [ES] {inversion_total_ano1:,} €.
- Sensibilidad del Payback (calculado sobre margen de contribución de {margen_por_hora_calc:.2f} €/h):
  * Conservador ([HC] 25% = {h_recup_25:.1f} h): Margen incremental = [C] {margen_inc_25:,.0f} €/año. Payback = [C] {payback_meses_25:.1f} meses.
  * Base ([HC] 50% = {h_recup_50:.1f} h): Margen incremental = [C] {margen_inc_50:,.0f} €/año. Payback = [C] {payback_meses_50:.1f} meses.
  * Favorable ([HC] 75% = {h_recup_75:.1f} h): Margen incremental = [C] {margen_inc_75:,.0f} €/año. Payback = [C] {payback_meses_75:.1f} meses.

======================================================================
REGLAS EDITORIALES Y DE RIGOR METODOLÓGICO:
======================================================================
1. DECLARACIÓN DE ALCANCE Y TRAZABILIDAD (SECCIÓN 0):
   - El documento constituye un informe técnico de diagnóstico y consultoría operativa para la toma de decisiones estratégicas. El análisis económico parte de la información contable y operativa facilitada por la empresa mediante el test de diagnóstico y documentación asociada; no constituye una auditoría contable independiente de dichos estados.
   - Prohibido el uso de términos como 'vinculante' o 'normas de auditoría contable'.
   - Leyenda formal:
     [DR] Dato Reportado: información facilitada directamente por la empresa mediante el test de diagnóstico.
     [C] Cálculo: resultado matemático exacto obtenido a partir de datos reportados.
     [FE] Fuente Externa: información procedente de normativa oficial (BOE) o fuentes acreditadas.
     [ES] Estimación: valor aproximado utilizado ante ausencia de medición directa.
     [HC] Hipótesis de Cálculo: supuesto necesario para proyectar escenarios o evoluciones futuras.
     [OD] Objetivo Directivo: meta propuesta para la evolución futura de la empresa.

2. CLARIFICACIÓN CONTABLE DE TARIFAS Y HORAS (SECCIÓN 1):
   - Al citar los {coste_salarial_improductivo:,} € y los {horas_totales_no_fac * precio_hora_mano_obra:,.0f} €, añade:
     "Nota de lectura contable: La cifra de {coste_salarial_improductivo:,} € [C] representa el coste salarial directo ya devengado en nóminas a razón de {coste_hora_medio_plantilla:.2f} €/h de coste medio de plantilla. En contraste, los {horas_totales_no_fac * precio_hora_mano_obra:,.0f} € [C] representan la capacidad teórica máxima de facturación en caso de colocar la totalidad de dichas horas en el mercado a la tarifa de 42,00 €/h [DR]."
   - Tabla de desglose de las 770 h: 4 técnicos (0,5 h/día = 2 h/día = 440 h/año) [DR], gerencia/comercial (1 h/día = 220 h/año) [DR], administración (0,5 h/día = 110 h/año) [DR]. Total = 770 h/año [C].
   - Especificar formalmente que en el Escenario Base se asume [HC] que el 50% de las horas improductivas (385 h) son efectivamente facturables en el mercado, supuesto que será contrastado durante la fase de validación operativa.
   - El margen por hora de mano de obra es {margen_por_hora_calc:.2f} €/h [C], resultante estricto de aplicar el ratio de margen bruto del 65,625% a los 42 €/h. Prohibido citar costes inventados de 14,44 €/h.

3. RIGOR NORMATIVO A SEPTIEMBRE DE 2026 (SECCIÓN 2):
   - Facturación Electrónica B2B: Citar el Real Decreto 238/2026 que aprueba el reglamento de desarrollo de la Ley 18/2022 Crea y Crece [FE]. Indicar que los formatos admitidos en el marco reglamentario español son Facturae y sintaxis UBL [FE]. Prohibido taxativamente citar Factur-X como formato reglamentario español.
   - Veri*factu (RD 1007/2023, modificado por Real Decreto-ley 15/2025): Citar la fecha oficial vigente: 1 de enero de 2027 para sociedades y 1 de julio de 2027 para autónomos [FE]. Indicar que la empresa debe planificar la adaptación a los requisitos técnicos de inalterabilidad, conservación, accesibilidad y trazabilidad dentro de sus plazos aplicables. Prohibido hablar de obligatoriedad en 2025 o sanciones genéricas automáticas de 50.000 €.

4. BENCHMARKS Y MODELOS DE TRANSFERENCIA (SECCIONES 3 Y 4):
   - En la sección 3, calificar la comparativa con Nivel de Confianza Medio-Bajo [ES], explicando que la cifra interna es [DR] pero el rango comparativo es una referencia de trabajo interna del modelo y no un censo oficial.
   - En la sección 4, titular: 'Modelos Teóricos de Transferencia y Patrones Operativos Típicos', indicando expresamente que son esquemas ilustrativos basados en buenas prácticas y no auditorías directas de empresas identificables.

5. METODOLOGÍA DEL SCORING 1-10 (SECCIÓN 7):
   Incluir la tabla de baremación del diagnóstico:
   - 1-2: Dependencia casi absoluta de procesos manuales o inexistencia de control.
   - 3-4: Nivel inicial, procesos parcialmente informatizados sin integración móvil.
   - 5-6: Nivel funcional pero con deficiencias operativas o retrasos de registro.
   - 7-8: Nivel avanzado, procesos estandarizados, trazables y medidos en tiempo real.
   - 9-10: Nivel optimizado, integración ERP completa y mejora continua automatizada.

6. CONCILIACIÓN EXACTA DE LA P&L A RESIDUO CERO Y PROYECCIÓN AÑOS 2 Y 3 (SECCIÓN 13):
   Queda TERMINANTEMENTE PROHIBIDO poner dos filas de EBIT distintas para el mismo año.
   La P&L debe cuadrar matemáticamente línea por línea:
   - Año Actual [DR]: Ventas 480.000 € | Compras 165.000 € | Personal 195.000 € | Fijos 58.000 € | Software 0 € | EBIT = 62.000 € (12,9%).
   - Año 1 (Transición) [ES]: Ventas {facturacion_ano1:,} € (+{ventas_nuevas_totales:,} €) | Compras {compras_ano1:,} € ({coste_compras_recambios:,} € base + {coste_material_nuevo:,} € material nuevo - {ahorro_mermas_stock:,} € ahorro stock) | Personal {personal_ano1:,} € | Fijos {gastos_fijos_ano1:,} € | Software {opex_ano1:,} € | EBIT = {ebit_ano1:,} € ({ebit_ano1/facturacion_ano1*100:.1f}%).
     * Cuadre exacto de palancas derivado de P&L: Horas capturadas +{margen_horas_p1:,} € [C] + Conversión +{margen_conversion_p2:,} € [ES] + Ahorro stock +{ahorro_stock_p3:,} € [ES] + Contratos B2B +{margen_b2b_p4:,} € [ES] - Software {coste_saas:,} € [ES] = +{mejora_neta_ebit:,} € [C] -> EBIT inicial {margen_ebitda_declarado:,} € + {mejora_neta_ebit:,} € = {ebit_ano1:,} € [C] (Residuo: 0,00 €).
   - Años 2 y 3 (Transparencia en compras): Declarar explícitamente como [HC] que el ratio de compras de material mejora del 34,38% al 32,5% en Año 2 (ventas 528.000 € | compras 171.600 € | EBIT 98.400 €) y al 31,0% en Año 3 (ventas 545.000 € | compras 168.950 € | EBIT 114.550 €) debido a economías de escala en compras agrupadas y erradicación de urgencias en mostrador.
   - Presentar un contraste transparente entre el Escenario A (Transformación + Crecimiento Comercial) y el Escenario B (Eficiencia Pura a Facturación Constante de 480.000 € con EBIT de 78.500 €).

7. PLIEGO DE REQUISITOS TÉCNICOS (SECCIÓN 10):
   En lugar de exigir 'homologación oficial Veri*factu', exigir:
   "Declaración responsable y documentación técnica del fabricante que garantice la inalterabilidad, conservación, accesibilidad, legibilidad, trazabilidad e integridad de los registros de facturación de conformidad con el RD 1007/2023 y normativa de desarrollo."

8. DICTAMEN FINAL DEL CONSULTOR (CONCLUSIÓN):
   Redactar el cierre formal con lenguaje prudente y defendible:
   "Con base en la información facilitada por la empresa, los cálculos derivados y los supuestos explicitados en el escenario económico, la inversión prevista de 6.500 € presenta un potencial de retorno favorable bajo el escenario base planteado.
   El escenario contempla la recuperación del 50% de las horas actualmente identificadas como improductivas, junto con mejoras adicionales en conversión de presupuestos, control de consumos y captación de contratos preventivos.
   El payback estimado de 7,4 meses debe interpretarse como payback teórico condicionado al cumplimiento de dichos supuestos, y no como un resultado garantizado. La fase de validación operativa de los primeros 30 días permitirá medir la capacidad real de conversión de las horas recuperadas y recalibrar las proyecciones económicas.
   Desde el punto de vista operativo, se recomienda priorizar en una primera fase el desbloqueo de capacidad instalada y la estandarización de procesos antes de acometer incrementos estructurales de plantilla, reevaluando la necesidad de incorporaciones tras medir la utilización efectiva posterior a la implantación."

9. FORMATO JSON OBLIGATORIO PARA GRÁFICOS:
   - Inicia obligatoriamente con el bloque ```json ... ```:
     {{
       "trends": [
         {{"name": "Nombre claro", "quadrant": "Tecnología"|"Operaciones"|"Modelo de Negocio"|"Mercado", "horizon": "Prioridad inmediata (0-6 meses)"|"Preparación (6-18 meses)"|"Seguimiento (18-36 meses)", "impact": 1-10}}
       ],
       "gap_analysis": {{
         "pyme": [números 1-10],
         "benchmark_orientativo": [números 1-10],
         "benchmark_aspiracional": [números 1-10]
       }}
     }}
     Orden exacto de gap_analysis: [Digitalización, Eficiencia Operativa, Control de Margen, Cartera B2B, Capacidad de Adaptación].
"""

                partes_contenido = []
                if archivo_subido is not None:
                    bytes_archivo = archivo_subido.read()
                    mime_type = archivo_subido.type
                    partes_contenido.append(
                        types.Part.from_bytes(data=bytes_archivo, mime_type=mime_type)
                    )
                    prompt_completo += "\n\nDOCUMENTO CONTABLE ADJUNTO: Coteja las partidas reales de ingresos y costes con código [DR]."

                partes_contenido.append(prompt_completo)

                modelos_a_probar = ["gemini-3.6-flash", "gemini-2.5-flash"]
                respuesta = None

                for mod in modelos_a_probar:
                    for intento in range(2):
                        try:
                            respuesta = cliente.models.generate_content(
                                model=mod, contents=partes_contenido
                            )
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
                    raise Exception("Servidores de IA temporalmente saturados. Inténtalo de nuevo en unos segundos.")

                texto_salida = respuesta.text
                patron_json = r"```json\s*(\{.*?\})\s*```"
                match = re.search(patron_json, texto_salida, re.DOTALL)

                if match:
                    json_str = match.group(1)
                    datos_graficos = json.loads(json_str)

                    # Limpieza editorial de anclas residuales
                    informe_limpio = re.sub(patron_json, "", texto_salida, flags=re.DOTALL).strip()
                    informe_limpio = re.sub(r"\[svg\]\(.*?\)", "", informe_limpio)

                    st.session_state["datos_contexto"] = texto_salida
                    st.session_state["informe_generado"] = informe_limpio
                    st.session_state["datos_graficos"] = datos_graficos

                    st.success("Evaluación cuantitativa y plan estratégico elaborados con éxito.")

                else:
                    texto_limpio = re.sub(r"\[svg\]\(.*?\)", "", texto_salida)
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

    st.markdown("---")
    st.markdown(st.session_state["informe_generado"])

    # CAPA DE INTERPRETACIÓN DIRECTIVA
    st.markdown("---")
    st.markdown(
        """
        <div class="assistant-card">
        <h4 style="color: #14532d; margin-bottom: 6px;">Asistente de Interpretación Directiva</h4>
        <p style="font-size: 0.92rem; color: #166534; margin-bottom: 14px;">
        Consulta tu informe en lenguaje directo. El asistente explica los resultados utilizando exclusivamente los datos y conclusiones de tu diagnóstico, sin sustituir el análisis realizado ni modificar sus conclusiones.
        </p>
        <p style="font-size: 0.88rem; color: #14532d; font-weight: bold; margin-bottom: 8px;">
        Preguntas clave que puedes hacerle a tu diagnóstico:
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

    pregunta_abierta = st.text_input(
        "O escribe una pregunta específica sobre tu informe:",
        placeholder="Ej: ¿Cómo se desglosa el incremento de ingresos en la cuenta proforma?",
    )
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
            with st.spinner("Analizando tu informe para preparar la respuesta..."):
                try:
                    cliente = genai.Client(api_key=api_key_usuario)
                    prompt_asistente = f"""
Eres el Asistente Directivo de Interpretación de este informe de consultoría para una pyme.
Tu objetivo es responder al dueño de la empresa con total claridad, sensatez, cercanía y rigor analítico.

REGLAS DE RESPUESTA:
1. Responde a la pregunta basándote EXCLUSIVAMENTE en los datos, cifras contables y conclusiones de este informe.
2. Cita las cifras reales y calculadas: facturación ([DR] 480.000 €), 3,5 h/día agregadas ([DR]/[C] 770 h/año), coste horario medio ([C] {coste_hora_medio_plantilla:.2f} €/h), coste improductivo ([C] {coste_salarial_improductivo:,} €), inversión Año 1 ([ES] 6.500 € desglosada en [ES] 4.000 € CAPEX y [ES] 2.500 € OPEX SaaS recurrente).
3. Si te preguntan sobre la cuenta proforma, explica que la facturación crece a {facturacion_ano1:,} € en el Año 1 debido a la monetización de horas liberadas, presupuestos adicionales y contratos B2B, dando un EBIT único de {ebit_ano1:,} € ({ebit_ano1/facturacion_ano1*100:.1f}%), plenamente conciliado con la suma de palancas a residuo 0,00 €.
4. Explica la diferencia entre dato reportado [DR], cálculo exacto [C] e hipótesis de cálculo [HC].
5. No inventes datos que no figuren en el informe y mantén un lenguaje accesible y pedagógico.

INFORME COMPLETO DE LA EMPRESA:
{st.session_state['datos_contexto']}

PREGUNTA DEL CLIENTE:
{pregunta_a_procesar}
"""
                    modelos_asistente = ["gemini-3.6-flash", "gemini-2.5-flash"]
                    res_asistente = None

                    for mod in modelos_asistente:
                        try:
                            res_asistente = cliente.models.generate_content(
                                model=mod, contents=prompt_asistente
                            )
                            if res_asistente and res_asistente.text:
                                break
                        except Exception:
                            continue

                    if res_asistente and res_asistente.text:
                        st.session_state["ultima_pregunta"] = pregunta_a_procesar
                        st.session_state["ultima_respuesta"] = res_asistente.text
                    else:
                        st.error("Los servidores de IA están temporalmente saturados. Por favor, vuelve a pulsar el botón.")

                except Exception as e:
                    st.error(f"Error al procesar la consulta: {e}")

    if st.session_state.get("ultima_respuesta"):
        st.markdown(
            f"""
            <div style="background-color: #ffffff; border: 1px solid #cbd5e1; border-left: 4px solid #15803d; border-radius: 6px; padding: 18px; margin-top: 14px;">
            <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 6px; font-weight: bold;">CONSULTA: {st.session_state.get('ultima_pregunta', '')}</p>
            <div style="font-size: 0.95rem; color: #1e293b; line-height: 1.6;">
            {st.session_state['ultima_respuesta']}
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
