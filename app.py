import streamlit as st
import pandas as pd
import os
import json
import google.generativeai as genai

# ==============================================================================
# 1. CONFIGURACION Y CLIENTE IA
# ==============================================================================
st.set_page_config(
    page_title="KROMA TrendRadar | Inteligencia Estrategica e Innovacion",
    layout="wide"
)

default_key = os.environ.get("GEMINI_API_KEY", "")
if not default_key and "GEMINI_API_KEY" in st.secrets:
    default_key = st.secrets["GEMINI_API_KEY"]

with st.sidebar:
    st.header("Configuracion de Acceso")
    api_key_input = st.text_input(
        "Clave API Gemini:",
        value=default_key,
        type="password",
        help="Clave de Google AI Studio (aistudio.google.com)"
    )
    st.caption("La clave se mantiene activa durante toda la sesion.")

if api_key_input:
    genai.configure(api_key=api_key_input)

# ==============================================================================
# 2. MOTOR DE PROSPECCION Y RADAR DE TENDENCIAS
# ==============================================================================
def obtener_modelo_activo():
    preferidos = [
        "models/gemini-3.6-flash",
        "gemini-3.6-flash",
        "models/gemini-1.5-pro",
        "gemini-1.5-pro",
        "models/gemini-1.5-flash",
        "gemini-1.5-flash"
    ]
    
    for p in preferidos:
        try:
            m = genai.GenerativeModel(p)
            return m
        except Exception:
            continue

    try:
        modelos_disponibles = genai.list_models()
        for mod in modelos_disponibles:
            if "generateContent" in mod.supported_generation_methods:
                return genai.GenerativeModel(mod.name)
    except Exception:
        pass

    return genai.GenerativeModel("gemini-3.6-flash")

