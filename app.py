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
    page_title="Informe de Diagnóstico Operativo y Plan de Acción",
    page_icon="📄",
    layout="wide",
)

# Estilos CSS para sobriedad editorial de consultoría
st.markdown(
    """
    <style>
    .metric-box {
        background-color: #f8f9fa;
        border-left: 4px solid #1f2937;
        padding: 12px 16px;
        margin-bottom: 12px;
    }
    .callout-warning {
        background-color: #fbfbfb;
        border-left: 4px solid #b45309;
        padding: 12px 16px;
        margin: 10px 0;
        font-size: 0.92rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Auditoría Operativa y Plan de Acción Estratégico")
st.markdown(
    "Plataforma de evaluación cuantitativa, análisis de brecha operativa y priorización estratégica para pymes."
)
st.markdown("---")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Acceso y Configuración")
    api_key_usuario = st.text_input(
        "Clave de API (Gemini):",
        type="password",
        help="Introduce tu clave personal de acceso a la API.",
    )
    st.markdown("---")
    st.markdown("### Código de Evidencia Documental")
    st.caption(
        """
        • **[DR] Dato Real:** Aportado por la empresa o extraído de balances.\n
        • **[FE] Fuente Externa:** Estadísticas públicas y estudios contrastados.\n
        • **[ES] Estimación:** Cálculo derivado sobre las variables del modelo.\n
        • **[HC] Hipótesis:** Supuesto operativo sujeto a contraste.\n
        • **[OD] Objetivo:** Meta establecida en el plan de trabajo.
        """
    )

# --- SISTEMA DINÁMICO DE PUNTUACIÓN DE PRECISIÓN ---
score_precision = 40

# --- FORMULARIO ESTRUCTURADO EN 5 FASES ---
tab_gen, tab_fin, tab_ops, tab_mkt, tab_vision = st.tabs([
    "1. Estructura y Equipo",
    "2. Información Financiera",
    "3. Circuito Comercial y Operativo",
    "4. Mercado y Posicionamiento",
    "5. Dirección, Plan e Inversión",
])

# =====================================================================
# FASE 1: DATOS GENERALES, EQUIPO Y FLOTA
# =====================================================================
with tab_gen:
    st.markdown("#### Identificación Corporativa y Capacidad Operativa")
    g1, g2, g3 = st.columns(3)
    with g1:
        sector = st.text_input(
            "Sector y actividad principal:",
            value="Instalación y mantenimiento de climatización y aerotermia",
        )
        subsector = st.text_input(
            "Subsector o especialidad:",
            value="Frío industrial para hostelería y residencial premium",
        )
        pais_region = st.text_input(
            "Ámbito territorial:",
            value="España (Comunidad Valenciana)",
        )
    with g2:
        ano_creacion = st.number_input(
            "Año de constitución (opcional):",
            min_value=1950,
            max_value=2026,
            value=2012,
        )
        if ano_creacion != 2012:
            score_precision += 4

        tamano_equipo = st.number_input(
            "Plantilla total (personas):",
            min_value=1,
            max_value=500,
            value=6,
        )
        operarios_directos = st.number_input(
            "Técnicos directos en campo/taller:",
            min_value=1,
            max_value=500,
            value=4,
        )
    with g3:
        personal_admin = st.number_input(
            "Personal en soporte/administración:",
            min_value=0,
            max_value=50,
            value=1,
        )
        personal_comercial = st.number_input(
            "Personal dedicado a desarrollo comercial:",
            min_value=0,
            max_value=50,
            value=1,
        )
        tiene_flota = st.checkbox("La empresa cuenta con vehículos o furgonetas operativas", value=True)

    if tiene_flota:
        st.markdown("##### Gestión de Vehículos Operativos")
        f1, f2 = st.columns(2)
        with f1:
            num_vehiculos = st.number_input(
                "Número de furgonetas o vehículos de servicio:",
                min_value=1,
                max_value=100,
                value=4,
            )
        with f2:
            control_stock_vehiculos = st.selectbox(
                "Procedimiento actual de control de material en vehículo:",
                [
                    "Sin registro formal / Los operarios reponen material según necesidad",
                    "Registro manual en papel al inicio y fin de jornada",
                    "Hojas de cálculo periódicas",
                    "Identificación digital (códigos QR / aplicación móvil)",
                ],
            )
        score_precision += 6
    else:
        num_vehiculos = 0
        control_stock_vehiculos = "Sin flota de vehículos"

# =====================================================================
# FASE 2: FINANZAS, COBROS Y SUBIDA DE DOCUMENTOS
# =====================================================================
with tab_fin:
    st.markdown("#### Cuenta de Explotación y Tesorería")
    
    archivo_subido = st.file_uploader(
        "Adjuntar balance, cuenta de pérdidas y ganancias o listado contable (PDF, Excel, CSV) (opcional):",
        type=["pdf", "xlsx", "xls", "csv"],
        help="Permite cotejar partidas contables exactas y documentar las cifras con rigor.",
    )
    if archivo_subido is not None:
        score_precision += 15
        st.info(f"Documento incorporado: **{archivo_subido.name}**. El análisis contrastará los datos con este estado financiero.")

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
        if facturacion_anterior > 0:
            score_precision += 5
    with fn2:
        coste_personal = st.number_input(
            "Coste total anual de personal (Nóminas + Seguridad Social) (€):",
            min_value=5000,
            max_value=30000000,
            value=195000,
            step=5000,
        )
        coste_compras_recambios = st.number_input(
            "Consumo de materiales, repuestos y aprovisionamientos (€):",
            min_value=0,
            max_value=30000000,
            value=165000,
            step=5000,
        )
    with fn3:
        gastos_fijos = st.number_input(
            "Gastos generales de estructura (Alquiler, suministros, seguros) (€):",
            min_value=1000,
            max_value=10000000,
            value=58000,
            step=2000,
        )
        margen_ebitda_declarado = st.number_input(
            "Resultado de explotación o beneficio neto estimado (€):",
            min_value=-500000,
            max_value=10000000,
            value=62000,
            step=2000,
        )

    # Cálculos analíticos de balance
    costes_totales = coste_personal + coste_compras_recambios + gastos_fijos
    resultado_teorico = facturacion_anual - costes_totales
    discrepancia_contable = abs(resultado_teorico - margen_ebitda_declarado)
    facturacion_por_empleado = facturacion_anual / tamano_equipo if tamano_equipo > 0 else 0
    margen_bruto_pct = ((facturacion_anual - coste_compras_recambios) / facturacion_anual) * 100 if facturacion_anual > 0 else 0

    st.markdown("##### Ratios Derivados de Explotación")
    cf1, cf2, cf3 = st.columns(3)
    cf1.metric("Facturación por Empleado", f"{facturacion_por_empleado:,.0f} €/año")
    cf2.metric("Margen Bruto de Contribución", f"{margen_bruto_pct:.2f} %")
    cf3.metric("Resultado Teórico Calculado", f"{resultado_teorico:,.0f} €")

    if discrepancia_contable > 5000:
        st.markdown(
            f"""
            <div class="callout-warning">
            <b>Nota de limitación contable:</b> La resta de Facturación declarada ({facturacion_anual:,.0f} €) y Gastos totales ({costes_totales:,.0f} €) arroja un resultado de {resultado_teorico:,.0f} €, que no coincide con el beneficio indicado de {margen_ebitda_declarado:,.0f} €. Por criterio de cautela, el estudio se centrará en capacidad horaria y márgenes unitarios.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("Detalle de plazos de cobro y saldo pendiente (opcional)"):
        dias_cobro = st.number_input(
            "Periodo medio de cobro a clientes (días):",
            min_value=0,
            max_value=365,
            value=65,
        )
        saldo_pendiente_cobro = st.number_input(
            "Importe pendiente de cobro fuera del plazo pactado (€):",
            min_value=0,
            max_value=5000000,
            value=18000,
            step=1000,
        )
        if saldo_pendiente_cobro > 0:
            score_precision += 6

# =====================================================================
# FASE 3: VENTAS, PRESUPUESTOS Y OPERACIONES
# =====================================================================
with tab_ops:
    st.markdown("#### Proceso Comercial y Cuellos de Botella de Ejecución")
    op1, op2, op3 = st.columns(3)
    with op1:
        presupuestos_mes = st.number_input(
            "Presupuestos emitidos mensualmente (promedio):",
            min_value=1,
            max_value=5000,
            value=25,
        )
        tasa_conversion_presupuestos = st.slider(
            "Tasa estimada de aceptación de presupuestos (%):",
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
            "Tiempo diario dedicado a tareas de gestión no facturables (horas):",
            min_value=0.5,
            max_value=16.0,
            value=3.5,
            step=0.5,
            help="Comprende presupuestos no convertidos, trámites de partes de trabajo y coordinación.",
        )
        quien_hace_presupuestos = st.selectbox(
            "Responsable habitual de la elaboración de presupuestos:",
            [
                "Dirección / Gerencia",
                "Técnicos especialistas durante jornada de trabajo",
                "Personal administrativo",
                "Área comercial dedicada",
            ],
        )
        precio_hora_mano_obra = st.number_input(
            "Tarifa horaria facturada al cliente (€/h sin IVA):",
            min_value=15,
            max_value=300,
            value=42,
            step=1,
        )
    with op3:
        tiempo_cierre_factura = st.selectbox(
            "Plazo habitual entre ejecución del servicio y emisión de factura:",
            [
                "Misma jornada (in situ o procedimiento automático)",
                "Entre 24 y 48 horas",
                "Entre 3 y 7 días hábiles",
                "Facturación periódica a mes vencido",
            ],
        )
        origen_clientes = st.selectbox(
            "Vía principal de captación de clientela:",
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
        value="Los partes de trabajo en papel tardan varios días en procesarse. Se dedican 3,5 h diarias a tareas de gestión no facturables (presupuestos no aceptados y tramitación manual de partes). Se producen descuadres de stock en furgoneta que generan segundas visitas.",
        height=90,
    )

# =====================================================================
# FASE 4: CLIENTES, COMPETENCIA Y DIFERENCIACIÓN
# =====================================================================
with tab_mkt:
    st.markdown("#### Segmentación de Clientes y Factores Competitivos")
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
            "Proporción de ingresos bajo contratos de mantenimiento o cuota periódica (%):",
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
            "Ventaja competitiva actual (motivo principal de elección):",
            value="Capacidad de respuesta técnica con plazo inferior a 3 horas en averías críticas de hostelería local",
        )

    with st.expander("Concentración de ingresos por clientes (opcional)"):
        top5_concentracion = st.slider(
            "Porcentaje de facturación concentrado en los 5 principales clientes (%):",
            min_value=5,
            max_value=100,
            value=30,
        )
        if top5_concentracion != 30:
            score_precision += 5

