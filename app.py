import json
import re
from google import genai
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Strategic Foresight & Industrial Audit",
    page_icon="🧭",
    layout="wide",
)

st.title("🧭 Radar Estratégico & Auditoría de Competitividad PYME")
st.markdown(
    "Plataforma de **Auditoría Cuantitativa, Benchmarking Sectorial y Strategic Foresight** (Estándar Roland Berger / ITONICS)."
)
st.markdown("---")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🔐 Acceso y Configuración")
    api_key_usuario = st.text_input(
        "API Key de Gemini:",
        type="password",
        help="Introduce tu clave personal de Google AI Studio.",
    )
    st.markdown("---")
    st.markdown("### Taxonomía de Rigor Operativo")
    st.caption(
        "• **🟢 Datos Observados:** Cifras directas de la empresa.\n"
        "• **🔵 Benchmarks Sectoriales:** Estadísticas oficiales del país.\n"
        "• **🟠 Derivaciones Matemáticas:** Fórmulas financieras explícitas.\n"
        "• **🔴 Proyecciones:** Modelado de sensibilidad y escenarios."
    )

# --- RECOGIDA DE DATOS TÉCNICOS INTEGRAL (4 PESTAÑAS) ---
st.subheader("📋 Formulario de Auditoría y Parámetros Contables Reales")

tab_fin, tab_ops, tab_mkt, tab_vision = st.tabs([
    "1. Datos Financieros & Costes Reales",
    "2. Operaciones & Cuello de Botella",
    "3. Mercado, Competencia & País",
    "4. Capacidad de Inversión & Horizonte",
])

with tab_fin:
    st.markdown("#### Balance y Estructura de Costes (Cifras Anuales)")
    c1, c2, c3 = st.columns(3)
    with c1:
        facturacion_anual = st.number_input(
            "Facturación anual exacta (€):",
            min_value=10000,
            max_value=50000000,
            value=210000,
            step=5000,
        )
        coste_personal = st.number_input(
            "Gasto anual en personal (Bruto + Seg. Social) (€):",
            min_value=5000,
            max_value=30000000,
            value=84000,
            step=2000,
        )
    with c2:
        coste_compras_recambios = st.number_input(
            "Gasto anual en consumibles / compras / recambios (€):",
            min_value=0,
            max_value=30000000,
            value=78000,
            step=2000,
        )
        gastos_fijos = st.number_input(
            "Gastos fijos anuales (Alquiler, suministros, seguros, gestoría) (€):",
            min_value=1000,
            max_value=10000000,
            value=28000,
            step=1000,
        )
    with c3:
        margen_ebitda_declarado = st.number_input(
            "Beneficio neto antes de impuestos aproximado (€):",
            min_value=-500000,
            max_value=10000000,
            value=20000,
            step=1000,
        )
        ticket_medio_operacion = st.number_input(
            "Ticket medio real por cliente / factura (€):",
            min_value=10,
            max_value=50000,
            value=220,
            step=10,
        )

with tab_ops:
    st.markdown("#### Capacidad Operativa y Fricción Diaria")
    c4, c5, c6 = st.columns(3)
    with c4:
        sector = st.text_input(
            "Sector y nicho de actividad:",
            value="Taller mecánico multimarca y mecánica rápida",
        )
        tamano_equipo = st.number_input(
            "Número total de empleados en plantilla:",
            min_value=1,
            max_value=500,
            value=3,
        )
        operarios_directos = st.number_input(
            "De ellos, ¿cuántos producen directamente (técnicos/operarios)?:",
            min_value=1,
            max_value=500,
            value=2,
        )
    with c5:
        precio_hora_mano_obra = st.number_input(
            "Tarifa oficial cobrada por hora de mano de obra (€/hora sin IVA):",
            min_value=15,
            max_value=300,
            value=48,
            step=1,
        )
        horas_perdidas_dia = st.number_input(
            "Horas dedicadas al día a llamadas, presupuestos no aceptados y citas:",
            min_value=0.0,
            max_value=16.0,
            value=2.5,
            step=0.5,
        )
        tasa_conversion_presupuestos = st.slider(
            "% de presupuestos emitidos que el cliente acaba aceptando:",
            min_value=5,
            max_value=100,
            value=40,
        )
    with c6:
        stack_tecnologico = st.selectbox(
            "Stack tecnológico actual:",
            [
                "Hojas de cálculo (Excel/Sheets) y papel físico",
                "Software de gestión local antiguo (no conectado/no web)",
                "Software cloud básico sin automatizaciones",
                "ERP/CRM moderno integrado por APIs",
            ],
        )
        friccion_operativa = st.text_area(
            "Descripción detallada del cuello de botella principal:",
            value="Interrupciones continuas al teléfono de clientes pidiendo presupuesto o consultando estado de su vehículo. Los operarios paran de trabajar para responder llamadas. Dificultad para retener mecánicos cualificados.",
            height=100,
        )

