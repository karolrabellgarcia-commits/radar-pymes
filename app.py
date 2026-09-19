import streamlit as st
import pandas as pd
import os
import json
import google.generativeai as genai

# ==============================================================================
# 1. CONFIGURACION Y CLIENTE IA
# ==============================================================================
st.set_page_config(
    page_title="KROMA TrendRadar | Inteligencia Estrategica e Innovacion Pragmatica",
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
# 2. MOTOR DE PROSPECCION Y RADAR DE INNOVACION PRAGMATICA
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
    Actua como Socio Director de Innovacion Estrategica y Operaciones para Pymes Industriales y de Servicios.
    Tu cliente es el Director General y el Comite de Direccion de la siguiente pyme:

    PERFIL OPERATIVO Y COMERCIAL:
    - Razon Social: {perfil.get('nombre_empresa')}
    - Sector y Nicho Concreto: {perfil.get('sector_nicho')}
    - Facturacion Anual Aprox. y Margen Bruto Medio: {perfil.get('tamano_margen')}
    - Modelo Comercial y Clientes Principales: {perfil.get('modelo_actual')}
    - Parque de Maquinaria / Activos Clave: {perfil.get('activos_instalados')}
    - Capacidad de Inversion Real (CAPEX Maximo para Innovacion): {perfil.get('capacidad_inversion')}
    - Amenaza Inmediata / Presion de Mercado: {perfil.get('amenaza')}

    LEYES INQUEBRANTABLES DE TU DICTAMEN (PROHIBIDO EL HUMO TEORICO):
    1. REGLA DEL CIRCULANTE: Si recomiendas un modelo de recurrencia, suscripcion o servitizacion, ES OBLIGATORIO especificar como se financia el inmovilizado sin consumir la caja de la pyme (menciona esquemas de Vendor Finance, arrendamiento operativo con entidades tipo Grenke, BNP Paribas Lease Group, DLL, Santander Leasing, etc.). La pyme debe cobrar a D+30 el total del pedido.
    2. REGLA DE INTEGRACION (NO INVENTAR SOFTWARE): Queda terminantemente prohibido sugerir que la pyme programe software propio, cree gemelos digitales caseros o desarrolle hardware IoT desde cero si no es una empresa de telecomunicaciones. Se recomiendan alianzas, integraciones de hardware estandar o soluciones SaaS consolidadas en marca blanca.
    3. REGLA DE LOS CICLOS B2B: Los plazos deben ajustarse a la realidad comercial (los ciclos de decision duran de 3 a 9 meses). En 30 dias no se crean plataformas; en 30 dias se audita el catalogo, se contacta a proveedores tecnologicos y se negocian acuerdos de canal.
    4. TONO: Cero emoticonos. Lenguaje tecnico-financiero, directo, pragmatico y exigente.

    GENERA EXCLUSIVAMENTE UN OBJETO JSON VALIDO CON ESTA ESTRUCTURA (sin bloques markdown de codigo ```json ni texto adicional):
    {{
        "resumen_vision": "Parrafo ejecutivo que aterriza donde estan los margenes en los proximos 24 meses y como defenderse de la comoditizacion sin arruinar la tesoreria.",
        "macrotendencias": [
            {{
                "nombre": "Nombre preciso de la tendencia sectorial",
                "horizonte": "6-12 meses / 12-24 meses",
                "impacto_cuenta_perdidas": "Traduccion a perdida o ganancia de pedidos reales (ej. exclusion de licitaciones, caida de margenes por normativa, etc.)",
                "accion_defensiva_pyme": "Que decision concreta de planta, catalogo o aprovisionamiento neutraliza esta amenaza con su maquinaria actual."
            }},
            {{
                "nombre": "Segunda tendencia sectorial",
                "horizonte": "...",
                "impacto_cuenta_perdidas": "...",
                "accion_defensiva_pyme": "..."
            }}
        ],
        "tecnologias_aplicadas": [
            {{
                "tecnologia": "Nombre de la tecnologia o solucion de automatizacion/IA",
                "estrategia_adquisicion": "Comprar SaaS / Integrar Marca Blanca / Hardware Estandar (PROHIBIDO DESARROLLO PROPIO)",
                "caso_uso_operativo": "Donde se inserta en su cadena de produccion, almacén o venta y que coste ahorra o que valor anade",
                "proveedor_tipo_benchmark": "Tipo de proveedor comercial o solucion existente en el mercado que lo suministra llave en mano"
            }},
            {{
                "tecnologia": "Segunda tecnologia",
                "estrategia_adquisicion": "...",
                "caso_uso_operativo": "...",
                "proveedor_tipo_benchmark": "..."
            }}
        ],
        "nuevos_modelos_negocio": [
            {{
                "concepto": "Nombre del modelo de monetizacion",
                "mecanismo_financiero_cobro": "Explicacion de como cobra la pyme (al contado o cuotas) y quien financia el riesgo de impago y el circulante",
                "barrera_defensiva": "Por que un distribuidor tradicional o un competidor asiatico/low-cost no puede replicarlo facilmente"
            }},
            {{
                "concepto": "Segundo modelo de negocio",
                "mecanismo_financiero_cobro": "...",
                "barrera_defensiva": "..."
            }}
        ],
        "matriz_priorizacion": [
            {{
                "iniciativa": "Nombre de la iniciativa 1",
                "impacto_margen": "Alto / Medio / Muy Alto",
                "complejidad_inversion": "Baja (Subcontratable/SaaS) / Media (Adaptar linea actual) / Muy Alta",
                "plazo_retorno": "3-4 meses / 6 meses / > 12 meses",
                "veredicto_estrategico": "Victoria Rapida / Prioridad Estrategica / Exploracion Clave / Descartar"
            }},
            {{
                "iniciativa": "Nombre de la iniciativa 2",
                "impacto_margen": "...",
                "complejidad_inversion": "...",
                "plazo_retorno": "...",
                "veredicto_estrategico": "..."
            }},
            {{
                "iniciativa": "Nombre de la iniciativa 3",
                "impacto_margen": "...",
                "complejidad_inversion": "...",
                "plazo_retorno": "...",
                "veredicto_estrategico": "..."
            }},
            {{
                "iniciativa": "Nombre de la iniciativa 4 (Generalmente el error tipico que deben descartar)",
                "impacto_margen": "Teorico Alto",
                "complejidad_inversion": "Muy Alta / Suicidio de Caja",
                "plazo_retorno": "> 18 meses",
                "veredicto_estrategico": "Descartar Tajantemente"
            }}
        ],
        "pilotos_accion": [
            {{
                "plazo": "Fase 1: Dias 1 a 30 (Auditoria Interna y Homologacion de Partners)",
                "accion": "Revision de cartera de productos que admiten la transformacion y contacto formal con partners o financieras.",
                "entregable_tangible": "Documento o acuerdo previo obtenido al finalizar el mes 1"
            }},
            {{
                "plazo": "Fase 2: Dias 31 a 60 (Lanzamiento de Kit Tecnico y Oferta Comercial)",
                "accion": "Preparacion de la oferta comercial empaquetada y herramientas de prescripcion sin inversor de software.",
                "entregable_tangible": "Catalogo de servicios o kit comercial listo para red de ventas"
            }},
            {{
                "plazo": "Fase 3: Dias 61 a 90 (Piloto Controlado con 3 Clientes Clave)",
                "accion": "Presentacion a puerta cerrada con 3 cuentas de confianza para validar el modelo y el precio.",
                "entregable_tangible": "Oferta formal emitida con estructura financiera cerrada"
            }},
            {{
                "plazo": "Fase 4: Dias 91 a 180 (Escalado a Cartera y Medicion de Margen)",
                "accion": "Apertura al 100% de la fuerza comercial y sustitucion gradual de referencias obsoletas.",
                "entregable_tangible": "Volumen de facturacion neta y margen bruto consolidado"
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
# 3. FORMULARIO CONTINUO Y PRECARGADO (CASO NUEVO: PACKAGING INDUSTRIAL B2B)
# ==============================================================================
st.title("KROMA TrendRadar — Inteligencia Estrategica e Innovacion Pragmatica")
st.caption("Prospeccion sectorial, scouting de tecnologia de terceros y estructuracion de ingresos para Pymes sin arriesgar circulante.")

with st.expander("Perfil de Operaciones, Finanzas y Estrategia de la Pyme", expanded=True):
    with st.form("form_radar_pragmatico"):
        c1, c2 = st.columns(2)
        with c1:
            nombre_empresa = st.text_input("Razon Social:", value="BioPack Iberia S.L.")
            sector_nicho = st.text_input("Sector y Nicho Concreto:", value="Fabricacion y termoformado de envases tecnicos de carton y celulosa para alimentacion e industria Horeca")
            tamano_margen = st.text_input("Facturacion y Margen Bruto Medio Actual:", value="3.400.000 EUR anuales | Margen bruto de explotacion del 32%")
            modelo_actual = st.text_input("Canal Comercial y Segmento Principal:", value="Distribuidores regionales de hosteleria (60%), industria alimentaria procesadora (30%) y venta directa a cadenas (10%)")
        with c2:
            activos_instalados = st.text_input("Parque de Maquinaria y Activos Clave:", value="4 lineas de termoformado semiautomatico, 2 troqueladoras planas y nave industrial en propiedad con 4.200 m2")
            capacidad_inversion = st.text_input("CAPEX Maximo para Nuevas Iniciativas:", value="45.000 EUR de fondos propios en 12 meses (recelo total a endeudamiento bancario adicional)")
            amenaza = st.text_input("Presion o Amenaza Inmediata de Mercado:", value="Entrada masiva de envases de caña de azucar y carton de fabricantes asiaticos un 22% mas baratos y nueva directiva europea de ecodiseño (PPWR)")

        submit_btn = st.form_submit_button("Generar Dictamen de Innovacion y Prospeccion")

if submit_btn:
    perfil = {
        "nombre_empresa": nombre_empresa,
        "sector_nicho": sector_nicho,
        "tamano_margen": tamano_margen,
        "modelo_actual": modelo_actual,
        "activos_instalados": activos_instalados,
        "capacidad_inversion": capacidad_inversion,
        "amenaza": amenaza
    }
    with st.spinner("Analizando fuerzas de mercado, partners tecnologicos y estructuras financieras de circulante..."):
        st.session_state["radar_resultado"] = generar_radar_innovacion(perfil)
        st.session_state["perfil_activo"] = perfil

# ==============================================================================
# 4. ENTREGA COMPLETA Y SECUENCIAL EN PANTALLA (SIN PESTANAS, SIN PDF)
# ==============================================================================
if "radar_resultado" in st.session_state:
    radar = st.session_state["radar_resultado"]
    perfil = st.session_state["perfil_activo"]

    if "error" in radar:
        st.error(radar["error"])
    else:
        st.markdown("---")

        # Punto 1: Vision Estrategica y Diagnostico de Margen
        st.subheader("1. Dictamen Ejecutivo de Direccion y Preservacion de Margen")
        st.info(radar.get("resumen_vision", ""))

        st.markdown("---")

        # Punto 2: Tendencias Sectoriales Aterrizadas en Pedidos
        st.subheader("2. Tendencias Estructurales y su Impacto en Perdidas y Ganancias")
        st.caption("Fuerzas regulatorias y de mercado que provocaran perdida real de clientes si no se reacciona.")
        for t in radar.get("macrotendencias", []):
            with st.container():
                st.markdown(f"**{t.get('nombre')}** — *Plazo de Impacto: {t.get('horizonte')}*")
                col_t1, col_t2 = st.columns(2)
                col_t1.error(f"**Impacto Directo en Cuenta de Resultados:**\n\n{t.get('impacto_cuenta_perdidas')}")
                col_t2.success(f"**Respuesta Defensiva con Maquinaria Actual:**\n\n{t.get('accion_defensiva_pyme')}")
                st.divider()

        # Punto 3: Scouting Tecnologico Pragmatico (Build vs Buy)
        st.subheader("3. Scouting Tecnologico y Automatizacion sin Desarrollo Propio")
        st.caption("Adopcion de tecnologia contrastada de terceros en planta y operaciones comerciales sin contratar desarrolladores.")
        for tc in radar.get("tecnologias_aplicadas", []):
            with st.container():
                st.markdown(f"**{tc.get('tecnologia')}**")
                st.write(f"**Via de Adquisicion:** `{tc.get('estrategia_adquisicion')}`")
                st.write(f"**Aplicacion en Planta / Venta:** {tc.get('caso_uso_operativo')}")
                st.caption(f"Proveedor Tipo / Solucion Existente en Mercado: {tc.get('proveedor_tipo_benchmark')}")
                st.divider()

        # Punto 4: Modelos de Negocio con Circulante Blindado
        st.subheader("4. Nuevas Vias de Monetizacion con Financiacion Externa de Circulante")
        st.caption("Esquemas de recurrencia y servicios de valor donde la pyme cobra el pedido al contado y la financiera asume el riesgo.")
        for mb in radar.get("nuevos_modelos_negocio", []):
            with st.container():
                st.markdown(f"**{mb.get('concepto')}**")
                st.write(f"**Mecanismo Financiero de Cobro:** {mb.get('mecanismo_financiero_cobro')}")
                st.write(f"**Barrera Defensiva frente a Low-Cost:** {mb.get('barrera_defensiva')}")
                st.divider()

        # Punto 5: Matriz de Priorizacion y Descarte
        st.subheader("5. Matriz de Priorizacion Estrategica y Descarte de Errores")
        st.caption("Evaluacion rigurosa de impacto frente a consumo de recursos.")
        df_mat = pd.DataFrame(radar.get("matriz_priorizacion", []))
        if not df_mat.empty:
            df_mat.columns = ["Iniciativa", "Impacto en Margen", "Complejidad / Inversion", "Plazo de Retorno", "Veredicto Estrategico"]
            st.dataframe(df_mat, use_container_width=True)

        st.markdown("---")

        # Punto 6: Plan de Accion Realista (30, 60, 90, 180 dias)
        st.subheader("6. Hoja de Ruta de Ejecucion Comercial y Operativa")
        st.caption("Itinerario adaptado a los tiempos reales de homologacion industrial y respuesta de clientes.")
        for pl in radar.get("pilotos_accion", []):
            with st.container():
                st.markdown(f"**{pl.get('plazo')}**")
                st.write(f"**Actuacion Ejecutiva:** {pl.get('accion')}")
                st.info(f"Entregable Tangible / Hito Clave: {pl.get('entregable_tangible')}")
                st.divider()
