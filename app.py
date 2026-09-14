from google import genai
import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Radar Estratégico para Pymes", page_icon="📈", layout="wide"
)

st.title("📈 Radar de Tendencias, Innovación y Estrategia")
st.markdown(
    "Herramienta de diagnóstico prospectivo para pequeñas empresas y startups."
)
st.markdown("---")

# --- BARRA LATERAL (CONFIGURACIÓN) ---
with st.sidebar:
    st.header("🔐 Acceso")
    api_key_usuario = st.text_input(
        "Introduce tu API Key de Gemini:",
        type="password",
        help="Clave personal obtenida en Google AI Studio.",
    )
    st.markdown("---")
    st.markdown("### Metodología")
    st.caption(
        "El análisis cruza macrotendencias de mercado con las capacidades financieras "
        "y operativas específicas de tu negocio para generar un plan viable."
    )

# --- FORMULARIO DE RECOGIDA DE DATOS (LOS 4 BLOQUES) ---
st.subheader("📋 Datos del Negocio")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**1. Identidad y Modelo de Ingresos**")
    sector = st.text_input(
        "Sector y nicho de actividad:",
        placeholder="Ej: Distribución de recambios, Clínica dental, Ecommerce de moda...",
    )
    modelo_ingresos = st.selectbox(
        "Modelo principal de ingresos:",
        [
            "Venta en tienda física / local",
            "Comercio electrónico (B2C)",
            "Venta B2B / Distribución mayorista",
            "Servicios profesionales por horas o proyectos",
            "Suscripción / Cuota recurrente",
            "Mixto (físico y digital)",
        ],
    )

    st.markdown("**2. Tamaño y Tracción Actual**")
    rango_facturacion = st.selectbox(
        "Facturación anual aproximada:",
        [
            "Menos de 100.000 €",
            "Entre 100.000 € y 300.000 €",
            "Entre 300.000 € y 1.000.000 €",
            "Más de 1.000.000 €",
        ],
    )
    tamano_equipo = st.selectbox(
        "Equipo de trabajo:",
        [
            "1 persona (autónomo/fundador solo)",
            "2 a 5 personas",
            "6 a 15 personas",
            "Más de 15 personas",
        ],
    )

with col2:
    st.markdown("**3. Dolor o Reto Crítico Actual**")
    cuello_botella = st.text_area(
        "¿Qué problema o barrera frena el crecimiento del negocio hoy?:",
        placeholder="Ej: Márgenes cada vez más bajos por subida de costes, dependencia de un solo cliente grande, dificultades para atraer clientes jóvenes, procesos manuales lentos...",
        height=125,
    )

    st.markdown("**4. Capacidad de Inversión y Plazo**")
    presupuesto_innovacion = st.selectbox(
        "Capacidad de inversión estimada para mejoras en 12 meses:",
        [
            "Mínima (soluciones gratuitas o de muy bajo coste)",
            "Moderada (1.000 € - 5.000 €)",
            "Media (5.000 € - 20.000 €)",
            "Alta (> 20.000 €)",
        ],
    )
    horizonte_analisis = st.slider(
        "Horizonte temporal del análisis (años):",
        min_value=1,
        max_value=4,
        value=2,
    )

st.markdown("---")

# --- PROCESAMIENTO Y GENERACIÓN DEL INFORME ---
if st.button(
    "🚀 Generar Informe Estratégico", type="primary", use_container_width=True
):
    if not api_key_usuario:
        st.error(
            "⚠️ Es necesario introducir la API Key en el menú lateral izquierdo para procesar la solicitud."
        )
    elif not sector or not cuello_botella:
        st.warning(
            "⚠️ Por favor, completa al menos el campo de 'Sector' y el 'Problema principal' para poder emitir un análisis riguroso."
        )
    else:
        with st.spinner(
            "Analizando mercado, contrastando tendencias y elaborando plan ejecutivo..."
        ):
            try:
                cliente = genai.Client(api_key=api_key_usuario)

                prompt_sistema = f"""
                Eres un socio director de consultoría estratégica y prospectiva de negocio (Strategic Foresight), especializado en PYMES y empresas en crecimiento.
                Tu tarea es realizar un informe ejecutivo exhaustivo, realista y pragmático para el siguiente cliente:

                DATOS DE LA EMPRESA:
                - Sector y nicho: {sector}
                - Modelo de ingresos: {modelo_ingresos}
                - Facturación anual: {rango_facturacion}
                - Tamaño de equipo: {tamano_equipo}
                - Dolor o cuello de botella principal: {cuello_botella}
                - Presupuesto disponible para cambios: {presupuesto_innovacion}
                - Horizonte temporal: {horizonte_analisis} años

                CRITERIOS EDITORIALES OBLIGATORIOS:
                - No uses clichés ni generalidades vacías.
                - Ajusta cada recomendación estrictamente al presupuesto ({presupuesto_innovacion}) y tamaño de equipo ({tamano_equipo}).
                - No recomiendes soluciones corporativas gigantescas si la empresa factura poco.

                ESTRUCTURA RIGUROSA DEL INFORME (En formato Markdown profesional):
                ## 1. Diagnóstico del Negocio y Análisis de Cuello de Botella
                (Radiografía crítica de la situación y evaluación del riesgo operativo/financiero derivado de su problema declarado).

                ## 2. Tendencias de Mercado y Movimientos Competitivos ({horizonte_analisis} años)
                (Macrotendencias que afectarán a su entorno y qué innovaciones o tácticas están implementando competidores líderes en su nicho).

                ## 3. Oportunidades Tecnológicas y de Innovación Viables
                (2 o 3 soluciones técnicas o de automatización directamente ejecutables con su presupuesto y recursos actuales).

                ## 4. Matriz de Riesgo e Inacción
                (Consecuencias directas en margen, costes y pérdida de clientes si la empresa decide no actuar en los próximos meses).

                ## 5. Impacto Económico y Operativo Estimado
                (Proyección estimada de beneficios: porcentaje de ahorro potencial en costes, mejora estimada de margen o retención si adoptan las soluciones).

                ## 6. Hoja de Ruta Ejecutiva (30 - 90 - 180 días)
                - **Fase Inmediata (Día 1 a 30):** Acción rápida de validación o corrección sin coste alto.
                - **Fase de Integración (Día 31 a 90):** Implantación técnica o ajuste operativo principal.
                - **Fase de Consolidación (Día 91 a 180):** Medición de resultados y ventaja competitiva.
                """

                respuesta = cliente.models.generate_content(
                    model="gemini-2.5-flash", contents=prompt_sistema
                )

                st.success("✅ Informe completado satisfactoriamente.")
                st.markdown(respuesta.text)

            except Exception as error:
                st.error(f"Error al conectar con el servicio: {error}")