def generar_radar_innovacion(perfil: dict) -> dict:
    if not api_key_input:
        return {
            "error": "Falta la clave API. Introduzca su clave en el panel lateral para iniciar el analisis."
        }

    prompt = f"""
    Actua como Socio Director de una firma global de prospeccion e inteligencia estrategica (metodologia Trendone, Gartner, Board of Innovation).
    Tu mision es elaborar un Dossier Continuo de Tendencias, Scouting Tecnologico y Oportunidades de Innovacion Disruptiva para la siguiente pyme:

    PERFIL CORPORATIVO:
    - Entidad: {perfil.get('nombre_empresa')}
    - Sector y Nicho Especifico: {perfil.get('sector_nicho')}
    - Propuesta Actual y Segmento de Clientes: {perfil.get('modelo_actual')}
    - Ventaja Competitiva Actual / Fortaleza: {perfil.get('fortaleza')}
    - Nivel de Ambicion Estrategica: {perfil.get('ambicion')}
    - Amenaza de Mercado Identificada: {perfil.get('amenaza')}

    CRITERIOS DE RIGOR ESTRATEGICO:
    - Evita cualquier generalidad o recomendacion superficial (como uso de redes sociales o digitalizacion generica).
    - Centrate en tendencias de mercado emergentes comprobadas, aplicaciones tecnologicas de impacto directo en su cadena de valor y modelos de negocio de alto margen.
    - El tono debe ser analitico, ejecutivo, preciso y cuantitativamente orientativo.
    - No utilices emoticonos ni iconos decorativos en las respuestas.

    RESPONDE EXCLUSIVAMENTE CON UN OBJETO JSON VALIDO CON ESTA ESTRUCTURA EXACTA (sin bloques markdown de codigo ```json ni texto complementario):
    {{
        "resumen_vision": "Sintesis prospectiva sobre la evolucion estrategica de la entidad a tres anos vista...",
        "macrotendencias": [
            {{
                "nombre": "Nombre formal de la tendencia",
                "horizonte": "Inmediato (0-12m) / Medio Plazo (1-3 anos) / Largo Plazo (3-5 anos)",
                "impacto_sector": "Transformacion estructural del entorno competitivo",
                "oportunidad_pyme": "Oportunidad de captura de valor aplicable para esta empresa"
            }},
            {{
                "nombre": "Segunda tendencia",
                "horizonte": "...",
                "impacto_sector": "...",
                "oportunidad_pyme": "..."
            }},
            {{
                "nombre": "Tercera tendencia",
                "horizonte": "...",
                "impacto_sector": "...",
                "oportunidad_pyme": "..."
            }}
        ],
        "tecnologias_aplicadas": [
            {{
                "tecnologia": "Nombre de la tecnologia o solucion de IA",
                "madurez": "Emergente / En Crecimiento / Madura",
                "caso_uso_real": "Caso de aplicacion directa en producto, canal u operaciones",
                "ejemplo_mercado": "Referencia de empresa o entidad pionera a nivel global"
            }},
            {{
                "tecnologia": "Segunda tecnologia",
                "madurez": "...",
                "caso_uso_real": "...",
                "ejemplo_mercado": "..."
            }},
            {{
                "tecnologia": "Tercera tecnologia",
                "madurez": "...",
                "caso_uso_real": "...",
                "ejemplo_mercado": "..."
            }}
        ],
        "nuevos_modelos_negocio": [
            {{
                "concepto": "Denominacion del modelo de negocio",
                "mecanismo_ingreso": "Estructura de monetizacion y origen del margen",
                "ventaja_defensiva": "Barrera de entrada y proteccion frente a competidores"
            }},
            {{
                "concepto": "Segundo modelo",
                "mecanismo_ingreso": "...",
                "ventaja_defensiva": "..."
            }}
        ],
        "matriz_priorizacion": [
            {{
                "iniciativa": "Denominacion del proyecto",
                "categoria": "Ganancia Inmediata / Apuesta Estrategica / Experimento Agil",
                "impacto_negocio": "Alto / Medio / Transformador",
                "complejidad": "Baja / Media / Alta"
            }},
            {{
                "iniciativa": "Segunda iniciativa",
                "categoria": "...",
                "impacto_negocio": "...",
                "complejidad": "..."
            }},
            {{
                "iniciativa": "Tercera iniciativa",
                "categoria": "...",
                "impacto_negocio": "...",
                "complejidad": "..."
            }},
            {{
                "iniciativa": "Cuarta iniciativa",
                "categoria": "...",
                "impacto_negocio": "...",
                "complejidad": "..."
            }}
        ],
        "pilotos_accion": [
            {{
                "plazo": "Fase 1: 30 Dias (Definicion y Prototipado)",
                "accion": "Prueba de concepto de bajo coste y validacion rapida",
                "kpi_exito": "Indicador cuantitativo de validacion"
            }},
            {{
                "plazo": "Fase 2: 90 Dias (Despliegue Controlado)",
                "accion": "Piloto de mercado con clientes cualificados",
                "kpi_exito": "Metrica de traccion inicial"
            }},
            {{
                "plazo": "Fase 3: 180 Dias (Escalado e Integracion)",
                "accion": "Incorporacion al portafolio comercial estandar",
                "kpi_exito": "Metrica de contribucion a ingresos"
            }}
        ]
    }}
    """

    try:
        modelo = obtener_modelo_activo()
        res = modelo.generate_content(prompt)
        t = res.text.strip()
        if t.startswith("```json"):
            t = t[7:]
        if t.startswith("```"):
            t = t[3:]
        if t.endswith("```"):
            t = t[:-3]
        return json.loads(t.strip())
    except Exception as e:
        return {"error": f"Error al generar con Gemini: {str(e)}"}

# ==============================================================================
# 3. ENTRADA DE DATOS
# ==============================================================================
st.title("KROMA TrendRadar — Inteligencia de Mercado e Innovacion")
st.caption("Radar continuo de prospeccion estrategica, disrupcion tecnologica y nuevos modelos de negocio.")

with st.expander("Configurar Perfil de la Empresa a Prospectar", expanded=True):
    with st.form("form_radar"):
        col1, col2 = st.columns(2)
        with col1:
            nombre_empresa = st.text_input("Nombre de la Empresa", value="Actiuform Design S.L.")
            sector_nicho = st.text_input("Sector y Nicho Especifico", value="Diseno, fabricacion y distribucion de mobiliario de oficina y espacios contract")
            modelo_actual = st.text_input("Propuesta Actual y Clientes", value="Venta B2B de mobiliario estandar y a medida a traves de distribuidores, arquitectos y licitaciones")
        with col2:
            fortaleza = st.text_input("Principal Activo / Fortaleza Actual", value="Fabrica flexible propia, control de calidad y red consolidada de arquitectos prescriptores")
            ambicion = st.selectbox("Nivel de Ambicion Innovadora", [
                "Disruptiva: Nuevos modelos de negocio, servicios por suscripcion e IA aplicada",
                "Adyacente: Nuevos canales digitales, personalizacion bajo demanda y sostenibilidad circular",
                "Incremental: Digitalizacion de procesos y ampliacion de catalogo de productos"
            ])
            amenaza = st.text_input("Mayor Desafio o Amenaza Percibida", value="Comoditizacion de precios por importaciones y reduccion de metros de oficina tradicional por teletrabajo")

        submit_btn = st.form_submit_button("Ejecutar Analisis de Mercado y Prospeccion")

