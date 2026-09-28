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
        "subsector": "Termoformado de celulosa y envases microcanal para HORECA",
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
            "deuda_bancaria_total": 540000.0,
            "plantilla": 24
        }
    },
    "A31456789": {
        "cif": "A31456789",
        "razon_social": "Cartonajes del Norte S.A.",
        "cnae": "1721 - Fabricacion de papel y carton ondulado",
        "subsector": "Cajas de carton ondulado pesado y embalaje industrial exportacion",
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
            "deuda_bancaria_total": 850000.0,
            "plantilla": 38
        }
    }
}

st.title("KROMA Enterprise — Outside-In Intelligence Scan")
st.caption("Dossier de Inteligencia Estrategica y Diagnostico de Vulnerabilidad | Sector Packaging Industrial (CNAE 1721 / 2222)")

st.info("""
**REGLA DE EVIDENCIA KROMA:** Ninguna inferencia técnica, regulatoria o económica se presenta como hecho sin una evidencia primaria que cierre la inferencia. 
Cuando la evidencia no existe desde fuentes públicas, KROMA cuantifica la hipótesis, declara el nivel de incertidumbre y especifica la diligencia de validación requerida para el Comité de Dirección.
""")

col_cif, col_modo = st.columns([2, 2])
with col_cif:
    cif_ingresado = st.text_input("Identificador Fiscal (CIF) a Auditar:", value="B98765432").strip().upper()
with col_modo:
    empresa_detectada = EMPRESAS_REGISTRADAS.get(cif_ingresado)
    if empresa_detectada:
        st.success(f"Entidad localizada: **{empresa_detectada['razon_social']}** ({empresa_detectada['comunidad_autonoma']})")
    else:
        st.warning("CIF no pre-registrado en demo. Introduce los datos registrales a continuación:")

