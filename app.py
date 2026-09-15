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

st.title("🧭 Diagnóstico Operativo & Strategic Foresight")
st.markdown(
    "Plataforma de **Auditoría Operativa, Benchmarking y Prospectiva Práctica** para PYMES."
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
    st.markdown("### Clasificación de Datos")
    st.caption(
        "• 🟢 **Dato real:** Facilitado por la empresa.\n"
        "• 🔵 **Fuente externa:** Estudio o estadística contrastada.\n"
        "• 🟡 **Estimación propia:** Cálculo matemático derivado.\n"
        "• 🟠 **Hipótesis:** Supuesto operativo a validar.\n"
        "• 🟣 **Objetivo:** Meta a alcanzar en el plan."
    )

# --- RECOGIDA DE DATOS ---
st.subheader("📋 Datos Operativos y Financieros de la Empresa")

tab_fin, tab_ops, tab_mkt, tab_vision = st.tabs([
    "1. Datos Financieros",
    "2. Operaciones Diarias",
    "3. Mercado y Clientes",
    "4. Inversión y Plazos",
])

with tab_fin:
    st.markdown("#### Cifras Económicas Anuales")
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
            "Coste anual de personal (Nóminas + SS) (€):",
            min_value=5000,
            max_value=30000000,
            value=195000,
            step=2000,
        )
    with c2:
        coste_compras_recambios = st.number_input(
            "Gasto en compras / materiales / repuestos (€):",
            min_value=0,
            max_value=30000000,
            value=165000,
            step=2000,
        )
        gastos_fijos = st.number_input(
            "Gastos fijos anuales (Alquileres, seguros, suministros) (€):",
            min_value=1000,
            max_value=10000000,
            value=58000,
            step=1000,
        )
    with c3:
        margen_ebitda_declarado = st.number_input(
            "Beneficio neto anual estimado (€):",
            min_value=-500000,
            max_value=10000000,
            value=62000,
            step=1000,
        )
        ticket_medio_operacion = st.number_input(
            "Ticket medio por factura/trabajo (€):",
            min_value=10,
            max_value=50000,
            value=1450,
            step=25,
        )

    costes_totales_calc = coste_personal + coste_compras_recambios + gastos_fijos
    resultado_teorico = facturacion_anual - costes_totales_calc
    hay_inconsistencia = abs(resultado_teorico - margen_ebitda_declarado) > 5000
    if hay_inconsistencia:
        st.warning(
            f"⚠️ **Inconsistencia contable:** Facturación ({facturacion_anual:,.0f} €) - Gastos ({costes_totales_calc:,.0f} €) = {resultado_teorico:,.0f} €. Difiere del beneficio declarado ({margen_ebitda_declarado:,.0f} €). El informe priorizará ratios de horas y márgenes unitarios."
        )

with tab_ops:
    st.markdown("#### Capacidad de Trabajo y Cuello de Botella")
    c4, c5, c6 = st.columns(3)
    with c4:
        sector = st.text_input(
            "Sector o actividad:",
            value="Instalación y mantenimiento de climatización/aerotermia comercial y residencial",
        )
        tamano_equipo = st.number_input(
            "Número total de empleados:", min_value=1, max_value=500, value=6
        )
        operarios_directos = st.number_input(
            "De ellos, técnicos/operarios en campo:",
            min_value=1,
            max_value=500,
            value=4,
        )
    with c5:
        precio_hora_mano_obra = st.number_input(
            "Precio cobrado por hora de mano de obra (€/hora sin IVA):",
            min_value=15,
            max_value=300,
            value=42,
            step=1,
        )
        horas_perdidas_dia = st.number_input(
            "Horas al día dedicadas a llamadas, citas y presupuestos:",
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
            "Herramientas actuales:",
            [
                "Partes de trabajo en papel y hojas de cálculo",
                "Software de escritorio local básico",
                "Herramientas en la nube sin conectar entre sí",
                "Software de gestión integrado (ERP/FSM)",
            ],
        )
        friccion_operativa = st.text_area(
            "Problema principal del día a día:",
            value="Los partes de trabajo en papel tardan varios días en facturarse. Se pierden 3,5 h al día haciendo presupuestos que no se aprueban. Descontrol en los materiales que van en las furgonetas.",
            height=100,
        )

