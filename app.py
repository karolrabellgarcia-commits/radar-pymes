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
        "• **🟢 Dato Observado:** Cifras reales aportadas por la empresa.\n"
        "• **🔵 Fuente Externa:** Benchmarks oficiales y contrastados.\n"
        "• **🟠 Derivación Matemática:** Fórmulas financieras explícitas.\n"
        "• **🟡 Supuesto:** Hipótesis de trabajo de partida.\n"
        "• **🔴 Proyección:** Modelado condicional de escenarios."
    )

# --- RECOGIDA DE DATOS CONTABLES Y OPERATIVOS REALES ---
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
            "Gasto anual en personal (Nóminas + Seg. Social) (€):",
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
            "Gastos fijos anuales (Alquiler, suministros, seguros) (€):",
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
            "Horas dedicadas al día a llamadas, presupuestos y citas:",
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
Eres un Socio Director de Consultoría Estratégica y Strategic Foresight de élite (estándar Roland Berger, McKinsey, ITONICS).
Dispones de los DATOS CONTABLES Y OPERATIVOS REALES aportados por la empresa.

======================================================================
DATOS AUDITADOS DE LA EMPRESA (BASELINE DECLARADO):
======================================================================
- Facturación anual real: 🟢 {facturacion_anual:,} €
- Coste salarial total anual (personal + seguridad social): 🟢 {coste_personal:,} €
- Gasto en recambios / compras / COGS anual: 🟢 {coste_compras_recambios:,} €
- Gastos fijos operativos anuales: 🟢 {gastos_fijos:,} €
- Beneficio neto declarado: 🟢 {margen_ebitda_declarado:,} €
- Ticket medio real por factura: 🟢 {ticket_medio_operacion} €
- Plantilla total: 🟢 {tamano_equipo} personas (Operarios directos: 🟢 {operarios_directos})
- Tarifa cobrada por hora de taller: 🟢 {precio_hora_mano_obra} €/hora (sin IVA)
- Horas diarias perdidas al teléfono / presupuestos no cerrados: 🟢 {horas_perdidas_dia} h/día
- Días laborables computables: 🟢 220 días/año
- Tasa de aceptación de presupuestos: 🟢 {tasa_conversion_presupuestos}%
- Stack tecnológico actual: 🟢 {stack_tecnologico}
- Cuello de botella operacional: 🟢 {friccion_operativa}
- Ubicación / Marco geográfico: 🟢 {pais_region}
- Mix de clientes: 🟢 {porcentaje_b2c}% Particulares (B2C) / {porcentaje_b2b}% Empresas (B2B)
- Competidor / Amenaza declarada: 🟢 {competidor_referencia}
- Moat / Ventaja declarada: 🟢 {ventaja_competitiva}
- Presupuesto disponible en 12 meses: 🟢 {presupuesto_disponible:,} €
- Horizonte temporal de análisis: 🟢 {horizonte} años

======================================================================
REGLAS OBLIGATORIAS DE RIGOR Y PROTOCOLO EDITORIAL:
======================================================================
1. LEYENDA TIPOGRÁFICA OBLIGATORIA:
   Cada métrica, cifra o afirmación relevante del informe DEBE ir precedida de uno de estos símbolos:
   🟢 [DATO OBSERVADO]: Cifras reales facilitadas por la empresa arriba indicadas.
   🔵 [DATO FUENTE EXTERNA]: Citas oficiales (especifica: Fuente | Año | Ámbito geográfico).
   🟠 [DERIVACIÓN MATEMÁTICA]: Cálculos exactos derivados de los datos reales del cliente.
   🟡 [SUPUESTO OPERATIVO]: Hipótesis de trabajo de partida (abierta a contraste con el cliente).
   🔴 [PROYECCIÓN / ESCENARIO]: Simulación condicional ("bajo este escenario..."), NUNCA certeza o forecast causal.

2. PROHIBICIÓN RADICAL DE INVENTAR DATOS DEL CLIENTE:
   - Prohibido asumir o inventar datos financieros o de clientes. Si un dato no fue facilitado, clasifícalo como: "🟡 [SUPUESTO OPERATIVO]: Pendiente de validación contable por el cliente" y añade la fórmula para calcularlo.