# =====================================================================
# FASE 5: ESTRATEGIA, VISIÓN 3 AÑOS E INVERSIÓN
# =====================================================================
with tab_vision:
    st.markdown("#### Plan Estratégico y Capacidad Financiera")
    v1, v2 = st.columns(2)
    with v1:
        presupuesto_disponible = st.number_input(
            "Presupuesto máximo asignable a modernización operativa en 12 meses (€):",
            min_value=0,
            max_value=500000,
            value=6500,
            step=500,
        )
        horizonte = st.slider(
            "Horizonte temporal del análisis (años):",
            min_value=1,
            max_value=5,
            value=3,
        )
        objetivo_principal_crecimiento = st.selectbox(
            "Prioridad estratégica directiva:",
            [
                "Incrementar el margen neto y la rentabilidad sobre la estructura actual",
                "Ampliar volumen de facturación y captar cuota de mercado en segmento empresas",
                "Reducir la dependencia operativa del equipo directivo",
                "Contener costes y estandarizar procedimientos de trabajo",
            ],
        )

    with v2:
        st.markdown("##### Evaluación de Perspectiva Directiva")
        pregunta_115_inaccion = st.text_area(
            "Impacto previsto si no se introducen cambios en el periodo considerado:",
            value="Los márgenes operativos tenderán a reducirse por la evolución de costes de personal, competidores de mayor tamaño captarán clientes pyme mediante ofertas empaquetadas y se deteriorará la rentabilidad.",
            height=70,
        )
        pregunta_116_deseo = st.text_area(
            "Problema prioritario a resolver en el corto plazo según la dirección:",
            value="Eliminar el tiempo consumido en presupuestos de averías que no prosperan y reducir el plazo de liquidación de partes de trabajo a menos de 24 horas.",
            height=70,
        )

    score_precision = min(score_precision + 15, 100)

