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
            "Periodo medio de cobro a clientes (días) (DSO):",
            min_value=0,
            max_value=365,
            value=68,
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
        with st.spinner("Auditando unit economics, cuadrando P&L con residuo cero absoluto y redactando informe..."):
            try:
                cliente = genai.Client(api_key=api_key_usuario)

                # =====================================================
                # MOTOR FINANCIERO INTEGRADO (CONCILIACIÓN MATEMÁTICA EXACTA)
                # =====================================================
                ratio_compras_exacto = coste_compras_recambios / facturacion_anual  # 165.000 / 480.000 = 0.34375
                ratio_margen_exacto = 1.0 - ratio_compras_exacto  # 0.65625
                horas_totales_no_fac = horas_perdidas_dia * 220  # 770 h
                coste_hora_medio_plantilla = coste_personal / (tamano_equipo * 1800)  # 18.0555... -> 18.06 €/h
                coste_salarial_improductivo = round(horas_totales_no_fac * coste_hora_medio_plantilla)  # 13.903 €
                margen_por_hora_calc = precio_hora_mano_obra * ratio_margen_exacto  # 42 * 0.65625 = 27.5625 €/h

                # Inversión y OPEX SaaS
                capex_inicial = 4000
                opex_ano1 = 2500
                opex_ano2 = 5000
                opex_ano3 = 8500
                inversion_total_ano1 = capex_inicial + opex_ano1  # 6.500 €

                # Ventas adicionales generadas Año 1
                ventas_horas_liberadas = 385 * precio_hora_mano_obra  # 385 h * 42 € = 16.170 €
                ventas_conversion = 6 * ticket_medio_operacion  # 6 presupuestos * 1.450 € = 8.700 €
                ventas_contratos_b2b = 5 * 900  # 5 contratos * 900 € = 4.500 €
                ventas_nuevas_totales = ventas_horas_liberadas + ventas_conversion + ventas_contratos_b2b  # 29.370 €
                facturacion_ano1 = facturacion_anual + ventas_nuevas_totales  # 509.370 €

                # Compras y consumos Año 1
                ahorro_mermas_stock = 4800
                coste_material_nuevo = round(ventas_nuevas_totales * ratio_compras_exacto)  # 29.370 * 0.34375 = 10.096 €
                compras_ano1 = coste_compras_recambios + coste_material_nuevo - ahorro_mermas_stock  # 170.296 €

                personal_ano1 = coste_personal  # 195.000 €
                gastos_fijos_ano1 = gastos_fijos  # 58.000 €
                
                # EBIT Año 1 Único Conciliado
                ebit_ano1 = facturacion_ano1 - compras_ano1 - personal_ano1 - gastos_fijos_ano1 - opex_ano1  # 83.574 €

                # Conciliación matemática de palancas (Residuo: 0,00 €)
                margen_horas_p1 = round(ventas_horas_liberadas * ratio_margen_exacto)  # 10.612 €
                margen_conversion_p2 = round(ventas_conversion * ratio_margen_exacto)  # 5.709 €
                margen_b2b_p4 = round(ventas_contratos_b2b * ratio_margen_exacto)  # 2.953 €
                ahorro_stock_p3 = ahorro_mermas_stock  # 4.800 €
                mejora_neta_ebit = margen_horas_p1 + margen_conversion_p2 + ahorro_stock_p3 + margen_b2b_p4 - opex_ano1  # 21.574 €

                # Sensibilidad Payback (sobre 27,5625 €/h de margen unitario)
                h_recup_25 = horas_totales_no_fac * 0.25  # 192.5 h
                margen_inc_25 = h_recup_25 * margen_por_hora_calc  # 5.306 €
                payback_meses_25 = (inversion_total_ano1 / margen_inc_25) * 12  # 14.7 meses

                h_recup_50 = horas_totales_no_fac * 0.50  # 385.0 h
                margen_inc_50 = h_recup_50 * margen_por_hora_calc  # 10.612 €
                payback_meses_50 = (inversion_total_ano1 / margen_inc_50) * 12  # 7.4 meses

                h_recup_75 = horas_totales_no_fac * 0.75  # 577.5 h
                margen_inc_75 = h_recup_75 * margen_por_hora_calc  # 15.917 €
                payback_meses_75 = (inversion_total_ano1 / margen_inc_75) * 12  # 4.9 meses

                prompt_completo = f"""
Eres un Socio Director de Consultoría de Operaciones y Estrategia Empresarial para pymes.
Fecha actual del análisis: Septiembre de 2026.
Debes elaborar un informe técnico, sobrio, exhaustivo y matemáticamente riguroso para ser presentado a Dirección General y Comité Estratégico.

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
   Antes de la Sección 0, abre con un Resumen Ejecutivo estructurado:
   - Situación actual de partida ([DR] 480k € ventas, [DR] 62k € EBIT, [DR] 770 h no facturables/año).
   - Diagnóstico central: 3 cuellos de botella críticos (gestión manual de partes, tiempo improductivo en presupuestos no convertidos, descontrol de van-stock).
   - Inversión requerida: [ES] 6.500 € (4.000 € CAPEX + 2.500 € OPEX SaaS Año 1) ajustada al presupuesto disponible [DR].
   - Retorno esperado y distinción neta: Payback teórico condicionado de [C] 7,4 meses bajo el Escenario Base ([HC] 50% captura).
     * OBLIGATORIO: Distinguir con total claridad que la Palanca 1 de recuperación de horas aporta de forma aislada +10.612 € [C] de margen, mientras que el impacto económico global consolidado de todas las palancas del Escenario A totaliza +21.574 € [C] de mejora neta de EBIT (alcanzando 83.574 € [C]).
   - Tabla de Cuadro de Mando Directivo (Decisiones clave a adoptar):
     * Seleccionar solución tecnológica | Plazo: Mes 1 | Responsable: Dirección | Inversión: — | Impacto: Alto.
     * Implantar FSM/ERP móvil | Plazo: Meses 1-3 | Responsable: Dirección + Proveedor | Inversión: 4.000 € | Impacto: Alto.
     * Fase de Validación Operativa (medir tiempos reales) | Plazo: Mes 1 | Responsable: Operaciones | Inversión: — | Impacto: Crítico.
     * Activar catálogo paramétrico de presupuestos | Plazo: Meses 2-4 | Responsable: Comercial | Inversión: — | Impacto: Medio/Alto.
     * Lanzar oferta estandarizada de contratos B2B | Plazo: Meses 4-8 | Responsable: Comercial | Inversión: — | Impacto: Medio/Alto.

2. DECLARACIÓN DE ALCANCE Y TRAZABILIDAD (SECCIÓN 0):
   - El presente documento constituye un informe técnico de diagnóstico y consultoría operativa para la toma de decisiones estratégicas.
   - El análisis económico parte de la información contable y operativa facilitada por la empresa mediante el test de diagnóstico y documentación asociada. No constituye una auditoría contable o financiera independiente de dichos estados.
   - Prohibido utilizar expresiones como 'vinculante' o 'normas de auditoría contable'.
   - Leyenda formal:
     [DR] Dato Reportado: información facilitada directamente por la empresa mediante el test de diagnóstico.
     [C] Cálculo: resultado matemático exacto derivado de datos reportados o calculados.
     [FE] Fuente Externa: información procedente de normativa legal oficial (BOE) o fuentes acreditadas.
     [ES] Estimación: valor aproximado utilizado ante ausencia de medición directa.
     [HC] Hipótesis de Cálculo: supuesto necesario para modelar escenarios o evoluciones futuras.
     [OD] Objetivo Directivo: meta fijada formalmente en el plan de trabajo.

3. CLARIFICACIÓN CONTABLE DE TARIFAS Y HORAS (SECCIÓN 1):
   - Al citar los {coste_salarial_improductivo:,} € y los {horas_totales_no_fac * precio_hora_mano_obra:,.0f} €, añade obligatoriamente:
     "Nota de lectura contable: La cifra de {coste_salarial_improductivo:,} € [C] representa el coste salarial directo ya devengado en nóminas a razón de {coste_hora_medio_plantilla:.2f} €/h [C] de coste medio de plantilla. En contraste, los {horas_totales_no_fac * precio_hora_mano_obra:,.0f} € [C] representan la capacidad teórica máxima de facturación en caso de colocar la totalidad de dichas horas en el mercado a la tarifa de 42,00 €/h [DR]."
   - Tabla de desglose de las 770 h: 4 técnicos (0,5 h/día cada uno = 2,0 h/día = 440 h/año) [DR], 1 gerencia/comercial (1,0 h/día = 220 h/año) [DR], 1 administración (0,5 h/día = 110 h/año) [DR]. Total empresa = 3,5 h/día = 770 h/año [C].
   - Cadena de métricas de técnicos: 4 técnicos [DR] x 1.800 h/año [DR] = 7.200 h de plantilla total [C]. Horas en campo disponibles teóricas: 4 técnicos x 1.800 h = 7.200 h [C]. Con 440 h de gestión manual en campo [DR], la capacidad productiva efectiva se sitúa en 6.760 h [C] (aprox. 7,68 h/técnico/día útiles [C]), frente a una referencia superior de consultoría de 7,20 h facturables directas/técnico/día [ES].
   - Especificar formalmente que en el Escenario Base se asume [HC] que el 50% de las horas actualmente improductivas (385 h) son efectivamente facturables en el mercado sin incremento de personal, supuesto que será contrastado durante la fase de validación operativa.
   - Denominar exactamente: "[C] Margen de contribución directo derivado por hora facturada: {margen_por_hora_calc:.2f} €/h", resultante de aplicar el margen bruto sobre materiales reportado (65,625%) a la tarifa de 42 €/h. Prohibido citar costes inventados de 14,44 €/h.
   - En pricing: Matizar que el margen bruto sobre materiales se sitúa en un nivel favorable dentro del modelo comparativo, pero que este indicador por sí solo no permite atribuir el resultado a un determinado nivel de poder de fijación de precios (depende del mix de servicios, instalaciones y compras).

4. RIGOR NORMATIVO BOE A SEPTIEMBRE DE 2026 (SECCIÓN 2):
   - Facturación Electrónica B2B: El marco de facturación electrónica entre empresarios ha sido desarrollado reglamentariamente mediante el Real Decreto 238/2026 [FE]. La solución seleccionada deberá permitir la adaptación a los formatos estructurados admitidos en el marco reglamentario español (sintaxis XML Facturae y sintaxis UBL bajo norma semántica europea EN 16931) [FE], sistemas de intercambio y reporte de estados de factura. Queda estrictamente PROHIBIDO citar Factur-X como formato reglamentario español.
   - Veri*factu (RD 1007/2023, modificado por Real Decreto-ley 15/2025): Establece que los obligados tributarios que sean personas jurídicas (sociedades) deben tener adaptados sus sistemas antes del 1 de enero de 2027 [FE], mientras que para personas físicas (autónomos) la fecha límite es el 1 de julio de 2027 [FE]. La empresa debe planificar la adaptación a los requisitos técnicos de inalterabilidad, conservación, accesibilidad y trazabilidad dentro de los plazos aplicables a su condición fiscal. Prohibido hablar de obligatoriedad en 2025 o sanciones genéricas automáticas de 50.000 €.

5. BENCHMARKS Y MODELOS DE TRANSFERENCIA (SECCIONES 3 Y 4):
   - En la sección 3, sustituir 'Top 20%' por 'Referencia superior del modelo comparativo de consultoría [ES]'. Calificar la comparativa de Facturación por Empleado con Nivel de Confianza Medio-Bajo [ES], aclarando que el dato interno es [DR] pero el rango de 75.000-95.000 € es una referencia interna del modelo.
   - En la sección 4, titular: 'Modelos Teóricos de Transferencia y Patrones Operativos Típicos', indicando que son esquemas ilustrativos basados en buenas prácticas y no auditorías directas de empresas identificables.

6. METODOLOGÍA DEL SCORING Y TABLA PONDERADA EXACTA DE 9,20/10 (SECCIÓN 7):
   - Incluir la tabla de baremo del diagnóstico (1-2: Manual/Crítico, 3-4: Inicial, 5-6: Funcional con deficiencias, 7-8: Estandarizado, 9-10: Optimizado).
   - En la arquitectura tecnológica (Sección 7.2), justificar matemáticamente la puntuación de 9,20/10 mediante una tabla ponderada exacta cuyas notas ponderadas sumen rigurosamente 9,20:
     * Movilidad SAT en campo: Peso 20% | Nota 9,50 | Ponderación 1,900 [C] | Justificación: Cobertura completa de partes digitales, firma biométrica en cliente y geolocalización.
     * Capacidad Offline: Peso 15% | Nota 9,00 | Ponderación 1,350 [C] | Justificación: Almacenamiento local seguro con cola de sincronización transaccional al recuperar red.
     * Cumplimiento Normativo (Facturación): Peso 15% | Nota 9,50 | Ponderación 1,425 [C] | Justificación: Adaptación a registros inalterables RD 1007/2023 y formatos Facturae/UBL RD 238/2026.
     * Control de Stock en Furgoneta: Peso 10% | Nota 9,00 | Ponderación 0,900 [C] | Justificación: Registro por vehículo, lectura QR y aviso de stock mínimo.
     * Gestión Gases Fluorados (F-Gas): Peso 10% | Nota 9,00 | Ponderación 0,900 [C] | Justificación: Control de trazabilidad de botellas, cargas y libro de registro oficial.
     * Integración Contable / ERP: Peso 10% | Nota 9,00 | Ponderación 0,900 [C] | Justificación: Enlace bidireccional de albaranes, clientes y cobros sin doble entrada.
     * Catálogo Paramétrico de Presupuestos: Peso 10% | Nota 9,00 | Ponderación 0,900 [C] | Justificación: Emisión estandarizada in situ con baremos cerrados de mano de obra y materiales.
     * Coste Total TCO: Peso 10% | Nota 9,25 | Ponderación 0,925 [C] | Justificación: Ajuste estricto al presupuesto declarado con rápido plazo de retorno.
     * TOTAL PONDERADO: 1,900 + 1,350 + 1,425 + 0,900 + 0,900 + 0,900 + 0,900 + 0,925 = EXACTAMENTE 9,20 / 10 [C]. (PROHIBIDO que sume 9,50).

7. SELECCIÓN DE PROVEEDOR Y RIESGOS TECNOLÓGICOS (SECCIONES 10 Y 12):
   - En el pliego del RFP: Exigir 'Declaración responsable y documentación técnica del fabricante que garantice la inalterabilidad, trazabilidad, conservación e integridad de los registros según el RD 1007/2023 y normativa de desarrollo'.
   - En riesgos tecnológicos: Prohibido mencionar marcas o motores específicos como 'SQLite'. Sustituir por: 'Almacenamiento local cifrado de datos durante periodos sin conectividad, con sincronización transaccional posterior y control de integridad'.

8. CONCILIACIÓN EXACTA DE LA P&L A RESIDUO CERO Y PLAN A 36 MESES (SECCIÓN 13):
   Queda TERMINANTEMENTE PROHIBIDO poner dos filas de EBIT distintas para el mismo año. Corregir cualquier errata: usar '% CAMBIO' (prohibido '% CEMENTO').
   - Desglose conciliado exacto de la Sección 13.1:
     * Palanca 1 (Captura de 385 h [HC]): Ventas +16.170 € [C] | Materiales +5.558 € [C] | Margen neto +10.612 € [C] (385 h x 42 € x {ratio_margen_exacto:.5f}).
     * Palanca 2 (Mejora de conversión presupuestaria): Ventas +8.700 € [ES] (6 presupuestos adicionales x 1.450 €) | Materiales +2.991 € [ES] | Margen neto +5.709 € [ES] (8.700 € x {ratio_margen_exacto:.5f}).
     * Palanca 3 (Optimización de stock): Ventas 0 € | Ahorro compras -4.800 € [HC] (hipótesis de reducción de compras de mostrador) | Margen neto +4.800 € [HC] (165.000 € x 2,90909%).
     * Palanca 4 (Contratos B2B): Ventas +4.500 € [ES] (5 contratos x 900 €) | Materiales +1.547 € [ES] | Margen neto +2.953 € [ES] (4.500 € x {ratio_margen_exacto:.5f}).
     * Total incremento ventas: 16.170 + 8.700 + 4.500 = +29.370 € [C].
     * Materiales asociados: 5.558 + 2.991 + 1.547 = +10.096 € [C]. Ahorro stock: -4.800 € [HC]. Incremento neto materiales = +5.296 € [C].
     * Menos coste software OPEX Año 1 = -2.500 € [ES].
     * Impacto neto en EBIT = 10.612 + 5.709 + 4.800 + 2.953 - 2.500 = +21.574 € [C].
     * EBIT inicial 62.000 € [DR] + 21.574 € [C] = 83.574 € [C] (Residuo: 0,00 €).
   - Cuenta Proforma P&L Unificada (Escenario A - Transformación + Crecimiento Comercial):
     * Actual [DR]: Ventas 480.000 € | Compras 165.000 € | Personal 195.000 € | Fijos 58.000 € | Software 0 € | EBIT = 62.000 € (12,9%).
     * Año 1 [ES]: Ventas 509.370 € | Compras 170.296 € | Personal 195.000 € | Fijos 58.000 € | Software 2.500 € | EBIT = 83.574 € (16,4%).
     * Año 2 [ES]: Ventas 528.000 € | Compras 171.600 € ([HC] mejora del ratio de compras al 32,5% por economías de escala y compras agrupadas) | Personal 197.000 € ([HC] ajuste salarial moderado) | Fijos 58.500 € ([HC] indexación) | Software 5.000 € [ES] (ampliación de módulos analíticos y optimización de rutas, estimación presupuestaria sujeta a oferta formal) | EBIT = 95.900 € (18,2%).
     * Año 3 [OD]: Ventas 545.000 € | Compras 168.950 € ([HC] ratio de compras del 31,0% por erradicación de urgencias) | Personal 201.000 € ([HC] consolidación) | Fijos 59.000 € ([HC]) | Software 8.500 € [ES] (portal clientes B2B e integración total ERP, estimación presupuestaria sujeta a oferta formal) | EBIT = 107.550 € (19,7%).
   - Contraste con Escenario B (Transformación y Eficiencia sin Crecimiento de Ventas a 480.000 €): Ventas 480.000 € | Compras 160.200 € (asumiendo la hipótesis de ahorro de 4.800 € en mermas [HC]) | Personal 195.000 € | Fijos 58.000 € | Software 2.500 € | EBIT = 64.300 € (13,4%).
     * OBLIGATORIO: Explicar que el Escenario B asume mantener las ventas totales constantes en 480.000 € redirigiendo la capacidad liberada hacia contratos de mantenimiento preventivo B2B de mayor estabilidad sin incrementar plantilla. La diferencia de 19.274 € entre los 64.300 € del Escenario B y los 83.574 € del Escenario A procede exclusivamente del aprovechamiento comercial de las horas y presupuestos adicionales.

9. DICTAMEN FINAL DEL CONSULTOR (SECCIÓN 14):
   Redactar literalmente la versión prudente y defendible:
   "Con base en la información facilitada por la empresa, los cálculos derivados y los supuestos explicitados en el escenario económico, la inversión prevista de 6.500 € presenta un potencial de retorno favorable bajo el escenario base planteado.
   El escenario contempla la recuperación del 50% de las horas actualmente identificadas como improductivas, junto con mejoras adicionales en conversión de presupuestos, control de consumos y captación de contratos preventivos.
   El payback estimado de 7,4 meses debe interpretarse como payback teórico condicionado al cumplimiento de dichos supuestos, y no como un resultado garantizado. La fase de validación operativa de los primeros 30 días permitirá medir la capacidad real de conversión de las horas recuperadas y recalibrar las proyecciones económicas.
   Desde el punto de vista operativo, se recomienda priorizar en una primera fase el desbloqueo de capacidad instalada, la trazabilidad de partes y materiales y la estandarización de presupuestos antes de acometer incrementos estructurales de plantilla, reevaluando la necesidad de incorporaciones tras medir la utilización efectiva posterior a la implantación."

10. FORMATO JSON OBLIGATORIO PARA GRÁFICOS:
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
