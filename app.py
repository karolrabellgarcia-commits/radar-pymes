import json
import re
import time
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

st.title("🧭 Auditoría Operativa & Strategic Foresight")
st.markdown(
    "Plataforma de **Auditoría Cuantitativa, Benchmarking Sectorial y Prospectiva Estratégica** (Estándar Roland Berger / ITONICS)."
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
    st.markdown("### Taxonomía de Evidencia")
    st.caption(
        "• **🟢 Dato Declarado:** Aportado por la empresa (pendiente de cotejo contable).\n"
        "• **🔵 Benchmark Referencia:** Estadísticas públicas / sectoriales.\n"
        "• **🟠 Derivación Matemática:** Fórmulas explícitas sobre datos facilitados.\n"
        "• **🟡 Hipótesis Operativa:** Supuesto de trabajo editable.\n"
        "• **🔴 Simulación / Escenario:** Proyección condicional (no forecast)."
    )

# --- RECOGIDA DE DATOS CONTABLES Y OPERATIVOS ---
st.subheader("📋 Parámetros de Explotación y Límites de la Empresa")

tab_fin, tab_ops, tab_mkt, tab_vision = st.tabs([
    "1. Datos Financieros Declarados",
    "2. Operaciones & Capacidad Productiva",
    "3. Mercado, Competencia & Territorio",
    "4. Capacidad de Inversión & Alcance",
])

with tab_fin:
    st.markdown("#### Cuenta de Explotación Declarada (Cifras Anuales)")
    c1, c2, c3 = st.columns(3)
    with c1:
        facturacion_anual = st.number_input(
            "Facturación anual declarada (€):",
            min_value=10000,
            max_value=50000000,
            value=480000,
            step=5000,
        )
        coste_personal = st.number_input(
            "Gasto anual en personal (Nóminas + SS) (€):",
            min_value=5000,
            max_value=30000000,
            value=195000,
            step=2000,
        )
    with c2:
        coste_compras_recambios = st.number_input(
            "Gasto anual en compras / consumibles / COGS (€):",
            min_value=0,
            max_value=30000000,
            value=165000,
            step=2000,
        )
        gastos_fijos = st.number_input(
            "Gastos de estructura / fijos (Naves, seguros, suministros) (€):",
            min_value=1000,
            max_value=10000000,
            value=58000,
            step=1000,
        )
    with c3:
        margen_ebitda_declarado = st.number_input(
            "Beneficio neto / EBITDA declarado (€):",
            min_value=-500000,
            max_value=10000000,
            value=62000,
            step=1000,
        )
        ticket_medio_operacion = st.number_input(
            "Ticket medio de servicio (€):",
            min_value=10,
            max_value=50000,
            value=1450,
            step=25,
        )

    # Verificación preliminar de cuadre contable
    costes_totales_calc = coste_personal + coste_compras_recambios + gastos_fijos
    resultado_teorico = facturacion_anual - costes_totales_calc
    discrepancia_contable = abs(resultado_teorico - margen_ebitda_declarado)
    if discrepancia_contable > 5000:
        st.warning(
            f"⚠️ **Inconsistencia detectada en balance declarado:** Facturación ({facturacion_anual:,.0f} €) - Costes Totales ({costes_totales_calc:,.0f} €) = {resultado_teorico:,.0f} €, lo cual difiere del Beneficio declarado ({margen_ebitda_declarado:,.0f} €). El informe activará protocolo de cuarentena contable."
        )

with tab_ops:
    st.markdown("#### Capacidad Operativa y Fricción Declarada")
    c4, c5, c6 = st.columns(3)
    with c4:
        sector = st.text_input(
            "Actividad y subsector:",
            value="Instalación y mantenimiento de climatización/aerotermia comercial y residencial",
        )
        tamano_equipo = st.number_input(
            "Plantilla total:", min_value=1, max_value=500, value=6
        )
        operarios_directos = st.number_input(
            "Operarios directos en campo:",
            min_value=1,
            max_value=500,
            value=4,
        )
    with c5:
        precio_hora_mano_obra = st.number_input(
            "Tarifa facturada mano de obra (€/hora sin IVA):",
            min_value=15,
            max_value=300,
            value=42,
            step=1,
        )
        horas_perdidas_dia = st.number_input(
            "Horas/día estimadas en tareas no facturables (presupuestos, llamadas):",
            min_value=0.0,
            max_value=16.0,
            value=3.5,
            step=0.5,
        )
        tasa_conversion_presupuestos = st.slider(
            "% estimado de presupuestos aceptados:",
            min_value=5,
            max_value=100,
            value=35,
        )
    with c6:
        stack_tecnologico = st.selectbox(
            "Nivel tecnológico actual:",
            [
                "Manual / Hojas de cálculo y partes de trabajo en papel",
                "Software de escritorio local no integrado",
                "Herramientas cloud independientes (sin API / sin integración)",
                "ERP / Field Service Management (FSM) integrado",
            ],
        )
        friccion_operativa = st.text_area(
            "Cuello de botella principal declarado:",
            value="Retraso de hasta 5 días en pasar partes de papel a factura. Pérdida de 3,5 h/día elaborando presupuestos técnicos que no se convierten. Descontrol de stock en furgonetas.",
            height=100,
        )

with tab_mkt:
    st.markdown("#### Entorno Competitivo y Clientes")
    c7, c8 = st.columns(2)
    with c7:
        pais_region = st.text_input(
            "Ámbito territorial:", value="España (Comunidad Valenciana)"
        )
        porcentaje_b2c = st.slider(
            "% Facturación Particulares (B2C):",
            min_value=0,
            max_value=100,
            value=40,
        )
        porcentaje_b2b = 100 - porcentaje_b2c
        st.caption(
            f"Facturación Empresas / Terciario (B2B): **{porcentaje_b2b}%**"
        )
    with c8:
        competidor_referencia = st.text_input(
            "Amenaza o competidor de referencia:",
            value="Empresas de servicios energéticos (ESEs) y comercializadoras con contratos de mantenimiento integrados",
        )
        ventaja_competitiva = st.text_input(
            "Ventaja competitiva actual (Moat real contrastable):",
            value="Capacidad de respuesta técnica < 3h para clientes hosteleros en averías críticas",
        )

with tab_vision:
    st.markdown("#### Presupuesto y Plazos")
    c9, c10 = st.columns(2)
    with c9:
        presupuesto_disponible = st.number_input(
            "Capacidad máxima de inversión en 12 meses (€):",
            min_value=0,
            max_value=500000,
            value=6500,
            step=500,
        )
    with c10:
        horizonte = st.slider(
            "Horizonte temporal de prospectiva (años):",
            min_value=1,
            max_value=5,
            value=3,
        )

st.markdown("---")


# --- VISUALIZACIONES INTERACTIVAS (PLOTLY) ---
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
                ticktext=["ACT (0-12m)", "PREPARE (1-3a)", "WATCH (3-5a)"],
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

    pyme_scores = gap_data.get("pyme", [2, 4, 4, 5, 3])
    media_scores = gap_data.get("benchmark_sectorial", [5, 5, 5, 5, 4])
    lideres_scores = gap_data.get("frontera_desempeno", [9, 8, 8, 9, 8])

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=pyme_scores,
            theta=categories,
            fill="toself",
            name="Empresa Auditada",
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=media_scores,
            theta=categories,
            fill="toself",
            name="Benchmark Sectorial Referencia",
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=lideres_scores,
            theta=categories,
            fill="toself",
            name="Frontera de Desempeño Digital",
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
    "🚀 Ejecutar Auditoría Industrial & Generar Informe de Strategic Foresight",
    type="primary",
    use_container_width=True,
):
    if not api_key_usuario:
        st.error(
            "⚠️ Introduce tu API Key de Gemini en la barra lateral izquierda."
        )
    else:
        with st.spinner(
            "Verificando integridad contable, derivando ratios operativos y proyectando radar de prospectiva..."
        ):
            try:
                cliente = genai.Client(api_key=api_key_usuario)

                prompt_completo = f"""
Eres un Socio Director de Consultoría Estratégica y Strategic Foresight de máximo nivel (estándar Roland Berger, McKinsey, ITONICS).
Dispones de los DATOS FACILITADOS POR LA EMPRESA. Tu obligación es mantener la máxima honestidad intelectual y rigor metodológico.

DATOS FACILITADOS POR LA EMPRESA:
- Facturación anual declarada: 🟢 {facturacion_anual:,} €
- Gasto en personal (nóminas + SS): 🟢 {coste_personal:,} €
- Gasto en recambios / compras / COGS: 🟢 {coste_compras_recambios:,} €
- Gastos fijos operativos: 🟢 {gastos_fijos:,} €
- Beneficio neto declarado: 🟢 {margen_ebitda_declarado:,} €
- Ticket medio: 🟢 {ticket_medio_operacion} €
- Plantilla: 🟢 {tamano_equipo} personas (Operarios directos en campo: 🟢 {operarios_directos})
- Tarifa facturada por hora de mano de obra: 🟢 {precio_hora_mano_obra} €/h (sin IVA)
- Horas/día dedicadas a tareas no facturables: 🟢 {horas_perdidas_dia} h/día (declaradas por gerencia, pendientes de muestreo)
- Días laborables computables: 🟢 220 días/año
- Tasa declarada de conversión de presupuestos: 🟢 {tasa_conversion_presupuestos}%
- Nivel tecnológico: 🟢 {stack_tecnologico}
- Cuello de botella declarado: 🟢 {friccion_operativa}
- Territorio: 🟢 {pais_region}
- Mix clientes: 🟢 {porcentaje_b2c}% B2C / 🟢 {porcentaje_b2b}% B2B
- Amenaza declarada: 🟢 {competidor_referencia}
- Ventaja competitiva declarada: 🟢 {ventaja_competitiva}
- Capacidad de inversión 12m: 🟢 {presupuesto_disponible:,} €
- Horizonte: 🟢 {horizonte} años

======================================================================
DIRECTRICES DE RIGOR, AUDITORÍA Y PROTOCOLO EDITORIAL OBLIGATORIO:
======================================================================
1. GESTIÓN DE DISCREPANCIAS CONTABLES:
   - Facturación declarada: {facturacion_anual:,} €. Suma de costes declarados: {costes_totales_calc:,} €. Resultado teórico: {resultado_teorico:,} €. Beneficio declarado: {margen_ebitda_declarado:,} €.
   - Si existe discrepancia relevante entre el beneficio declarado y el balance teórico, DEBES incluir al inicio una "⚠️ Advertencia de Cuarentena Financiera" indicando que las cifras absolutas de rentabilidad son provisionales y que el análisis se focaliza en eficiencia operativa y márgenes unitarios.

2. PROHIBICIÓN DE SUMAR MAGNITUDES HETEROGÉNEAS (COSTE DE INACCIÓN):
   - NUNCA sumes en una cifra total el coste salarial, la facturación cesante teórica y una posible sanción regulatoria.
   - Presenta una TABLA DE IMPACTOS DESAGREGADOS:
     * Coste salarial directo identificable (pago de nómina por horas no facturables).
     * Capacidad potencial no monetizada (facturación cesante máxima teórica sujeta a demanda).
     * Exposición regulatoria (riesgo potencial de sanción bajo inspección, NO pérdida de caja segura).
     * Total: Declarar explícitamente "No sumable directamente por corresponder a naturalezas contables distintas".

3. BENCHMARKING RIGUROSO Y NO CIRCULAR:
   - No cites estadísticas genéricas sin especificar: Fuente estimada | Año | Muestra/Ámbito. Si no dispones de página y tabla exacta, denomínalo "Benchmark Sectorial de Referencia Orientativo".
   - Define formalmente la escala de scoring (0 a 10):
     * 0-2: Inexistente / Manual
     * 3-4: Básico reactivo
     * 5-6: Benchmark sectorial medio
     * 7-8: Práctica avanzada conectada
     * 9-10: Frontera de desempeño tecnológico/experimental

4. PRAGMATISMO TECNOLÓGICO (CERO HYPE):
   - PROHIBIDO recomendar "RFID" para pymes de este tamaño; prescribe "Control digital de stock en furgonetas mediante QR".
   - PROHIBIDO recomendar "Tarificadores por IA" en la Fase 1; prescribe "Presupuestación paramétrica estandarizada / reglas lógicas en software FSM".
   - Elimina la palabra "Moat"; usa "Ventaja competitiva actual".

5. TABLA DE EVIDENCIA Y NIVELES DE CONFIANZA:
   - Añade una tabla formal de evidencia que evalúe 5 afirmaciones clave del estudio:
     | Afirmación / Parámetro | Origen del Dato | Grado de Confianza (Alto/Medio/Bajo) | Implicación Metodológica |

6. CORRECCIÓN DEL ROI Y SENSIBILIDAD:
   - Margen Incremental = Horas Recuperadas Facturables x Tarifa Horaria x Margen de Contribución Real.
   - Beneficio Incremental = Margen Incremental - (CAPEX amortizado + OPEX software).
   - Muestra tabla de sensibilidad con escenarios de captura del 25%, 50% y 75%.
   - Modula el payback: "Bajo el escenario de captura del 50%, el modelo estima un payback orientativo de X meses".

7. ROADMAP CON RESPONSABLES Y KPIS CON TRAYECTORIA:
   - Cada acción en el Playbook (30-90-180 días) DEBE tener: Acción | Responsable formal | Dependencia técnica | KPI (Baseline actual -> Objetivo intermedio -> Meta final).

8. FORMATO JSON OBLIGATORIO PARA PLOTLY:
   - Inicia con bloque ```json ... ```:
     {{
       "trends": [
         {{"name": "...", "quadrant": "Tecnología"|"Operaciones"|"Modelo de Negocio"|"Mercado / Cliente", "horizon": "Act"|"Prepare"|"Watch", "impact": 1-10, "description": "..."}}
       ],
       "gap_analysis": {{
         "pyme": [números 1-10],
         "benchmark_sectorial": [números 1-10],
         "frontera_desempeno": [números 1-10]
       }}
     }}
     Orden del gap_analysis: [Madurez Digital, Eficiencia Operativa, Retención de Margen, Diversificación B2B, Agilidad Estratégica].

======================================================================
ESTRUCTURA DEL INFORME (METODOLOGÍA + AUDITORÍA + 15 MÓDULOS):
======================================================================

# INFORME DE AUDITORÍA INDUSTRIAL, BENCHMARKING Y STRATEGIC FORESIGHT

## FICHA METODOLÓGICA & LÍMITES DEL ESTUDIO
- Alcance, fecha de corte, baseline declarado.
- Tabla de Niveles de Confianza y Evidencia (auditoría de fuentes de los parámetros clave).
- Definición formal de la escala de scoring (0-10) y concepto de "Frontera de Desempeño".
- Advertencia sobre consistencia contable del balance declarado.

## RESUMEN EJECUTIVO & DECISIONES DIRECTIVAS
- Tabla: Decisiones Clave para Gerencia (Decisión | Cuándo / Plazo | Coste Neto Estimado | Impacto Esperado).
- 5 Conclusiones ejecutivas directas del diagnóstico (en lenguaje prudente).

## 1. Auditoría Operativa & Unit Economics de Campo
- Análisis de la estructura de explotación declarada.
- Cuantificación de horas improductivas declaradas (🟠 {horas_perdidas_dia * 220:.0f} h/año) y desglose de coste salarial real asignado.
- Capacidad teórica de facturación cesante.

## 2. Contexto Macroeconómico, Demografía y Presión Regulatoria ({pais_region})
- 🔵 Regulaciones vigentes: Veri*factu (RD 1007/2023), Ley Crea y Crece (Factura electrónica B2B), F-Gas / Gases fluorados si aplica al sector. Requisitos técnicos y sanciones.
- 🔵 Negociación colectiva y costes de mano de obra técnica en {pais_region}.

## 3. Benchmarking Sectorial Cuantitativo: Empresa vs. Sector vs. Frontera Digital
- Tabla comparativa estricta con columnas: Indicador | Empresa Auditada | Benchmark Sectorial Orientativo | Frontera de Desempeño Digital | Fuente / Metodología de Contraste.
- Citas documentadas o catalogadas como "Benchmark de referencia".

## 4. Frontera de Innovación Internacional (Casos Reales de Transferencia)
- Mínimo 2 casos de estudio reales con nombre comercial (ej. Thermondo, ServiceTitan u operadores similares).
- Ficha de transferencia: Contexto de la empresa, solución adoptada, resultados observados, qué es transferible y qué NO es transferible a escala de esta pyme.

## 5. Taxonomía de Tendencias: Macro, Micro & Señales Débiles (Weak Signals)
- Clasificación de tendencias: Evidencia -> Impacto -> Incertidumbre -> Implicación para la estructura de costes de la empresa.

## 6. Scoring Multidimensional de Tendencias y Matriz Impacto × Incertidumbre
- Matriz con: Tendencia | Cuadrante | Horizonte (Act/Prepare/Watch) | Impacto (1-10) | Madurez | Grado de Incertidumbre.
- Matriz de 4 cuadrantes: Actuar (Alto impacto / Baja incertidumbre), Preparar escenarios (Alto impacto / Alta incertidumbre), Monitorizar (Bajo impacto / Baja incertidumbre), Vigilar (Bajo impacto / Alta incertidumbre).

## 7. Análisis de Brecha Competitiva (Gap Analysis Cuantitativo)
- Justificación objetiva de las puntuaciones (0 a 10) otorgadas a la empresa a partir de sus datos reales.
- Tabla: Dimensión -> Situación Auditada -> Benchmark Sectorial -> Gap -> Impacto Económico -> Acción Concreta.

## 8. Modelado de 4 Escenarios Plausibles (2x2 Matrix)
- Cruce de las 2 incertidumbres sectoriales críticas en {pais_region}.
- Matriz con Plausibilidad (Alta/Media/Baja), Impacto en Rentabilidad y Señales tempranas observables de confirmación.

## 9. Backcasting Inverso (Ingeniería Inversa a {horizonte} Años)
- Año 3: Definición del estado de éxito objetivo (rango objetivo B2B/B2C, no cifra fija arbitraria).
- Año 2: Hitos intermedios y consolidación de herramientas FSM/digitales.
- Año 1: Fundamentos y erradicación del papel en partes de trabajo y presupuestos.

## 10. Matriz de Decisión Tecnológica: Build / Buy / Partner / Kill
- Clasificación justificada: Desarrollo propio de procesos, Compra SaaS comercial (FSM/QR), Alianzas y Eliminación inmediata de prácticas obsoletas.

## 11. Sistema de Disparadores y Alertas Tempranas (Early Warning Triggers)
- Indicadores objetivos observables del mercado o costes y la acción correctora a activar.

## 12. Matriz de Coste de Inacción Desagregada (Sin Sumas Heterogéneas)
- Tabla comparativa a 12, 24 y 36 meses desglosando por separado: Coste salarial improductivo, Facturación cesante potencial y Exposición a contingencias.

## 13. Vías de Financiación Pública y Optimización Fiscal ({pais_region})
- Identificación de líneas de ayuda reales y vigentes, programas autonómicos y bonificaciones de formación continua (FUNDAE).

## 14. Matriz de Fricción Cultural y Gestión del Cambio
- Resistencias por perfil (Técnicos de campo, Gerencia, Cliente tradicional) y protocolo de mitigación e incentivos.

## 15. Hoja de Ruta Ejecutiva: Playbook 30 - 90 - 180 Días
- Fases estructuradas con: Tarea, Responsable formal, Dependencia técnica previa, KPIs de control (Baseline actual -> Meta intermedia -> Meta final) y Presupuesto desglosado en CAPEX vs. OPEX acotado estrictamente a los 🟢 {presupuesto_disponible:,} € disponibles.
- Análisis de sensibilidad del ROI financiero neto (escenarios al 25%, 50% y 75% de recuperación horaria) con cálculo prudente de payback.
"""

                # Mecanismo de reintentos con soporte para saturación de servidores (503)
                modelos_a_probar = ["gemini-3.6-flash", "gemini-2.5-flash"]
                respuesta = None

                for mod in modelos_a_probar:
                    for intento in range(2):
                        try:
                            respuesta = cliente.models.generate_content(
                                model=mod, contents=prompt_completo
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
                    raise Exception(
                        "Los servidores de IA están temporalmente saturados. Inténtalo de nuevo en unos instantes."
                    )

                texto_salida = respuesta.text

                # Extraer JSON para los gráficos Plotly
                patron_json = r"```json\s*(\{.*?\})\s*```"
                match = re.search(patron_json, texto_salida, re.DOTALL)

                if match:
                    json_str = match.group(1)
                    datos_graficos = json.loads(json_str)

                    st.success("✅ Auditoría y Foresight procesados exitosamente.")

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
