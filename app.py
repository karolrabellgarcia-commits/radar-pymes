import os
import sys
import json
import streamlit as st
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from engine.financial_engine import FinancialEngine

st.set_page_config(
    page_title="KROMA Enterprise | Outside-In Intelligence Scan",
    layout="wide"
)

st.markdown("""
<style>
    .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
    div[data-testid="stMetricValue"] { font-size: 1.6rem; font-weight: 700; }
    .stDataFrame { margin-top: 0.3rem; margin-bottom: 0.3rem; }
    .executive-card {
        background-color: #f8f9fa;
        border-left: 5px solid #0d6efd;
        padding: 16px;
        margin-bottom: 18px;
        border-radius: 4px;
        color: #1a1a1a;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Configuracion de Entidad")
    st.caption("Protocolo Activo: Outside-In Intelligence Scan (CNAE 1721 / 2222)")
    st.divider()
    st.markdown("**Taxonomia Metodologica:**")
    st.markdown("- `[DATO REGISTRAL]` Cuentas anuales depositadas")
    st.markdown("- `[CÁLCULO KROMA]` Modelizacion determinista s/balance")
    st.markdown("- `[HIPÓTESIS]` Inferencia sectorial exterior")
    st.markdown("- `[A VALIDAR EN PLANTA]` Auditoria y contraste interno")

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

# Base de datos extensible multientidad para packaging
EMPRESAS_REGISTRADAS = {
    "B98765432": {
        "cif": "B98765432",
        "razon_social": "BioPack Levantina de Envases S.L.",
        "cnae": "1721 - Fabricacion de papel y carton ondulado",
        "subsector": "Termoformado alimentario y envases microcanal HORECA",
        "comunidad_autonoma": "Comunidad Valenciana",
        "territorio_foral": False,
        "plantilla": 24,
        "balance": {
            "ventas": 3410000.0,
            "coste_materiales_consumos": 1580000.0,
            "personal": 980000.0,
            "gastos_explotacion_opex": 560150.0,
            "ebitda": 289850.0,
            "clientes_cobro_pendiente": 765000.0,
            "existencias_stock": 390000.0,
            "proveedores_deuda": 320000.0,
            "tesoreria_disponible": 65000.0,
            "deuda_bancaria_corto_plazo": 210000.0,
            "deuda_bancaria_largo_plazo": 330000.0,
            "deuda_bancaria_total": 540000.0,
            "plantilla": 24
        }
    },
    "A31456789": {
        "cif": "A31456789",
        "razon_social": "Cartonajes del Norte S.A.",
        "cnae": "1721 - Fabricacion de papel y carton ondulado",
        "subsector": "Cajas de carton ondulado pesado y embalaje industrial",
        "comunidad_autonoma": "Comunidad Foral de Navarra",
        "territorio_foral": True,
        "plantilla": 38,
        "balance": {
            "ventas": 5820000.0,
            "coste_materiales_consumos": 2790000.0,
            "personal": 1450000.0,
            "gastos_explotacion_opex": 920000.0,
            "ebitda": 660000.0,
            "clientes_cobro_pendiente": 1120000.0,
            "existencias_stock": 610000.0,
            "proveedores_deuda": 490000.0,
            "tesoreria_disponible": 140000.0,
            "deuda_bancaria_corto_plazo": 290000.0,
            "deuda_bancaria_largo_plazo": 560000.0,
            "deuda_bancaria_total": 850000.0,
            "plantilla": 38
        }
    },
    "B14437008": {
        "cif": "B14437008",
        "razon_social": "Envases Rambleños S.L.",
        "cnae": "1721 - Fabricacion de papel y carton ondulado",
        "subsector": "Envases hortofruticolas y cajas de carton canal doble",
        "comunidad_autonoma": "Andalucia",
        "territorio_foral": False,
        "plantilla": 45,
        "balance": {
            "ventas": 7250000.0,
            "coste_materiales_consumos": 3650000.0,
            "personal": 1820000.0,
            "gastos_explotacion_opex": 1050000.0,
            "ebitda": 730000.0,
            "clientes_cobro_pendiente": 1680000.0,
            "existencias_stock": 820000.0,
            "proveedores_deuda": 710000.0,
            "tesoreria_disponible": 210000.0,
            "deuda_bancaria_corto_plazo": 380000.0,
            "deuda_bancaria_largo_plazo": 750000.0,
            "deuda_bancaria_total": 1130000.0,
            "plantilla": 45
        }
    }
}

st.title("KROMA Enterprise — Outside-In Intelligence Scan")
st.caption("Dossier de Inteligencia Estrategica, Riesgo Financiero y Diagnostico de Vulnerabilidad | Sector Packaging (CNAE 1721 / 2222)")

col_cif, col_modo = st.columns([2, 2])
with col_cif:
    cif_ingresado = st.text_input("Identificador Fiscal (CIF) a Auditar:", value="B98765432").strip().upper()
with col_modo:
    empresa_detectada = EMPRESAS_REGISTRADAS.get(cif_ingresado)
    if empresa_detectada:
        st.success(f"Entidad localizada: **{empresa_detectada['razon_social']}** ({empresa_detectada['comunidad_autonoma']})")
    else:
        st.warning("CIF no pre-registrado. Introduce los datos del Registro Mercantil a continuación:")

# Formulario universal para cualquier empresa no indexada
if not empresa_detectada:
    with st.expander("Parametros Contables Registrales (Modo Cualquier CIF)", expanded=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            razon_custom = st.text_input("Razon Social:", "Packaging Industrial Personalizado S.L.")
            comunidad_custom = st.selectbox("Comunidad Autonoma:", ["Comunidad Valenciana", "Comunidad Foral de Navarra", "Cataluna", "Murcia", "Andalucia", "Madrid", "Pais Vasco", "Castilla y Leon", "Aragon", "Otra"])
            subsector_custom = st.selectbox("Subsector / Especialidad Fabril:", [
                "Termoformado alimentario y envases celulosicos grasos",
                "Cajas de carton ondulado pesado y embalaje industrial",
                "Packaging e-commerce y cajas automontables",
                "Envases hortofruticolas y bandejas de campo"
            ])
            ventas_custom = st.number_input("Cifra de Negocios (EUR):", value=4200000.0, step=50000.0)
            coste_mat_custom = st.number_input("Consumo Aprovisionamientos (EUR):", value=1950000.0, step=50000.0)
        with col_f2:
            ebitda_custom = st.number_input("EBITDA Contable (EUR):", value=390000.0, step=20000.0)
            clientes_custom = st.number_input("Deudores Comerciales (Clientes):", value=890000.0, step=20000.0)
            stock_custom = st.number_input("Existencias (Stock):", value=480000.0, step=20000.0)
        with col_f3:
            prov_custom = st.number_input("Proveedores Deuda:", value=410000.0, step=20000.0)
            deuda_cp = st.number_input("Deuda Bancaria Corto Plazo:", value=250000.0, step=20000.0)
            deuda_lp = st.number_input("Deuda Bancaria Largo Plazo:", value=430000.0, step=20000.0)
            plantilla_custom = st.number_input("Plantilla Media:", value=28, step=1)

    es_foral = "Navarra" in comunidad_custom or "Pais Vasco" in comunidad_custom
    empresa_activa = {
        "cif": cif_ingresado,
        "razon_social": razon_custom,
        "cnae": "1721 - Fabricacion de papel y carton ondulado",
        "subsector": subsector_custom,
        "comunidad_autonoma": comunidad_custom,
        "territorio_foral": es_foral,
        "plantilla": plantilla_custom,
        "balance": {
            "ventas": ventas_custom,
            "coste_materiales_consumos": coste_mat_custom,
            "personal": 1100000.0,
            "gastos_explotacion_opex": 760000.0,
            "ebitda": ebitda_custom,
            "clientes_cobro_pendiente": clientes_custom,
            "existencias_stock": stock_custom,
            "proveedores_deuda": prov_custom,
            "tesoreria_disponible": 95000.0,
            "deuda_bancaria_corto_plazo": deuda_cp,
            "deuda_bancaria_largo_plazo": deuda_lp,
            "deuda_bancaria_total": deuda_cp + deuda_lp,
            "plantilla": plantilla_custom
        }
    }
else:
    empresa_activa = empresa_detectada

btn_ejecutar = st.button("Generar Outside-In Intelligence Scan")

if btn_ejecutar or "scan_ejecutado" in st.session_state:
    st.session_state["scan_ejecutado"] = True

    try:
        normativas, tecnologias, benchmark, subvenciones = cargar_base_datos()
    except Exception as e:
        st.error(f"Error en lectura de repositorios: {str(e)}")
        st.stop()

    balance_activo = empresa_activa["balance"]
    fin_data = FinancialEngine.calcular_diagnostico_completo(balance_activo, benchmark)
    ratios = fin_data["ratios_empresa"]
    peer = fin_data["benchmark_peer"]
    circ = fin_data["potencial_circulante"]
    reg_quant = fin_data["cuantificacion_regulatoria"]

    deuda_cp = balance_activo.get("deuda_bancaria_corto_plazo", balance_activo["deuda_bancaria_total"] * 0.40)
    deuda_lp = balance_activo.get("deuda_bancaria_largo_plazo", balance_activo["deuda_bancaria_total"] * 0.60)
    deuda_neta = max(0.0, balance_activo["deuda_bancaria_total"] - ratios["tesoreria"])
    ratio_dfn_ebitda = round(deuda_neta / ratios["ebitda"], 2) if ratios["ebitda"] > 0 else 99.0
    cobertura_cp_ebitda = round(deuda_cp / ratios["ebitda"], 2) if ratios["ebitda"] > 0 else 99.0

    st.markdown("---")

    # =========================================================================
    # PREGUNTA 1: ¿DÓNDE SE LE ESTÁ FUGANDO EL DINERO?
    # =========================================================================
    st.subheader(f"1. Fuga Consolidada de Caja y Margen: {empresa_activa['razon_social']}")
    
    fuga_caja_circulante = circ['potencial_teorico_total']
    masa_ventas_gran_consumo = ratios["ventas"] * 0.45
    coste_factoring_dso = masa_ventas_gran_consumo * (circ['dias_brecha_dso'] / 365.0) * 0.035
    merma_sellado_estimada = (balance_activo["coste_materiales_consumos"] * 0.65) * 0.022
    fuga_total_anual_consolidada = fuga_caja_circulante + coste_factoring_dso + merma_sellado_estimada

    col_fg1, col_fg2, col_fg3, col_fg4 = st.columns(4)
    col_fg1.metric("Fuga Consolidada de Liquidez", f"~{fuga_total_anual_consolidada:,.0f} EUR", "Impacto Identificado")
    col_fg2.metric("Caja Atrapada en Circulante", f"{fuga_caja_circulante:,.0f} EUR", f"Ciclo Caja: {ratios['ciclo_caja_dias']} d")
    col_fg3.metric("Merma Materia Prima (65% mix)", f"~{merma_sellado_estimada:,.0f} EUR/año", "2.2% en sellado/merma")
    col_fg4.metric("Sobrecoste Financiero Cobro", f"~{coste_factoring_dso:,.0f} EUR/año", "Anticipo de papel a 3.5%")

    st.markdown("##### Posicion frente a 50 Empresas Competidoras (Benchmark CNAE 1721)")
    df_dist = pd.DataFrame([
        {
            "Indicador Financiero": "Periodo Medio de Cobro (DSO)*",
            "Entidad Auditada": f"{ratios['dso']} dias",
            "Mediana Cohorte": f"{peer['dso_mediana']} dias",
            "Desviacion": f"+{circ['dias_brecha_dso']} dias s/mediana",
            "Caja Retenida": f"{circ['potencial_dso_eur']:,.0f} EUR",
            "Posicion en Sector": peer["posicion_dso"]
        },
        {
            "Indicador Financiero": "Permanencia de Inventario (DIO)",
            "Entidad Auditada": f"{ratios['dio']} dias",
            "Mediana Cohorte": f"{peer['dio_mediana']} dias",
            "Desviacion": f"+{circ['dias_brecha_dio']} dias s/mediana",
            "Caja Retenida": f"{circ['potencial_dio_eur']:,.0f} EUR",
            "Posicion en Sector": peer["posicion_dio"]
        },
        {
            "Indicador Financiero": "Pago a Proveedores (DPO)",
            "Entidad Auditada": f"{ratios['dpo']} dias",
            "Mediana Cohorte": "60.0 dias",
            "Desviacion": f"{ratios['dpo'] - 60.0:+.1f} dias",
            "Caja Retenida": "Financiacion de Compras",
            "Posicion en Sector": "Tramo Sectorial"
        },
        {
            "Indicador Financiero": "Apalancamiento Neto (DFN/EBITDA)",
            "Entidad Auditada": f"{ratio_dfn_ebitda}x",
            "Mediana Cohorte": "1.80x",
            "Desviacion": "Saludable (<2.5x)" if ratio_dfn_ebitda < 2.5 else "Tensión de Deuda",
            "Caja Retenida": f"Deuda CP: {deuda_cp:,.0f} EUR",
            "Posicion en Sector": f"Vencimiento CP: {cobertura_cp_ebitda}x EBITDA"
        }
    ])
    st.dataframe(df_dist, use_container_width=True)

    with st.expander("Auditoria de Friccion Operativa en Circulante"):
        st.markdown(f"""
        1. **Friccion de Clientes (DSO {ratios['dso']} dias):** Reducir los {circ['dias_brecha_dso']} dias de exceso frente a grandes cuentas alimentarias no es viable comercialmente. Exigiria cesion de papel comercial (factoring/confirming), lo que supondria un coste bancario explícito de **~{coste_factoring_dso:,.0f} EUR anuales**.
        2. **Friccion de Compras de Bobina (DIO {ratios['dio']} dias):** Los {circ['dias_brecha_dio']} dias de stock por encima de la mediana responden a la prima de inmovilizado obligada por los lotes minimos de pedido (MOQ) de los fabricantes papeleros (Saica, Smurfit, DS Smith).
        3. **(*) Cautela de IVA:** El DSO registral ({ratios['dso']} d) incluye un sesgo mecanico al alza de ~14 dias debido al 21% de IVA devengado en cuentas a cobrar sobre ventas netas.
        """)

    with st.expander("Stress Test de Vulnerabilidad: Sensibilidad del EBITDA ante Subidas de Bobina"):
        consumo_base = balance_activo["coste_materiales_consumos"]
        ebitda_base = ratios["ebitda"]
        st_3 = consumo_base * 0.03
        st_5 = consumo_base * 0.05
        st_10 = consumo_base * 0.10
        df_stress = pd.DataFrame([
            {"Escenario Coste Bobina": "Subida Papel +3%", "Sobrecoste Anual": f"+{st_3:,.0f} EUR", "EBITDA Resultante": f"{max(0, ebitda_base - st_3):,.0f} EUR", "Erosion de Margen": f"-{(st_3/ebitda_base)*100:.1f}%"},
            {"Escenario Coste Bobina": "Subida Papel +5%", "Sobrecoste Anual": f"+{st_5:,.0f} EUR", "EBITDA Resultante": f"{max(0, ebitda_base - st_5):,.0f} EUR", "Erosion de Margen": f"-{(st_5/ebitda_base)*100:.1f}%"},
            {"Escenario Coste Bobina": "Subida Papel +10%", "Sobrecoste Anual": f"+{st_10:,.0f} EUR", "EBITDA Resultante": f"{max(0, ebitda_base - st_10):,.0f} EUR", "Erosion de Margen": f"-{(st_10/ebitda_base)*100:.1f}%"}
        ])
        st.dataframe(df_stress, use_container_width=True)

    st.markdown("---")

    # =========================================================================
    # PREGUNTA 2: ¿CUÁNTO LE VA A COSTAR EN MULTAS Y ECOTASAS?
    # =========================================================================
    st.subheader(f"2. Matriz de Cuantificacion de Riesgo Regulatorio ({empresa_activa['comunidad_autonoma']})")
    
    pct_ebitda_reg = (reg_quant['coste_regulatorio_directo_anual'] / ratios['ebitda']) * 100.0 if ratios['ebitda'] > 0 else 0.0

    cr1, cr2, cr3 = st.columns(3)
    cr1.metric(
        "Coste Regulatorio Directo Anual",
        f"{reg_quant['coste_regulatorio_directo_anual']:,.0f} EUR/año",
        f"{pct_ebitda_reg:.1f}% del EBITDA Oficial",
        delta_color="inverse"
    )
    cr2.metric(
        "Ecotasa RAP Industrial (RD 1055/2022)",
        f"~{reg_quant['impacto_anual_scrap']:,.0f} EUR/año",
        f"{reg_quant['toneladas_procesadas']:,.0f} t/año a ~120 EUR/t"
    )
    cr3.metric(
        "Ventas en Riesgo Inmediato PFAS",
        f"~{reg_quant['volumen_ventas_riesgo_pfas']:,.0f} EUR",
        "Reglamento UE 2025/40 (Corte Agosto 2026)",
        delta_color="inverse"
    )

    df_reg_cuant = pd.DataFrame([
        {
            "Marco Normativo": "RD 1055/2022 (RAP Industrial / SCRAP)",
            "Articulo / Regulacion": "Sección Envases Comerciales",
            "Volumen / Referencia Afectada": f"{reg_quant['toneladas_procesadas']:,.0f} t de carton/embalaje",
            "Impacto Economico Directo": f"{reg_quant['impacto_anual_scrap']:,.0f} EUR/año",
            "Mecanismo de Traslado": "Obligacion legal de pago a SCRAP (Envalora/Pro Circular). Riesgo de asuncion en margen si el cliente rechaza repercusion.",
            "Nivel de Urgencia": "🔴 EN VIGOR (Exigible)"
        },
        {
            "Marco Normativo": "Reglamento (UE) 2025/40 (PPWR)",
            "Articulo / Regulacion": "Artículo 5 (Restricción PFAS)",
            "Volumen / Referencia Afectada": f"~{reg_quant['volumen_ventas_riesgo_pfas']:,.0f} EUR (30% ventas)",
            "Impacto Economico Directo": "Riesgo de rescision de contrato",
            "Mecanismo de Traslado": "Prohibición de venta si la barrera antigrasa lleva fluorados. Pérdida inmediata de homologación con distribución alimentaria.",
            "Nivel de Urgencia": "🔴 12-Agosto-2026"
        },
        {
            "Marco Normativo": "Ley Foral 14/2023" if empresa_activa["territorio_foral"] else "Ley 7/2022 (Régimen Estatal)",
            "Articulo / Regulacion": "Título VII (Impuesto Plastico)",
            "Volumen / Referencia Afectada": f"~{reg_quant['toneladas_procesadas'] * 0.025:.1f} t de film virgen en sellado",
            "Impacto Economico Directo": f"{reg_quant['impacto_impuesto_plastico']:,.0f} EUR/año",
            "Mecanismo de Traslado": "Gravamen fiscal de 0,45 EUR/kg de polímero virgen en termosellado.",
            "Nivel de Urgencia": "🔴 EN VIGOR (Liquidación)"
        },
        {
            "Marco Normativo": "Reglamento (UE) 2025/40 (PPWR)",
            "Articulo / Regulacion": "Artículo 24 (Ratio Espacio Vacío)",
            "Volumen / Referencia Afectada": "Gama estandar e-commerce / agrupacion",
            "Impacto Economico Directo": "Coste adaptacion troqueles (~18.000 EUR)",
            "Mecanismo de Traslado": "Obligacion de maximo 50% de aire. Obsolescencia de troqueles y moldes sobredimensionados.",
            "Nivel de Urgencia": "🟡 01-Enero-2030"
        }
    ])
    st.dataframe(df_reg_cuant, use_container_width=True)

    st.markdown("---")

    # =========================================================================
    # SECCIÓN 3: PALANCA TECNOLÓGICA Y FINANCIACIÓN FUERA DE BALANCE
    # =========================================================================
    st.subheader("3. Hipotesis Tecnologica: Optimizacion de Sellado y Desglose Financiero")
    st.caption("Modelizacion sobre TRL 9 en base al consumo real de materiales de la entidad. No constituye prescripcion de proveedor.")

    tech = tecnologias[0]
    col_s1, col_s2 = st.columns([2, 2])
    with col_s1:
        mix_sellado_pct = st.slider(
            "Materia Prima destinada a lineas de sellado/termoformado (% de compras):",
            min_value=30, max_value=100, value=65, step=5,
            help="Permite aislar las compras que realmente pasan por termosellado de aquellas destinadas a troquelado plano."
        )

    base_consumo_afectada = balance_activo["coste_materiales_consumos"] * (mix_sellado_pct / 100.0)
    
    # Subvención regional adaptativa
    if "Comunidad Valenciana" in empresa_activa["comunidad_autonoma"]:
        subv_nombre = "IVACE+i Packaging DOGV 9842"
    elif "Navarra" in empresa_activa["comunidad_autonoma"]:
        subv_nombre = "Gobierno de Navarra / FEDER Industria Circular"
    elif "Andalucia" in empresa_activa["comunidad_autonoma"]:
        subv_nombre = "Agencia IDEA / TRADE Innovacion Industrial"
    elif "Cataluna" in empresa_activa["comunidad_autonoma"]:
        subv_nombre = "ACCIÓ Cupones Industria Circular"
    else:
        subv_nombre = "CDTI / Ayudas Regionales FEDER"

    sim = FinancialEngine.simular_escenario_tecnologico_dinamico(
        capex_bruto=tech["capex_llave_en_mano"],
        coste_materiales_anual=base_consumo_afectada,
        tasa_recuperacion_merma=0.022,
        pct_subvencion=0.40,
        plazo_meses=36
    )

    coste_total_cuotas_renting = sim['cuota_mensual_estimada'] * 36
    coste_neto_renting_con_subv = coste_total_cuotas_renting - sim['subvencion_proyectada']

    t1, t2 = st.columns(2)
    with t1:
        st.markdown(f"##### Opcion A: Compra Directa con Subvencion ({tech['nombre']})")
        st.write(f"- **CAPEX Bruto Llave en Mano:** {tech['capex_llave_en_mano']:,.2f} EUR")
        st.write(f"- **Subvencion Proyectada (40%):** -{sim['subvencion_proyectada']:,.2f} EUR (`{subv_nombre}`)")
        st.write(f"- **Desembolso Neto Final en Tesoreria:** **{sim['inversion_neta_proyectada']:,.2f} EUR**")
        st.caption("Requiere disponer del 100% de liquidez previa; el abono de la subvención opera ex-post tras justificación.")
    with t2:
        st.markdown("##### Opcion B: Arrendamiento Operativo (Renting Fuera de Balance)")
        st.write(f"- **Cuota mensual proyectada (36 meses):** **{sim['cuota_mensual_estimada']:,.2f} EUR/mes**")
        st.write(f"- **Ahorro operativo mensual calibrado (2.2%):** **~{sim['ahorro_mensual_teorico']:,.0f} EUR/mes**")
        st.write(f"- **Cash Flow Operativo Neto Mensual:** **+~{sim['diferencial_mensual_proyectado']:,.0f} EUR/mes**")
        st.caption(f"Coste neto de renting a 3 años tras cobro de subvencion: **~{coste_neto_renting_con_subv:,.2f} EUR**.")

    st.markdown("---")

    # =========================================================================
    # PREGUNTA 3: ORDEN DEL DÍA DEL CONSEJO (100% DINÁMICO PARA ESTA EMPRESA)
    # =========================================================================
    st.subheader(f"4. Orden del Día Ejecutivo: Propuestas de Acuerdo para el Consejo de {empresa_activa['razon_social']}")
    st.caption("Acuerdos formalizados con justificacion economica personalizada y texto resolutivo para votacion.")

    st.markdown(f"""
    <div class="executive-card">
        <h4>PUNTO 1: Blindaje de Margen y Repercusión Contractual de la Ecotasa RAP (RD 1055/2022)</h4>
        <p><strong>Justificación Económica:</strong> {empresa_activa['razon_social']} procesa aproximadamente <strong>{reg_quant['toneladas_procesadas']:,.0f} toneladas anuales</strong> de cartón/embalaje. La tarifa de adhesión a SCRAP (Envalora/Pro Circular) supone un sobrecoste anual directo de <strong>~{reg_quant['impacto_anual_scrap']:,.0f} EUR</strong>. Si la dirección comercial no traslada esta cuota en factura, la empresa absorberá un impacto negativo directo del <strong>{pct_ebitda_reg:.1f}% de su EBITDA actual ({ratios['ebitda']:,.0f} EUR)</strong>.</p>
        <p><strong>PROPUESTA DE ACUERDO:</strong> <em>«Aprobar la inclusión con carácter obligatorio e improrrogable en todas las tarifas comerciales de {empresa_activa['razon_social']} de una partida desagregada bajo el concepto 'Ecotasa RAP RD 1055/2022', trasladando íntegramente el coste unitario por kilogramo a los clientes a partir del próximo ciclo de facturación, instruyendo a la Dirección Comercial para que no autorice excepciones sin autorización expresa de este Consejo.»</em></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="executive-card">
        <h4>PUNTO 2: Requerimiento Notarial y Auditoría de Proveedores de Bobina por Límites PFAS (Reglamento UE 2025/40)</h4>
        <p><strong>Justificación Económica:</strong> El Artículo 5 del Reglamento (UE) 2025/40 prohíbe comercializar envases alimentarios con PFAS a partir del 12 de agosto de 2026. Para {empresa_activa['razon_social']}, el catálogo antigrasa/alimentario representa aproximadamente <strong>~{reg_quant['volumen_ventas_riesgo_pfas']:,.0f} EUR de facturación anual (30% de la cifra de negocios)</strong>. Operar sin Declaraciones de Conformidad (DoC) verificadas expone a la compañía a la rescisión fulminante de contratos por parte de la gran distribución alimentaria.</p>
        <p><strong>PROPUESTA DE ACUERDO:</strong> <em>«Comisionar a la Dirección Técnica para que en un plazo máximo de 45 días naturales requiera formalmente a los proveedores de bobina y química la entrega de Declaraciones de Conformidad (DoC) y ensayos analíticos acreditados que certifiquen niveles inferiores a 25 ppb. En caso de ausencia de certificación en dicho plazo, se autoriza la apertura de homologación urgente de proveedores alternativos que garanticen suministro conforme.»</em></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="executive-card">
        <h4>PUNTO 3: Aprobación Condicionada de Ensayo Piloto de Visión Multiespectral SWIR Fuera de Balance</h4>
        <p><strong>Justificación Económica:</strong> Sobre una base calibrada de <strong>{base_consumo_afectada:,.0f} EUR anuales</strong> en líneas de sellado ({mix_sellado_pct}% de las compras de {empresa_activa['razon_social']}), la reducción del 2,2% en defectos genera un ahorro recurrente de <strong>~{sim['ahorro_mensual_teorico']:,.0f} EUR/mes</strong>, frente a una cuota de renting de <strong>{sim['cuota_mensual_estimada']:,.2f} EUR/mes</strong>, generando un flujo de caja neto positivo de <strong>+~{sim['diferencial_mensual_proyectado']:,.0f} EUR/mes</strong>.</p>
        <p><strong>PROPUESTA DE ACUERDO:</strong> <em>«Autorizar a la Dirección de Operaciones la ejecución de un ensayo in-situ sin coste de compromiso con un integrador de visión multiespectral durante un plazo de 15 días en la línea principal de sellado. Dicha autorización queda condicionada a certificar una tasa de falsos rechazos inferior al 0,3%. Cumplido dicho hito, se autoriza la formalización del renting operativo a 36 meses y la solicitud simultánea de la subvención '{subv_nombre}'.»</em></p>
    </div>
    """, unsafe_allow_html=True)