with tab_mkt:
    st.markdown("#### Clientes y Competencia")
    c7, c8 = st.columns(2)
    with c7:
        pais_region = st.text_input(
            "Ubicación:", value="España (Comunidad Valenciana)"
        )
        porcentaje_b2c = st.slider(
            "% Clientes particulares (B2C):",
            min_value=0,
            max_value=100,
            value=40,
        )
        porcentaje_b2b = 100 - porcentaje_b2c
        st.caption(f"Clientes empresas (B2B): **{porcentaje_b2b}%**")
    with c8:
        competidor_referencia = st.text_input(
            "Competidor de referencia o mayor amenaza:",
            value="Grandes empresas de servicios energéticos y comercializadoras con contratos cerrados de mantenimiento",
        )
        ventaja_competitiva = st.text_input(
            "Ventaja competitiva actual:",
            value="Rapidez de respuesta en menos de 3 horas para clientes de hostelería en averías urgentes",
        )

with tab_vision:
    st.markdown("#### Presupuesto y Horizonte")
    c9, c10 = st.columns(2)
    with c9:
        presupuesto_disponible = st.number_input(
            "Presupuesto máximo de inversión en 12 meses (€):",
            min_value=0,
            max_value=500000,
            value=6500,
            step=500,
        )
    with c10:
        horizonte = st.slider(
            "Años a proyectar:", min_value=1, max_value=5, value=3
        )

st.markdown("---")


# --- GRÁFICOS PLOTLY ---
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
        title="Trend Radar: Dónde poner la atención",
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
            name="Tu Empresa (Actual)",
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
            name="Benchmark Aspiracional",
        )
    )

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=True,
        title="Matriz de Brecha: Dónde estamos vs. Dónde queremos estar",
        height=450,
    )
    return fig