# --- VISUALIZACIÓN DEL NIVEL DE PRECISIÓN ---
st.markdown("---")
col_bar1, col_bar2 = st.columns([3, 1])
with col_bar1:
    st.progress(score_precision / 100)
with col_bar2:
    if score_precision >= 85:
        st.markdown(f"**Nivel de Precisión de Auditoría: {score_precision}%** (Estándar Directivo)")
    elif score_precision >= 65:
        st.markdown(f"**Nivel de Precisión de Auditoría: {score_precision}%** (Nivel Avanzado)")
    else:
        st.markdown(f"**Nivel de Precisión de Auditoría: {score_precision}%** (Diagnóstico Preliminar)")

# =====================================================================
# FUNCIONES GRÁFICAS (PLOTLY) - ESTILO EDITORIAL SOBRIO
# =====================================================================
def render_trend_radar(trends_data):
    horizon_map = {
        "Prioridad inmediata (0-6 meses)": 1,
        "Preparación (6-18 meses)": 2,
        "Seguimiento (18-36 meses)": 3,
        "Act": 1,
        "Prepare": 2,
        "Watch": 3,
    }
    quadrant_angle = {
        "Tecnología": 45,
        "Operaciones": 135,
        "Modelo de Negocio": 225,
        "Mercado": 315,
        "Mercado / Cliente": 315,
    }

    plot_rows = []
    for t in trends_data:
        h_val = t.get("horizon", "Prepare")
        base_r = horizon_map.get(h_val, 2)
        q_val = t.get("quadrant", "Tecnología")
        base_theta = quadrant_angle.get(q_val, 45)
        impact = t.get("impact", 5)

        r_jitter = base_r + (impact - 5) * 0.04
        theta_jitter = (base_theta + (hash(t.get("name", "")) % 30) - 15) % 360

        plot_rows.append({
            "name": t.get("name"),
            "r": r_jitter,
            "theta": theta_jitter,
            "horizon": h_val,
            "quadrant": q_val,
            "impact": impact,
        })

    df = pd.DataFrame(plot_rows)
    fig = go.Figure()

    # Trazas con paleta sobria (azul pizarra corporativo y gris oscuro)
    fig.add_trace(
        go.Scatterpolar(
            r=df["r"],
            theta=df["theta"],
            mode="markers+text",
            text=df["name"],
            textposition="top center",
            textfont=dict(family="Arial", size=10, color="#1f2937"),
            marker=dict(
                size=df["impact"] * 2.2,
                color="#2563eb",
                line=dict(color="#1e3a8a", width=1.5),
                opacity=0.85,
            ),
            hovertemplate="<b>%{text}</b><br>Cuadrante: %{customdata[0]}<br>Impacto: %{customdata[1]}/10<extra></extra>",
            customdata=df[["quadrant", "impact"]],
            showlegend=False,
        )
    )

    fig.update_layout(
        polar=dict(
            bgcolor="#ffffff",
            radialaxis=dict(
                visible=True,
                range=[0, 3.5],
                tickvals=[1, 2, 3],
                ticktext=[
                    "Prioridad inmediata (0-6m)",
                    "Preparación (6-18m)",
                    "Seguimiento (18-36m)",
                ],
                tickfont=dict(size=9, color="#4b5563"),
                linecolor="#e5e7eb",
                gridcolor="#f3f4f6",
            ),
            angularaxis=dict(
                tickvals=[45, 135, 225, 315],
                ticktext=["Tecnología", "Operaciones", "Modelo de Negocio", "Mercado"],
                tickfont=dict(size=11, color="#111827", family="Arial"),
                linecolor="#d1d5db",
                gridcolor="#f3f4f6",
                direction="clockwise",
            ),
        ),
        paper_bgcolor="#ffffff",
        title=dict(
            text="Mapa de Tendencias y Prioridades Estratégicas",
            font=dict(size=14, color="#111827", family="Arial"),
            x=0.02,
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        height=520,
    )
    return fig


def render_gap_radar(gap_data):
    categories = [
        "Digitalización",
        "Eficiencia Operativa",
        "Control de Margen",
        "Cartera B2B",
        "Agilidad Estratégica",
    ]

    pyme_scores = gap_data.get("pyme", [2, 4, 4, 5, 3])
    media_scores = gap_data.get("benchmark_orientativo", [5, 5, 5, 5, 4])
    aspiracional_scores = gap_data.get("benchmark_aspiracional", [8, 8, 8, 8, 8])

    fig = go.Figure()

    # Nivel actual: Gris oscuro
    fig.add_trace(
        go.Scatterpolar(
            r=pyme_scores,
            theta=categories,
            fill="toself",
            fillcolor="rgba(31, 41, 55, 0.15)",
            line=dict(color="#1f2937", width=2),
            name="Situación Actual [DR]",
        )
    )
    # Referencia sectorial: Gris claro punteado
    fig.add_trace(
        go.Scatterpolar(
            r=media_scores,
            theta=categories,
            fill="none",
            line=dict(color="#9ca3af", width=1.5, dash="dash"),
            name="Referencia Orientativa [ES]",
        )
    )
    # Referencia de mejora: Azul corporativo sobrio
    fig.add_trace(
        go.Scatterpolar(
            r=aspiracional_scores,
            theta=categories,
            fill="none",
            line=dict(color="#1e40af", width=2),
            name="Referencia de Mejora [OD]",
        )
    )

    fig.update_layout(
        polar=dict(
            bgcolor="#ffffff",
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                tickvals=[2, 4, 6, 8, 10],
                tickfont=dict(size=9, color="#6b7280"),
                gridcolor="#f3f4f6",
                linecolor="#e5e7eb",
            ),
            angularaxis=dict(
                tickfont=dict(size=10, color="#111827"),
                gridcolor="#f3f4f6",
                linecolor="#e5e7eb",
            ),
        ),
        paper_bgcolor="#ffffff",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=10),
        ),
        title=dict(
            text="Matriz de Brecha Operativa: Situación Actual vs. Referencias",
            font=dict(size=14, color="#111827", family="Arial"),
            x=0.02,
        ),
        margin=dict(l=40, r=40, t=60, b=60),
        height=450,
    )
    return fig