with tab_mkt:
    st.markdown("#### Mercado, Geografía y Base de Clientes")
    c7, c8 = st.columns(2)
    with c7:
        pais_region = st.text_input(
            "País y región operativa:", value="España (Comunidad de Madrid)"
        )
        porcentaje_b2c = st.slider(
            "% de facturación que proviene de Particulares (B2C):",
            min_value=0,
            max_value=100,
            value=75,
        )
        porcentaje_b2b = 100 - porcentaje_b2c
        st.caption(
            f"Facturación a Empresas / Flotas (B2B): **{porcentaje_b2b}%**"
        )
    with c8:
        competidor_referencia = st.text_input(
            "Competidor de referencia o mayor amenaza directa:",
            value="Redes de mecánica rápida (Norauto, Midas, FeuVert) y talleres de concesionario oficial",
        )
        ventaja_competitiva = st.text_input(
            "Motivo real por el que el cliente actual os elige (Moat):",
            value="Confianza de más de 12 años, trato personal directo y honestidad en el diagnóstico",
        )

with tab_vision:
    st.markdown("#### Restricciones de Inversión y Alcance")
    c9, c10 = st.columns(2)
    with c9:
        presupuesto_disponible = st.number_input(
            "Presupuesto real máximo para inversión tecnológica/procesos en 12 meses (€):",
            min_value=0,
            max_value=500000,
            value=3500,
            step=500,
        )
    with c10:
        horizonte = st.slider(
            "Horizonte temporal de prospección (años):",
            min_value=1,
            max_value=5,
            value=3,
        )

st.markdown("---")


# --- FUNCIONES DE VISUALIZACIÓN INTERACTIVA (PLOTLY) ---
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
            "description": t.get("description", ""),
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
                + "<br>Horizonte: %{customdata[0]}<br>Impacto: %{customdata[1]}/10<extra></extra>",
                customdata=sub_df[["horizon", "impact"]],
            )
        )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 3.5],
                tickvals=[1, 2, 3],
                ticktext=["ACT (0-6m)", "PREPARE (6-18m)", "WATCH (18m+)"],
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
        title="Trend Radar Concéntrico (Estándar TRENDONE / ITONICS)",
        height=580,
    )
    return fig


def render_gap_radar(gap_data):
    categories = [
        "Madurez Digital",
        "Eficiencia Operativa",
        "Retención de Margen",
        "Diversificación B2B",
        "Agilidad Estratégica",
    ]

    pyme_scores = gap_data.get("pyme", [3, 4, 3, 2, 3])
    media_scores = gap_data.get("media_nacional", [5, 5, 5, 4, 4])
    lideres_scores = gap_data.get("frontera_global", [9, 8, 8, 9, 8])

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
            name="Media Sectorial País",
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=lideres_scores,
            theta=categories,
            fill="toself",
            name="Frontera de Desempeño",
        )
    )

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=True,
        title="Matriz de Brecha Competitiva (Gap Analysis Cuantitativo)",
        height=450,
    )
    return fig


