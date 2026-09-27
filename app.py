import streamlit as st
import pandas as pd
import json
import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import google.generativeai as genai
from engine.financial_engine import FinancialEngine

st.set_page_config(
    page_title="KROMA Enterprise | Outside-In Intelligence Scan",
    layout="wide"
)

default_key = os.environ.get("GEMINI_API_KEY", "")
if not default_key and "GEMINI_API_KEY" in st.secrets:
    default_key = st.secrets["GEMINI_API_KEY"]

with st.sidebar:
    st.header("Configuracion del Sistema")
    api_key_input = st.text_input(
        "Clave API Gemini:",
        value=default_key,
        type="password",
        help="Clave de acceso a modelos analiticos"
    )
    st.caption("Protocolo Activo: Outside-In Intelligence Scan")
    st.divider()
    st.markdown("**Taxonomia de Evidencia:**")
    st.markdown("- `[DATO REGISTRAL]` Cuentas publicas oficiales (SABI / RM)")
    st.markdown("- `[CÁLCULO KROMA]` Modelizacion determinista y percentiles")
    st.markdown("- `[HIPÓTESIS]` Inferencia de catalogo y exposicion exterior")
    st.markdown("- `[A VALIDAR EN PLANTA]` Requiere contraste documental interno")

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

st.title("KROMA Enterprise — Outside-In Intelligence Scan")
st.caption("Dossier de Inteligencia Estrategica y Vulnerabilidad Operativa | Sector Packaging (CNAE 1721)")

col_cif, col_btn = st.columns([3, 1])
with col_cif:
    cif_ingresado = st.text_input("Identificador Fiscal (CIF) de la Entidad:", value="B98765432")
with col_btn:
    st.write("")
    st.write("")
    btn_ejecutar = st.button("Generar Dossier Estrategico")

