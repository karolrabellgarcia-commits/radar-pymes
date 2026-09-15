import json
import re
from google import genai
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Strategic Foresight & Trend Radar",
    page_icon="🧭",
    layout="wide",
)

st.title("🧭 Radar Estratégico de Tendencias e Innovación")
st.markdown(
    "Plataforma de **Strategic Foresight y Benchmarking de Mercado** para PYMES y empresas en crecimiento (Estándar TRENDONE / ITONICS)."
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
    st.markdown("### Taxonomía de Foresight")
    st.caption(
        "• **Act (0-6m):** Adopción inmediata para proteger margen.\n"
        "• **Prepare (6-18m):** Pruebas de concepto y pilotos.\n"
        "• **Watch (18m+):** Vigilancia tecnológica y regulatoria."
    )

# --- ENTRADA DE DATOS GUIADA EN PESTAÑAS ---
st.subheader("📋 Recogida de Datos de la Empresa")

tab_ops, tab_mkt, tab_vision = st.tabs([
    "1. Radiografía Operativa & Finanzas",
    "2. Mercado, Competencia & País",
    "3. Objetivos & Restricciones",
])

with tab_ops:
    col1, col2 = st.columns(2)
    with col1:
        sector = st.text_input(
            "Sector y nicho específico:",
            placeholder="Ej: Taller mecánico multimarca y mantenimiento de flotas ligeras",
        )
        modelo_ingresos = st.selectbox(
            "Modelo principal de ingresos:",
            [
                "Servicios profesionales por horas o proyectos",
                "Venta B2B / Distribución mayorista",
                "Comercio minorista / Venta en tienda física",
                "Comercio electrónico (B2C)",
                "Suscripción / Mantenimiento recurrente",
                "Mixto (Servicios + Venta de producto)",
            ],
        )
        rango_facturacion = st.selectbox(
            "Facturación anual actual:",
            [
                "Menos de 100.000 €",
                "100.000 € - 300.000 €",
                "300.000 € - 1.000.000 €",
                "1.000.000 € - 3.000.000 €",
                "Más de 3.000.000 €",
            ],
        )
    with col2:
        tamano_equipo = st.selectbox(
            "Tamaño del equipo de trabajo:",
            [
                "1 persona (Fundador solo)",
                "2 a 5 personas",
                "6 a 15 personas",
                "Más de 15 personas",
            ],
        )
        stack_tecnologico = st.selectbox(
            "Nivel actual de madurez tecnológica:",
            [
                "Bajo: Procesos manuales, papel o libretas",
                "Medio-Bajo: Hojas de cálculo (Excel/Sheets) y comunicación por teléfono",
                "Medio: Software de gestión local o no conectado",
                "Avanzado: Herramientas SaaS en la nube y conectadas por API",
            ],
        )
        friccion_operativa = st.text_area(
            "Cuello de botella principal y fugas de tiempo/margen:",
            placeholder="Ej: Mucho tiempo al teléfono atendiendo citas y presupuestos, falta de mecánicos cualificados y dificultad para retenerlos.",
            height=100,
        )

with tab_mkt:
    col3, col4 = st.columns(2)
    with col3:
        pais_region = st.text_input(
            "País y región de operación:",
            placeholder="Ej: España (Comunidad de Madrid)",
            value="España",
        )
        tipo_cliente = st.selectbox(
            "Composición de la base de clientes:",
            [
                "100% Particulares (B2C)",
                "Mayoría Particulares (70% B2C / 30% B2B)",
                "Equilibrado (50% B2C / 50% B2B)",
                "Mayoría Empresas (30% B2C / 70% B2B)",
                "100% Empresas (B2B)",
            ],
        )
    with col4:
        competidor_referencia = st.text_input(
            "Competidor de referencia o mayor amenaza en tu zona/sector:",
            placeholder="Ej: Grandes cadenas (Norauto, Midas) y talleres oficiales con apps móviles",
        )
        ventaja_competitiva = st.text_input(
            "¿Por qué compran los clientes actuales? (Moat declarado):",
            placeholder="Ej: Confianza personal de muchos años, cercanía física y trato directo",
        )

with tab_vision:
    col5, col6 = st.columns(2)
    with col5:
        presupuesto = st.selectbox(
            "Capacidad de inversión en innovación (próximos 12 meses):",
            [
                "Mínima (< 1.000 € / solo software gratuito o de muy bajo coste)",
                "Moderada (1.000 € - 5.000 €)",
                "Media (5.000 € - 20.000 €)",
                "Alta (> 20.000 €)",
            ],
        )
    with col6:
        horizonte = st.slider(
            "Horizonte temporal de prospectiva (años):",
            min_value=1,
            max_value=5,
            value=3,
        )

st.markdown("---")


# --- FUNCIONES AUXILIARES PARA GRÁFICOS INTERACTIVOS (PLOTLY) ---
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

        # Variación ligera para evitar superposición perfecta
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
            name="Tu Empresa (Actual)",
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
            name="Líderes de Frontera",
        )
    )

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=True,
        title="Matriz de Brecha Competitiva (Gap Analysis)",
        height=450,
    )
    return fig