# Formulario para cualquier CIF no indexado previamente
if not empresa_detectada:
    with st.expander("Parametros Contables Registrales (Modo Cualquier CIF)", expanded=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            razon_custom = st.text_input("Razon Social:", "Packaging Industrial Personalizado S.L.")
            comunidad_custom = st.selectbox("Comunidad Autonoma:", ["Comunidad Valenciana", "Comunidad Foral de Navarra", "Cataluna", "Murcia", "Andalucia", "Madrid", "Pais Vasco", "Otra"])
            ventas_custom = st.number_input("Cifra de Negocios (EUR):", value=4200000.0, step=50000.0)
            coste_mat_custom = st.number_input("Consumo Aprovisionamientos (EUR):", value=1950000.0, step=50000.0)
        with col_f2:
            ebitda_custom = st.number_input("EBITDA Contable (EUR):", value=390000.0, step=20000.0)
            clientes_custom = st.number_input("Deudores Comerciales (Clientes):", value=890000.0, step=20000.0)
            stock_custom = st.number_input("Existencias (Stock):", value=480000.0, step=20000.0)
        with col_f3:
            prov_custom = st.number_input("Proveedores Deuda:", value=410000.0, step=20000.0)
            deuda_custom = st.number_input("Deuda Bancaria:", value=680000.0, step=50000.0)
            plantilla_custom = st.number_input("Plantilla Media:", value=28, step=1)

    es_foral = "Navarra" in comunidad_custom or "Pais Vasco" in comunidad_custom
    empresa_activa = {
        "cif": cif_ingresado,
        "razon_social": razon_custom,
        "cnae": "1721 - Fabricacion de papel y carton ondulado",
        "subsector": "Transformacion de carton y envase alimentario",
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
            "deuda_bancaria_total": deuda_custom,
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

    st.markdown("---")

    # SECCION 1: ANÁLISIS FINANCIERO Y DISTRIBUCIÓN
    st.subheader(f"1. Radiografia de Estados Financieros: {empresa_activa['razon_social']}")
    st.caption(f"Cuentas Anuales Oficiales depositadas frente a cohorte de 50 empresas de referencia (CNAE 1721).")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("[DATO REGISTRAL] Cifra de Negocios", f"{ratios['ventas']:,.0f} EUR", "Ejercicio Fiscal")
    c2.metric("[DATO REGISTRAL] EBITDA Oficial", f"{ratios['ebitda']:,.0f} EUR", f"Margen: {ratios['ebitda_pct']}%")
    c3.metric("[CÁLCULO KROMA] Plazo Cobro (DSO)*", f"{ratios['dso']} dias", f"Mediana: {peer['dso_mediana']} d", delta_color="inverse")
    c4.metric("[CÁLCULO KROMA] Rotacion Stock (DIO)", f"{ratios['dio']} dias", f"Mediana: {peer['dio_mediana']} d", delta_color="inverse")

    st.markdown("##### Posicion de la Entidad frente a la Distribucion de Referencia (50 Peers)")
    df_dist = pd.DataFrame([
        {
            "Indicador Financiero": "Periodo Medio de Cobro (DSO)*",
            "Entidad Auditada": f"{ratios['dso']} dias",
            "P25": f"{peer['dso_p25']} dias",
            "Mediana": f"{peer['dso_mediana']} dias",
            "P75": f"{peer['dso_p75']} dias",
            "P90": f"{peer['dso_p90']} dias",
            "Posicion en Cohorte": peer["posicion_dso"]
        },
        {
            "Indicador Financiero": "Permanencia de Inventario (DIO)",
            "Entidad Auditada": f"{ratios['dio']} dias",
            "P25": f"{peer['dio_p25']} dias",
            "Mediana": f"{peer['dio_mediana']} dias",
            "P75": f"{peer['dio_p75']} dias",
            "P90": f"{peer['dio_p90']} dias",
            "Posicion en Cohorte": peer["posicion_dio"]
        }
    ])
    st.dataframe(df_dist, use_container_width=True)

    with st.expander("Nota Metodologica, Homogeneidad y Cautela de IVA"):
        met = benchmark["metodologia"]
        st.write(f"- **Universo de referencia:** {met['universo_analizado']}.")
        st.write(f"- **Segmentacion:** {met['filtro_tamano']}.")
        st.write(f"- **Tratamiento estadistico:** {met['depuracion_estadistica']}.")
        st.write(f"- **Formula DSO:** `{met['formula_dso']}`")
        st.write(f"- **Formula DIO:** `{met['formula_dio']}`")
        st.caption(f"**(*) Cautela de IVA sobre DSO:** Cálculo registral estándar sin deflactar efecto impositivo indirecto devengado en cuentas a cobrar. Dado que la cuenta de clientes incluye IVA devengado (21%) mientras que la cifra de negocios es neta, el ratio registral presenta un sesgo mecánico al alza de entre 12 y 16 días respecto al plazo de crédito contractualmente pactado.")
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
        - Potencial teorico modelizado: Calculo mecanico sin friccion operativa.
        - Potencial operacionalmente validable: Ajustado tras ponderar compromisos de servicio y compras minimas.
        - Potencial economico recuperable: Caja neta liberable mediante renegociacion de plazos y saneamiento de stock.
        """)

    with col_pot2:
        st.markdown("##### [A VALIDAR EN PLANTA] Requerimientos de Auditoria y Restricciones de Fabricacion")
        st.markdown(f"""
        Para contrastar la hipotesis de circulante frente a la realidad de planta, el Comite debe ponderar:
        1. **Concentracion de Saldos Deudores:** Determinar qué porcentaje de la deuda comercial vencida y no vencida se concentra en las principales cuentas de distribucion y en qué medida explica la desviacion del DSO.
        2. **Restriccion Operativa de Aprovisionamiento (MOQ Bobina):** La brecha de existencias ({circ['dias_brecha_dio']} dias) refleja con frecuencia la prima de inmovilizado asumida para garantizar continuidad de servicio frente a los lotes minimos de pedido (MOQ) y lead times impuestos por los fabricantes de papel y carton virgen.
        3. **Estructura y Antigüedad de Inventario:** Desglosar existencias entre bobina virgen, producto en curso (WIP), stock de seguridad contractual y referencias obsoletas.
        4. **Rotacion por SKU:** Analizar la velocidad de rotacion de familias criticas para separar inventario de rotacion rapida frente a inmovilizado improductivo.
        """)

    st.markdown("---")

    # SECCION 3: MAPA DE EXPOSICIÓN REGULATORIA PPWR Y LEY 7/2022
    st.subheader("3. Matriz de Exposicion Regulatoria: PPWR y Fiscalidad de Envases")
    st.caption(f"Cruce de normativa comunitaria vinculante frente al catalogo comercial observable en {empresa_activa['comunidad_autonoma']}.")

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
            "Regulacion Aplicable": "Ley Foral 14/2023" if empresa_activa["territorio_foral"] else "Ley 7/2022 (0,45 EUR/kg)",
            "Hipotesis KROMA": "Sujecion segun condicion de contribuyente",
            "Validacion Documental Requerida": "Gramaje plastico no reciclado por SKU",
            "Nivel Confianza": "🟡 HIPOTESIS"
        }
    ])
    st.dataframe(df_reg_resumen, use_container_width=True)

    for norm in normativas:
        # Adaptación territorial estricta de la fiscalidad de plástico
        marco_legal = norm['marco_legal']
        titulo_norma = norm['titulo']
        if norm['id'] == "ESP-LEY-7-2022":
            if empresa_activa["territorio_foral"]:
                marco_legal = "Ley Foral 14/2023 (Navarra) de Régimen Tributario Foral sobre Envases de Plástico"
                titulo_norma = "Impuesto sobre Envases de Plástico No Reutilizables (Régimen Foral de Navarra)"
            else:
                marco_legal = "Ley 7/2022, de 8 de abril, de residuos y suelos contaminados (Régimen Común Estatal)"
                titulo_norma = "Impuesto sobre Envases de Plástico No Reutilizables (Régimen Común Estatal)"

        with st.container():
            st.markdown(f"#### {norm['articulo']}: {titulo_norma}")
            st.write(f"**Marco Regulatorio:** `{marco_legal}` | **Fecha Aplicable:** `{norm['fecha_aplicacion']}`")
            
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

    # SECCION 4: HIPÓTESIS TECNOLÓGICA Y FINANCIACIÓN
    st.subheader("4. Escenario de Hipotesis Tecnologica y Financiacion Fuera de Balance")
    st.caption("Modelizacion sobre TRL 9 en base al consumo real de materiales. No constituye prescripcion vinculante de proveedor.")

    tech = tecnologias[0]
    
    # Subvención regional adaptativa según la comunidad de la empresa
    subv_seleccionada = subvenciones[0]
    if "Comunidad Valenciana" in empresa_activa["comunidad_autonoma"]:
        subv_nombre = "IVACE+i Innovacion Packaging - DOGV 9842"
    elif "Navarra" in empresa_activa["comunidad_autonoma"]:
        subv_nombre = "Gobierno de Navarra / FEDER - Fomento Industria Circular"
    else:
        subv_nombre = "CDTI / Fondos Europeos FEDER Regional"

    # Simulación ligada al consumo real de materiales de la entidad auditada
    sim = FinancialEngine.simular_escenario_tecnologico_dinamico(
        capex_bruto=tech["capex_llave_en_mano"],
        coste_materiales_anual=balance_activo["coste_materiales_consumos"],
        tasa_recuperacion_merma=0.022,
        pct_subvencion=0.40,
        plazo_meses=36
    )

    t1, t2 = st.columns(2)
    with t1:
        st.markdown(f"##### Hipotesis de Referencia: {tech['nombre']}")
        st.write(f"- **Categoria:** {tech['categoria']} (TRL {tech['trl']})")
        st.write(f"- **CAPEX Estimativo Llave en Mano:** {tech['capex_llave_en_mano']:,.2f} EUR")
        st.write(f"- **Subvencion Potencial Proyectada (40%):** -{sim['subvencion_proyectada']:,.2f} EUR (`{subv_nombre}`)")
        st.write(f"- **Inversion Neta Resultante:** {sim['inversion_neta_proyectada']:,.2f} EUR")
        st.caption("Nota Financiera: La subvención a fondo perdido opera ex-post mediante abono directo del organismo convocante; el contrato de renting financiero computa sobre el valor bruto del activo.")
    with t2:
        st.markdown("##### Estructuracion Fuera de Balance (Renting 36m)")
        st.write(f"- Cuota de renting proyectada: **{sim['cuota_mensual_estimada']:,.2f} EUR/mes**")
        st.write(f"- Ahorro mensual modelizado ({sim['pct_merma_modelizado']}% s/consumos): **~{sim['ahorro_mensual_teorico']:,.0f} EUR/mes**")
        st.write(f"- Diferencial mensual neto proyectado: **~{sim['diferencial_mensual_proyectado']:,.0f} EUR/mes**")
        st.caption(f"Base de cálculo: Modelizado sobre la partida registrada de aprovisionamientos ({sim['base_consumo_anual']:,.0f} EUR/año). Asume una reduccion potencial de defectos de sellado del {sim['pct_merma_modelizado']}%.")

    with st.expander("[A VALIDAR EN PLANTA] Variables Criticas de Integracion Tecnica"):
        st.markdown("""
        Antes de cualquier decision de inversion, la direccion tecnica debe validar:
        1. **Tipologia y Defecto Objetivo:** Determinar si el fallo principal es burbuja de aire, contaminacion grasa o desalineacion de troquel.
        2. **Sensibilidad y Falso Rechazo:** Medir la tasa admisible de falsos positivos para evitar expulsiones indebidas de envases conformes.
        3. **Velocidad y Sincronizacion:** Compatibilidad con la velocidad real de linea (ppm) y conexion encoder/PLC con la termoselladora existente.
        4. **Mecanismo de Expulsion Fisica:** Comprobar si existe espacio para brazo soplador o desviador neumatico sin comprometer el flujo del transportador.
        5. **Disponibilidad e Impacto en OEE:** Calcular los tiempos de limpieza de opticas por presencia de polvo de celulosa en ambiente.
        """)