# --- PROCESAMIENTO ANALÍTICO ---
if st.button(
    "🚀 Generar Diagnóstico Operativo & Strategic Foresight",
    type="primary",
    use_container_width=True,
):
    if not api_key_usuario:
        st.error(
            "⚠️ Introduce tu API Key de Gemini en la barra lateral izquierda."
        )
    else:
        with st.spinner(
            "Analizando datos operativos, revisando consistencia y generando informe práctico..."
        ):
            try:
                cliente = genai.Client(api_key=api_key_usuario)

                prompt_completo = f"""
Eres un Consultor de Operaciones y Estrategia Empresarial con lenguaje claro, directo y accesible.
Trabajas con datos facilitados por la empresa. Debes ser útil, riguroso y transparente, sin adornos innecesarios.

DATOS FACILITADOS POR LA EMPRESA:
- Facturación anual declarada: 🟢 {facturacion_anual:,} €
- Coste anual personal: 🟢 {coste_personal:,} €
- Compras de material / consumibles: 🟢 {coste_compras_recambios:,} €
- Gastos fijos: 🟢 {gastos_fijos:,} €
- Beneficio declarado: 🟢 {margen_ebitda_declarado:,} €
- Ticket medio de trabajo: 🟢 {ticket_medio_operacion} €
- Empleados totales: 🟢 {tamano_equipo} (Técnicos directos: 🟢 {operarios_directos})
- Tarifa facturada por hora de mano de obra: 🟢 {precio_hora_mano_obra} €/h
- Horas/día dedicadas a presupuestos y gestión: 🟢 {horas_perdidas_dia} h/día (estimación de gerencia, pendiente de medición)
- Días de trabajo al año: 🟢 220 días
- % de presupuestos aceptados: 🟢 {tasa_conversion_presupuestos}%
- Herramientas actuales: 🟢 {stack_tecnologico}
- Problema principal: 🟢 {friccion_operativa}
- Ubicación: 🟢 {pais_region}
- Mix de clientes: 🟢 {porcentaje_b2c}% Particulares (B2C) / 🟢 {porcentaje_b2b}% Empresas (B2B)
- Competidor / Amenaza: 🟢 {competidor_referencia}
- Ventaja competitiva actual: 🟢 {ventaja_competitiva}
- Presupuesto de inversión en 12 meses: 🟢 {presupuesto_disponible:,} €
- Años a proyectar: 🟢 {horizonte} años

======================================================================
REGLAS OBLIGATORIAS (PROHIBICIONES Y ESTILO):
======================================================================
1. LEYENDA OBLIGATORIA AL PRINCIPIO:
   🟢 Dato real de la empresa
   🔵 Fuente externa contrastada
   🟡 Estimación propia (cálculo derivado)
   🟠 Hipótesis a comprobar
   🟣 Objetivo deseado

2. CONTROL DE INCONSISTENCIAS FINANCIERAS:
   - Facturación declarada: {facturacion_anual:,} €. Gastos declarados: {costes_totales_calc:,} €. Resultado teórico: {resultado_teorico:,} €. Beneficio declarado: {margen_ebitda_declarado:,} €.
   - Si no cuadra, pon un aviso de 2 líneas:
     "⚠️ Limitación de los datos económicos: Los gastos declarados y la facturación no coinciden con el beneficio indicado. Por prudencia, este informe se centra en la organización del trabajo, tiempos de respuesta y horas facturables hasta revisar la contabilidad detallada."

3. COSTE DE NO ACTUAR (PROHIBIDO SUMAR CONCEPTOS DISTINTOS):
   - PROHIBIDO sumar salarios, horas cesantes y posibles multas en una cifra total como '83.000 €'.
   - Presenta una tabla sencilla:
     * Coste administrativo estimado (horas dedicadas x coste salarial hora)
     * Facturación potencial no capturada (horas recuperables x precio hora, sujeta a demanda)
     * Riesgo regulatorio (potencial en caso de inspección, no pérdida segura de dinero)
     * Total: Indicar claramente "No sumables directamente por ser conceptos distintos".

4. REGULACIÓN SIN EXAGERAR MULTAS:
   - Cita Veri*factu (RD 1007/2023) y Facturación Electrónica explicando qué exige (software con registro inalterable, adiós al papel/Excel).
   - NUNCA pongas "sanción de 50.000 €" como si fuera a ocurrir mañana; di "riesgo de sanciones en caso de no adaptación en los plazos fijados por la normativa".

5. BENCHMARKING REALISTA:
   - En la tabla de comparación, usa: "Tu Empresa | Media Sectorial Estimada | Benchmark Aspiracional".
   - Explica que el Benchmark Aspiracional es el nivel de empresas del sector que ya trabajan con procesos ágiles y digitales.

6. CERO HUMO TECNOLÓGICO:
   - PROHIBIDO hablar de "RFID", "telemetría", "IoT" o "tarificador por IA" para la fase inicial de esta pyme.
   - Recomienda soluciones sencillas y probadas: control de material en furgoneta mediante códigos QR, partes de trabajo digitales en tablet/móvil y plantillas estandarizadas de presupuestos.
   - NUNCA uses la palabra "Moat"; usa "Ventaja competitiva actual".
   - PROHIBIDO usar palabras exageradas como "fuga masiva", "innegociable", "extinción" o "quiebra".

7. CADA TENDENCIA DEBE EXPLICAR EL "¿Y QUÉ?":
   - Para cada tendencia clave indica: ¿Qué está pasando? -> ¿Qué significa para nosotros? -> ¿Qué decisión tomamos? -> ¿Cómo lo medimos?

8. ROADMAP PRÁCTICO:
   - Cada acción a 30, 90 y 180 días debe incluir: Acción | Quién lo hace (Responsable) | Requisito previo | KPI concreto (De X actual a Y objetivo).

9. FORMATO JSON PARA GRÁFICOS:
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
     Orden del gap_analysis: [Digitalización, Eficiencia Operativa, Control de Margen, Cartera B2B, Agilidad Estratégica].

======================================================================
ESTRUCTURA DEL INFORME:
======================================================================
# INFORME DE DIAGNÓSTICO OPERATIVO Y ESTRATEGIA PRÁCTICA

## 0. Ficha de Datos y Leyenda
(Leyenda de símbolos, límites del estudio y aviso de consistencia contable si aplica).

## RESUMEN PARA DIRECCIÓN: 4 DECISIONES CLAVE
(Tabla con: Decisión | Cuándo ponerla en marcha | Responsable | Coste estimado | Beneficio esperado).

## 1. Dónde se pierde tiempo y dinero (Auditoría de Operaciones)
(Cálculo de horas dedicadas a tareas no facturables y desglose claro entre coste salarial e ingresos potenciales).

## 2. Normativa y Cambios del Entorno ({pais_region})
(Veri*factu, factura electrónica y convenios, explicados en cristiano y sin alarmismos).

## 3. Comparativa: Dónde estamos vs. Dónde queremos estar
(Tabla con datos de la empresa, media estimada y benchmark aspiracional).

## 4. Dos Buenas Prácticas de Referencia
(Dos ejemplos de empresas que hayan solucionado este problema, qué hicieron bien y qué podemos aplicar nosotros).

## 5. Tendencias que nos afectan y "¿Y esto qué significa?"
(Explicación práctica de las tendencias del radar con su implicación directa).

## 6. Radar de Tendencias: Dónde poner el foco
(Matriz sencilla: Actuar ya / Prepararse / Vigilar).

## 7. Áreas de Mejora Prioritarias (Matriz de Brecha)
(Explicación de las 5 dimensiones del gráfico de brecha).

## 8. Cuatro Posibles Escenarios de Futuro
(Qué puede pasar en el sector y cómo estar preparados en cada caso, sin jugar a adivinos).

## 9. Del Futuro al Presente: Objetivos a {horizonte} Años
(Dónde queremos estar dentro de {horizonte} años y qué pasos previos dar en el Año 2 y Año 1).

## 10. Qué Construir, Qué Comprar y Qué Dejar de Hacer
(Decisiones prácticas: procesos propios, software a contratar y tareas manuales que hay que eliminar).

## 11. Señales de Alerta para Reaccionar a Tiempo
(3 señales concretas del mercado que nos avisan de que hay que ajustar el plan).

## 12. Coste de No Hacer Nada (Desglosado)
(Tabla que separa claramente horas pagadas, oportunidad de venta y riesgo normativo, sin sumarlos).

## 13. Opciones de Ayudas y Financiación ({pais_region})
(Subvenciones abiertas o deducciones por formación profesional bonificada).

## 14. Cómo Involucrar al Equipo
(Cómo explicar el cambio a los técnicos y clientes tradicionales sin generar rechazo).

## 15. Plan de Acción: Qué Hacer en 30, 90 y 180 Días
(Plan paso a paso con responsables, requisitos, presupuesto y cálculo prudente de recuperación de la inversión con 25%, 50% y 75% de éxito).
"""

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
                        "Servidores temporalmente ocupados. Prueba de nuevo en unos segundos."
                    )

                texto_salida = respuesta.text

                # Extraer JSON
                patron_json = r"```json\s*(\{.*?\})\s*```"
                match = re.search(patron_json, texto_salida, re.DOTALL)

                if match:
                    json_str = match.group(1)
                    datos_graficos = json.loads(json_str)

                    st.success("✅ Diagnóstico generado con éxito.")

                    st.subheader("📊 Visualización Rápida")
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
