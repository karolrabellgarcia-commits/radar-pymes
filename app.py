import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import google.generativeai as genai

# ==============================================================================
# 1. CONFIGURACION DEL SISTEMA
# ==============================================================================
st.set_page_config(
    page_title="KROMA Enterprise | Diagnostico Oficial y Benchmarking",
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
        help="Clave de acceso de Google AI Studio"
    )
    st.caption("Capa 1: Motor generativo y sintesis directiva.")
    st.divider()
    st.markdown("**Bases de Datos Conectadas:**")
    st.markdown("- Registro Mercantil / SABI (Balances 2022-2024)")
    st.markdown("- BDNS / BOE (Convocatorias de Subvencion)")
    st.markdown("- Ecosistema Vendor Finance (Grenke / DLL / BNP)")

if api_key_input:
    genai.configure(api_key=api_key_input)

def obtener_modelo():
    preferidos = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash"]
    for p in preferidos:
        try:
            return genai.GenerativeModel(p)
        except Exception:
            continue
    return genai.GenerativeModel("gemini-1.5-flash")

# ==============================================================================
# 2. CAPA 2 Y 3: SIMULADOR DE INGESTA DE BALANCES OFICIALES Y BENCHMARK (SABI)
# ==============================================================================
BASE_DATOS_SABI = {
    "B98765432": {
        "razon_social": "BioPack Levantina de Envases S.L.",
        "cnae": "1721 - Fabricacion de papel y carton ondulado; envases y embalajes",
        "provincia": "Valencia",
        "empleados": 24,
        "historico_financiero": {
            "2022": {"ventas": 2850000, "ebitda": 245000, "deuda_neta": 620000, "dso": 88, "dio": 46},
            "2023": {"ventas": 3120000, "ebitda": 280000, "deuda_neta": 580000, "dso": 84, "dio": 44},
            "2024": {"ventas": 3410000, "ebitda": 289850, "deuda_neta": 540000, "dso": 82, "dio": 42}
        },
        "balance_actual": {
            "ventas": 3410000,
            "coste_materiales": 1580000,
            "personal": 980000,
            "gastos_explotacion": 560150,
            "ebitda": 289850,
            "ebitda_pct": 8.5,
            "clientes_cobro_pendiente": 765000, # DSO 82 dias
            "existencias_stock": 390000,        # DIO 42 dias
            "proveedores_deuda": 320000,
            "tesoreria_disponible": 65000
        },
        "benchmark_sectorial_50_rivales": {
            "ebitda_medio_pct": 12.8,
            "ebitda_top25_pct": 15.4,
            "dso_medio_dias": 58,
            "dio_medio_dias": 28,
            "facturacion_por_empleado_media": 185000,
            "facturacion_por_empleado_empresa": 142083
        }
    }
}

# ==============================================================================
# 3. CAPA 4: RADAR DE SUBVENCIONES Y MARKETPLACE DE SOLUCIONES
# ==============================================================================
SUBVENCIONES_ACTIVAS = [
    {
        "organismo": "IVACE / Feder - Economia Circular e Innovacion Industrial",
        "convocatoria": "Adaptacion de lineas de termoformado y extrusion a biomateriales monomateriales",
        "dotacion": "Hasta 40% a fondo perdido (Max. 75.000 EUR)",
        "plazo": "Vigente - Cierre proximo en 45 dias habiles",
        "requisito_clave": "Reduccion minima del 15% en huella de carbono y eliminacion de recubrimientos no separables.",
        "enlace_tramite": "https://sede.ivace.es/tramites/economia-circular-pyme"
    },
    {
        "organismo": "Ministerio de Industria - Programa Activa Industria 4.0 / Kit Consulting",
        "convocatoria": "Auditoria e implantacion de vision artificial y sensórica en planta",
        "dotacion": "100% subvencionado hasta 12.000 EUR de diagnostico + deduccion fiscal I+D+i",
        "plazo": "Abierta convocatoria continua",
        "requisito_clave": "Pyme industrial de 10 a 249 trabajadores con contabilidad auditada.",
        "enlace_tramite": "https://www.industria.gob.es/ayudas/activa-industria"
    }
]