3. CORRECCIÓN FINANCIERA ESTRICTA (ROI Y COSTE DE INACCIÓN):
   - NUNCA uses "Facturación Recuperada" como beneficio. Facturación ≠ Beneficio.
   - Fórmula de Margen Incremental = Horas Recuperadas Facturables x Tarifa Horaria x Margen de Contribución Real.
   - Beneficio Neto = Margen Incremental - (CAPEX amortizado + OPEX recurrente).
   - ROI (%) = (Beneficio Neto / Inversión Neta Total) x 100.
   - Presenta un análisis de sensibilidad con 3 niveles: Captura del 25%, 50% y 75% de las horas liberadas.
   - Separa nítidamente Pérdida Operativa Real de Coste de Oportunidad Teórico y de Riesgo Sancionador.

4. ESCENARIOS Y LENGUAJE:
   - Elimina afirmaciones categóricas como "quiebra inminente", "va a suceder" o "Top 10% indiscutible".
   - Usa "sugiere", "podría indicar", "bajo este escenario".
   - Sustituye "Top 10%" por "Frontera de Desempeño / Benchmark Aspiracional Digital".

5. FORMATO DE SALIDA:
   - Inicia obligatoriamente con el bloque ```json ... ``` delimitando los datos para los radares Plotly:
     {{
       "trends": [
         {{"name": "...", "quadrant": "Tecnología"|"Operaciones"|"Modelo de Negocio"|"Mercado / Cliente", "horizon": "Act"|"Prepare"|"Watch", "impact": 1-10, "description": "..."}}
       ],
       "gap_analysis": {{
         "pyme": [números 1-10],
         "media_nacional": [números 1-10],
         "frontera_global": [números 1-10]
       }}
     }}
     Orden del gap_analysis: [Madurez Digital, Eficiencia Operativa, Retención de Margen, Diversificación B2B, Agilidad Estratégica].
   - Tras el JSON, redacta el informe en Markdown respetando la estructura indicada.

======================================================================
ESTRUCTURA DEL INFORME (METODOLOGÍA + RESUMEN + 15 MÓDULOS):
======================================================================

# INFORME DE AUDITORÍA INDUSTRIAL, STRATEGIC FORESIGHT Y BENCHMARKING

## FICHA METODOLÓGICA Y LIMITACIONES DEL ESTUDIO
- Objetivo y alcance temporal/geográfico.
- Fecha de corte de la información.
- Baseline del cliente auditado.
- Metodología de Scoring (0 a 10): Define los 5 niveles (0=Inexistente, 2=Inicial/Manual, 4=Básico reactivo, 6=Desarrollado, 8=Avanzado, 10=Frontera).
- Definición formal de "Frontera de Desempeño".
- Limitaciones metodológicas del estudio.

## RESUMEN EJECUTIVO & DECISIONES CLAVE
- Tabla: Decisiones Innegociables que debe tomar el Gerente (Decisión | Cuándo / Plazo | Coste Neto Estimado | Impacto Esperado).
- 5 Conclusiones ejecutivas directas del diagnóstico.

## 1. Auditoría Operativa & Unit Economics Reales
- Desglose contable real: Facturación (🟢 {facturacion_anual:,} €), COGS (🟢 {coste_compras_recambios:,} €), Personal (🟢 {coste_personal:,} €), Gastos Fijos (🟢 {gastos_fijos:,} €) y Margen Neto resultante.
- Horas anuales perdidas (🟠 {horas_perdidas_dia * 220:.0f} horas) y cuantificación de la pérdida directa de nómina vs. facturación cesante con la tarifa real de 🟢 {precio_hora_mano_obra} €/h.

## 2. Contexto Macroeconómico, Demografía y Presión Regulatoria ({pais_region})
- 🔵 Normativas vigentes y en despliegue técnico: Veri*factu (RD 1007/2023), Ley Crea y Crece (facturación electrónica B2B). Requisitos técnicos obligatorios y sanciones reales.
- 🔵 Datos del mercado y convenios laborales de aplicación.

