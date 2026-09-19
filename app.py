import streamlit as st
import pandas as pd
import json
import os
import google.generativeai as genai

from engine.financial_engine import FinancialEngine
from engine.generator import DossierGenerator

# ==============================================================================
# CONFIGURACIÓN DEL SISTEMA
# ==============================================================================
st.set_page_config(
    page_title="KROMA Enterprise | Packaging & Industrial Intelligence",
    layout="wide"
)

# Carga de API Key
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
    st.caption("Vertical Activo: Envases, Embalajes y Termoformado (CNAE 1721 / 2222)")
    st.divider()
    st.markdown("**Bases de Datos Estructuradas:**")
    st.markdown("- Registro Mercantil / SABI (50 Balances auditados)")
    st.markdown("- Normativa UE (PPWR, Ley 7/2022, Directiva SUP)")
    st.markdown("- Catalogo Tecnologias COTS (TRL 8-9)")
    st.markdown("- Motor Matematico Determinista Activo")

if api_key_input:
    genai.configure(api_key=api_key_input)

def obtener_modelo():
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
# CARGA DE BASES DE DATOS ESTRUCTURADAS
# ==============================================================================
def cargar_base_datos():
    ruta_base = os.path.dirname(__file__)
    
    with open(os.path.join(ruta_base, "data", "normativas_ppwr.json"), "r", encoding="utf-8") as f:
        normativas = json.load(f)
        
    with open(os.path.join(ruta_base, "data", "catalogo_tecnologias.json"), "r", encoding="utf-8") as f:
        tecnologias = json.load(f)
        
    with open(os.path.join(ruta_base, "data", "benchmark_sabi_1721.json"), "r", encoding="utf-8") as f:
        benchmark = json.load(f)
        
    with open(os.path.join(ruta_base, "data", "subvenciones_bdns.json"), "r", encoding="utf-8") as f:
        subvenciones = json.load(f)
        
    return normativas, tecnologias, benchmark, subvenciones

# Datos auditados de la entidad de referencia
EMPRESA_AUDITADA = {
    "cif": "B98765432",
    "razon_social": "BioPack Levantina de Envases S.L.",
    "cnae": "1721 - Fabricacion de papel y carton ondulado; envases y embalajes",
    "subsector": "Termoformado de celulosa y envases microcanal para HORECA e industria alimentaria",
    "provincia": "Valencia",
    "plantilla": 24,
    "balance_actual": {
        "ventas": 3410000.0,
        "coste_materiales_consumos": 1580000.0,
        "personal": 980000.0,
        "gastos_explotacion_opex": 560150.0,
        "ebitda": 289850.0,
        "clientes_cobro_pendiente": 765000.0,
        "existencias_stock": 390000.0,
        "proveedores_deuda": 320000.0,
        "tesoreria_disponible": 65000.0,
        "deuda_bancaria_total": 540000.0,
        "plantilla": 24
    }
}

# ==============================================================================
# INTERFAZ Y EJECUCIÓN
# ==============================================================================
st.title("KROMA Enterprise — Intelligence Dossier: Packaging Industrial")
st.caption("Auditoria estrategica, comparativa ciega con 50 balances SABI y plan de ejecucion financiera de planta.")

col_cif, col_btn = st.columns([3, 1])
with col_cif:
    cif_ingresado = st.text_input("Introduzca el CIF de la empresa para iniciar la auditoria:", value="B98765432")
with col_btn:
    st.write("")
    st.write("")
    btn_ejecutar = st.button("Ejecutar Auditoria Integral")

