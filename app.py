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

with st.sidebar:
    st.header("Configuracion del Sistema")
    st.caption("Protocolo Activo: Outside-In Intelligence Scan")
    st.divider()
    st.markdown("**Taxonomia Metodologica:**")
    st.markdown("- `[DATO REGISTRAL]` Cuentas anuales depositadas (SABI / RM)")
    st.markdown("- `[CÁLCULO KROMA]` Modelizacion cuantitativa determinista")
    st.markdown("- `[HIPÓTESIS]` Inferencia de catalogo y exposicion exterior")
    st.markdown("- `[A VALIDAR EN PLANTA]` Diligencia y contraste documental interno")

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
    "comunidad_autonoma": "Comunidad Valenciana",
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
st.caption("Dossier de Inteligencia Estrategica y Diagnostico de Vulnerabilidad | Sector Packaging Industrial (CNAE 1721)")

st.info("""
**REGLA DE EVIDENCIA KROMA:** Ninguna inferencia técnica, regulatoria o económica se presenta como hecho sin una evidencia primaria que cierre la inferencia. 
Cuando la evidencia no existe desde fuentes públicas, KROMA cuantifica la hipótesis, declara el nivel de incertidumbre y especifica la diligencia de validación requerida para el Comité de Dirección.
""")

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
        st.error(f"Error en lectura de repositorios: {str(e)}")
        st.stop()

    fin_data = FinancialEngine.calcular_diagnostico_completo(EMPRESA_AUDITADA["balance_actual"], benchmark)
    ratios = fin_data["ratios_empresa"]
    peer = fin_data["benchmark_peer"]
    circ = fin_data["potencial_circulante"]

    st.markdown("---")

    # SECCION 1: ANÁLISIS FINANCIERO Y DISTRIBUCIÓN
    st.subheader(f"1. Radiografia de Estados Financieros: {EMPRESA_AUDITADA['razon_social']}")
    st.caption("Cuentas Anuales Oficiales depositadas en el Registro Mercantil frente a cohorte de 50 empresas de referencia.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("[DATO REGISTRAL] Cifra de Negocios", f"{ratios['ventas']:,.0f} EUR", "Ejercicio 2024")
    c2.metric("[DATO REGISTRAL] EBITDA Oficial", f"{ratios['ebitda']:,.0f} EUR", f"Margen: {ratios['ebitda_pct']}%")
    c3.metric("[CÁLCULO KROMA] Plazo Cobro (DSO)", f"{ratios['dso']} dias", f"Mediana: {peer['dso_mediana']} d", delta_color="inverse")
    c4.metric("[CÁLCULO KROMA] Rotacion Stock (DIO)", f"{ratios['dio']} dias", f"Mediana: {peer['dio_mediana']} d", delta_color="inverse")

    st.markdown("##### Posicion de la Entidad frente a la Distribucion de Referencia (50 Peers)")
    df_dist = pd.DataFrame([
        {
            "Indicador Financiero": "Periodo Medio de Cobro (DSO)",
            "BioPack Levantina": f"{ratios['dso']} dias",
            "P25": f"{peer['dso_p25']} dias",
            "Mediana": f"{peer['dso_mediana']} dias",
            "P75": f"{peer['dso_p75']} dias",
            "P90": f"{peer['dso_p90']} dias",
            "Posicion en Cohorte": peer["posicion_dso"]
        },
        {
            "Indicador Financiero": "Permanencia de Inventario (DIO)",
            "BioPack Levantina": f"{ratios['dio']} dias",
            "P25": f"{peer['dio_p25']} dias",
            "Mediana": f"{peer['dio_mediana']} dias",
            "P75": f"{peer['dio_p75']} dias",
            "P90": f"{peer['dio_p90']} dias",
            "Posicion en Cohorte": peer["posicion_dio"]
        }
    ])
    st.dataframe(df_dist, use_container_width=True)

    with st.expander("Nota Metodologica y Cautela de Homogeneidad"):
        met = benchmark["metodologia"]
        st.write(f"- **Universo de referencia:** {met['universo_analizado']}.")
        st.write(f"- **Segmentacion:** {met['filtro_tamano']}.")
        st.write(f"- **Tratamiento estadistico:** {met['depuracion_estadistica']}.")
        st.write(f"- **Formula DSO:** `{met['formula_dso']}`")
        st.write(f"- **Formula DIO:** `{met['formula_dio']}`")
        st.caption(f"**Aviso sobre comparabilidad del DIO:** {met['cautela_comparabilidad_dio']}")

    st.markdown("---")

    # SECCION 2: CIRCULANTE Y POTENCIAL TEÓRICO
    st.subheader("2. Intelligence Scan de Circulante: Potencial Teorico de Liberacion de Caja")
    st.caption("Modelizacion mecanica de convergencia hacia la mediana del grupo de comparacion.")

    col_pot1, col_pot2 = st.columns([2, 3])
    with col_pot1:
        st.metric(
            label="Potencial Teorico por Convergencia a Mediana",
            value=f"~{circ['potencial_teorico_total']:,.0f} EUR",
            help="Calculo teorico de convergencia mecanica. No presupone que el 100% de esta diferencia sea operativamente recuperable."
        )
        st.write(f"- **Clientes (DSO):** Estimado ~{circ['potencial_dso_eur']:,.0f} EUR ({circ['dias_brecha_dso']} dias s/mediana)")
        st.write(f"- **Existencias (DIO):** Estimado ~{circ['potencial_dio_eur']:,.0f} EUR ({circ['dias_brecha_dio']} dias s/mediana)")
        
        st.caption("""
        **Estructura de Realizacion:**
        - Potencial teorico modelizado: ~456.616 EUR.
        - Potencial operacionalmente validable: [Pendiente de contraste].
        - Potencial economico recuperable: [Condicionado a negociacion de cobro y stock].
        """)

    with col_pot2:
        st.markdown("##### [A VALIDAR EN PLANTA] Requerimientos de Auditoria Interna")
        st.markdown("""
        Para contrastar la hipotesis de circulante frente a la realidad operativa, el Comite debe auditar:
        1. **Concentracion de Saldos Deudores:** Determinar qué porcentaje de la deuda comercial vencida y no vencida se concentra en las principales cuentas de distribucion y en qué medida explica la desviacion del DSO.
        2. **Estructura y Antigüedad de Inventario:** Desglosar existencias entre bobina virgen, producto en curso (WIP), stock de seguridad y referencias obsoletas.
        3. **Condiciones de Compra (MOQ) y Lead Times:** Identificar si el volumen de existencias responde a lotes minimos de pedido impuestos por fabricantes de papel o a compras especulativas.
        4. **Rotacion por SKU:** Analizar la velocidad de rotacion de familias criticas para separar stock sano de inmovilizado improductivo.
        """)

    st.markdown("---")

    # SECCION 3: MAPA DE EXPOSICIÓN REGULATORIA PPWR Y LEY 7/2022
    st.subheader("3. Matriz de Exposicion Regulatoria: PPWR y Fiscalidad de Envases")
    st.caption("Cruce de normativa comunitaria vinculante frente al catalogo comercial observable.")

    df_reg_resumen = pd.DataFrame([
        {
            "Familia / Catalogo Observado": "Barquetas celulosa alimentaria",
            "Evidencia Publica": "[REGISTRAL / WEB]",
            "Regulacion Aplicable": "PPWR Art. 5 (PFAS)",
            "Hipotesis KROMA": "Riesgo de exclusion si incorpora fluorados",
            "Validacion Documental Requerida": "DoC proveedor y ensayo analitico",
            "Nivel Confianza": "🟡 HIPOTESIS"
        },
        {
            "Familia / Catalogo Observado": "Cajas de transporte y e-commerce",
            "Evidencia Publica": "[REGISTRAL / WEB]",
            "Regulacion Aplicable": "PPWR Art. 24 (Espacio vacio)",
            "Hipotesis KROMA": "Ajuste dimensional bajo metodologia CE",
            "Validacion Documental Requerida": "Auditoria de volumen aire por SKU",
            "Nivel Confianza": "🟡 HIPOTESIS"
        },
        {
            "Familia / Catalogo Observado": "Embalajes logisticos secundarios",
            "Evidencia Publica": "[REGISTRAL / WEB]",
            "Regulacion Aplicable": "PPWR Art. 26 y 29 (Reutilizacion)",
            "Hipotesis KROMA": "Demanda de formatos compatibles con pooling",
            "Validacion Documental Requerida": "Mix cliente industrial vs gran consumo",
            "Nivel Confianza": "🟡 HIPOTESIS"
        },
        {
            "Familia / Catalogo Observado": "Envases takeaway servicio rapido",
            "Evidencia Publica": "[REGISTRAL / WEB]",
            "Regulacion Aplicable": "PPWR Art. 32 (Refill HORECA)",
            "Hipotesis KROMA": "Erosion potencial de envase monouso",
            "Validacion Documental Requerida": "Desglose facturacion sala vs delivery",
            "Nivel Confianza": "🟡 HIPOTESIS"
        },
        {
            "Familia / Catalogo Observado": "Complejos carton-plastico / film",
            "Evidencia Publica": "[REGISTRAL / WEB]",
            "Regulacion Aplicable": "Ley 7/2022 (0,45 EUR/kg)",
            "Hipotesis KROMA": "Sujecion segun condicion de contribuyente",
            "Validacion Documental Requerida": "Gramaje plastico no reciclado por SKU",
            "Nivel Confianza": "🟡 HIPOTESIS"
        }
    ])
    st.dataframe(df_reg_resumen, use_container_width=True)

    for norm in normativas:
        with st.container():
            st.markdown(f"#### {norm['articulo']}: {norm['titulo']}")
            st.write(f"**Marco Regulatorio:** `{norm['marco_legal']}` | **Fecha Aplicable:** `{norm['fecha_aplicacion']}`")
            
            c_r1, c_r2 = st.columns(2)
            with c_r1:
                st.markdown(f"**[EVIDENCIA OBSERVABLE]** {norm['familia_catalogo_afectada']}")
                st.markdown(f"**[HIPOTESIS KROMA]** {norm['hipotesis_kroma']}")
                st.write("**Escenarios de Exposicion Comercial:**")
                st.write(f"- *Conservador:* {norm['escenarios_exposicion']['conservador']}")
                st.write(f"- *Base:* {norm['escenarios_exposicion']['base']}")
                st.write(f"- *Severo:* {norm['escenarios_exposicion']['severo']}")
            with c_r2:
                st.markdown("**[A VALIDAR EN PLANTA] Diligencia Documental Requerida:**")
                st.info(norm['validacion_requerida_planta'])
            st.divider()

    # SECCION 4: HIPÓTESIS TECNOLÓGICA Y VIABILIDAD OPERATIVA
    st.subheader("4. Escenario de Hipotesis Tecnologica y Financiacion Fuera de Balance")
    st.caption("Exploracion de soluciones comerciales estandar (TRL 9). No constituye prescripcion vinculante de proveedor.")

    tech = tecnologias[0]
    subv = subvenciones[0]
    sim = FinancialEngine.simular_escenario_tecnologico(
        capex_bruto=tech["capex_llave_en_mano"],
        ahorro_anual_estimado=tech["ahorro_anual_estimado_pyme"],
        pct_subvencion=subv["porcentaje_fondo_perdido"]
    )

    t1, t2 = st.columns(2)
    with t1:
        st.markdown(f"##### Hipotesis de Referencia: {tech['nombre']}")
        st.write(f"- **Categoria:** {tech['categoria']} (TRL {tech['trl']})")
        st.write(f"- **CAPEX Estimativo Llave en Mano:** {tech['capex_llave_en_mano']:,.2f} EUR")
        st.write(f"- **Subvencion Potencial Proyectada:** -{sim['subvencion_proyectada']:,.2f} EUR ({subv['organismo'].split(' ')[0]} - {subv['codigo_bdns']})")
        st.write(f"- **Inversion Neta Resultante:** {sim['inversion_neta_proyectada']:,.2f} EUR")
    with t2:
        st.markdown("##### Estructuracion Financiera Fuera de Balance (Renting 36m)")
        st.write(f"- Cuota de renting proyectada: **{sim['cuota_mensual_estimada']:,.2f} EUR/mes**")
        st.write(f"- Ahorro mensual potencial estimado: **~{sim['ahorro_mensual_teorico']:,.0f} EUR/mes**")
        st.write(f"- Diferencial mensual proyectado: **~{sim['diferencial_mensual_proyectado']:,.0f} EUR/mes**")
        st.caption("Aviso: Modelo basado en hipotesis sectoriales de merma; requiere validacion de tasa real, volumen, causalidad de defecto y capacidad efectiva de rechazo.")

    with st.expander("[A VALIDAR EN PLANTA] Variables Criticas de Integracion Tecnica"):
        st.markdown("""
        Antes de cualquier decision de inversion, la direccion tecnica debe validar:
        1. **Tipologia y Defecto Objetivo:** Determinar si el fallo principal es burbuja de aire, contaminacion grasa o desalineacion de troquel.
        2. **Sensibilidad y Falso Rechazo:** Medir la tasa admisible de falsos positivos para evitar expulsiones indebidas de envases conformes.
        3. **Velocidad y Sincronizacion:** Compatibilidad con la velocidad real de linea (ppm) y conexion encoder/PLC con la termoselladora existente.
        4. **Mecanismo de Expulsion Fisica:** Comprobar si existe espacio para brazo soplador o desviador neumatico sin comprometer el flujo del transportador.
        5. **Disponibilidad e Impacto en OEE:** Calcular los tiempos de limpieza de opticas por presencia de polvo de celulosa en ambiente.
        """)