if btn_ejecutar or "scan_ejecutado" in st.session_state:
    try:
        normativas, tecnologias, benchmark, subvenciones = cargar_base_datos()
    except Exception as e:
        st.error(f"Error en lectura de repositorio: {str(e)}")
        st.stop()

    fin_data = FinancialEngine.calcular_diagnostico_completo(EMPRESA_AUDITADA["balance_actual"], benchmark)
    ratios = fin_data["ratios_empresa"]
    peer = fin_data["benchmark_peer"]
    circ = fin_data["potencial_circulante"]

    st.markdown("---")

    # SECCION 1: ANÁLISIS DE BALANCES Y COMPARATIVA CON EL PEER GROUP
    st.subheader(f"1. Radiografia de Estados Financieros: {EMPRESA_AUDITADA['razon_social']}")
    st.caption("Cuentas Anuales Oficiales depositadas en el Registro Mercantil frente a 50 peers del sector.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("[DATO REGISTRAL] Cifra de Negocios", f"{ratios['ventas']:,.0f} EUR", "Ejercicio 2024")
    c2.metric("[DATO REGISTRAL] EBITDA Contable", f"{ratios['ebitda']:,.0f} EUR", f"Margen: {ratios['ebitda_pct']}%")
    c3.metric("[CÁLCULO KROMA] Plazo Cobro (DSO)", f"{ratios['dso']} dias", f"Mediana sector: {peer['dso_mediana']} d", delta_color="inverse")
    c4.metric("[CÁLCULO KROMA] Rotacion Stock (DIO)", f"{ratios['dio']} dias", f"Mediana sector: {peer['dio_mediana']} d", delta_color="inverse")

    st.markdown("##### Posicionamiento en la Distribucion de 50 Empresas Comparables (CNAE 1721)")
    df_dist = pd.DataFrame([
        {
            "Indicador Financiero": "Periodo Medio de Cobro (DSO)",
            "BioPack Levantina": f"{ratios['dso']} dias",
            "P25 (Top Eficiente)": f"{peer['dso_p25']} dias",
            "Mediana Sector": f"{peer['dso_mediana']} dias",
            "P75": f"{peer['dso_p75']} dias",
            "P90 (Riesgo Alto)": f"{peer['dso_p90']} dias",
            "Posicion en Cohorte": peer["posicion_dso"]
        },
        {
            "Indicador Financiero": "Permanencia de Inventario (DIO)",
            "BioPack Levantina": f"{ratios['dio']} dias",
            "P25 (Top Eficiente)": f"{peer['dio_p25']} dias",
            "Mediana Sector": f"{peer['dio_mediana']} dias",
            "P75": f"{peer['dio_p75']} dias",
            "P90 (Riesgo Alto)": f"{peer['dio_p90']} dias",
            "Posicion en Cohorte": peer["posicion_dio"]
        }
    ])
    st.dataframe(df_dist, use_container_width=True)

    with st.expander("Nota Metodologica del Benchmark"):
        met = benchmark["metodologia"]
        st.write(f"- Universo de referencia: {met['universo_analizado']}.")
        st.write(f"- Segmentacion por facturacion: {met['filtro_tamano']}.")
        st.write(f"- Tratamiento estadistico: {met['depuracion_estadistica']}.")
        st.write(f"- Formula analitica DSO: {met['formula_dso']}.")
        st.write(f"- Formula analitica DIO: {met['formula_dio']}.")

    st.markdown("---")

    # SECCION 2: ANÁLISIS DE CIRCULANTE Y POTENCIAL DE CAJA
    st.subheader("2. Intelligence Scan de Circulante: Potencial de Liberacion de Caja")
    st.caption("Modelizacion mecanica de convergencia hacia la mediana sectorial.")

    col_pot1, col_pot2 = st.columns([2, 3])
    with col_pot1:
        st.metric(
            label="Potencial Maximo de Caja Liberable",
            value=f"Hasta {circ['total_potencial_liberable']:,.0f} EUR",
            help="Calculo teorico de convergencia hacia la mediana. No presupone recuperabilidad operativa del 100%."
        )
        st.write(f"- **Clientes (DSO):** Hasta {circ['potencial_clientes']:,.0f} EUR ({circ['dias_brecha_dso']} dias s/mediana)")
        st.write(f"- **Existencias (DIO):** Hasta {circ['potencial_stock']:,.0f} EUR ({circ['dias_brecha_dio']} dias s/mediana)")
        st.caption("Aviso de Cautela: La brecha constituye una hipotesis de ineficiencia que debe contrastarse contractualmente con el aging de deudores y la politica de aprovisionamiento.")

    with col_pot2:
        st.markdown("##### [A VALIDAR EN PLANTA] Requerimientos de Auditoria Interna")
        st.markdown("""
        Para contrastar el potencial teorico con la realidad operativa, el Comite debe validar:
        1. **Aging de Saldos Deudores:** Verificar si el 80% de la demora se concentra en grandes cuentas de distribucion.
        2. **Estructura de Existencias:** Separar el inventario entre bobina virgen, producto en curso (WIP) y referencias obsoletas.
        3. **Condiciones de Compra (MOQ):** Identificar si el volumen de stock responde a pedidos minimos impuestos por fabricantes papeleros.
        """)

    st.markdown("---")

    # SECCION 3: MAPA DE EXPOSICIÓN REGULATORIA PPWR
    st.subheader("3. Matriz de Exposicion Regulatoria: PPWR y Ley 7/2022")
    st.caption("Cruce de normativa comunitaria vinculante frente al catalogo comercial observable.")

    for norm in normativas:
        with st.container():
            st.markdown(f"#### {norm['articulo']}: {norm['titulo']}")
            st.write(f"**Marco Regulatorio:** {norm['marco_legal']} | **Fecha Limite de Aplicacion:** {norm['fecha_limite']}")
            
            c_r1, c_r2 = st.columns(2)
            with c_r1:
                st.markdown(f"**[EVIDENCIA PUBLICA] Catalogo Observado:** {norm['familia_catalogo_afectada']}")
                st.markdown(f"**[HIPOTESIS KROMA]** {norm['hipotesis_kroma']}")
                st.write("**Escenarios de Exposicion Comercial:**")
                st.write(f"- *Escenario Conservador:* {norm['escenarios_exposicion']['bajo']}")
                st.write(f"- *Escenario Base:* {norm['escenarios_exposicion']['medio']}")
                st.write(f"- *Escenario Severo:* {norm['escenarios_exposicion']['alto']}")
            with c_r2:
                st.markdown("**[A VALIDAR EN PLANTA] Diligencia Tecnica Requerida:**")
                st.markdown(f"> {norm['validacion_requerida_planta']}")
            st.divider()

    # SECCION 4: HIPÓTESIS TECNOLÓGICA Y ESTRUCTURACIÓN FINANCIERA
    st.subheader("4. Hipotesis de Adaptacion Tecnica y Estructuracion Financiera")
    st.caption("Soluciones comerciales homologadas en Espana (TRL 9) y financiacion fuera de balance.")

    tech = tecnologias[0]
    subv = subvenciones[0]
    sim = FinancialEngine.simular_vendor_finance(
        capex_bruto=tech["capex_llave_en_mano"],
        ahorro_anual=tech["ahorro_anual_estimado_pyme"],
        pct_subvencion=subv["porcentaje_fondo_perdido"]
    )

    t1, t2 = st.columns(2)
    with t1:
        st.markdown(f"##### {tech['nombre']}")
        st.write(f"- **Fabricante / Integrador:** {tech['fabricante']} ({tech['integrador_espana']})")
        st.write(f"- **CAPEX Estimado Llave en Mano:** {tech['capex_llave_en_mano']:,.2f} EUR")
        st.write(f"- **Subvencion Aplicable Estimada ({subv['organismo'].split(' ')[0]}):** -{sim['subvencion_estimada']:,.2f} EUR ({subv['codigo_bdns']})")
        st.write(f"- **Inversion Neta Resultante:** {sim['coste_neto_adquisicion']:,.2f} EUR")
    with t2:
        st.markdown("##### Estructuracion Operativa de Arrendamiento (36 Meses)")
        st.write(f"- Cuota de renting proyectada: **{sim['cuota_mensual_renting']:,.2f} EUR/mes**")
        st.write(f"- Ahorro mensual teorico en mermas: **+{sim['ahorro_mensual']:,.2f} EUR/mes**")
        st.write(f"- Flujo de caja neto proyectado: **+{sim['cash_flow_neto_mensual']:,.2f} EUR/mes**")
        st.caption("[A VALIDAR EN PLANTA] Auditar tasas reales de merma en turno de noche y verificar compatibilidad fisica con la bancada de sellado existente.")
