import json
import re
import time
from google import genai
from google.genai import types
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Industrial Audit & Strategic Foresight Platform",
    page_icon="🧭",
    layout="wide",
)

st.title("🧭 Plataforma de Auditoría Industrial & Strategic Foresight")
st.markdown(
    "Motor cuantitativo de **Auditoría Operativa, Benchmarking Sectorial y Prospectiva Estratégica** para PYMES."
)
st.markdown("---")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🔐 Acceso y Configuración")
    api_key_usuario = st.text_input(
        "API Key de Gemini:",
        type="password",
        help="Introduce tu API Key personal de Google AI Studio.",
    )
    st.markdown("---")
    st.markdown("### Taxonomía de Rigor Analítico")
    st.caption(
        "• 🟢 **Dato Declarado:** Aportado por la empresa o extraído de sus documentos.\n"
        "• 🔵 **Fuente Externa:** Benchmark oficial o estudio sectorial contrastado.\n"
        "• 🟡 **Estimación Matemática:** Derivación contable calculada por el modelo.\n"
        "• 🟠 **Hipótesis a Validar:** Supuesto operativo provisional.\n"
        "• 🟣 **Objetivo Estratégico:** Meta fijada en el roadmap de adopción."
    )

# --- SISTEMA DINÁMICO DE PUNTUACIÓN DE PRECISIÓN ---
# Inicializamos variables para evaluar el nivel de precisión
score_precision = 40  # Base inicial por datos mínimos obligatorios

# --- FORMULARIO ESTRUCTURADO EN 5 FASES ---
tab_gen, tab_fin, tab_ops, tab_mkt, tab_vision = st.tabs([
    "1. Empresa, Equipo & Flota",
    "2. Finanzas, Cobros & Archivos",
    "3. Ventas, Presupuestos & Operaciones",
    "4. Clientes, Competencia & Ventaja",
    "5. Estrategia, Visión 3 Años & Inversión",
])