MARKETPLACE_PARTNERS = [
    {
        "area": "Vendor Finance y Liquidez de Ventas",
        "partner": "Grenke Finance / DLL Leasing",
        "solucion": "Esquema de arrendamiento operativo para que BioPack cobre a 30 dias el 100% de los envases/maquinas dispensadoras mientras el cliente abona cuota mensual sin riesgo de impago.",
        "contacto_directo": "canal.industrial@grenke.es (Ref: Homologacion KROMA)",
        "scoring_preliminar": "Apto (Deuda Neta / EBITDA: 1.86x - Calificacion favorable)"
    },
    {
        "area": "Vision Artificial y Control de Mermas",
        "partner": "Pekat Vision / Integrador Homologado Autonómico",
        "solucion": "Sistema llave en mano de camaras lineales para deteccion de poros en sellado termico a 120 golpes/minuto.",
        "contacto_directo": "proyectos@integracion-vision.es (Pliego tecnico base preconfigurado)",
        "presupuesto_estimado": "28.500 EUR (Elegible 40% subvencion IVACE)"
    }
]

# ==============================================================================
# 4. CAPA 1: RAZONAMIENTO Y SINTESIS DIRECTIVA CON GEMINI
# ==============================================================================
def generar_dictamen_cruzado(datos_empresa, benchmark, subvenciones):
    if not api_key_input:
        return "Configure la clave API en la barra lateral para generar la sintesis analitica."

    prompt = f"""
    Actua como Socio Principal de Auditoria Financiera y Estrategica para Pymes.
    Analiza este cruce de datos oficiales del Registro Mercantil (SABI) frente al Benchmark de 50 rivales:

    EMPRESA: {datos_empresa['razon_social']} (CNAE: {datos_empresa['cnae']})
    - Facturacion 2024: {datos_empresa['balance_actual']['ventas']:,.0f} EUR | EBITDA: {datos_empresa['balance_actual']['ebitda']:,.0f} EUR ({datos_empresa['balance_actual']['ebitda_pct']}%)
    - Plazo Medio de Cobro (DSO): {datos_empresa['balance_actual']['clientes_cobro_pendiente']} EUR pendientes ({datos_empresa['historico_financiero']['2024']['dso']} dias)
    - Rotacion de Stock (DIO): {datos_empresa['balance_actual']['existencias_stock']} EUR ({datos_empresa['historico_financiero']['2024']['dio']} dias)
    - Ventas por Empleado: {benchmark['facturacion_por_empleado_empresa']:,.0f} EUR/persona

    BENCHMARK REAL DE 50 RIVALES DEL MISMO CNAE Y TRAMO:
    - EBITDA Medio del Sector: {benchmark['ebitda_medio_pct']}% (Top 25% cuartil superior: {benchmark['ebitda_top25_pct']}%)
    - DSO Medio Sectorial: {benchmark['dso_medio_dias']} dias
    - DIO Medio Sectorial: {benchmark['dio_medio_dias']} dias
    - Ventas por Empleado Media: {benchmark['facturacion_por_empleado_media']:,.0f} EUR/persona

    SUBVENCIONES Y PARTNERS DISPONIBLES:
    {json.dumps(subvenciones, ensure_ascii=False)}

    INSTRUCCIONES DIRECTIVAS:
    1. Cuantifica con precision quirurgica cuanta caja tiene atrapada la empresa por desviarse del benchmark sectorial en cobros y existencias.
    2. Identifica la brecha de margen y productividad respecto al Top 25% del sector.
    3. Formula una recomendacion ejecutiva directa articulada con el partner financiero (Vendor Finance) y la subvencion activa correspondiente.
    4. Cero emoticonos, tono implacable de comite de direccion y rigor contable absoluto.

    Redacta un dictamen ejecutivo en 3 parrafos tecnicos densos.
    """
    try:
        m = obtener_modelo()
        res = m.generate_content(prompt)
        return res.text.strip()
    except Exception as e:
        return f"Error al generar sintesis: {str(e)}"

# ==============================================================================
# 5. INTERFAZ: ENTRADA POR CIF Y PANEL CONTINUO
# ==============================================================================
st.title("KROMA Enterprise — Diagnostico Basado en Datos Oficiales y Benchmarking")
st.caption("Cruce automatizado de cuentas anuales (SABI), radar de subvenciones abiertas y marketplace de ejecucion.")

c_cif, c_btn = st.columns([3, 1])
with c_cif:
    cif_input = st.text_input("Introduzca el CIF de la entidad para iniciar la ingesta:", value="B98765432")
with c_btn:
    st.write("")
    st.write("")
    consultar_btn = st.button("Ingestar Balances y Comparar")