# --- PROCESAMIENTO ANALÍTICO ---
if st.button(
    "🚀 Generar Análisis de Strategic Foresight & Trend Radar",
    type="primary",
    use_container_width=True,
):
    if not api_key_usuario:
        st.error(
            "⚠️ Es obligatorio introducir tu API Key de Gemini en la barra lateral izquierda."
        )
    elif not sector or not friccion_operativa:
        st.warning(
            "⚠️ Por favor, introduce al menos el Sector y el Cuello de botella principal para procesar el análisis."
        )
    else:
        with st.spinner(
            "Ejecutando motor de Strategic Foresight, calculando taxonomía de tendencias y benchmarking de mercado..."
        ):
            try:
                cliente = genai.Client(api_key=api_key_usuario)

                prompt_completo = f"""
                Eres un socio director de Strategic Foresight y Prospectiva Tecnológica de élite (estándar TRENDONE, ITONICS y Roland Berger).
                Realiza un análisis prospectivo y de benchmarking exhaustivo, ultraespecífico y cuantitativo para esta empresa:

                DATOS DEL CLIENTE:
                - Sector y nicho: {sector}
                - Modelo de ingresos: {modelo_ingresos}
                - Facturación anual: {rango_facturacion}
                - Tamaño del equipo: {tamano_equipo}
                - Madurez tecnológica actual: {stack_tecnologico}
                - Fricción operativa / Cuello de botella: {friccion_operativa}
                - País y mercado geográfico: {pais_region}
                - Perfil de clientes: {tipo_cliente}
                - Competidor / Amenaza declarada: {competidor_referencia}
                - Ventaja competitiva declarada: {ventaja_competitiva}
                - Presupuesto disponible en 12 meses: {presupuesto}
                - Horizonte temporal: {horizonte} años

                REGLAS METODOLÓGICAS:
                1. Al principio de tu respuesta debes incluir un bloque de código JSON con delimitadores ```json ... ``` que contenga:
                   - "trends": Una lista de 6 a 8 tendencias evaluadas. Cada una debe ser un objeto con:
                     {{"name": "Nombre breve", "quadrant": "Tecnología"|"Operaciones"|"Modelo de Negocio"|"Mercado / Cliente", "horizon": "Act"|"Prepare"|"Watch", "impact": 1-10, "description": "Breve descripción"}}
                   - "gap_analysis": Un objeto con:
                     {{"pyme": [5 números de 1 a 10], "media_nacional": [5 números de 1 a 10], "frontera_global": [5 números de 1 a 10]}}
                     en el orden exacto: [Madurez Digital, Eficiencia Operativa, Retención de Margen, Diversificación B2B, Agilidad Estratégica].

                2. A continuación del bloque JSON, desarrolla el informe exhaustivo en Markdown estructurado rigurosamente en los siguientes 15 MÓDULOS DE ALTO IMPACTO:

                # INFORME ESTRATÉGICO DE FORESIGHT Y BENCHMARKING SECTORIAL

                ## 1. Auditoría Operativa & Unit Economics
                (Cálculo explícito en euros de horas perdidas, fugas de margen por fricción y vulnerabilidad operativa).

                ## 2. Macroeconomía, Demografía y Presión Regulatoria ({pais_region})
                (Leyes laborales, directivas ambientales, facturación electrónica, convenios colectivos y demografía del consumidor en su país).

                ## 3. Benchmarking Competitivo Nacional
                (Ratios operativos clave: Facturación por empleado del cliente vs. media nacional vs. top 10% del sector en {pais_region}).

                ## 4. Frontera de Innovación Global (Best Practices Internacionales)
                (Cita al menos 2 casos de estudio reales con nombre comercial de startups o pymes en Alemania, EE. UU. o Países Nórdicos que hayan solucionado este problema).

                ## 5. Taxonomía de Tendencias: Macro, Micro & Weak Signals
                (Desglose analítico de las tendencias mapeadas en el Radar de Prospectiva).

                ## 6. Scoring Multidimensional de Tendencias
                (Tabla Markdown con columnas: Tendencia | Cuadrante | Horizonte | Impacto (1-10) | Madurez | Ajuste Estratégico).

                ## 7. Análisis de Brecha Competitiva (Gap Analysis)
                (Explicación de las 5 dimensiones comparativas de competitividad).

                ## 8. Modelado de 4 Escenarios Plausibles (2x2 Matrix)
                (Cruce de las dos mayores incertidumbres del sector en {pais_region} proyectando 4 cuadrantes de futuro a {horizonte} años).

                ## 9. Backcasting Inverso (Ingeniería Inversa del Futuro a {horizonte} Años)
                (Definición del estado de éxito futuro y qué condiciones obligatorias deben construirse en el Año 2 y Año 1).

                ## 10. Matriz de Decisión: Build / Buy / Partner / Kill
                (Clasificación explícita de qué tecnologías o procesos debe Desarrollar, Comprar SaaS, Subcontratar o Eliminar).

                ## 11. Sistema de Disparadores y Alertas Tempranas (Early Warning Triggers)
                (Eventos observables regulatorios o de mercado que obligan a actuar antes de tiempo).

                ## 12. Matriz de Coste de Inacción (Cost of Inaction)
                (Proyección económica en euros de pérdida de caja y clientes a 12, 24 y 36 meses si la empresa no ejecuta cambios).

                ## 13. Mecanismos de Financiación Pública y Subvenciones ({pais_region})
                (Programas de ayuda a la digitalización, incentivos o deducciones fiscales aplicables a su territorio).

                ## 14. Matriz de Fricción Cultural y Adopción del Cambio
                (Diagnóstico de resistencias del personal, plan de formación y gestión del rechazo del cliente tradicional).

                ## 15. Hoja de Ruta Ejecutiva: Playbook 30 - 90 - 180 Días
                (Plan de choque inmediato, fase de implantación tecnológica y consolidación comercial con presupuesto acotado a {presupuesto}).
                """

                respuesta = cliente.models.generate_content(
                    model="gemini-2.0-flash", contents=prompt_completo
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

                    # Limpiar el bloque JSON del texto para presentar el informe en Markdown limpio
                    informe_markdown = re.sub(
                        patron_json, "", texto_salida, flags=re.DOTALL
                    ).strip()
                    st.markdown(informe_markdown)

                else:
                    # En caso de que el modelo devuelva el texto sin delimitar el JSON
                    st.markdown(texto_salida)

            except Exception as e:
                st.error(f"Error durante el procesamiento: {e}")