# =====================================================================
# EJECUCIÓN DEL ANÁLISIS
# =====================================================================
if st.button(
    "Ejecutar Auditoría Operativa y Generar Informe Estratégico",
    type="primary",
    use_container_width=True,
):
    if not api_key_usuario:
        st.error("Es necesario introducir la clave de API en la barra lateral izquierda.")
    else:
        with st.spinner("Procesando parámetros contables, evaluando capacidad horaria y elaborando dictamen..."):
            try:
                cliente = genai.Client(api_key=api_key_usuario)

                prompt_completo = f"""
Eres un Socio Director de Consultoría de Operaciones y Estrategia Empresarial.
Dispones de los datos cuantitativos facilitados por la empresa. Debes elaborar un informe técnico, sobrio, exhaustivo y defendible ante un comité directivo.

BASE DE DATOS AUDITADA:
- Actividad / Especialidad: [DR] {sector} | {subsector}
- Ámbito territorial: [DR] {pais_region}
- Año de constitución: [DR] {ano_creacion}
- Plantilla total: [DR] {tamano_equipo} personas (Técnicos de campo: [DR] {operarios_directos} | Soporte administrativo: [DR] {personal_admin} | Ventas: [DR] {personal_comercial})
- Vehículos operativos: [DR] {num_vehiculos} unidades (Control de stock en vehículo: [DR] {control_stock_vehiculos})
- Facturación anual del ejercicio: [DR] {facturacion_anual:,} € (Ejercicio previo: [DR] {facturacion_anterior:,} €)
- Coste total de personal: [DR] {coste_personal:,} €
- Gasto en materiales y aprovisionamientos: [DR] {coste_compras_recambios:,} €
- Gastos generales de estructura: [DR] {gastos_fijos:,} €
- Beneficio de explotación declarado: [DR] {margen_ebitda_declarado:,} €
- Facturación por empleado: [ES] {facturacion_por_empleado:,.0f} €/año
- Margen bruto de contribución: [ES] {margen_bruto_pct:.2f}%
- Ticket medio por actuación: [DR] {ticket_medio_operacion} €
- Emisión de presupuestos: [DR] {presupuestos_mes} unidades/mes (Tasa de aceptación declarada: [DR] {tasa_conversion_presupuestos}%)
- Tiempo dedicado a gestión no facturable: [DR] {horas_perdidas_dia} horas/día (presupuestos no aceptados, tramitación de partes y coordinación)
- Responsable de presupuestos: [DR] {quien_hace_presupuestos}
- Tarifa horaria facturada de mano de obra: [DR] {precio_hora_mano_obra} €/h (sin IVA)
- Margen de contribución directo sobre tarifa horaria: [ES] {precio_hora_mano_obra * (margen_bruto_pct/100):.2f} €/h ({precio_hora_mano_obra} €/h x {margen_bruto_pct:.2f}%)
- Plazo de cierre de partes a facturación: [DR] {tiempo_cierre_factura}
- Canal principal de captación: [DR] {origen_clientes}
- Nivel de digitalización actual: [DR] {stack_tecnologico}
- Cuello de botella declarado: [DR] {friccion_operativa}
- Composición de cartera: [DR] {porcentaje_b2c}% Particulares | {porcentaje_b2b}% Empresas
- Ingresos bajo cuota recurrente: [DR] {ingresos_recurrentes_pct}%
- Competidor de referencia: [DR] {competidor_referencia}
- Factor diferencial actual: [DR] {ventaja_competitiva}
- Presupuesto de inversión en modernización (12 meses): [DR] {presupuesto_disponible:,} €
- Periodo de planificación: [DR] {horizonte} años
- Prioridad estratégica declarada: [DR] {objetivo_principal_crecimiento}
- Estimación directiva ante inacción (3 años): [DR] "{pregunta_115_inaccion}"
- Objetivo operativo prioritario de dirección: [DR] "{pregunta_116_deseo}"
- Grado de precisión de la información facilitada: [ES] {score_precision}%

======================================================================
NORMAS EDITORIALES Y DE RIGOR METODOLÓGICO (ESTRICTAS):
======================================================================
1. PROHIBICIÓN RADICAL DE EMOJIS Y SÍMBOLOS INFANTILES:
   - Queda estrictamente PROHIBIDO el uso de emoticonos, círculos de colores (🟢, 🔵, 🟡, 🟠, 🟣), señales de advertencia (⚠️) o bombillas (💡).
   - Utiliza de forma sistemática los códigos alfanuméricos discretos:
     * [DR] Dato real aportado por la empresa.
     * [FE] Fuente externa contrastada.
     * [ES] Estimación calculada a partir de los datos.
     * [HC] Hipótesis operativa sujeta a comprobación.
     * [OD] Objetivo deseado del plan de trabajo.

2. ENCABEZADOS Y LENGUAJE CORPORATIVO SOBRIO:
   - Utiliza títulos sobrios: "Decisiones prioritarias", "Indicadores de alerta", "Oportunidades de mejora", "Riesgos identificados", "Próximos pasos".
   - Sustituye expresiones informales:
     * "Actuar Ya" -> "Prioridad inmediata: 0–6 meses"
     * "Prepararse" -> "Preparación: 6–18 meses"
     * "Vigilar" -> "Seguimiento: 18–36 meses"
     * "Qué construir, comprar, dejar de hacer" -> "Decisiones sobre capacidades y recursos"
     * "Coste de no hacer nada" -> "Impacto estimado de mantener la situación actual"
     * "Benchmark aspiracional" -> "Referencia de mejora"
     * "Radar de tendencias" -> "Mapa de tendencias y prioridades"
   - Prohibido el uso de términos apocalípticos o coloquiales: "quiebra inminente", "fuga masiva", "moat", "extinción".

3. NOTAS METODOLÓGICAS FORMALES:
   - Para las estimaciones, añade: "Nota metodológica: Las cifras identificadas como estimaciones se han calculado a partir de los datos disponibles y deberán validarse con información contable u operativa adicional."
   - Para las hipótesis: "Hipótesis pendiente de validación: Este punto se incluye como línea de trabajo y no como hecho confirmado."

4. RIGOR EN EL CÁLCULO DE CAPACIDAD HORARIA (770 HORAS):
   - Definir con exactitud: "3,5 h/día (770 h/año) [DR] dedicadas a tareas de gestión no facturables (presupuestación no convertida, tramitación manual de partes y coordinación operativa)."
   - Denominar los 32.340 € teóricos estrictamente como: "Capacidad productiva máxima teórica [ES] (magnitud analítica no acumulable a caja sin absorción efectiva por demanda de mercado)."
   - PROHIBIDO sumar en una cifra global el coste salarial, la capacidad potencial y las contingencias normativas. Presentar tabla desagregada con impacto salarial, capacidad potencial y contingencias, indicando que son magnitudes no sumables directamente.

5. REFERENCIAS COMPARATIVAS Y BENCHMARKING:
   - Si una cifra comparativa no dispone de una fuente pública con tabla y fecha precisa, identifícala formalmente como "Referencia orientativa / benchmark de diseño [ES]", con nivel de confianza medio o bajo.

6. ESCENARIOS MEDIANTE RANGOS E INDUCTORES (SIN PORCENTAJES CERRADOS FICTICIOS):
   - Prohibido asignar porcentajes fijos arbitrarios (no escribir "+30%").
   - Utilizar rangos fundamentados en palancas operativas:
     * Escenario A (Optimización operativa): Margen en rango [+15% a +25%], condicionado a cuota en empresas y control digital de stock.
     * Escenario B (Integración en plataformas): Margen comprimido en rango [-5% a +5%].
     * Escenario C (Especialización en urgencias): Margen en rango [+5% a +12%].
     * Escenario D (Inacción operativa): Deterioro en rango [-10% a -20%].

7. SALVAGUARDAS LEGALES Y FINANCIERAS:
   - Marco normativo: Exponer Veri*factu (RD 1007/2023) y Facturación Electrónica B2B en sus plazos y requisitos técnicos reales, tratando las eventuales penalizaciones como "riesgo regulatorio sujeto a inspección y subsanación".
   - Financiación: Indicar que "las ayudas públicas están sujetas a convocatorias vigentes, dotación presupuestaria y cumplimiento de bases reguladoras en la fecha efectiva de solicitud."

8. FORMATO JSON OBLIGATORIO PARA PLOTLY:
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
     Orden exacto de gap_analysis: [Digitalización, Eficiencia Operativa, Control de Margen, Cartera B2B, Agilidad Estratégica].

======================================================================
ESTRUCTURA DEL INFORME (MEMORÁNDUM TÉCNICO DE 15 SECCIONES):
======================================================================
# INFORME DE EVALUACIÓN OPERATIVA Y PLAN DE ACCIÓN ESTRATÉGICO

## 0. Marco Metodológico y Grado de Precisión de la Información
(Definición formal de los códigos [DR], [FE], [ES], [HC], [OD]. Nivel de precisión del estudio: [ES] {score_precision}%. Advertencia de cautela contable en caso de discrepancias de balance).

## Resumen Ejecutivo: Decisiones Prioritarias
(Tabla: Decisión directiva | Plazo de ejecución | Propietario | Asignación presupuestaria | Impacto esperado en margen).
(Cotejo técnico con el objetivo prioritario planteado por Gerencia).

## 1. Diagnóstico de Eficiencia y Unit Economics Operativos
(Estructura analítica de ingresos, aprovisionamientos, personal y estructura. Análisis de facturación por empleado).
(Cuantificación del tiempo de gestión no facturable: [ES] {horas_perdidas_dia * 220:.0f} horas/año, separando el impacto salarial de la capacidad productiva teórica).

## 2. Marco Normativo y Exigencias Regulatorias ({pais_region})
(Requisitos técnicos y calendario de adaptación a Veri*factu RD 1007/2023 y Facturación Electrónica B2B).

## 3. Comparativa Sectorial y Referencias de Posición
(Tabla: Variable analizada | Situación de la empresa [DR] | Referencia orientativa [ES] | Referencia de mejora [OD] | Grado de confianza metodológica).

## 4. Referencias Prácticas de Transferencia Operativa
(Análisis de dos operadores técnicos en mercados homologables: soluciones incorporadas y elementos aplicables a esta estructura).

## 5. Dinámicas del Entorno y Repercusión en el Negocio
(Análisis de tendencias relevantes, causas inductoras e implicación directa en decisiones de gestión).

## 6. Mapa de Tendencias y Prioridades de Actuación
(Clasificación de prioridades: Prioridad inmediata 0-6 meses / Preparación 6-18 meses / Seguimiento 18-36 meses. Matriz Impacto x Incertidumbre).

## 7. Análisis de Brecha Operativa (Matriz de Brecha)
(Evaluación fundamentada de las 5 dimensiones representadas en la matriz gráfica).

## 8. Análisis de Escenarios Plausibles
(Cruce de incertidumbres principales con niveles de plausibilidad, rangos de rentabilidad esperados e inductores de seguimiento. Contraste con el diagnóstico a 3 años de Gerencia).

## 9. Despliegue Temporal Inverso: Hitos a {horizonte} Años
(Definición del estado objetivo a {horizonte} años y retroceso temporal: hitos a consolidar en Año 2 y en Año 1).

## 10. Decisiones sobre Capacidades y Recursos
(Clasificación técnica: desarrollo interno, contratación de servicios tecnológicos especializados, acuerdos y eliminación de procesos manuales).

## 11. Indicadores de Alerta y Disparadores Operativos
(Métricas del entorno que deben activar revisiones en el plan de actuación).

## 12. Impacto Estimado de Mantener la Situación Actual
(Tabla desagregada a 12, 24 y 36 meses: coste de nómina asignado a gestión, capacidad potencial no capturada y riesgo normativo, con nota formal de no sumabilidad directa).

## 13. Vías de Financiación y Optimización de Costes ({pais_region})
(Líneas de apoyo público y bonificaciones para formación técnica FUNDAE, con salvaguarda sobre convocatorias vigentes).

## 14. Plan de Habilitación del Equipo y Gestión del Cambio
(Protocolo de formación para operarios de campo, administración y adaptación de clientes habituales).

## 15. Plan de Acción y Hoja de Ruta (Fases 30, 90 y 180 Días)
(Cronograma con acciones, responsables formalmente asignados, dependencias técnicas, progresión de KPIs y presupuesto CAPEX/OPEX ajustado a [DR] {presupuesto_disponible:,} €).
(Análisis de sensibilidad del retorno de la inversión bajo escenarios de absorción de capacidad al 25%, 50% y 75%, con estimación de plazo de recuperación).
"""

                partes_contenido = []
                if archivo_subido is not None:
                    bytes_archivo = archivo_subido.read()
                    mime_type = archivo_subido.type
                    partes_contenido.append(
                        types.Part.from_bytes(data=bytes_archivo, mime_type=mime_type)
                    )
                    prompt_completo += "\n\nDOCUMENTO CONTABLE INCORPORADO: Utiliza este archivo para cotejar y documentar las partidas contables exactas de la empresa con código [DR]."

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
                    raise Exception("Servidores temporalmente ocupados. Por favor, reintenta en unos instantes.")

                texto_salida = respuesta.text

                # Extracción del bloque JSON
                patron_json = r"```json\s*(\{.*?\})\s*```"
                match = re.search(patron_json, texto_salida, re.DOTALL)

                if match:
                    json_str = match.group(1)
                    datos_graficos = json.loads(json_str)

                    st.success("Evaluación cuantitativa y plan estratégico elaborados con éxito.")

                    # Visualización gráfica sobria
                    st.subheader("Representación Gráfica de Posición y Prioridades")
                    col_r1, col_r2 = st.columns(2)

                    with col_r1:
                        if "trends" in datos_graficos:
                            fig_radar = render_trend_radar(datos_graficos["trends"])
                            st.plotly_chart(fig_radar, use_container_width=True)

                    with col_r2:
                        if "gap_analysis" in datos_graficos:
                            fig_gap = render_gap_radar(datos_graficos["gap_analysis"])
                            st.plotly_chart(fig_gap, use_container_width=True)

                    st.markdown("---")

                    informe_markdown = re.sub(patron_json, "", texto_salida, flags=re.DOTALL).strip()
                    st.markdown(informe_markdown)

                else:
                    st.markdown(texto_salida)

            except Exception as e:
                st.error(f"Error durante el procesamiento: {e}")