if btn_ejecutar or "informe_generado" in st.session_state:
    try:
        normativas, tecnologias, benchmark, subvenciones = cargar_base_datos()
    except Exception as e:
        st.error(f"Error al cargar las bases de datos de data/: {str(e)}")
        st.stop()

    # 1. Calculo matematico determinista
    fin_data = FinancialEngine.calcular_diagnostico_completo(EMPRESA_AUDITADA["balance_actual"], benchmark)
    
    # 2. Seleccion de Tecnologia y Simulacion Vendor Finance
    tech_sel = tecnologias[0]
    subv_sel = subvenciones[0]
    fin_sim = FinancialEngine.simular_vendor_finance(
        capex_bruto=tech_sel["capex_llave_en_mano"],
        ahorro_anual=tech_sel["ahorro_anual_estimado_pyme"],
        pct_subvencion=subv_sel["porcentaje_fondo_perdido"]
    )

    ratios = fin_data["ratios_empresa"]
    caja = fin_data["caja_inmovilizada"]

    st.markdown("---")

    # --------------------------------------------------------------------------
    # BLOQUE 1: RADIOGRAFÍA CONTABLE OFICIAL FRENTE A 50 RIVALES
    # --------------------------------------------------------------------------
    st.subheader(f"1. Radiografia de Cuentas Anuales Oficiales: {EMPRESA_AUDITADA['razon_social']}")
    st.caption(f"CNAE: {EMPRESA_AUDITADA['cnae']} | Muestra de cotejo: 50 empresas auditadas del mismo segmento de facturacion.")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Facturacion 2024", f"{ratios['ventas']:,.0f} EUR", "+9.3% interanual")
    m2.metric("Margen EBITDA Real", f"{ratios['ebitda_pct']}%", f"Sector medio: {benchmark['indicadores']['margen_ebitda']['mediana']}%", delta_color="inverse")
    m3.metric("Plazo Medio de Cobro (DSO)", f"{ratios['dso']} dias", f"Sector medio: {benchmark['indicadores']['dso_dias_cobro']['mediana']} dias", delta_color="inverse")
    m4.metric("Caja Atrapada s/Sector", f"{caja['total_caja_liberable']:,.0f} EUR", "Clientes + Stock inmovilizado", delta_color="inverse")

    st.markdown("##### Comparativa Estructural frente a los 50 Mayores Rivales del Mismo CNAE")
    df_comp = pd.DataFrame([
        {
            "Metrica Financiera / Operativa": "Margen de Explotacion EBITDA",
            "BioPack Levantina": f"{ratios['ebitda_pct']:.1f} % ({ratios['ebitda']:,.0f} EUR)",
            "Mediana 50 Rivales": f"{benchmark['indicadores']['margen_ebitda']['mediana']:.1f} %",
            "Top 25% (Lideres de Sector)": f"{benchmark['indicadores']['margen_ebitda']['p75_top']:.1f} %",
            "Diagnostico de Planta": f"Brecha de margen del {benchmark['indicadores']['margen_ebitda']['mediana'] - ratios['ebitda_pct']:.1f}% por exceso de merma"
        },
        {
            "Metrica Financiera / Operativa": "Periodo Medio de Cobro (DSO)",
            "BioPack Levantina": f"{ratios['dso']:.1f} dias",
            "Mediana 50 Rivales": f"{benchmark['indicadores']['dso_dias_cobro']['mediana']:.1f} dias",
            "Top 25% (Lideres de Sector)": f"{benchmark['indicadores']['dso_dias_cobro']['p25_top_rapido']:.1f} dias",
            "Diagnostico de Planta": f"{caja['caja_atrapada_clientes']:,.0f} EUR financiando a distribuidores a coste cero"
        },
        {
            "Metrica Financiera / Operativa": "Permanencia de Inventario (DIO)",
            "BioPack Levantina": f"{ratios['dio']:.1f} dias",
            "Mediana 50 Rivales": f"{benchmark['indicadores']['dio_dias_inventario']['mediana']:.1f} dias",
            "Top 25% (Lideres de Sector)": f"{benchmark['indicadores']['dio_dias_inventario']['p25_top_eficiente']:.1f} dias",
            "Diagnostico de Planta": f"{caja['caja_atrapada_stock']:,.0f} EUR inmovilizados en bobinas de carton"
        },
        {
            "Metrica Financiera / Operativa": "Productividad por Empleado",
            "BioPack Levantina": f"{ratios['ventas_empleado']:,.0f} EUR/persona",
            "Mediana 50 Rivales": f"{benchmark['indicadores']['ventas_por_empleado_eur']['mediana']:,.0f} EUR/persona",
            "Top 25% (Lideres de Sector)": f"{benchmark['indicadores']['ventas_por_empleado_eur']['p75_top']:,.0f} EUR/persona",
            "Diagnostico de Planta": "Paradas de maquina frecuentes por micro-fallos en sellado"
        }
    ])
    st.dataframe(df_comp, use_container_width=True)

    st.markdown("---")

    # --------------------------------------------------------------------------
    # BLOQUE 2: VULNERABILIDAD NORMATIVA Y AMENAZAS DEL CATÁLOGO
    # --------------------------------------------------------------------------
    st.subheader("2. Analisis de Vulnerabilidad Normativa y Amenazas del Catalogo")
    st.caption("Evaluacion de impacto de los Articulos 5, 9 y 26 del Reglamento PPWR y la Ley 7/2022 sobre la cartera actual:")

    if api_key_input:
        ai_m = obtener_modelo()
        generator = DossierGenerator(ai_m)
        with st.spinner("Generando dictamen de vulnerabilidad normativa..."):
            cap1 = generator.generar_capitulo_vulnerabilidad(EMPRESA_AUDITADA, fin_data, normativas)
        st.info(cap1)
    else:
        st.warning("Configure su GEMINI_API_KEY en la barra lateral para generar los capitulos redactados por la IA.")

    st.markdown("---")

    # --------------------------------------------------------------------------
    # BLOQUE 3: RADIOGRAFÍA DEL FONDO DE MANIOBRA Y ESTRÉS DE CIRCULANTE
    # --------------------------------------------------------------------------
    st.subheader("3. Radiografia del Fondo de Maniobra y Estres de Circulante")
    st.caption("Impacto de la inmovilizacion de caja por demoras en cobros y existencias no rotadas:")

    if api_key_input:
        with st.spinner("Generando analisis de estres de circulante..."):
            cap2 = generator.generar_capitulo_circulante(fin_data, benchmark)
        st.markdown(cap2)

    st.markdown("---")

    # --------------------------------------------------------------------------
    # BLOQUE 4: SOLUCIONES COTS Y ESTRUCTURACIÓN DE VENDOR FINANCE
    # --------------------------------------------------------------------------
    st.subheader("4. Scouting Tecnologico COTS y Estructuracion de Vendor Finance")
    st.caption("Adopcion de tecnologia comercial existente sin desarrollo propio, financiada con el ahorro generado:")

    c_t1, c_t2 = st.columns([3, 2])
    with c_t1:
        st.markdown(f"##### {tech_sel['nombre']}")
        st.write(f"**Fabricante / Integrador:** `{tech_sel['fabricante']}` | Integrador en Espana: `{tech_sel['integrador_espana']}`")
        st.write(f"**Tiempo de Puesta en Marcha:** `{tech_sel['tiempo_parada_planta']}`")
        st.write(f"**Descripcion Tecnica:** {tech_sel['descripcion_tecnica']}")
        st.success(f"**Ahorro Anual Garantizado en Merma:** +{tech_sel['ahorro_anual_estimado_pyme']:,.0f} EUR/ano (Reduccion del {tech_sel['reduccion_merma_garantizada_pct']}%)")

    with c_t2:
        st.markdown("##### Estructuracion Financiera (Vendor Finance a 36 Meses)")
        df_fin = pd.DataFrame([
            {"Concepto": "Inversion Llave en Mano (Hardware + Integracion)", "Importe": f"{fin_sim['capex_bruto']:,.2f} EUR"},
            {"Concepto": f"(-) Subvencion {subv_sel['organismo'].split(' ')[0]} ({int(subv_sel['porcentaje_fondo_perdido']*100)}%)", "Importe": f"-{fin_sim['subvencion_estimada']:,.2f} EUR"},
            {"Concepto": "(=) Coste Neto Final para la Empresa", "Importe": f"{fin_sim['coste_neto_adquisicion']:,.2f} EUR"},
            {"Concepto": "Cuota Mensual de Renting a 36 Meses (Grenke/DLL)", "Importe": f"{fin_sim['cuota_mensual_renting']:,.2f} EUR/mes"},
            {"Concepto": "Ahorro Mensual en Compras de Material", "Importe": f"+{fin_sim['ahorro_mensual']:,.2f} EUR/mes"},
            {"Concepto": "CASH-FLOW NETO MENSUAL GENERADO", "Importe": f"+{fin_sim['cash_flow_neto_mensual']:,.2f} EUR/mes"}
        ])
        st.dataframe(df_fin, use_container_width=True)
        st.info(f"Ratio de Cobertura: El ahorro mensual cubre **{fin_sim['cobertura_servicio_cuota']} veces** la cuota del renting desde el primer mes.")

    st.markdown("---")

    # --------------------------------------------------------------------------
    # BLOQUE 5: CONVOCATORIAS OFICIALES ACTIVAS (CONEXIÓN BDNS)
    # --------------------------------------------------------------------------
    st.subheader("5. Convocatorias de Subvencion Publica Vigentes y Aplicables")
    st.caption("Lineas de ayuda oficiales cruzadas con el CNAE 1721:")

    for subv in subvenciones:
        with st.container():
            st.markdown(f"**{subv['organismo']} — {subv['programa']}**")
            st.markdown(f"*{subv['codigo_bdns']}*")
            c_s1, c_s2 = st.columns(2)
            c_s1.write(f"**Intensidad:** {int(subv['porcentaje_fondo_perdido']*100)}% a fondo perdido (Tope: {subv['tope_subvencion_eur']:,.0f} EUR)\n\n**Plazo:** {subv['plazo_cierre']}")
            c_s2.write(f"**Gastos Elegibles:** {subv['tipo_gasto_elegible']}")
            st.markdown(f"[Acceso a Sede Electronica y Tramitacion Oficial]({subv['enlace_sede']})")
            st.divider()

    # --------------------------------------------------------------------------
    # BLOQUE 6: HOJA DE RUTA DETALLADA DE EJECUCIÓN (30-60-90-180 DÍAS)
    # --------------------------------------------------------------------------
    st.subheader("6. Hoja de Ruta de Ejecucion Tecnica y Comercial (30-60-90-180 Dias)")
    st.caption("Plan de despliegue operacional para el Comite de Direccion con entregables tangibles:")

    if api_key_input:
        with st.spinner("Generando plan de operaciones detallado..."):
            roadmap = generator.generar_hoja_ruta_ejecucion(tech_sel, fin_sim, subv_sel)
        
        for paso in roadmap:
            with st.container():
                st.markdown(f"##### {paso.get('periodo')}")
                st.write(f"**Actuacion Operativa:** {paso.get('actuacion_tecnica')}")
                st.info(f"Entregable Exigible al Comite: {paso.get('entregable_comite')}")
                st.divider()