if submit_btn:
    perfil = {
        "nombre_empresa": nombre_empresa,
        "sector_nicho": sector_nicho,
        "modelo_actual": modelo_actual,
        "fortaleza": fortaleza,
        "ambicion": ambicion,
        "amenaza": amenaza
    }
    with st.spinner("Analizando macrotendencias globales, aplicaciones tecnologicas y modelos de negocio..."):
        st.session_state["radar_resultado"] = generar_radar_innovacion(perfil)
        st.session_state["perfil_activo"] = perfil

# ==============================================================================
# 4. VISUALIZACION CONTINUA EN PANTALLA (SIN PESTANAS)
# ==============================================================================
if "radar_resultado" in st.session_state:
    radar = st.session_state["radar_resultado"]
    perfil = st.session_state["perfil_activo"]

    if "error" in radar:
        st.error(radar["error"])
    else:
        st.markdown("---")
        
        # Punto 1: Vision Estrategica
        st.subheader("1. Vision Estrategica de Direccion (Horizonte 3 Anos)")
        st.info(radar.get("resumen_vision", ""))

        st.markdown("---")

        # Punto 2: Radar de Tendencias
        st.subheader("2. Radar de Macro y Micro Tendencias Sectoriales")
        st.caption("Fuerzas de mercado que transformaran las reglas de competencia en el sector.")
        for t in radar.get("macrotendencias", []):
            with st.container():
                st.markdown(f"**{t.get('nombre')}** — *Horizonte: {t.get('horizonte')}*")
                c_a, c_b = st.columns(2)
                c_a.write(f"**Impacto Estructural en el Sector:**\n{t.get('impacto_sector')}")
                c_b.success(f"**Oportunidad Concreta para la Entidad:**\n{t.get('oportunidad_pyme')}")
                st.divider()

        # Punto 3: Scouting Tecnologico e IA
        st.subheader("3. Scouting Tecnologico y Aplicaciones de Inteligencia Artificial")
        st.caption("Tecnologias emergentes aplicadas quirurgicamente a la cadena de valor.")
        for tc in radar.get("tecnologias_aplicadas", []):
            with st.container():
                st.markdown(f"**{tc.get('tecnologia')}** — *Nivel de Madurez: {tc.get('madurez')}*")
                st.write(f"**Caso de Aplicacion en Operaciones o Producto:** {tc.get('caso_uso_real')}")
                st.caption(f"Referencia Global / Benchmark: {tc.get('ejemplo_mercado')}")
                st.divider()

        # Punto 4: Modelos de Negocio
        st.subheader("4. Nuevos Modelos de Negocio y Vias de Monetizacion")
        st.caption("Estructuras de generacion de ingresos para desacoplar el crecimiento del margen tradicional.")
        for mb in radar.get("nuevos_modelos_negocio", []):
            with st.container():
                st.markdown(f"**{mb.get('concepto')}**")
                st.write(f"**Mecanismo de Ingresos:** {mb.get('mecanismo_ingreso')}")
                st.write(f"**Ventaja Defensiva (Barrera de Entrada):** {mb.get('ventaja_defensiva')}")
                st.divider()

        # Punto 5: Matriz de Priorizacion
        st.subheader("5. Matriz de Priorizacion de Iniciativas")
        st.caption("Clasificacion de proyectos segun su retorno potencial frente a la complejidad de ejecucion.")
        df_mat = pd.DataFrame(radar.get("matriz_priorizacion", []))
        if not df_mat.empty:
            st.dataframe(df_mat, use_container_width=True)

        st.markdown("---")

        # Punto 6: Hoja de Ruta de Pilotos
        st.subheader("6. Hoja de Ruta de Experimentacion y Pilotos de Mercado")
        st.caption("Itinerario metodologico para validar las iniciativas con riesgo acotado.")
        for pl in radar.get("pilotos_accion", []):
            with st.container():
                st.markdown(f"**{pl.get('plazo')}**")
                st.write(f"**Accion Ejecutiva:** {pl.get('accion')}")
                st.info(f"Indicador Clave de Validacion (KPI): {pl.get('kpi_exito')}")
                st.divider()