# --- PROCESAMIENTO ANALÍTICO ---
if st.button(
    "🚀 Ejecutar Auditoría Industrial & Generar Informe de Strategic Foresight",
    type="primary",
    use_container_width=True,
):
    if not api_key_usuario:
        st.error(
            "⚠️ Es obligatorio introducir tu API Key de Gemini en la barra lateral izquierda."
        )
    else:
        with st.spinner(
            "Procesando balance contable, calculando unit economics exactos y proyectando radar de prospectiva..."
        ):
            try:
                cliente = genai.Client(api_key=api_key_usuario)

                prompt_completo = f"""
Eres un Socio Director de Consultoría de Operaciones y Strategic Foresight de élite (estándar Roland Berger, McKinsey, ITONICS).
Dispones de los DATOS CONTABLES Y OPERATIVOS REALES Y EXACTOS aportados por la empresa. 

======================================================================
DATOS AUDITADOS DE LA EMPRESA (PROHIBIDO ASUMIR O INVENTAR NÚMEROS):
======================================================================
- Facturación anual real: 🟢 {facturacion_anual:,} €
- Coste salarial total anual (personal + seguridad social): 🟢 {coste_personal:,} €
- Gasto en recambios / compras / COGS anual: 🟢 {coste_compras_recambios:,} €
- Gastos fijos operativos anuales: 🟢 {gastos_fijos:,} €
- Beneficio neto / EBITDA aproximado declarado: 🟢 {margen_ebitda_declarado:,} €
- Ticket medio por factura/cliente: 🟢 {ticket_medio_operacion} €
- Plantilla total: 🟢 {tamano_equipo} personas
- Operarios productivos directos: 🟢 {operarios_directos} personas
- Tarifa cobrada por hora de taller: 🟢 {precio_hora_mano_obra} €/hora (sin IVA)
- Horas diarias perdidas al teléfono / presupuestos no cerrados: 🟢 {horas_perdidas_dia} horas/día
- Días laborables computables: 🟢 220 días/año
- Tasa real de aceptación de presupuestos: 🟢 {tasa_conversion_presupuestos}%
- Stack tecnológico actual: 🟢 {stack_tecnologico}
- Cuello de botella operacional: 🟢 {friccion_operativa}
- Ubicación / País / Región: 🟢 {pais_region}
- Mix de facturación: 🟢 {porcentaje_b2c}% B2C (Particulares) / {porcentaje_b2b}% B2B (Empresas/Flotas)
- Competidor / Amenaza declarada: 🟢 {competidor_referencia}
- Moat / Ventaja declarada: 🟢 {ventaja_competitiva}
- Presupuesto de inversión disponible (12 meses): 🟢 {presupuesto_disponible:,} €
- Horizonte temporal de análisis: 🟢 {horizonte} años

======================================================================
REGLAS ESTRICTAS DE CÁLCULO Y PROTOCOLO EDITORIAL:
======================================================================
1. LEYENDA TIPOGRÁFICA OBLIGATORIA:
   🟢 [DATO OBSERVADO]: Cifras reales facilitadas por la empresa arriba indicadas.
   🔵 [DATO FUENTE EXTERNA]: Benchmarks oficiales (cita: Fuente | Año | Ámbito).
   🟠 [DERIVACIÓN MATEMÁTICA]: Cálculos exactos derivados de los datos reales del cliente.
   🔴 [PROYECCIÓN / ESCENARIO]: Simulación condicional basada en escenarios.
   (Queda PROHIBIDO el uso de 🟡 Supuestos para datos ya aportados).

2. CÁLCULO FINANCIERO Y DE ROI SIN SESGOS:
   - Horas anuales perdidas = 🟢 {horas_perdidas_dia} h/día x 220 días = 🟠 [{horas_perdidas_dia * 220:.0f} horas/año].
   - Coste hora salarial real = 🟢 {coste_personal} € / (🟢 {tamano_equipo} empleados x 1.760 h laborables año) = 🟠 X €/h.
   - Pérdida salarial directa en tareas administrativas = Horas anuales perdidas x Coste hora salarial.
   - Coste de oportunidad (Facturación cesante máxima teórica) = Horas anuales perdidas x 🟢 {precio_hora_mano_obra} €/h.
   - Margen de contribución real de taller = 1 - (🟢 {coste_compras_recambios} / 🟢 {facturacion_anual}).
   - Margen incremental neto = Horas recuperadas facturadas x 🟢 {precio_hora_mano_obra} €/h x Margen de contribución.
   - Beneficio Neto Incremental = Margen incremental - (Coste amortizado software + licencias anuales).
   - ROI = (Beneficio Neto Incremental / 🟢 {presupuesto_disponible} €) x 100.
   - ANÁLISIS DE SENSIBILIDAD: Calcula obligatoriamente el retorno en 3 escenarios de éxito: Recuperando solo el 25%, el 50% y el 75% de las horas perdidas.

3. TABLAS DE BENCHMARKING:
   - La columna de la empresa debe contener ÚNICAMENTE los datos auditados o sus derivados matemáticos directos (Facturación por empleado = 🟢 {facturacion_anual} / 🟢 {tamano_equipo}).
   - Compara contra "Media Sectorial {pais_region}" y "Frontera de Desempeño Digital" indicando la fuente externa o método de contraste.

4. FORMATO DE SALIDA:
   - Comienza obligatoriamente con el bloque ```json ... ``` delimitando los datos para Plotly:
     {{
       "trends": [
         {{"name": "...", "quadrant": "Tecnología"|"Operaciones"|"Modelo de Negocio"|"Mercado / Cliente", "horizon": "Act"|"Prepare"|"Watch", "impact": 1-10, "description": "..."}}
       ],
       "gap_analysis": {{
         "pyme": [números 1-10 auditados],
         "media_nacional": [números 1-10],
         "frontera_global": [números 1-10]
       }}
     }}
     Orden exacto de gap_analysis: [Madurez Digital, Eficiencia Operativa, Retención de Margen, Diversificación B2B, Agilidad Estratégica].
   - Tras el JSON, redacta el informe en Markdown riguroso respetando los 15 apartados numerados.

======================================================================
ESTRUCTURA DEL INFORME (15 MÓDULOS DE ALTO RIGOR):
======================================================================

# INFORME DE AUDITORÍA INDUSTRIAL, STRATEGIC FORESIGHT Y BENCHMARKING
(Ficha Metodológica de entrada: Parámetros del cliente auditados, Fecha de corte, Criterios de scoring 0-10 y Limitaciones del análisis).

## RESUMEN EJECUTIVO & DECISIONES CLAVE
- Tabla de Decisiones Innegociables para Gerencia (Decisión | Plazo de ejecución | Coste Neto Estimado | Impacto en Margen).
- 5 Conclusiones cuantitativas del diagnóstico.

## 1. Auditoría Operativa & Unit Economics Reales
- Desglose contable real: Facturación (🟢 {facturacion_anual:,} €), COGS (🟢 {coste_compras_recambios:,} €), Personal (🟢 {coste_personal:,} €), Gastos Fijos (🟢 {gastos_fijos:,} €) y Margen Neto resultante.
- Cálculo de horas hombre perdidas al año (🟠 {horas_perdidas_dia * 220:.0f} horas) y cuantificación de la pérdida directa de nómina vs. facturación cesante con la tarifa real de 🟢 {precio_hora_mano_obra} €/h.

## 2. Contexto Macroeconómico, Demográfico y Regulatorio ({pais_region})
- 🔵 Regulaciones vigentes: Veri*factu (RD 1007/2023), Facturación Electrónica B2B (Ley Crea y Crece). Requisitos técnicos obligatorios y sanciones reales.
- 🔵 Datos de mercado y convenios colectivos del sector aplicables a su plantilla.

## 3. Benchmarking Sectorial Cuantitativo: Empresa vs. Media vs. Frontera Digital
- Tabla comparativa con datos reales del cliente: Facturación por empleado (🟢 {facturacion_anual / tamano_equipo:,.0f} €), Ticket medio (🟢 {ticket_medio_operacion} €), % B2B (🟢 {porcentaje_b2b}%), Tasa de conversión de presupuestos (🟢 {tasa_conversion_presupuestos}%).
- Comparativa contra Media Nacional y Frontera de Desempeño.

## 4. Frontera de Innovación Internacional (Casos Reales con Nombre Comercial)
- Mínimo 2 casos de estudio reales (Alemania, EE. UU., etc.). Empresa, contexto, solución técnica adoptada y métricas de transferencia aplicables a escala de esta pyme.

## 5. Taxonomía de Tendencias: Macro, Micro & Señales Débiles (Weak Signals)
- Clasificación de tendencias: Evidencia -> Impacto -> Incertidumbre -> Implicación para esta empresa con su estructura de costes.

## 6. Scoring Multidimensional de Tendencias
- Matriz con: Tendencia | Cuadrante | Horizonte (Act/Prepare/Watch) | Impacto (1-10) | Madurez | Grado de Incertidumbre.

## 7. Análisis de Brecha (Gap Analysis) y Conexión con la Acción
- Justificación matemática de las puntuaciones (0 a 10) otorgadas a la empresa a partir de sus datos reales.
- Tabla: Dimensión -> Situación Auditada -> Benchmark -> Gap -> Impacto Económico -> Acción Concreta.

## 8. Modelado de 4 Escenarios Plausibles (2x2 Matrix)
- Cruce de las 2 incertidumbres sectoriales críticas en {pais_region}.
- Matriz con Plausibilidad, Impacto en Margen y Señales tempranas observables de confirmación.

## 9. Backcasting Inverso (Ingeniería Inversa a {horizonte} Años)
- Definición del estado de éxito objetivo a {horizonte} años y condiciones necesarias hacia atrás (Año 2 y Año 1).

## 10. Matriz de Decisión Tecnológica: Build / Buy / Partner / Kill
- Clasificación estricta de procesos y herramientas (Desarrollo interno, Compra SaaS, Alianza, Eliminación inmediata).

## 11. Sistema de Disparadores y Alertas Tempranas (Early Warning Triggers)
- Umbrales objetivos y eventos observables del entorno que forzarán la activación de medidas correctoras.

## 12. Matriz de Coste de Inacción Desagregada
- Desglose riguroso a 12, 24 y 36 meses separando Fuga de Margen Demostrada, Coste de Oportunidad y Exposición Sancionadora.

## 13. Financiación Pública y Optimización Fiscal ({pais_region})
- Vías de financiación vigentes, programas autonómicos y bonificaciones de formación continua (ej. FUNDAE).

## 14. Matriz de Fricción Cultural y Gestión del Cambio
- Resistencias por perfil (Operarios de taller, Gerente, Cliente B2C tradicional) y protocolo de mitigación e incentivos.

## 15. Hoja de Ruta Ejecutiva: Playbook 30 - 90 - 180 Días
- Fases de despliegue con: Tarea, Responsable, Dependencia técnica previa, KPIs de control y Presupuesto (CAPEX vs. OPEX) acotado estrictamente a los 🟢 {presupuesto_disponible:,} € disponibles.
- Análisis de sensibilidad del ROI neto (escenarios al 25%, 50% y 75% de éxito de recuperación horaria).
"""

                respuesta = cliente.models.generate_content(
                    model="gemini-3.6-flash", contents=prompt_completo
                )

                texto_salida = respuesta.text

                # Extraer JSON para los gráficos
                patron_json = r"```json\s*(\{.*?\})\s*```"
                match = re.search(patron_json, texto_salida, re.DOTALL)

                if match:
                    json_str = match.group(1)
                    datos_graficos = json.loads(json_str)

                    st.success("✅ Diagnóstico y Radar procesados exitosamente.")

                    # Despliegue de los Radares interactivos
                    st.subheader("📊 Visualización Gráfica de Prospectiva")
                    col_r1, col_r2 = st.columns(2)

                    with col_r1:
                        if "trends" in datos_graficos:
                            fig_radar = render_trend_radar(
                                datos_graficos["trends"]
                            )
                            st.plotly_chart(fig_radar, use_container_width=True)

                    with col_r2:
                        if "gap_analysis" in datos_graficos:
                            fig_gap = render_gap_radar(
                                datos_graficos["gap_analysis"]
                            )
                            st.plotly_chart(fig_gap, use_container_width=True)

                    st.markdown("---")

                    informe_markdown = re.sub(
                        patron_json, "", texto_salida, flags=re.DOTALL
                    ).strip()
                    st.markdown(informe_markdown)

                else:
                    st.markdown(texto_salida)

            except Exception as e:
                st.error(f"Error durante el procesamiento: {e}")