## 3. Benchmarking Sectorial: Empresa vs. Media País vs. Frontera de Desempeño
- Tabla comparativa estricta con datos del cliente: Facturación por empleado (🟢 {facturacion_anual / tamano_equipo:,.0f} €), Ticket medio (🟢 {ticket_medio_operacion} €), % B2B (🟢 {porcentaje_b2b}%), Tasa de conversión (🟢 {tasa_conversion_presupuestos}%).
- Comparativa frente a Media Sectorial y Frontera de Desempeño con fuentes documentadas.

## 4. Frontera de Innovación Internacional (Casos Reales de Estudio)
- Mínimo 2 casos de estudio reales con nombre comercial (Alemania, EE. UU., etc.). Empresa, contexto, solución técnica adoptada y qué parte es transferible a escala de esta pyme.

## 5. Taxonomía de Tendencias: Macro, Micro & Señales Débiles (Weak Signals)
- Clasificación de tendencias: Evidencia -> Impacto -> Incertidumbre -> Implicación para esta empresa con su estructura de costes.

## 6. Scoring Multidimensional de Tendencias y Matriz Impacto × Incertidumbre
- Matriz detallada: Tendencia | Cuadrante | Horizonte (Act/Prepare/Watch) | Impacto (1-10) | Madurez | Grado de Incertidumbre.
- Matriz de 4 cuadrantes: Alto impacto/Baja incertidumbre (Actuar), Alto impacto/Alta incertidumbre (Preparar escenarios), Bajo impacto/Baja incertidumbre (Monitorizar), Bajo impacto/Alta incertidumbre (Vigilar).

## 7. Análisis de Brecha (Gap Analysis) y Conexión con la Acción
- Justificación matemática de las puntuaciones (0 a 10) otorgadas a la empresa a partir de sus datos reales.
- Tabla: Dimensión -> Situación Auditada -> Benchmark -> Gap -> Impacto Económico -> Acción Vinculada.

## 8. Modelado de 4 Escenarios Plausibles (2x2 Matrix)
- Cruce de las 2 incertidumbres sectoriales críticas en {pais_region}.
- Matriz con Plausibilidad (Alta/Media/Baja), Impacto en Margen y Señales tempranas observables de confirmación para cada cuadrante.

## 9. Backcasting Inverso (Ingeniería Inversa a {horizonte} Años)
- Año 3: Definición del estado de éxito objetivo.
- Año 2: Hitos intermedios y capacidades técnicas que deben estar operativas.
- Año 1: Fundamentos y eliminación de fricciones operativas prioritarias.

## 10. Matriz de Decisión Tecnológica: Build / Buy / Partner / Kill
- Clasificación estricta de procesos y herramientas (Desarrollo interno, Compra SaaS, Alianza, Eliminación inmediata).

## 11. Sistema de Disparadores y Alertas Tempranas (Early Warning Triggers)
- Indicadores objetivos observables del entorno (regulatorios, comerciales o de costes) y la acción inmediata a activar.

## 12. Matriz de Coste de Inacción Desagregada
- Desglose riguroso a 12, 24 y 36 meses separando Fuga de Margen Demostrada, Coste de Oportunidad y Exposición Sancionadora.

## 13. Vías de Financiación Pública y Optimización Fiscal ({pais_region})
- Identificación de líneas de ayuda reales y vigentes, programas autonómicos y bonificaciones de formación continua (ej. FUNDAE).

## 14. Matriz de Fricción Cultural y Adopción del Cambio
- Resistencias por perfil (Operarios de taller, Gerente, Cliente B2C tradicional) y protocolo de mitigación e incentivos.

## 15. Hoja de Ruta Ejecutiva: Playbook 30 - 90 - 180 Días
- Fases de despliegue con: Tarea, Responsable directo, Dependencias previas, KPIs de control (Baseline -> Objetivo) y Presupuesto desglosado en CAPEX vs. OPEX acotado a los 🟢 {presupuesto_disponible:,} € disponibles.
- Análisis de sensibilidad del ROI financiero neto (escenarios al 25%, 50% y 75% de recuperación horaria).
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
