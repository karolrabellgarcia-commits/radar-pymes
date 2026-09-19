import streamlit as st
import pandas as pd
import json
import os
import google.generativeai as genai

# ==============================================================================
# 1. CONFIGURACIÓN DEL SISTEMA Y GESTIÓN DE API
# ==============================================================================
st.set_page_config(
    page_title="KROMA Enterprise | Radar Estratégico y Benchmarking por CIF",
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
    st.caption("Capa 1: Motor de sintesis directiva y evaluacion de riesgos.")
    st.divider()
    st.markdown("**Capas de Datos Conectadas:**")
    st.markdown("- Capa 2: Registro Mercantil / SABI (Balances)")
    st.markdown("- Capa 3: Benchmarking Ciego (50 Rivales CNAE)")
    st.markdown("- Capa 4: Radar BDNS y Scoring Vendor Finance")

if api_key_input:
    genai.configure(api_key=api_key_input)

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
            return genai.GenerativeModel(p)
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

# ==============================================================================
# 2. CAPAS 2 Y 3: BASE DE DATOS REGISTRO MERCANTIL / SABI & BENCHMARKING
# ==============================================================================
BASE_DATOS_SABI = {
    "B98765432": {
        "razon_social": "BioPack Levantina de Envases S.L.",
        "cnae": "1721 - Fabricacion de papel y carton ondulado; envases y embalajes",
        "provincia": "Valencia",
        "plantilla": 24,
        "historico_3y": {
            "2022": {"ventas": 2850000, "ebitda": 245000, "ebitda_pct": 8.6, "dso": 88, "dio": 46},
            "2023": {"ventas": 3120000, "ebitda": 280000, "ebitda_pct": 9.0, "dso": 84, "dio": 44},
            "2024": {"ventas": 3410000, "ebitda": 289850, "ebitda_pct": 8.5, "dso": 82, "dio": 42}
        },
        "balance_actual": {
            "ventas": 3410000,
            "coste_materiales": 1580000,
            "personal": 980000,
            "gastos_explotacion": 560150,
            "ebitda": 289850,
            "ebitda_pct": 8.5,
            "clientes_cobro_pendiente": 765000,
            "existencias_stock": 390000,
            "proveedores_deuda": 320000,
            "tesoreria_disponible": 65000,
            "deuda_bancaria_total": 540000,
            "ratio_deuda_ebitda": 1.86,
            "capex_maximo_anual": 45000
        },
        "benchmark_50_rivales": {
            "muestra_tamano": 50,
            "cnae_analizado": "1721 (Segmento 2M a 6M EUR en España)",
            "ebitda_medio_pct": 12.8,
            "ebitda_top25_pct": 15.4,
            "dso_medio_dias": 58,
            "dio_medio_dias": 28,
            "ventas_por_empleado_media": 185000,
            "ventas_por_empleado_empresa": 142083
        }
    },
    "A28123456": {
        "razon_social": "Mecanizados y Matrices del Norte S.A.",
        "cnae": "2562 - Ingenieria mecanica por cuenta de terceros / Mecanizado",
        "provincia": "Navarra",
        "plantilla": 18,
        "historico_3y": {
            "2022": {"ventas": 2100000, "ebitda": 210000, "ebitda_pct": 10.0, "dso": 92, "dio": 35},
            "2023": {"ventas": 2350000, "ebitda": 230000, "ebitda_pct": 9.8, "dso": 90, "dio": 38},
            "2024": {"ventas": 2580000, "ebitda": 245100, "ebitda_pct": 9.5, "dso": 87, "dio": 36}
        },
        "balance_actual": {
            "ventas": 2580000,
            "coste_materiales": 920000,
            "personal": 1020000,
            "gastos_explotacion": 394900,
            "ebitda": 245100,
            "ebitda_pct": 9.5,
            "clientes_cobro_pendiente": 615000,
            "existencias_stock": 254000,
            "proveedores_deuda": 210000,
            "tesoreria_disponible": 52000,
            "deuda_bancaria_total": 480000,
            "ratio_deuda_ebitda": 1.95,
            "capex_maximo_anual": 35000
        },
        "benchmark_50_rivales": {
            "muestra_tamano": 50,
            "cnae_analizado": "2562 (Segmento 1.5M a 5M EUR en España)",
            "ebitda_medio_pct": 14.2,
            "ebitda_top25_pct": 17.1,
            "dso_medio_dias": 62,
            "dio_medio_dias": 22,
            "ventas_por_empleado_media": 172000,
            "ventas_por_empleado_empresa": 143333
        }
    }
}

# ==============================================================================
# 3. CAPA 4: RADAR DE SUBVENCIONES VIGENTES Y PARTNERS VENDOR FINANCE
# ==============================================================================
SUBVENCIONES_OFICIALES = [
    {
        "organismo": "IVACE / Fondos Feder - Programa Economia Circular",
        "convocatoria": "Sustitucion de recubrimientos plasticos por dispersion acuosa en lineas termicas",
        "cobertura": "Hasta 40% a fondo perdido (Tope: 75.000 EUR)",
        "plazo": "Convocatoria activa - Cierre en 45 dias habiles",
        "cnaes_admisibles": ["1721", "2222"],
        "requisito_clave": "Reduccion certificada del 15% de residuos no reciclables en producto acabado.",
        "enlace_oficial": "https://sede.ivace.es/tramites/economia-circular-pyme"
    },
    {
        "organismo": "Ministerio de Industria - Activa Industria 4.0",
        "convocatoria": "Implantacion de vision artificial y sensorica estandar para reduccion de mermas",
        "cobertura": "100% asesoramiento tecnico + 35% inversion en equipamiento homologado",
        "plazo": "Ventanilla abierta ejercicio 2026",
        "cnaes_admisibles": ["1721", "2562", "28"],
        "requisito_clave": "Pyme industrial manufacturera con al menos 2 ejercicios depositados en Registro Mercantil.",
        "enlace_oficial": "https://www.industria.gob.es/ayudas/activa-industria"
    }
]

PARTNERS_VENDOR_FINANCE = [
    {
        "area": "Estructuracion de Circulante y Venta por Servicio (FaaS)",
        "entidad": "Grenke Bank / DLL Group (Vendor Finance)",
        "mecanismo": "Arrendamiento operativo: la pyme cobra el 100% de la maquinaria/lote a D+30 sin recurso y el cliente final abona cuota mensual sin consumir CIRBE bancaria de la pyme.",
        "scoring_entidad": "Pre-aprobado comercial (Ratio Deuda/EBITDA < 2.5x cumplido)",
        "contacto_directo": "operaciones.iberica@grenke.es (Ref: Homologacion KROMA)"
    },
    {
        "area": "Vision Artificial y Automatizacion sin Desarrollo Propio",
        "entidad": "Integrador Homologado Pekat Vision / Cognex Iberia",
        "mecanismo": "Instalacion de camaras comerciales sobre linea existente en 48 horas de parada tecnica. Cero programacion a medida.",
        "coste_orientativo": "28.500 EUR (Financiable mediante subvencion IVACE/Industria al 40% + renting a 36 meses)",
        "contacto_directo": "soluciones.industriales@integracion-vision.es"
    }
]

# ==============================================================================
# 4. CAPA 1: RAZONAMIENTO Y SÍNTESIS ESTRATÉGICA CON GEMINI
# ==============================================================================
def generar_dictamen_integral(empresa, benchmark, caja_atrapada_total, exceso_dso_eur, exceso_stock_eur):
    if not api_key_input:
        return "Configure la clave API Gemini en la barra lateral para generar el dictamen de direccion."

    prompt = f"""
    Actua como Director Principal de Consultoria Estrategica y Finanzas Corporativas para Pymes.
    Analiza este cruce de balances oficiales (SABI) frente a la muestra ciega de 50 competidores:

    EMPRESA AUDITADA:
    - Razon Social: {empresa['razon_social']} (CNAE: {empresa['cnae']})
    - Ventas 2024: {empresa['balance_actual']['ventas']:,.0f} EUR
    - EBITDA Real: {empresa['balance_actual']['ebitda']:,.0f} EUR ({empresa['balance_actual']['ebitda_pct']}%)
    - Plazo de Cobro (DSO): {empresa['historico_3y']['2024']['dso']} dias | Saldo en Clientes: {empresa['balance_actual']['clientes_cobro_pendiente']:,.0f} EUR
    - Rotacion de Stock (DIO): {empresa['historico_3y']['2024']['dio']} dias | Stock en Planta: {empresa['balance_actual']['existencias_stock']:,.0f} EUR
    - Ventas / Empleado: {benchmark['ventas_por_empleado_empresa']:,.0f} EUR/persona
    - CAPEX Maximo Disponible: {empresa['balance_actual']['capex_maximo_anual']:,.0f} EUR

    BENCHMARKING DE 50 RIVALES REALES (MISMO CNAE Y TRAMO):
    - EBITDA Medio del Sector: {benchmark['ebitda_medio_pct']}% (Top 25%: {benchmark['ebitda_top25_pct']}%)
    - DSO Medio Sectorial: {benchmark['dso_medio_dias']} dias
    - DIO Medio Sectorial: {benchmark['dio_medio_dias']} dias
    - Ventas / Empleado Media: {benchmark['ventas_por_empleado_media']:,.0f} EUR/persona

    DESVIACIONES CUANTIFICADAS:
    - Caja atrapada por cobrar mas tarde que la media: {exceso_dso_eur:,.0f} EUR
    - Caja inmovilizada por exceso de inventario: {exceso_stock_eur:,.0f} EUR
    - Total liquidez liberable sin prestamos: {caja_atrapada_total:,.0f} EUR

    INSTRUCCIONES DIRECTIVAS INQUEBRANTABLES:
    1. Redacta un dictamen financiero y operativo implacable. Cero palabreria y cero lugares comunes.
    2. Prohibido sugerir que la empresa programe software propio o cree soluciones desde cero.
    3. Detalla como articular la solucion utilizando Vendor Finance externo para no ahogar la caja.
    4. Estructura un Roadmap formal de 3 fases (Dias 1-30, Dias 31-60, Dias 61-90).
    5. No utilices emoticonos ni iconos decorativos.

    RESPONDE EXCLUSIVAMENTE CON UN OBJETO JSON VALIDO:
    {{
        "dictamen_financiero": "Analisis de brecha de margen y evaluacion de la caja inmovilizada frente a rivales...",
        "causa_raiz_operativa": "Por que la pyme se desvia del cuartil superior en productividad y dias de inventario...",
        "solucion_estructurada_circulante": "Como financiar la modernizacion a traves de Vendor Finance sin deuda bancaria tradicional...",
        "roadmap_ejecucion": [
            {{
                "fase": "Dias 1 a 30",
                "hito": "Auditoria de referencias criticas y registro de memoria tecnica en sede electronica de subvencion.",
                "entregable": "Documento o resguardo oficial obtenido"
            }},
            {{
                "fase": "Dias 31 a 60",
                "hito": "Scoring con financiera de renting (Grenke/DLL) y recepcion de hardware estandar de vision/sellado.",
                "entregable": "Contrato de arrendamiento operativo aprobado y acta de instalacion"
            }},
            {{
                "fase": "Dias 61 a 90",
                "hito": "Lanzamiento de lote industrial piloto y renegociacion de plazos con distribuidores clave.",
                "entregable": "Primera orden comercial facturada y reduccion documentada de DSO a 60 dias"
            }}
        ]
    }}
    """
    try:
        m = obtener_modelo_activo()
        res = m.generate_content(prompt)
        t = res.text.strip()
        if t.startswith("```json"):
            t = t[7:]
        if t.startswith("```"):
            t = t[3:]
        if t.endswith("```"):
            t = t[:-3]
        return json.loads(t.strip())
    except Exception as e:
        return {"error": f"Error al generar sintesis con IA: {str(e)}"}

# ==============================================================================
# 5. INTERFAZ DE USUARIO: CONSULTA POR CIF Y DESPLIEGUE CONTINUO
# ==============================================================================
st.title("KROMA Enterprise — Inteligencia Estratégica Industrial por CIF")
st.caption("Ingesta oficial de cuentas anuales, comparativa ciega con 50 rivales de sector y ejecucion directa sin arriesgar circulante.")

col_input, col_action = st.columns([3, 1])
with col_input:
    cif_seleccionado = st.text_input(
        "Introduzca el CIF de la entidad (o seleccione de la muestra activa):",
        value="B98765432",
        help="Pruebe con B98765432 (Packaging y celulosa) o A28123456 (Mecanizado CNC)"
    )
with col_action:
    st.write("")
    st.write("")
    consultar = st.button("Ejecutar Auditoria por CIF")

if cif_seleccionado:
    if cif_seleccionado not in BASE_DATOS_SABI:
        st.error("CIF no localizado en la muestra activa. Utilice 'B98765432' o 'A28123456' para evaluar la demo.")
    else:
        empresa = BASE_DATOS_SABI[cif_seleccionado]
        bench = empresa["benchmark_50_rivales"]
        bal = empresa["balance_actual"]

        # Calculo exacto de dinero atrapado frente al benchmark
        ventas_dia = bal["ventas"] / 365.0
        coste_dia = bal["coste_materiales"] / 365.0

        dias_exceso_cobro = max(0, empresa["historico_3y"]["2024"]["dso"] - bench["dso_medio_dias"])
        exceso_dso_eur = dias_exceso_cobro * ventas_dia

        dias_exceso_stock = max(0, empresa["historico_3y"]["2024"]["dio"] - bench["dio_medio_dias"])
        exceso_stock_eur = dias_exceso_stock * coste_dia

        caja_atrapada_total = exceso_dso_eur + exceso_stock_eur

        st.markdown("---")

        # ----------------------------------------------------------------------
        # 1. RADIOGRAFIA FINANCIERA OFICIAL Y BENCHMARKING DE 50 RIVALES
        # ----------------------------------------------------------------------
        st.subheader(f"1. Radiografia de Cuentas Anuales Oficiales: {empresa['razon_social']}")
        st.caption(f"CIF: {cif_seleccionado} | CNAE: {empresa['cnae']} | Sede: {empresa['provincia']} | Muestra de cotejo: {bench['muestra_tamano']} empresas homologas.")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Facturacion 2024", f"{bal['ventas']:,.0f} EUR", "+9.3% s/2023")
        m2.metric("Margen EBITDA Real", f"{bal['ebitda_pct']:.1f} %", f"Media rivales: {bench['ebitda_medio_pct']:.1f}%", delta_color="inverse")
        m3.metric("Plazo Medio de Cobro (DSO)", f"{empresa['historico_3y']['2024']['dso']} dias", f"Media rivales: {bench['dso_medio_dias']} dias", delta_color="inverse")
        m4.metric("Caja Atrapada s/Sector", f"{caja_atrapada_total:,.0f} EUR", "Cobros demorados + Stock", delta_color="inverse")

        st.markdown("##### Comparativa Estructural frente a los 50 Mayores Rivales del Mismo CNAE")
        df_bench = pd.DataFrame([
            {
                "Ratio Analizado": "Margen de Explotacion EBITDA",
                "Su Empresa": f"{bal['ebitda_pct']:.1f} %",
                "Media de 50 Rivales": f"{bench['ebitda_medio_pct']:.1f} %",
                "Top 25% (Lideres de Sector)": f"{bench['ebitda_top25_pct']:.1f} %",
                "Brecha Cuantificada": f"{bal['ebitda_pct'] - bench['ebitda_medio_pct']:.1f} % de margen no capturado"
            },
            {
                "Ratio Analizado": "Periodo Medio de Cobro de Clientes (DSO)",
                "Su Empresa": f"{empresa['historico_3y']['2024']['dso']} dias",
                "Media de 50 Rivales": f"{bench['dso_medio_dias']} dias",
                "Top 25% (Lideres de Sector)": "45 dias",
                "Brecha Cuantificada": f"{exceso_dso_eur:,.0f} EUR inmovilizados financiando a terceros"
            },
            {
                "Ratio Analizado": "Permanencia de Inventario y Stock (DIO)",
                "Su Empresa": f"{empresa['historico_3y']['2024']['dio']} dias",
                "Media de 50 Rivales": f"{bench['dio_medio_dias']} dias",
                "Top 25% (Lideres de Sector)": "20 dias",
                "Brecha Cuantificada": f"{exceso_stock_eur:,.0f} EUR atrapados en almacen"
            },
            {
                "Ratio Analizado": "Productividad por Empleado",
                "Su Empresa": f"{bench['ventas_por_empleado_empresa']:,.0f} EUR/empleado",
                "Media de 50 Rivales": f"{bench['ventas_por_empleado_media']:,.0f} EUR/empleado",
                "Top 25% (Lideres de Sector)": "220.000 EUR/empleado",
                "Brecha Cuantificada": "Suboptimizacion en turnos y horas de parada tecnica"
            }
        ])
        st.dataframe(df_bench, use_container_width=True)

        st.markdown("---")

        # ----------------------------------------------------------------------
        # 2. DICTAMEN DE DIRECCION ESTRATEGICA Y FINANCIERA (IA GEMINI)
        # ----------------------------------------------------------------------
        st.subheader("2. Dictamen Ejecutivo de Direccion")
        with st.spinner("Sintetizando balance oficial con benchmarking de mercado..."):
            analisis = generar_dictamen_integral(empresa, bench, caja_atrapada_total, exceso_dso_eur, exceso_stock_eur)

        if isinstance(analisis, dict) and "error" not in analisis:
            st.info(analisis.get("dictamen_financiero", ""))
            
            c_causa, c_sol = st.columns(2)
            c_causa.markdown("**Causa Raiz de la Ineficiencia:**")
            c_causa.write(analisis.get("causa_raiz_operativa", ""))
            
            c_sol.markdown("**Estructura Financiera Recomendada (Sin Consumir Balance):**")
            c_sol.write(analisis.get("solucion_estructurada_circulante", ""))

            st.markdown("##### Hoja de Ruta de Ejecucion Inmediata (30-60-90 Dias)")
            for item in analisis.get("roadmap_ejecucion", []):
                st.markdown(f"**{item.get('fase')} — {item.get('hito')}**")
                st.caption(f"Entregable Tangible Requerido: {item.get('entregable')}")
                st.divider()
        else:
            st.warning("No fue posible estructurar el dictamen de IA. Verifique la API Key en el menu lateral.")

        # ----------------------------------------------------------------------
        # 3. RADAR DE SUBVENCIONES VIGENTES (CONEXIÓN BDNS / BOE)
        # ----------------------------------------------------------------------
        st.subheader("3. Convocatorias de Subvencion Publica Vigentes y Aplicables")
        st.caption(f"Ayudas filtradas especificamente para el CNAE {empresa['cnae'].split(' - ')[0]} y tipologia de pyme:")

        cnae_code = empresa['cnae'].split(' - ')[0]
        subvenciones_filtradas = [s for s in SUBVENCIONES_OFICIALES if any(c in cnae_code for c in s["cnaes_admisibles"])]

        for sub in subvenciones_filtradas:
            with st.container():
                st.markdown(f"**{sub['organismo']}**")
                st.write(f"*{sub['convocatoria']}*")
                c_sub1, c_sub2 = st.columns(2)
                c_sub1.write(f"**Intensidad de Ayuda:** {sub['cobertura']}\n\n**Estado:** {sub['plazo']}")
                c_sub2.write(f"**Criterio de Asignacion:** {sub['requisito_clave']}")
                st.markdown(f"[Acceso Directo al Tramite en Sede Electronica]({sub['enlace_oficial']})")
                st.divider()

        # ----------------------------------------------------------------------
        # 4. MARKETPLACE DE ACCION DIRECTA (VENDOR FINANCE Y TECNOLOGIAS COTS)
        # ----------------------------------------------------------------------
        st.subheader("4. Partners Homologados y Canales Directos de Ejecucion")
        st.caption("Soluciones estructuradas para implantar en planta sin crear software y cobrando de inmediato:")

        for part in PARTNERS_VENDOR_FINANCE:
            with st.container():
                st.markdown(f"**Area:** `{part['area']}` | **Entidad:** **{part['entidad']}**")
                st.write(f"**Esquema Operativo:** {part['mecanismo']}")
                c_p1, c_p2 = st.columns(2)
                if "scoring_entidad" in part:
                    c_p1.success(f"**Scoring Financiero Preliminar:** {part['scoring_entidad']}")
                if "coste_orientativo" in part:
                    c_p1.info(f"**Coste Llave en Mano:** {part['coste_orientativo']}")
                c_p2.write(f"**Canal de Contacto Homologado:** `{part['contacto_directo']}`")
                st.divider()