# =====================================================================
# FASE 1: DATOS GENERALES, EQUIPO Y FLOTA
# =====================================================================
with tab_gen:
    st.markdown("#### 🏢 Perfil Corporativo y Capacidad Humana")
    g1, g2, g3 = st.columns(3)
    with g1:
        sector = st.text_input(
            "Sector / Actividad principal 🔴:",
            value="Instalación y mantenimiento de climatización y aerotermia",
        )
        subsector = st.text_input(
            "Subsector o especialidad concreta 🔴:",
            value="Frío industrial para hostelería y residencial premium",
        )
        pais_region = st.text_input(
            "Ubicación y ámbito geográfico 🔴:",
            value="España (Comunidad Valenciana)",
        )
    with g2:
        ano_creacion = st.number_input(
            "Año de constitución / creación 🟡 (Opcional):",
            min_value=1950,
            max_value=2026,
            value=2012,
        )
        if ano_creacion != 2012:
            score_precision += 4

        tamano_equipo = st.number_input(
            "Número total de empleados en plantilla 🔴:",
            min_value=1,
            max_value=500,
            value=6,
        )
        operarios_directos = st.number_input(
            "Técnicos / operarios directos en campo/taller 🔴:",
            min_value=1,
            max_value=500,
            value=4,
        )
    with g3:
        personal_admin = st.number_input(
            "Personal en administración/soporte 🟡:",
            min_value=0,
            max_value=50,
            value=1,
        )
        personal_comercial = st.number_input(
            "Personal dedicado a ventas/comercial 🟡:",
            min_value=0,
            max_value=50,
            value=1,
        )
        tiene_flota = st.checkbox("¿La empresa dispone de vehículos/furgonetas?", value=True)

    # Lógica condicional para vehículos
    if tiene_flota:
        st.markdown("##### 🚐 Gestión de Flota y Almacén Móvil")
        f1, f2 = st.columns(2)
        with f1:
            num_vehiculos = st.number_input(
                "Número de furgonetas/vehículos operativos 🔴:",
                min_value=1,
                max_value=100,
                value=4,
            )
        with f2:
            control_stock_vehiculos = st.selectbox(
                "¿Cómo se controla actualmente el stock en vehículos? 🔴:",
                [
                    "No se controla / Los operarios cogen material según necesidad",
                    "Partes en papel al inicio y fin de jornada",
                    "Hojas de cálculo periódicas",
                    "Sistema digitalizado (códigos de barras / QR)",
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
    st.markdown("#### 💶 Datos Económicos y Gestión de Tesorería")
    
    # Subida opcional de archivos de balance / PyG
    archivo_subido = st.file_uploader(
        "📎 Adjuntar balance, cuenta de resultados (PyG) o exportación contable (PDF, Excel, CSV) 🟡 (Opcional):",
        type=["pdf", "xlsx", "xls", "csv"],
        help="Permite a la IA cotejar las cifras reales y extraer partidas contables exactas.",
    )
    if archivo_subido is not None:
        score_precision += 15
        st.success(f"Documento cargado: **{archivo_subido.name}**. La IA cotejará este balance para eliminar discrepancias.")

    fn1, fn2, fn3 = st.columns(3)
    with fn1:
        facturacion_anual = st.number_input(
            "Facturación último ejercicio (€) 🔴:",
            min_value=10000,
            max_value=50000000,
            value=480000,
            step=10000,
        )
        facturacion_anterior = st.number_input(
            "Facturación año anterior (€) 🟡 (Opcional):",
            min_value=0,
            max_value=50000000,
            value=450000,
            step=10000,
        )
        if facturacion_anterior > 0:
            score_precision += 5
    with fn2:
        coste_personal = st.number_input(
            "Coste total de personal anual (Nóminas + SS) (€) 🔴:",
            min_value=5000,
            max_value=30000000,
            value=195000,
            step=5000,
        )
        coste_compras_recambios = st.number_input(
            "Gasto anual en materiales / repuestos / compras (€) 🔴:",
            min_value=0,
            max_value=30000000,
            value=165000,
            step=5000,
        )
    with fn3:
        gastos_fijos = st.number_input(
            "Gastos de estructura / fijos (Alquiler, suministros, seguros) (€) 🔴:",
            min_value=1000,
            max_value=10000000,
            value=58000,
            step=2000,
        )
        margen_ebitda_declarado = st.number_input(
            "Beneficio neto / EBITDA declarado aproximado (€) 🔴:",
            min_value=-500000,
            max_value=10000000,
            value=62000,
            step=2000,
        )

    # Cálculos automáticos de balance
    costes_totales = coste_personal + coste_compras_recambios + gastos_fijos
    resultado_teorico = facturacion_anual - costes_totales
    discrepancia_contable = abs(resultado_teorico - margen_ebitda_declarado)
    facturacion_por_empleado = facturacion_anual / tamano_equipo if tamano_equipo > 0 else 0
    margen_bruto_pct = ((facturacion_anual - coste_compras_recambios) / facturacion_anual) * 100 if facturacion_anual > 0 else 0

    st.markdown("##### 🟢 Indicadores Financieros Derivados en Tiempo Real:")
    cf1, cf2, cf3 = st.columns(3)
    cf1.metric("Facturación por Empleado", f"{facturacion_por_empleado:,.0f} €/año")
    cf2.metric("Margen Bruto de Contribución", f"{margen_bruto_pct:.1f} %")
    cf3.metric("Resultado Contable Calculado", f"{resultado_teorico:,.0f} €")

    if discrepancia_contable > 5000:
        st.warning(
            f"⚠️ **Inconsistencia contable:** Ventas ({facturacion_anual:,.0f} €) - Gastos ({costes_totales:,.0f} €) = {resultado_teorico:,.0f} €, lo que difiere del Beneficio declarado ({margen_ebitda_declarado:,.0f} €). Se activará la advertencia de cautela contable en el informe."
        )

    with st.expander("➕ Añadir datos avanzados de cobros y circulante (Mejora la precisión del análisis)"):
        dias_cobro = st.number_input(
            "Días medios de cobro a clientes (DSO):",
            min_value=0,
            max_value=365,
            value=65,
        )
        saldo_pendiente_cobro = st.number_input(
            "Importe aproximado pendiente de cobro fuera de plazo (€):",
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
    st.markdown("#### ⏱️ Circuito Comercial y Cuello de Botella Operativo")
    op1, op2, op3 = st.columns(3)
    with op1:
        presupuestos_mes = st.number_input(
            "Nº aproximado de presupuestos emitidos al mes 🔴:",
            min_value=1,
            max_value=5000,
            value=25,
        )
        tasa_conversion_presupuestos = st.slider(
            "% de presupuestos que el cliente acaba aceptando 🔴:",
            min_value=5,
            max_value=100,
            value=35,
        )
        ticket_medio_operacion = st.number_input(
            "Ticket medio de servicio / factura (€) 🔴:",
            min_value=10,
            max_value=50000,
            value=1450,
            step=50,
        )
    with op2:
        horas_perdidas_dia = st.number_input(
            "Horas/día dedicadas a presupuestos, citas y gestión administrativa 🔴:",
            min_value=0.5,
            max_value=16.0,
            value=3.5,
            step=0.5,
        )
        quien_hace_presupuestos = st.selectbox(
            "¿Quién prepara habitualmente los presupuestos técnicos? 🔴:",
            [
                "El propio Gerente / Dueño",
                "Técnicos oficiales en horas de taller/campo",
                "Personal administrativo",
                "Departamento comercial dedicado",
            ],
        )
        precio_hora_mano_obra = st.number_input(
            "Tarifa oficial mano de obra cobrada (€/hora sin IVA) 🔴:",
            min_value=15,
            max_value=300,
            value=42,
            step=1,
        )
    with op3:
        tiempo_cierre_factura = st.selectbox(
            "Tiempo desde que se finaliza un trabajo hasta que se emite la factura 🔴:",
            [
                "El mismo día (in situ o automático)",
                "Entre 24 y 48 horas",
                "Entre 3 y 7 días",
                "A final de mes por lotes",
            ],
        )
        origen_clientes = st.selectbox(
            "Canal principal de llegada de nuevos clientes 🔴:",
            [
                "Recomendaciones de clientes existentes (Boca a boca)",
                "Búsqueda local en Google / Web",
                "Prospección comercial directa",
                "Plataformas intermediarias / Subcontratación",
            ],
        )
        stack_tecnologico = st.selectbox(
            "Nivel tecnológico actual de la empresa 🔴:",
            [
                "Partes de trabajo en papel y hojas de cálculo (Excel/Sheets)",
                "Software de gestión local de escritorio no conectado",
                "Herramientas SaaS en la nube sin integrar entre sí",
                "ERP / Software FSM integral con sincronización móvil",
            ],
        )

    friccion_operativa = st.text_area(
        "Describe con tus palabras el mayor cuello de botella o fuga de tiempo de la operativa diaria 🔴:",
        value="Los partes de trabajo en papel tardan varios días en procesarse. Se pierden 3,5 h diarias elaborando presupuestos a medida que no se aceptan. Hay descontrol de material en las furgonetas y se pierden horas en segundas visitas.",
        height=90,
    )

# =====================================================================
# FASE 4: CLIENTES, COMPETENCIA Y VENTAJA COMPETITIVA
# =====================================================================
with tab_mkt:
    st.markdown("#### 👥 Base de Clientes, Competencia y Diferenciación")
    m1, m2 = st.columns(2)
    with m1:
        porcentaje_b2c = st.slider(
            "% de facturación procedente de Particulares (B2C) 🔴:",
            min_value=0,
            max_value=100,
            value=40,
        )
        porcentaje_b2b = 100 - porcentaje_b2c
        st.caption(f"Facturación procedente de Empresas / Terciario (B2B): **{porcentaje_b2b}%**")

        ingresos_recurrentes_pct = st.slider(
            "% de ingresos que provienen de contratos de mantenimiento o cuotas fijas 🔴:",
            min_value=0,
            max_value=100,
            value=15,
        )
    with m2:
        competidor_referencia = st.text_input(
            "Mayor amenaza o competidor de referencia en tu zona 🔴:",
            value="Grandes empresas de servicios energéticos y comercializadoras con contratos cerrados de mantenimiento",
        )
        ventaja_competitiva = st.text_input(
            "Ventaja competitiva actual (¿Por qué os compran a vosotros?) 🔴:",
            value="Rapidez técnica con respuesta en menos de 3 horas para averías urgentes en hostelería",
        )

    with st.expander("➕ Detalle de concentración de clientes (Mejora la precisión)"):
        top5_concentracion = st.slider(
            "% de facturación que concentran los 5 mayores clientes:",
            min_value=5,
            max_value=100,
            value=30,
        )
        if top5_concentracion != 30:
            score_precision += 5

# =====================================================================
# FASE 5: ESTRATEGIA, VISIÓN 3 AÑOS E INVERSIÓN (112-116)
# =====================================================================
with tab_vision:
    st.markdown("#### 🎯 Visión Directiva, Objetivos y Capacidad Financiera")
    v1, v2 = st.columns(2)
    with v1:
        presupuesto_disponible = st.number_input(
            "Presupuesto máximo de inversión en modernización para los próximos 12 meses (€) 🔴:",
            min_value=0,
            max_value=500000,
            value=6500,
            step=500,
        )
        horizonte = st.slider(
            "Horizonte temporal del análisis de prospectiva (años) 🔴:",
            min_value=1,
            max_value=5,
            value=3,
        )
        objetivo_principal_crecimiento = st.selectbox(
            "Prioridad estratégica principal para los próximos años 🔴:",
            [
                "Aumentar margen neto y rentabilidad sin aumentar plantilla",
                "Crecer en facturación y captar cuota de mercado en B2B",
                "Reducir la dependencia del dueño en el día a día operativo",
                "Optimizar costes y eliminar ineficiencias de tiempo",
            ],
        )

    with v2:
        st.markdown("##### 🔮 Preguntas Clave de Dirección General:")
        pregunta_115_inaccion = st.text_area(
            "Si la empresa no realiza ningún cambio en los próximos 3 años, ¿qué crees que ocurrirá? 🔴:",
            value="Los márgenes seguirán cayendo por el encarecimiento de la mano de obra, los competidores grandes captarán a nuestros clientes con ofertas empaquetadas y el negocio perderá rentabilidad.",
            height=70,
        )
        pregunta_116_deseo = st.text_area(
            "Si pudieras solucionar un solo problema de la empresa mañana por la mañana, ¿cuál sería? 🔴:",
            value="Eliminar por completo el tiempo que paso presupuestando averías que no se aprueban y cobrar los trabajos terminados en menos de 24 horas.",
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
        st.markdown(f"**Precisión del Diagnóstico: {score_precision}%** 🟢 (Estándar Directivo)")
    elif score_precision >= 65:
        st.markdown(f"**Precisión del Diagnóstico: {score_precision}%** 🟡 (Nivel Avanzado)")
    else:
        st.markdown(f"**Precisión del Diagnóstico: {score_precision}%** 🟠 (Diagnóstico Preliminar)")

st.caption("Aportar estados contables (PDF/Excel) o datos de cobro permite elevar el nivel de rigor del estudio al 100%.")

# =====================================================================
# FUNCIONES GRÁFICAS (PLOTLY)
# =====================================================================
def render_trend_radar(trends_data):
    horizon_map = {"Act": 1, "Prepare": 2, "Watch": 3}
    quadrant_angle = {
        "Tecnología": 45,
        "Operaciones": 135,
        "Modelo de Negocio": 225,
        "Mercado / Cliente": 315,
    }

    plot_rows = []
    for t in trends_data:
        base_r = horizon_map.get(t.get("horizon", "Prepare"), 2)
        base_theta = quadrant_angle.get(t.get("quadrant", "Tecnología"), 45)
        impact = t.get("impact", 5)

        r_jitter = base_r + (impact - 5) * 0.05
        theta_jitter = (base_theta + (hash(t.get("name", "")) % 40) - 20) % 360

        plot_rows.append({
            "name": t.get("name"),
            "r": r_jitter,
            "theta": theta_jitter,
            "horizon": t.get("horizon"),
            "quadrant": t.get("quadrant"),
            "impact": impact,
        })

    df = pd.DataFrame(plot_rows)
    fig = go.Figure()

    for q_name, angle in quadrant_angle.items():
        sub_df = df[df["quadrant"] == q_name]
        fig.add_trace(
            go.Scatterpolar(
                r=sub_df["r"],
                theta=sub_df["theta"],
                mode="markers+text",
                name=q_name,
                text=sub_df["name"],
                textposition="top center",
                marker=dict(size=sub_df["impact"] * 2.5, line=dict(width=1)),
                hovertemplate="<b>%{text}</b><br>Cuadrante: "
                + q_name
                + "<br>Horizonte: %{customdata[0]}<extra></extra>",
                customdata=sub_df[["horizon"]],
            )
        )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 3.5],
                tickvals=[1, 2, 3],
                ticktext=[
                    "CENTRO: ACTUAR AHORA",
                    "MEDIO: PREPARARSE",
                    "EXTERIOR: VIGILAR",
                ],
            ),
            angularaxis=dict(
                tickvals=[45, 135, 225, 315],
                ticktext=[
                    "Tecnología",
                    "Operaciones",
                    "Modelo de Negocio",
                    "Mercado / Cliente",
                ],
                direction="clockwise",
            ),
        ),
        showlegend=True,
        title="Trend Radar: Taxonomía de Adopción e Impacto",
        height=560,
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
    media_scores = gap_data.get("benchmark_sectorial", [5, 5, 5, 5, 4])
    aspiracional_scores = gap_data.get("benchmark_aspiracional", [8, 8, 8, 8, 8])

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=pyme_scores,
            theta=categories,
            fill="toself",
            name="Tu Empresa (Auditada)",
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=media_scores,
            theta=categories,
            fill="toself",
            name="Media Sectorial Estimada",
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=aspiracional_scores,
            theta=categories,
            fill="toself",
            name="Benchmark Aspiracional de Referencia",
        )
    )

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=True,
        title="Matriz de Brecha Operativa: Posición Real vs. Benchmark Aspiracional",
        height=450,
    )
    return fig


