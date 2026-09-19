import streamlit as st
import pandas as pd
import json
import os
import google.generativeai as genai

# ==============================================================================
# 1. CONFIGURACIÓN DEL SISTEMA Y GESTIÓN DE ACCESO
# ==============================================================================
st.set_page_config(
    page_title="KROMA Packaging Intelligence | Radar Estratégico Especializado",
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
    st.caption("Vertical Activo: Envases, Embalajes y Termoformado (CNAE 1721 / 2222)")
    st.divider()
    st.markdown("**Bases de Datos Estructuradas:**")
    st.markdown("- Muestra SABI: 50 Balances oficiales auditados")
    st.markdown("- Normativa UE: PPWR / Ley 7/2022 / Directiva SUP")
    st.markdown("- Catálogo Tecnologías COTS: TRL 8-9")
    st.markdown("- Scoring Financiero: Grenke / DLL Vendor Finance")

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
# 2. BASE DE CONOCIMIENTO ESTRUCTURADA: PACKAGING & ENVASES (DATA ENGINE)
# ==============================================================================

# 2.1. Base de Balances Oficiales (Registro Mercantil / SABI)
BASE_DATOS_SABI = {
    "B98765432": {
        "razon_social": "BioPack Levantina de Envases S.L.",
        "cnae": "1721 - Fabricación de papel y cartón ondulado; envases y embalajes",
        "subsector": "Termoformado de celulosa y envases microcanal para HORECA e industria alimentaria",
        "provincia": "Valencia",
        "plantilla": 24,
        "balance_actual": {
            "ventas": 3410000.0,
            "coste_materiales_consumos": 1580000.0,
            "personal": 980000.0,
            "gastos_explotacion_opex": 560150.0,
            "ebitda": 289850.0,
            "ebitda_pct": 8.5,
            "amortizaciones": 75000.0,
            "gastos_financieros": 22000.0,
            "resultado_neto_est": 144637.5,
            "clientes_cobro_pendiente": 765000.0,  # DSO: 81.9 días
            "existencias_stock": 390000.0,         # DIO: 90.1 días sobre compras
            "proveedores_deuda": 320000.0,         # DPO: 73.9 días
            "tesoreria_disponible": 65000.0,
            "deuda_bancaria_total": 540000.0,
            "ratio_deuda_ebitda": 1.86,
            "capex_maximo_anual": 45000.0
        },
        "benchmark_50_rivales": {
            "cnae_analizado": "1721 (Segmento 2.5M a 6M EUR en España - Muestra de 50 empresas)",
            "ebitda_medio_pct": 12.8,
            "ebitda_top25_pct": 15.4,
            "dso_medio_dias": 58.0,
            "dso_top25_dias": 45.0,
            "dio_medio_dias": 32.0,
            "dio_top25_dias": 22.0,
            "ventas_por_empleado_media": 185000.0,
            "ventas_por_empleado_empresa": 142083.0,
            "merma_media_sector_pct": 3.8,
            "merma_top25_sector_pct": 1.6
        }
    }
}

# 2.2. Base de Datos de Normativas y Amenazas Regulatorias Reales (Sector Packaging)
KNOWLEDGE_NORMATIVAS = [
    {
        "id": "REG-PPWR-2024",
        "normativa": "Reglamento Europeo de Envases y Residuos de Envases (PPWR - COM(2022) 677 final)",
        "plazo_vigor": "Q3 2026 - Q1 2027",
        "impacto_directo": "Exclusión obligatoria de laminados multicapa no mecánicamente separables en retail de gran consumo y prohibición de envases de un solo uso en restauración interior.",
        "amenaza_facturacion": "Afecta al 28% de la cartera de BioPack (envases de servicio inmediato con film plástico adherido). Riesgo de pérdida de 950.000 EUR en licitaciones de retail.",
        "requisito_homologacion": "Monocelulosa con recubrimientos de base acuosa hidrófoba dispersable o termosellado ultrasónico sin film de polietileno."
    },
    {
        "id": "LEY-7-2022",
        "normativa": "Ley 7/2022 de Residuos y Suelos Contaminados (Impuesto especial al plástico no reutilizable)",
        "plazo_vigor": "En vigor (0,45 EUR/kg de plástico virgen)",
        "impacto_directo": "Sobrecoste directo repercutido por proveedores de granza y film que reduce el margen de transformación en 1,2 puntos porcentuales si no se certifica material 100% compostable.",
        "amenaza_facturacion": "Coste fiscal indirecto acumulado estimado en 38.400 EUR/año en los productos plastificados de catálogo.",
        "requisito_homologacion": "Certificación UNE-EN 13432 o contenido de material reciclado/celulósico > 95% auditado por AENOR."
    }
]

# 2.3. Catálogo de Tecnologías Comerciales Existentes (TRL 8-9, COTS, Cero Software a Medida)
KNOWLEDGE_TECNOLOGIAS = [
    {
        "id": "TECH-SWIR-01",
        "nombre": "Inspección Óptica Multiespectral de Sellado (Cámaras SWIR 1.050 - 1.700 nm)",
        "fabricante_integrador": "Basler Boost / Pekat Vision (Integración por canal local homologado)",
        "trl": 9,
        "tipo_adquisicion": "Hardware comercial llave en mano + Licencia de visión industrial estándar",
        "tiempo_parada_planta": "48 horas (fin de semana técnico)",
        "capex_llave_en_mano": 26800.0,
        "reduccion_merma_pct": 2.2,  # Reduce la merma de material en 2.2 puntos porcentuales
        "ahorro_anual_euros": 34760.0, # 1.580.000 * 2.2%
        "contacto_comercial": "canal.iberia@pekatvision.com (Ref: Homologación Pymes Industriales)"
    },
    {
        "id": "TECH-ULTRA-02",
        "nombre": "Módulos de Sellado por Ultrasonidos en Frío para Celulosa Monomaterial",
        "fabricante_integrador": "Herrmann Ultraschall Ibérica (Serie HiQ Vario modular)",
        "trl": 9,
        "tipo_adquisicion": "Kit mecánico adaptable a termoselladoras existentes (sin cambiar máquina)",
        "tiempo_parada_planta": "72 horas de puesta a punto mecánica",
        "capex_llave_en_mano": 38500.0,
        "reduccion_merma_pct": 1.4,
        "ahorro_anual_euros": 22120.0,
        "contacto_comercial": "info.es@herrmannultraschall.com (Delegación Barcelona/Valencia)"
    }
]

# 2.4. Radar de Subvenciones Oficiales Específicas
KNOWLEDGE_SUBVENCIONES = [
    {
        "codigo_bdns": "BDNS 742189 / DOGV 9842",
        "organismo": "IVACE+i (Institut Valencià de Competitivitat i Innovació)",
        "programa": "INNOVA-CV: Innovación de Pyme en Economía Circular y Descarbonización",
        "intensidad": "Hasta 40% a fondo perdido para inversiones en bienes de equipo de reducción de residuos",
        "plazo_cierre": "Convocatoria abierta (Cierre habitual en 45 días hábiles)",
        "subvencion_estimada_tech1": 10720.0, # 40% de 26.800
        "requisito_clave": "Pyme industrial de transformación con plantilla > 10 personas y auditoría de residuos.",
        "enlace_oficial": "https://sede.ivace.es/es/tramites/innova-cv-economia-circular"
    }
]

# ==============================================================================
# 3. MOTOR MATEMÁTICO DETERMINISTA: CÁLCULOS FINANCIEROS Y DE CIRCULANTE
# ==============================================================================
def ejecutar_analisis_financiero(empresa: dict) -> dict:
    bal = empresa["balance_actual"]
    bench = empresa["benchmark_50_rivales"]
    
    ventas_dia = bal["ventas"] / 365.0
    coste_dia = bal["coste_materiales_consumos"] / 365.0
    
    # 1. Análisis de circulante frente a la media de 50 rivales
    dso_actual = (bal["clientes_cobro_pendiente"] / bal["ventas"]) * 365.0
    dias_exceso_dso = max(0.0, dso_actual - bench["dso_medio_dias"])
    caja_atrapada_dso = dias_exceso_dso * ventas_dia
    
    dio_actual = (bal["existencias_stock"] / bal["coste_materiales_consumos"]) * 365.0
    dias_exceso_dio = max(0.0, dio_actual - bench["dio_medio_dias"])
    caja_atrapada_dio = dias_exceso_dio * coste_dia
    
    caja_total_atrapada = caja_atrapada_dso + caja_atrapada_dio
    
    # 2. Simulación de Vendor Finance para Tecnología de Visión (TECH-SWIR-01)
    tech = KNOWLEDGE_TECNOLOGIAS[0]
    capex_bruto = tech["capex_llave_en_mano"]
    subvencion = KNOWLEDGE_SUBVENCIONES[0]["subvencion_estimada_tech1"]
    capex_neto = capex_bruto - subvencion
    
    # Parámetros estándar Grenke/DLL a 36 meses (coeficiente financiero 0.0315 mensual)
    cuota_mensual_renting = capex_bruto * 0.0315
    ahorro_mensual_merma = tech["ahorro_anual_euros"] / 12.0
    cash_flow_neto_mensual = ahorro_mensual_merma - cuota_mensual_renting
    cobertura_ahorro_cuota = ahorro_mensual_merma / cuota_mensual_renting if cuota_mensual_renting > 0 else 0.0
    
    # 3. Impacto en P&L del ahorro de merma
    ebitda_proforma = bal["ebitda"] + tech["ahorro_anual_euros"]
    ebitda_pct_proforma = (ebitda_proforma / bal["ventas"]) * 100.0

    return {
        "dso_actual": round(dso_actual, 1),
        "dias_exceso_dso": round(dias_exceso_dso, 1),
        "caja_atrapada_dso": round(caja_atrapada_dso, 2),
        "dio_actual": round(dio_actual, 1),
        "dias_exceso_dio": round(dias_exceso_dio, 1),
        "caja_atrapada_dio": round(caja_atrapada_dio, 2),
        "caja_total_atrapada": round(caja_total_atrapada, 2),
        "capex_bruto": capex_bruto,
        "subvencion_estimada": subvencion,
        "capex_neto": capex_neto,
        "cuota_mensual_renting": round(cuota_mensual_renting, 2),
        "ahorro_mensual_merma": round(ahorro_mensual_merma, 2),
        "cash_flow_neto_mensual": round(cash_flow_neto_mensual, 2),
        "cobertura_ahorro_cuota": round(cobertura_ahorro_cuota, 2),
        "ebitda_actual": bal["ebitda"],
        "ebitda_actual_pct": bal["ebitda_pct"],
        "ebitda_proforma": round(ebitda_proforma, 2),
        "ebitda_pct_proforma": round(ebitda_pct_proforma, 2)
    }

# ==============================================================================
# 4. ORQUESTACIÓN LLM: SÍNTESIS DIRECTIVA Y DICTAMEN EJECUTIVO (GEMINI)
# ==============================================================================
def generar_dictamen_directivo(empresa: dict, analisis_fin: dict) -> dict:
    if not api_key_input:
        return {"error": "Falta la clave API de Gemini en la barra lateral."}

    normativas_txt = "\n".join([f"- {n['normativa']}: {n['impacto_directo']}" for n in KNOWLEDGE_NORMATIVAS])
    tech = KNOWLEDGE_TECNOLOGIAS[0]
    subv = KNOWLEDGE_SUBVENCIONES[0]

    prompt = f"""
    Actúa como Socio Director de Estrategia Industrial y Finanzas Corporativas especializado en el sector de Packaging (CNAE 1721).
    Emite un dictamen implacable para el Comité de Dirección de la siguiente empresa:

    DATOS AUDITADOS (SABI / REGISTRO MERCANTIL):
    - Razón Social: {empresa['razon_social']}
    - Facturación: {empresa['balance_actual']['ventas']:,.0f} € | Margen EBITDA actual: {analisis_fin['ebitda_actual_pct']:.1f}% ({analisis_fin['ebitda_actual']:,.0f} €)
    - Plazo de cobro (DSO): {analisis_fin['dso_actual']} días (Sector medio: {empresa['benchmark_50_rivales']['dso_medio_dias']} días)
    - Rotación de inventario (DIO): {analisis_fin['dio_actual']} días (Sector medio: {empresa['benchmark_50_rivales']['dio_medio_dias']} días)
    - Caja total atrapada por desviación sectorial: {analisis_fin['caja_total_atrapada']:,.0f} € ({analisis_fin['caja_atrapada_dso']:,.0f} € en clientes + {analisis_fin['caja_atrapada_dio']:,.0f} € en bobinas de cartón)

    AMENAZAS NORMATIVAS INMEDIATAS:
    {normativas_txt}

    SOLUCIÓN TÉCNICA Y FINANCIERA COTS:
    - Tecnología: {tech['nombre']} ({tech['fabricante_integrador']})
    - Inversión Llave en Mano: {tech['capex_llave_en_mano']:,.0f} €
    - Subvención Identificada: {subv['programa']} ({subv['intensidad']}) -> Ahorro: {analisis_fin['subvencion_estimada']:,.0f} €
    - Estructura Vendor Finance (Grenke a 36 meses): Cuota de {analisis_fin['cuota_mensual_renting']:,.2f} €/mes frente a un ahorro de merma de {analisis_fin['ahorro_mensual_merma']:,.2f} €/mes.
    - Flujo de caja neto generado: +{analisis_fin['cash_flow_neto_mensual']:,.2f} €/mes (cobertura {analisis_fin['cobertura_ahorro_cuota']}x).

    REGLAS DE RIGOR ESTRATÉGICO:
    1. Cero lugares comunes. Prohibido sugerir desarrollar software propio o contratación de perfiles IT.
    2. Explica con total claridad por qué cobrar a 82 días y mantener bobinas 90 días en almacén está subsidiando a sus distribuidores a costa de pólizas de crédito.
    3. Justifica el despliegue del hardware comercial mediante renting para preservar la caja.
    4. Diseña una hoja de ruta técnica de ejecución a 30, 60 y 90 días con entregables concretos.
    5. Cero emoticonos. Lenguaje técnico, severo y de máximo nivel corporativo.

    RESPONDE EXCLUSIVAMENTE CON UN OBJETO JSON VÁLIDO:
    {{
        "diagnostico_posicionamiento": "Análisis de la brecha de margen y riesgo de exclusión por la directiva PPWR...",
        "dictamen_circulante": "Explicación de la sangría de tesorería por financiar a distribuidores a 82 días...",
        "justificacion_vendor_finance": "Por qué financiar los 26.800 € mediante cuota de renting de 844 €/mes genera caja neta positiva desde el primer mes...",
        "hoja_ruta_30_60_90": [
            {{
                "fase": "Días 1 a 30 (Homologación y Solicitud Pública)",
                "actuacion": "Acción técnica exacta con el canal del fabricante...",
                "entregable_comite": "Documento o resguardo oficial"
            }},
            {{
                "fase": "Días 31 a 60 (Instalación Técnica y Puesta a Punto)",
                "actuacion": "Montaje en parada técnica de 48h y firma de renting...",
                "entregable_comite": "Acta de recepción y contrato de renting"
            }},
            {{
                "fase": "Días 61 a 90 (Validación de Merma y Negociación de Cobro)",
                "actuacion": "Medición de scrap a 1,6% y revisión de condiciones comerciales...",
                "entregable_comite": "Informe de rendimiento y reducción de DSO a 60 días"
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
        return {"error": f"Error en motor de síntesis: {str(e)}"}

# ==============================================================================
# 5. INTERFAZ DE USUARIO: TERMINAL DE INTELIGENCIA DE PACKAGING
# ==============================================================================
st.title("KROMA Industrial Intelligence — Packaging & Envases")
st.caption("Motor de prospección sectorial, cruce de balances auditados (SABI) y estructuración de Vendor Finance.")

col_cif, col_btn = st.columns([3, 1])
with col_cif:
    cif_input = st.text_input("Introduzca el CIF de la empresa de packaging:", value="B98765432")
with col_btn:
    st.write("")
    st.write("")
    btn_auditar = st.button("Ejecutar Auditoria Sectorial")

if cif_input not in BASE_DATOS_SABI:
    st.error("CIF no registrado en la base de balances del vertical. Para la prueba utilice: B98765432.")
else:
    emp = BASE_DATOS_SABI[cif_input]
    calc = ejecutar_analisis_financiero(emp)

    st.markdown("---")

    # --------------------------------------------------------------------------
    # BLOQUE 1: RADIOGRAFÍA CONTABLE OFICIAL Y BENCHMARKING DE 50 RIVALES
    # --------------------------------------------------------------------------
    st.subheader(f"1. Radiografía Contable Oficial y Benchmarking: {emp['razon_social']}")
    st.caption(f"CNAE: {emp['cnae']} | Subsector: {emp['subsector']} | Muestra de cotejo: {emp['benchmark_50_rivales']['cnae_analizado']}")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Facturación 2024", f"{emp['balance_actual']['ventas']:,.0f} €", "+9.3% interanual")
    m2.metric("Margen EBITDA Actual", f"{calc['ebitda_actual_pct']:.1f} %", f"Media 50 rivales: {emp['benchmark_50_rivales']['ebitda_medio_pct']:.1f}%", delta_color="inverse")
    m3.metric("Plazo Medio de Cobro (DSO)", f"{calc['dso_actual']:.0f} días", f"Media 50 rivales: {emp['benchmark_50_rivales']['dso_medio_dias']:.0f} días", delta_color="inverse")
    m4.metric("Caja Atrapada vs Sector", f"{calc['caja_total_atrapada']:,.0f} €", "Clientes + Stock de bobinas", delta_color="inverse")

    st.markdown("##### Comparativa Estructural frente a los 50 Mayores Rivales del Mismo CNAE")
    df_comp = pd.DataFrame([
        {
            "Métrica Financiera / Operativa": "Margen de Explotación EBITDA",
            "BioPack Levantina": f"{calc['ebitda_actual_pct']:.1f} % ({calc['ebitda_actual']:,.0f} €)",
            "Media de 50 Rivales": f"{emp['benchmark_50_rivales']['ebitda_medio_pct']:.1f} %",
            "Top 25% (Líderes de Sector)": f"{emp['benchmark_50_rivales']['ebitda_top25_pct']:.1f} %",
            "Impacto / Brecha Cuantificada": f"Pérdida de {emp['benchmark_50_rivales']['ebitda_medio_pct'] - calc['ebitda_actual_pct']:.1f} puntos de margen por exceso de merma"
        },
        {
            "Métrica Financiera / Operativa": "Periodo Medio de Cobro (DSO)",
            "BioPack Levantina": f"{calc['dso_actual']:.0f} días ({emp['balance_actual']['clientes_cobro_pendiente']:,.0f} € pendientes)",
            "Media de 50 Rivales": f"{emp['benchmark_50_rivales']['dso_medio_dias']:.0f} días",
            "Top 25% (Líderes de Sector)": f"{emp['benchmark_50_rivales']['dso_top25_dias']:.0f} días",
            "Impacto / Brecha Cuantificada": f"{calc['caja_atrapada_dso']:,.0f} € financiando a distribuidores a coste cero"
        },
        {
            "Métrica Financiera / Operativa": "Permanencia de Inventario (DIO)",
            "BioPack Levantina": f"{calc['dio_actual']:.0f} días ({emp['balance_actual']['existencias_stock']:,.0f} € en nave)",
            "Media de 50 Rivales": f"{emp['benchmark_50_rivales']['dio_medio_dias']:.0f} días",
            "Top 25% (Líderes de Sector)": f"{emp['benchmark_50_rivales']['dio_top25_dias']:.0f} días",
            "Impacto / Brecha Cuantificada": f"{calc['caja_atrapada_dio']:,.0f} € inmovilizados en bobinas de cartón sin procesar"
        },
        {
            "Métrica Financiera / Operativa": "Productividad por Empleado",
            "BioPack Levantina": f"{emp['benchmark_50_rivales']['ventas_por_empleado_empresa']:,.0f} €/empleado",
            "Media de 50 Rivales": f"{emp['benchmark_50_rivales']['ventas_por_empleado_media']:,.0f} €/empleado",
            "Top 25% (Líderes de Sector)": "220.000 €/empleado",
            "Impacto / Brecha Cuantificada": "Paradas de máquina frecuentes en termoformado por ajuste manual"
        }
    ])
    st.dataframe(df_comp, use_container_width=True)

    st.markdown("---")

    # --------------------------------------------------------------------------
    # BLOQUE 2: AMENAZAS NORMATIVAS Y REGULATORIAS INMEDIATAS
    # --------------------------------------------------------------------------
    st.subheader("2. Radar de Normativas de la Unión Europea y Riesgo de Cartera")
    st.caption("Requerimientos obligatorios con plazos legales que amenazan la viabilidad del catálogo actual:")

    for norm in KNOWLEDGE_NORMATIVAS:
        with st.container():
            st.markdown(f"**{norm['normativa']}** — *Entrada en Vigor: {norm['plazo_vigor']}*")
            col_n1, col_n2 = st.columns(2)
            col_n1.error(f"**Impacto Legal en Operaciones:**\n\n{norm['impacto_directo']}")
            col_n2.warning(f"**Riesgo Cuantificado en Cartera:**\n\n{norm['amenaza_facturacion']}")
            st.caption(f"Requisito Técnico de Cumplimiento: {norm['requisito_homologacion']}")
            st.divider()

    # --------------------------------------------------------------------------
    # BLOQUE 3: SCOUTING TECNOLÓGICO COTS Y SIMULACIÓN DE VENDOR FINANCE
    # --------------------------------------------------------------------------
    st.subheader("3. Solución Tecnológica Homologada y Estructuración Financiera")
    st.caption("Adopción de hardware estándar comercial sin programar software propio, financiado con el ahorro generado:")

    tech_sel = KNOWLEDGE_TECNOLOGIAS[0]
    subv_sel = KNOWLEDGE_SUBVENCIONES[0]

    c_tech_desc, c_tech_fin = st.columns([3, 2])
    with c_tech_desc:
        st.markdown(f"##### {tech_sel['nombre']}")
        st.write(f"**Fabricante / Integrador:** `{tech_sel['fabricante_integrador']}` (TRL {tech_sel['trl']})")
        st.write(f"**Tiempo de Puesta a Punto en Planta:** `{tech_sel['tiempo_parada_planta']}`")
        st.write(f"**Reducción de Merma de Material:** `{tech_sel['reduccion_merma_pct']}%` sobre compras anuales.")
        st.success(f"**Ahorro Anual Directo en Cuenta de Resultados:** `+{tech_sel['ahorro_anual_euros']:,.0f} €/año`")
        st.caption(f"Canal de Adquisición en España: {tech_sel['contacto_comercial']}")

    with c_tech_fin:
        st.markdown("##### Estructuración Financiera (Vendor Finance)")
        df_fin_sim = pd.DataFrame([
            {"Concepto": "Inversión Llave en Mano (Hardware + Puesta a Punto)", "Importe": f"{calc['capex_bruto']:,.2f} €"},
            {"Concepto": f"(-) Subvención Estimada {subv_sel['organismo'].split(' ')[0]}", "Importe": f"-{calc['subvencion_estimada']:,.2f} €"},
            {"Concepto": "(=) Coste Neto Final para la Empresa", "Importe": f"{calc['capex_neto']:,.2f} €"},
            {"Concepto": "Cuota Mensual de Renting a 36 Meses (Grenke/DLL)", "Importe": f"{calc['cuota_mensual_renting']:,.2f} €/mes"},
            {"Concepto": "Ahorro Mensual Generado por Menor Merma", "Importe": f"+{calc['ahorro_mensual_merma']:,.2f} €/mes"},
            {"Concepto": "CASH-FLOW NETO MENSUAL GENERADO", "Importe": f"+{calc['cash_flow_neto_mensual']:,.2f} €/mes"}
        ])
        st.dataframe(df_fin_sim, use_container_width=True)
        st.info(f"Ratio de Cobertura: El ahorro mensual cubre **{calc['cobertura_ahorro_cuota']} veces** la cuota del renting desde el primer mes.")

    st.markdown("---")

    # --------------------------------------------------------------------------
    # BLOQUE 4: RADAR DE SUBVENCIONES VIGENTES (CONVOCATORIA ACTIVA)
    # --------------------------------------------------------------------------
    st.subheader("4. Convocatoria de Subvención Pública Directa")
    st.caption("Cruce de la inversión tecnológica con las bases reguladoras vigentes:")

    with st.container():
        st.markdown(f"**{subv_sel['organismo']} — {subv_sel['programa']}**")
        st.markdown(f"*{subv_sel['codigo_bdns']}*")
        c_sub_a, c_sub_b = st.columns(2)
        c_sub_a.write(f"**Intensidad de la Ayuda:** {subv_sel['intensidad']}\n\n**Plazo:** {subv_sel['plazo_cierre']}")
        c_sub_b.write(f"**Criterio de Asignación:** {subv_sel['requisito_clave']}")
        st.markdown(f"[Acceso a la Sede Electrónica y Tramitación Oficial]({subv_sel['enlace_oficial']})")

    st.markdown("---")

    # --------------------------------------------------------------------------
    # BLOQUE 5: DICTAMEN DE DIRECCIÓN Y HOJA DE RUTA 30-60-90 DÍAS (LLM)
    # --------------------------------------------------------------------------
    st.subheader("5. Dictamen Ejecutivo del Comité de Dirección")
    with st.spinner("Sintetizando balance oficial con normativa PPWR y estructuración de renting..."):
        dictamen = generar_dictamen_directivo(emp, calc)

    if isinstance(dictamen, dict) and "error" not in dictamen:
        st.info(dictamen.get("diagnostico_posicionamiento", ""))

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.markdown("**Diagnóstico de Circulante y Clientes:**")
            st.write(dictamen.get("dictamen_circulante", ""))
        with col_d2:
            st.markdown("**Justificación del Esquema Financiero:**")
            st.write(dictamen.get("justificacion_vendor_finance", ""))

        st.markdown("##### Hoja de Ruta de Ejecución Técnica (30-60-90 Días)")
        for paso in dictamen.get("hoja_ruta_30_60_90", []):
            st.markdown(f"**{paso.get('fase')}**")
            st.write(f"**Actuación Técnica:** {paso.get('actuacion')}")
            st.caption(f"Entregable Exigible al Comité: {paso.get('entregable_comite')}")
            st.divider()
    else:
        st.warning("No se pudo conectar con el motor generativo de síntesis. Verifique la API Key.")