if consultar_btn or "empresa_data" in st.session_state:
    if cif_input not in BASE_DATOS_SABI:
        st.error("CIF no localizado en la muestra activa. Para la prueba utilice el CIF precargado: B98765432.")
    else:
        emp = BASE_DATOS_SABI[cif_input]
        bench = emp["benchmark_sectorial_50_rivales"]
        st.session_state["empresa_data"] = emp

        # Calculo de dinero atrapado respecto al sector
        ventas_dia = emp["balance_actual"]["ventas"] / 365.0
        exceso_dias_cobro = max(0, emp["historico_financiero"]["2024"]["dso"] - bench["dso_medio_dias"])
        caja_atrapada_clientes = exceso_dias_cobro * ventas_dia

        coste_dia = emp["balance_actual"]["coste_materiales"] / 365.0
        exceso_dias_stock = max(0, emp["historico_financiero"]["2024"]["dio"] - bench["dio_medio_dias"])
        caja_atrapada_stock = exceso_dias_stock * coste_dia

        total_caja_liberable = caja_atrapada_clientes + caja_atrapada_stock

        st.markdown("---")
        
        # ----------------------------------------------------------------------
        # BLOQUE 1: RADIOGRAFIA OFICIAL Y BENCHMARKING FRENTE A 50 RIVALES
        # ----------------------------------------------------------------------
        st.subheader(f"1. Radiografia Financiera Oficial: {emp['razon_social']}")
        st.caption(f"CNAE: {emp['cnae']} | Datos auditados extraidos de Cuentas Anuales Oficiales.")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Facturacion 2024", f"{emp['balance_actual']['ventas']:,.0f} EUR", "+9.3% interanual")
        m2.metric("Margen EBITDA Real", f"{emp['balance_actual']['ebitda_pct']}%", f"Sector medio: {bench['ebitda_medio_pct']}%", delta_color="inverse")
        m3.metric("Plazo Medio de Cobro (DSO)", f"{emp['historico_financiero']['2024']['dso']} dias", f"Sector: {bench['dso_medio_dias']} dias", delta_color="inverse")
        m4.metric("Caja Atrapada s/Sector", f"{total_caja_liberable:,.0f} EUR", "Cobros + Stock excedente", delta_color="inverse")

        st.markdown("##### Comparativa Estructural frente a 50 Rivales Directos")
        df_bench = pd.DataFrame([
            {
                "Metrica Financiera / Operativa": "Margen EBITDA sobre Ventas",
                "BioPack Levantina": f"{emp['balance_actual']['ebitda_pct']:.1f} %",
                "Media 50 Rivales (CNAE 1721)": f"{bench['ebitda_medio_pct']:.1f} %",
                "Cuartil Superior (Top 25%)": f"{bench['ebitda_top25_pct']:.1f} %",
                "Diagnostico": "Brecha de -4.3% por exceso de merma y precios indexados tarde"
            },
            {
                "Metrica Financiera / Operativa": "Periodo Medio de Cobro (DSO)",
                "BioPack Levantina": f"{emp['historico_financiero']['2024']['dso']} dias",
                "Media 50 Rivales (CNAE 1721)": f"{bench['dso_medio_dias']} dias",
                "Cuartil Superior (Top 25%)": "45 dias",
                "Diagnostico": f"Financiando a distribuidores a coste cero ({caja_atrapada_clientes:,.0f} EUR inmovilizados)"
            },
            {
                "Metrica Financiera / Operativa": "Permanencia de Inventario (DIO)",
                "BioPack Levantina": f"{emp['historico_financiero']['2024']['dio']} dias",
                "Media 50 Rivales (CNAE 1721)": f"{bench['dio_medio_dias']} dias",
                "Cuartil Superior (Top 25%)": "21 dias",
                "Diagnostico": f"Exceso de bobinas de carton sin rotar ({caja_atrapada_stock:,.0f} EUR en nave)"
            },
            {
                "Metrica Financiera / Operativa": "Productividad (Ventas por Empleado)",
                "BioPack Levantina": f"{bench['facturacion_por_empleado_empresa']:,.0f} EUR/empleado",
                "Media 50 Rivales (CNAE 1721)": f"{bench['facturacion_por_empleado_media']:,.0f} EUR/empleado",
                "Cuartil Superior (Top 25%)": "220.000 EUR/empleado",
                "Diagnostico": "Suboptimizacion de turnos en lineas de termoformado"
            }
        ])
        st.dataframe(df_bench, use_container_width=True)

        st.markdown("---")

        # ----------------------------------------------------------------------
        # BLOQUE 2: SINTESIS EJECUTIVA DE LA IA (CRUCE SABI + BENCHMARK)
        # ----------------------------------------------------------------------
        st.subheader("2. Dictamen de Direccion Financiera y Estrategica")
        with st.spinner("Sintetizando balance oficial con datos de mercado..."):
            dictamen = generar_dictamen_cruzado(emp, bench, SUBVENCIONES_ACTIVAS)
        st.info(dictamen)

        st.markdown("---")

        # ----------------------------------------------------------------------
        # BLOQUE 3: SIMULADOR FINANCIERO DINAMICO (EN TIEMPO REAL)
        # ----------------------------------------------------------------------
        st.subheader("3. Simulador de Recuperacion de Flujo de Caja y Margen")
        st.caption("Ajuste los objetivos operativos para proyectar la inyeccion de liquidez inmediata:")

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            reduccion_dso = st.slider("Reduccion de dias de cobro (DSO):", min_value=0, max_value=30, value=int(exceso_dias_cobro))
            ahorro_mermas = st.slider("Reduccion porcentual de merma de material en planta:", min_value=0.0, max_value=6.0, value=2.5, step=0.5)
        
        caja_recuperada_dso = reduccion_dso * ventas_dia
        beneficio_anual_mermas = emp["balance_actual"]["coste_materiales"] * (ahorro_mermas / 100.0)
        ebitda_recalculado = emp["balance_actual"]["ebitda"] + beneficio_anual_mermas
        ebitda_pct_recalculado = (ebitda_recalculado / emp["balance_actual"]["ventas"]) * 100.0

        with col_s2:
            st.metric("Inyeccion de Liquidez Inmediata en Cuenta:", f"+{caja_recuperada_dso:,.0f} EUR", "Liberacion directa de circulante")
            st.metric("Incremento de EBITDA Neto Anual:", f"+{beneficio_anual_mermas:,.0f} EUR/ano", f"Margen pasa de {emp['balance_actual']['ebitda_pct']}% a {ebitda_pct_recalculado:.1f}%")

        st.markdown("---")

        # ----------------------------------------------------------------------
        # BLOQUE 4: RADAR DE SUBVENCIONES ACTIVAS (CONEXION BDNS / BOE)
        # ----------------------------------------------------------------------
        st.subheader("4. Convocatorias de Subvencion Oficiales Abiertas y Aplicables")
        st.caption("Líneas de ayuda publica cruzadas con el CNAE 1721 y las debilidades del balance auditado:")

        for subv in SUBVENCIONES_ACTIVAS:
            with st.container():
                st.markdown(f"**{subv['organismo']}**")
                st.markdown(f"*{subv['convocatoria']}*")
                c_sub1, c_sub2 = st.columns(2)
                c_sub1.write(f"**Dotacion:** {subv['dotacion']}\n\n**Plazo:** {subv['plazo']}")
                c_sub2.write(f"**Requisito Tecnico:** {subv['requisito_clave']}")
                st.markdown(f"[Acceso a Sede Electronica y Tramitacion Oficial]({subv['enlace_tramite']})")
                st.divider()

        # ----------------------------------------------------------------------
        # BLOQUE 5: MARKETPLACE DE ACCION DIRECTA (VENDOR FINANCE Y TECNOLOGIA)
        # ----------------------------------------------------------------------
        st.subheader("5. Fichas de Ejecucion Inmediata y Partners Validados")
        st.caption("Conexiones directas para implementar las soluciones sin desangrar el balance ni crear software propio:")

        for part in MARKETPLACE_PARTNERS:
            with st.container():
                st.markdown(f"**Area:** `{part['area']}` | **Partner Asignado:** **{part['partner']}**")
                st.write(f"**Solucion Estructurada:** {part['solucion']}")
                c_p1, c_p2 = st.columns(2)
                if "scoring_preliminar" in part:
                    c_p1.success(f"**Scoring Financiero:** {part['scoring_preliminar']}")
                if "presupuesto_estimado" in part:
                    c_p1.info(f"**Coste Llave en Mano:** {part['presupuesto_estimado']}")
                c_p2.write(f"**Canal Directo de Activacion:** `{part['contacto_directo']}`")
                st.divider()