# =====================================================================
# EJECUCIÓN DEL ANÁLISIS
# =====================================================================
if st.button(
    "🚀 Ejecutar Auditoría Industrial & Generar Informe de Strategic Foresight",
    type="primary",
    use_container_width=True,
):
    if not api_key_usuario:
        st.error("⚠️ Es obligatorio introducir tu API Key de Gemini en la barra lateral izquierda.")
    else:
        with st.spinner("Auditando unit economics, analizando balance y proyectando escenarios de adopción tecnológica..."):
            try:
                cliente = genai.Client(api_key=api_key_usuario)

                # Construcción del prompt de auditoría
                prompt_completo = f"""
Eres un Socio Director de Consultoría de Operaciones y Strategic Foresight de máximo nivel (estándar Roland Berger, McKinsey, ITONICS).
Dispones de los DATOS FACILITADOS POR LA EMPRESA. Tu obligación es mantener la máxima honestidad intelectual y rigor metodológico.

======================================================================
DATOS AUDITADOS DE LA EMPRESA (BASELINE DECLARADO):
======================================================================
- Actividad / Especialidad: 🟢 {sector} | {subsector}
- Ámbito territorial: 🟢 {pais_region}
- Año de fundación: 🟢 {ano_creacion}
- Plantilla total: 🟢 {tamano_equipo} empleados (Operarios directos en campo: 🟢 {operarios_directos} | Admin: 🟢 {personal_admin} | Comercial: 🟢 {personal_comercial})
- Flota de vehículos: 🟢 {num_vehiculos} furgonetas/vehículos (Control de stock: 🟢 {control_stock_vehiculos})
- Facturación último año: 🟢 {facturacion_anual:,} € (Año anterior: 🟢 {facturacion_anterior:,} €)
- Coste anual personal (Nóminas + SS): 🟢 {coste_personal:,} €
- Gasto en materiales / compras: 🟢 {coste_compras_recambios:,} €
- Gastos fijos operativos: 🟢 {gastos_fijos:,} €
- Beneficio neto / EBITDA declarado: 🟢 {margen_ebitda_declarado:,} €
- Facturación calculada por empleado: 🟡 {facturacion_por_empleado:,.0f} €/año
- Margen bruto de contribución calculado: 🟡 {margen_bruto_pct:.1f}%
- Ticket medio por servicio: 🟢 {ticket_medio_operacion} €
- Presupuestos al mes: 🟢 {presupuestos_mes} emitidos (Aceptación declarada: 🟢 {tasa_conversion_presupuestos}%)
- Horas/día dedicadas a tareas no facturables: 🟢 {horas_perdidas_dia} h/día (Declaradas por gerencia)
- Quién elabora los presupuestos: 🟢 {quien_hace_presupuestos}
- Tarifa cobrada por hora de mano de obra: 🟢 {precio_hora_mano_obra} €/h (sin IVA)
- Tiempo entre trabajo y factura: 🟢 {tiempo_cierre_factura}
- Canal principal de llegada: 🟢 {origen_clientes}
- Nivel tecnológico actual: 🟢 {stack_tecnologico}
- Cuello de botella declarado: 🟢 {friccion_operativa}
- Mix de clientes: 🟢 {porcentaje_b2c}% Particulares (B2C) / 🟢 {porcentaje_b2b}% Empresas (B2B)
- Ingresos recurrentes por contratos: 🟢 {ingresos_recurrentes_pct}%
- Amenaza / Competidor declarado: 🟢 {competidor_referencia}
- Ventaja competitiva actual: 🟢 {ventaja_competitiva}
- Presupuesto de inversión 12m: 🟢 {presupuesto_disponible:,} €
- Horizonte temporal: 🟢 {horizonte} años
- Prioridad estratégica declarada: 🟢 {objetivo_principal_crecimiento}
- Percepción del Gerente si no hace nada a 3 años: 🟢 "{pregunta_115_inaccion}"
- Deseo prioritario del Gerente: 🟢 "{pregunta_116_deseo}"
- Nivel de precisión del cuestionario: 🟢 {score_precision}%

======================================================================
REGLAS OBLIGATORIAS (PROHIBICIONES Y ESTILO DE RIGOR):
======================================================================
1. LEYENDA OBLIGATORIA AL PRINCIPIO:
   🟢 Dato real de la empresa
   🔵 Fuente externa contrastada
   🟡 Estimación propia (cálculo derivado)
   🟠 Hipótesis a comprobar
   🟣 Objetivo deseado

2. CONTROL DE INCONSISTENCIAS FINANCIERAS:
   - Facturación declarada: {facturacion_anual:,} €. Gastos declarados: {costes_totales:,} €. Resultado teórico: {resultado_teorico:,} €. Beneficio declarado: {margen_ebitda_declarado:,} €.
   - Si no cuadra, incluye un aviso explícito:
     "⚠️ Limitación de los datos económicos: Los gastos declarados y la facturación no coinciden exactamente con el beneficio indicado. Por prudencia contable, este informe se enfoca en tiempos productivos, capacidad instalada y márgenes unitarios hasta auditar la cuenta de pérdidas y ganancias definitiva."

3. PROHIBICIÓN DE SUMAR MAGNITUDES HETEROGÉNEAS (COSTE DE INACCIÓN):
   - PROHIBIDO sumar salarios pagados, facturación cesante y multas teóricas en una cifra global.
   - Presenta una tabla desagregada:
     * Coste salarial directo identificable (horas dedicadas x coste hora de nómina).
     * Capacidad potencial no monetizada (facturación cesante máxima teórica, sujeta a demanda).
     * Exposición regulatoria (riesgo potencial en caso de inspección, no dinero perdido).
     * Total: Declarar expresamente "No sumables directamente por responder a conceptos contables distintos".

4. REGULACIÓN SIN EXAGERAR MULTAS:
   - Analiza Veri*factu (RD 1007/2023) y Facturación Electrónica B2B en sus plazos reales para este tramo de plantilla.
   - Trata las posibles sanciones como "riesgo regulatorio sujeto a inspección y plazos de subsanación", nunca como pérdida segura inmediata.

5. PRAGMATISMO TECNOLÓGICO Y CERO HYPE:
   - En empresas de este tamaño está PROHIBIDO prescribir RFID o telemetría costosa; prescribe "Control digital de stock en furgonetas mediante códigos QR y app móvil".
   - En la Fase 1, PROHIBIDO hablar de "Tarificadores por IA"; prescribe "Presupuestación paramétrica estandarizada / reglas lógicas en software FSM".
   - Prohibida la palabra "Moat" (usa "Ventaja competitiva actual").
   - Prohibido el uso de términos alarmistas ("quiebra inminente", "fuga masiva", "extinción").

6. CONTRASTE DE LA VISIÓN DEL GERENTE:
   - Compara explícitamente lo que el gerente teme que pase a 3 años (pregunta 115) y lo que desearía solucionar (pregunta 116) con los datos cuantitativos del diagnóstico.

7. ROADMAP CON PROPIETARIOS Y PROGRESIÓN DE KPIS:
   - Cada fase a 30, 90 y 180 días debe incluir: Acción | Responsable formal | Requisito previo | KPI concreto (De X baseline a Y objetivo).
   - Presupuesto desglosado en CAPEX y OPEX acotado estrictamente a los 🟢 {presupuesto_disponible:,} € disponibles.
   - Tabla de sensibilidad de ROI al 25%, 50% y 75% de recuperación horaria.

8. FORMATO JSON OBLIGATORIO PARA PLOTLY:
   - Inicia obligatoriamente con el bloque ```json ... ```:
     {{
       "trends": [
         {{"name": "Nombre claro", "quadrant": "Tecnología"|"Operaciones"|"Modelo de Negocio"|"Mercado / Cliente", "horizon": "Act"|"Prepare"|"Watch", "impact": 1-10}}
       ],
       "gap_analysis": {{
         "pyme": [números 1-10],
         "benchmark_sectorial": [números 1-10],
         "benchmark_aspiracional": [números 1-10]
       }}
     }}
     Orden exacto del gap_analysis: [Digitalización, Eficiencia Operativa, Control de Margen, Cartera B2B, Agilidad Estratégica].

======================================================================
ESTRUCTURA DEL INFORME (15 MÓDULOS DE ALTO RIGOR):
======================================================================
# INFORME DE AUDITORÍA INDUSTRIAL, STRATEGIC FORESIGHT Y BENCHMARKING

## 0. Ficha Metodológica, Nivel de Confianza y Alcance
(Leyenda formal de colores, nivel de precisión auditado: 🟢 {score_precision}%, y aviso de consistencia contable).

## RESUMEN EJECUTIVO: 4 DECISIONES DIRECTIVAS CLAVE
(Tabla: Decisión | Cuándo ponerla en marcha | Responsable | Coste estimado | Impacto en Margen).
(Contraste con la respuesta del Gerente a la pregunta 116).

## 1. Auditoría Operativa & Unit Economics Reales
(Análisis de la estructura de explotación: ventas, mano de obra, consumibles, gastos fijos y facturación por empleado).
(Cálculo de horas no facturables declaradas: 🟠 {horas_perdidas_dia * 220:.0f} h/año, distinguiendo coste salarial directo de facturación cesante teórica).

## 2. Contexto Macroeconómico, Demografía y Presión Regulatoria ({pais_region})
(Análisis real de Veri*factu, Factura Electrónica B2B y convenios colectivos del sector aplicables).

## 3. Benchmarking Sectorial: Dónde estamos vs. Dónde queremos estar
(Tabla: Indicador | Tu Empresa | Media Sectorial Estimada | Benchmark Aspiracional | Fuente / Método).

## 4. Dos Casos Reales de Buenas Prácticas Sectoriales
(Dos ejemplos de empresas del sector en Europa o Norteamérica, qué hicieron y qué parte exacta es transferible a esta empresa).

## 5. Taxonomía de Tendencias y Análisis "¿Y esto qué significa?"
(Explicación práctica de las tendencias del sector con su implicación directa en decisiones de gerencia).

## 6. Radar de Tendencias: Dónde enfocar los recursos
(Matriz: Actuar ya / Prepararse / Vigilar y matriz Impacto x Incertidumbre).

## 7. Análisis de Brecha Operativa (Gap Analysis Cuantitativo)
(Explicación detallada de las 5 dimensiones del gráfico polar de brecha).

## 8. Cuatro Escenarios Plausibles de Futuro (2x2 Matrix)
(Cruce de las 2 mayores incertidumbres del sector con niveles de plausibilidad y señales tempranas de confirmación).
(Contraste con la visión del Gerente de la pregunta 115).

## 9. Backcasting Inverso: Del Futuro al Presente (Horizonte {horizonte} Años)
(Objetivo consolidado a {horizonte} años y retroceso metódico: qué debe estar cerrado en el Año 2 y en el Año 1).

## 10. Matriz de Decisión Tecnológica: Build / Buy / Partner / Kill
(Qué procesos crear internamente, qué software adquirir, qué alianzas forjar y qué tareas manuales erradicar de inmediato).

## 11. Sistema de Disparadores y Alertas Tempranas
(Señales objetivas del mercado o costes que deben obligar al gerente a ajustar el rumbo).

## 12. Matriz de Coste de Inacción Desagregada
(Tabla a 12, 24 y 36 meses sin sumar conceptos heterogéneos: coste salarial improductivo, ingresos cesantes potenciales y riesgo regulatorio).

## 13. Vías de Financiación Pública y Optimización Fiscal ({pais_region})
(Líneas de ayuda reales autonómicas, deducciones y bonificaciones de formación continua FUNDAE).

## 14. Gestión Cultural del Cambio y Adopción del Equipo
(Protocolo de incentivos y formación para técnicos de campo, administración y relación con clientes tradicionales).

## 15. Plan de Acción Ejecutivo: Playbook 30 - 90 - 180 Días
(Cronograma con acciones, responsables formales, requisitos técnicos previos, KPIs con progresión y desglose de CAPEX/OPEX).
(Tabla de sensibilidad del ROI neto con recuperación horaria al 25%, 50% y 75% y cálculo prudente de payback).
"""

                # Si el usuario subió un documento contable, lo adjuntamos a la llamada multimodal
                partes_contenido = []
                if archivo_subido is not None:
                    bytes_archivo = archivo_subido.read()
                    mime_type = archivo_subido.type
                    partes_contenido.append(
                        types.Part.from_bytes(data=bytes_archivo, mime_type=mime_type)
                    )
                    prompt_completo += "\n\nDOCUMENTO CONTABLE ADJUNTO: Utiliza este archivo para cotejar y verificar las partidas de ingresos, gastos y márgenes reales de la empresa."

                partes_contenido.append(prompt_completo)

                # Bucle de resiliencia ante saturación de servidores (503)
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
                    raise Exception("Servidores de IA temporalmente saturados. Por favor, reintenta en unos instantes.")

                texto_salida = respuesta.text

                # Extracción de JSON para renderizar los gráficos de Plotly
                patron_json = r"```json\s*(\{.*?\})\s*```"
                match = re.search(patron_json, texto_salida, re.DOTALL)

                if match:
                    json_str = match.group(1)
                    datos_graficos = json.loads(json_str)

                    st.success("✅ Auditoría industrial y Strategic Foresight procesados exitosamente.")

                    # Despliegue de los dos radares interactivos
                    st.subheader("📊 Visualización Estratégica de Posición y Tendencias")
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

                    # Renderizado del informe en Markdown limpio sin el bloque JSON
                    informe_markdown = re.sub(patron_json, "", texto_salida, flags=re.DOTALL).strip()
                    st.markdown(informe_markdown)

                else:
                    st.markdown(texto_salida)

            except Exception as e:
                st.error(f"Error durante el procesamiento: {e}")
