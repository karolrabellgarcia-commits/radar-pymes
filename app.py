import os
import sys
import json
from datetime import datetime
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
    .evidence-tag {
        font-size: 0.75rem;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        margin-right: 6px;
    }
    .tag-registral { background-color: #e3f2fd; color: #0d47a1; }
    .tag-calculado { background-color: #e8f5e9; color: #1b5e20; }
    .tag-modelo { background-color: #fff3e0; color: #e65100; }
    .tag-alerta { background-color: #ffebee; color: #b71c1c; }
    .executive-card {
        background-color: #f8f9fa;
        border-left: 5px solid #1565c0;
        padding: 16px;
        margin-bottom: 16px;
        border-radius: 4px;
        color: #212121;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Configuración de Entidad")
    st.caption("Protocolo Activo: Outside-In Scan (CNAE 1721 - Fabricación de papel y cartón ondulado)")
    st.divider()
    st.markdown("**Taxonomía de Evidencia:**")
    st.markdown("- <span class='evidence-tag tag-registral'>REGISTRAL</span> Cuentas anuales oficiales", unsafe_allow_html=True)
    st.markdown("- <span class='evidence-tag tag-calculado'>DERIVADO</span> Ratio matemático directo", unsafe_allow_html=True)
    st.markdown("- <span class='evidence-tag tag-modelo'>MODELO</span> Hipótesis sectorial / Escenario", unsafe_allow_html=True)
    st.markdown("- <span class='evidence-tag tag-alerta'>VALIDAR</span> Requiere contraste en planta", unsafe_allow_html=True)

def cargar_base_datos():
    ruta_base = os.path.dirname(__file__)
    with open(os.path.join(ruta_base, "data", "benchmark_sabi_1721.json"), "r", encoding="utf-8") as f:
        benchmark = json.load(f)
    return benchmark

EMPRESAS_REGISTRADAS = {
    "B98765432": {
        "cif": "B98765432",
        "razon_social": "BioPack Levantina de Envases S.L.",
        "cnae": "1721 - Fabricación de papel y cartón ondulado",
        "subsector": "Envases microcanal y bandejas celulósicas",
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
        "cnae": "1721 - Fabricación de papel y cartón ondulado",
        "subsector": "Cajas de cartón ondulado pesado y embalaje industrial",
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
    }
}

st.title("KROMA Enterprise — Outside-In Intelligence Scan")
st.caption("Diagnóstico Financiero, Benchmark Sectorial y Mapa de Exposición Regulatoria | CNAE 1721")

col_cif, col_modo = st.columns([2, 2])
with col_cif:
    cif_ingresado = st.text_input("Identificador Fiscal (CIF) a Auditar:", value="B98765432").strip().upper()
with col_modo:
    empresa_detectada = EMPRESAS_REGISTRADAS.get(cif_ingresado)
    if empresa_detectada:
        st.success(f"Entidad localizada: **{empresa_detectada['razon_social']}** ({empresa_detectada['comunidad_autonoma']})")
    else:
        st.warning("CIF no indexado. Introduce datos de balance depositados a continuación:")

if not empresa_detectada:
    with st.expander("Parámetros Contables Registrales (Modo Cualquier CIF)", expanded=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            razon_custom = st.text_input("Razón Social:", "Empresa de Packaging S.L.")
            comunidad_custom = st.selectbox("Comunidad Autónoma:", ["Comunidad Valenciana", "Comunidad Foral de Navarra", "Cataluña", "Murcia", "Andalucía", "Madrid", "País Vasco", "Otra"])
            ventas_custom = st.number_input("Cifra de Negocios (EUR):", value=4000000.0, step=50000.0)
            coste_mat_custom = st.number_input("Consumo Aprovisionamientos (EUR):", value=1900000.0, step=50000.0)
        with col_f2:
            ebitda_custom = st.number_input("EBITDA (EUR):", value=350000.0, step=20000.0)
            clientes_custom = st.number_input("Deudores Comerciales (Clientes):", value=850000.0, step=20000.0)
            stock_custom = st.number_input("Existencias (Stock):", value=450000.0, step=20000.0)
        with col_f3:
            prov_custom = st.number_input("Proveedores Deuda:", value=380000.0, step=20000.0)
            deuda_cp = st.number_input("Deuda Bancaria Corto Plazo:", value=220000.0, step=20000.0)
            deuda_lp = st.number_input("Deuda Bancaria Largo Plazo:", value=400000.0, step=20000.0)
            plantilla_custom = st.number_input("Plantilla Media:", value=25, step=1)

    es_foral = "Navarra" in comunidad_custom or "País Vasco" in comunidad_custom
    empresa_activa = {
        "cif": cif_ingresado,
        "razon_social": razon_custom,
        "cnae": "1721 - Fabricación de papel y cartón ondulado",
        "subsector": "Transformación de cartón y envases",
        "comunidad_autonoma": comunidad_custom,
        "territorio_foral": es_foral,
        "plantilla": plantilla_custom,
        "balance": {
            "ventas": ventas_custom,
            "coste_materiales_consumos": coste_mat_custom,
            "personal": 1000000.0,
            "gastos_explotacion_opex": 750000.0,
            "ebitda": ebitda_custom,
            "clientes_cobro_pendiente": clientes_custom,
            "existencias_stock": stock_custom,
            "proveedores_deuda": prov_custom,
            "tesoreria_disponible": 90000.0,
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
        benchmark = cargar_base_datos()
    except Exception as e:
        st.error(f"Error cargando base de datos: {str(e)}")
        st.stop()

    balance_activo = empresa_activa["balance"]
    fin_data = FinancialEngine.calcular_diagnostico_completo(balance_activo, benchmark)
    ratios = fin_data["ratios_empresa"]
    peer = fin_data["benchmark_peer"]
    circ = fin_data["potencial_circulante"]
    reg = fin_data["modelizacion_regulatoria"]

    deuda_cp = balance_activo.get("deuda_bancaria_corto_plazo", balance_activo["deuda_bancaria_total"] * 0.40)
    deuda_lp = balance_activo.get("deuda_bancaria_largo_plazo", balance_activo["deuda_bancaria_total"] * 0.60)
    deuda_neta = max(0.0, balance_activo["deuda_bancaria_total"] - ratios["tesoreria"])
    ratio_dfn_ebitda = round(deuda_neta / ratios["ebitda"], 2) if ratios["ebitda"] > 0 else 99.0

    st.markdown("---")

    # =========================================================================
    # 1. RADIOGRAFÍA FINANCIERA Y CIRCULANTE
    # =========================================================================
    st.subheader(f"1. Radiografía Financiera y Capital Circulante: {empresa_activa['razon_social']}")
    st.caption("Cuentas anuales depositadas frente a distribución de 50 empresas de referencia (CNAE 1721).")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cifra Neta Negocios", f"{ratios['ventas']:,.0f} EUR", "Dato Registral", delta_color="off")
    c2.metric("EBITDA Contable", f"{ratios['ebitda']:,.0f} EUR", f"Margen: {ratios['ebitda_pct']}%", delta_color="off")
    c3.metric("Ciclo de Caja (CCC)", f"{ratios['ciclo_caja_dias']} días", "DSO + DIO - DPO", delta_color="off")
    c4.metric("DFN / EBITDA", f"{ratio_dfn_ebitda}x", f"Deuda CP: {deuda_cp:,.0f} EUR", delta_color="off")

    st.markdown("##### Posición de la Entidad frente a la Cohorte de Comparación (SABI 50 Empresas)")
    df_dist = pd.DataFrame([
        {
            "Métrica Financiera": "Periodo Medio Cobro (DSO)*",
            "Dato Auditado": f"{ratios['dso']} días",
            "Mediana Sectorial": f"{peer['dso_mediana']} días",
            "Desviación": f"+{circ['dias_brecha_dso']} días",
            "Exceso Teórico en Balance": f"{circ['potencial_dso_eur']:,.0f} EUR",
            "Clasificación": peer["posicion_dso"]
        },
        {
            "Métrica Financiera": "Permanencia Stock (DIO)",
            "Dato Auditado": f"{ratios['dio']} días",
            "Mediana Sectorial": f"{peer['dio_mediana']} días",
            "Desviación": f"+{circ['dias_brecha_dio']} días",
            "Exceso Teórico en Balance": f"{circ['potencial_dio_eur']:,.0f} EUR",
            "Clasificación": peer["posicion_dio"]
        },
        {
            "Métrica Financiera": "Pago a Proveedores (DPO)",
            "Dato Auditado": f"{ratios['dpo']} días",
            "Mediana Sectorial": f"{peer['dpo_mediana']} días",
            "Desviación": f"{ratios['dpo'] - peer['dpo_mediana']:+.1f} días",
            "Exceso Teórico en Balance": f"-{circ['efecto_proveedores_eur']:,.0f} EUR (Financia)",
            "Clasificación": "Financiación Operativa"
        }
    ])
    st.dataframe(df_dist, use_container_width=True, hide_index=True)

    st.info(f"""
    **Análisis de Capital Circulante Neto (NWC):**
    - **Capital circulante potencialmente optimizable:** **~{circ['circulante_liberable_neto']:,.0f} EUR** (cálculo metodológico neto: Exceso Clientes + Exceso Stock - Efecto Proveedores respecto a medianas).
    - **(*) Cautela de IVA sobre DSO:** El DSO calculado sobre ventas netas puede sobreestimar el plazo económico si el saldo de clientes incluye IVA repercutido. Bajo el supuesto de que todo el saldo devengue el 21%, el ajuste teórico sería de aproximadamente -14 días.
    - **Restricciones operativas de planta:** La brecha de existencias suele reflejar lotes mínimos de compra (MOQ) de bobina y stock de seguridad exigido por clientes industriales.
    """)

    st.markdown("---")

    # =========================================================================
    # 2. ESCENARIOS DE SENSIBILIDAD DEL MARGEN (STRESS TEST)
    # =========================================================================
    st.subheader("2. Escenarios de Sensibilidad: Variación del Precio de Materia Prima")
    st.caption("Modelización estática sobre base de aprovisionamiento según nivel de repercusión (pass-through) a cliente.")

    consumo_base = balance_activo["coste_materiales_consumos"]
    ebitda_base = ratios["ebitda"]

    col_st1, col_st2 = st.columns([1, 3])
    with col_st1:
        incremento_coste_pct = st.selectbox("Variación Coste Bobina:", [3, 5, 10], index=1)
    
    coste_adicional_bruto = consumo_base * (incremento_coste_pct / 100.0)

    df_stress = pd.DataFrame([
        {
            "Escenario de Repercusión": "Escenario A: Pass-through 0% (Absorción íntegra en margen)",
            "Sobrecoste Asumido": f"+{coste_adicional_bruto:,.0f} EUR",
            "EBITDA Resultante": f"{max(0, ebitda_base - coste_adicional_bruto):,.0f} EUR",
            "Impacto sobre EBITDA": f"-{(coste_adicional_bruto / ebitda_base) * 100:.1f}%"
        },
        {
            "Escenario de Repercusión": "Escenario B: Pass-through 50% (Traslado parcial con retraso contractual)",
            "Sobrecoste Asumido": f"+{coste_adicional_bruto * 0.5:,.0f} EUR",
            "EBITDA Resultante": f"{max(0, ebitda_base - (coste_adicional_bruto * 0.5)):,.0f} EUR",
            "Impacto sobre EBITDA": f"-{((coste_adicional_bruto * 0.5) / ebitda_base) * 100:.1f}%"
        },
        {
            "Escenario de Repercusión": "Escenario C: Pass-through 100% (Indexación total a índice papel)",
            "Sobrecoste Asumido": "0 EUR (Repercutido)",
            "EBITDA Resultante": f"{ebitda_base:,.0f} EUR",
            "Impacto sobre EBITDA": "0.0% (Margen protegido)"
        }
    ])
    st.dataframe(df_stress, use_container_width=True, hide_index=True)

    st.markdown("---")

    # =========================================================================
    # 3. MAPA DE EXPOSICIÓN REGULATORIA (PPWR, RAP Y FISCALIDAD)
    # =========================================================================
    st.subheader(f"3. Mapa de Exposición Regulatoria y Cumplimiento ({empresa_activa['comunidad_autonoma']})")
    st.caption("Cruce normativo europeo y estatal: hechos jurídicos exigibles frente a hipótesis de planta.")

    df_reg = pd.DataFrame([
        {
            "Marco Normativo": "RD 1055/2022 (RAP Envases Comerciales)",
            "Ámbito Legal Estricto": "Obligación de adhesión a SCRAP (Envalora, Pro Circular, etc.) y financiación de gestión de residuos comerciales e industriales.",
            "Modelo de Exposición": f"Estimación base: ~{reg['toneladas_estimadas']:,.0f} t material procesado. Exposición bruta estimada: {reg['rap_rango_min']:,.0f} € - {reg['rap_rango_max']:,.0f} €/año.",
            "Validación Requerida en Planta": "Comprobar inscripción en Registro MITERD y si la cuota se factura desglosada o se absorbe en coste."
        },
        {
            "Marco Normativo": "Reglamento (UE) 2025/40 (PPWR) Art. 5",
            "Ámbito Legal Estricto": "Prohibición de puesta en mercado de envases en contacto con alimentos con PFAS por encima de los límites de corte (25 ppb dirigido / 250 ppb total).",
            "Modelo de Exposición": "Afectación condicionada a referencias que incorporen barrera antigrasa o química fluorada en catálogo alimentario.",
            "Validación Requerida en Planta": "Exigir Declaraciones de Conformidad (DoC) y ensayos analíticos certificados a los suministradores de bobina."
        },
        {
            "Marco Normativo": "Reglamento (UE) 2025/40 (PPWR) Art. 24",
            "Ámbito Legal Estricto": "Máximo 50% de espacio vacío exigible exclusivamente a operadores de envase agrupado, transporte y e-commerce.",
            "Modelo de Exposición": "No aplica de forma general a envases de venta primaria. Riesgo limitado a cajas logísticas sobredimensionadas.",
            "Validación Requerida en Planta": "Auditar si los clientes de transporte exigen rediseño dimensional en formatos estándar multipropósito."
        },
        {
            "Marco Normativo": "Ley 7/2022 (Impuesto Envases de Plástico)",
            "Ámbito Legal Estricto": "Tipo impositivo de 0,45 €/kg sobre el plástico no reciclado contenido en envases no reutilizables.",
            "Modelo de Exposición": "Sujeción condicionada a la condición jurídica de fabricante/importador y gramaje de film virgen no reciclado.",
            "Validación Requerida en Planta": "Certificados UNE-EN 15343 de suministradores de film para acreditar exención por contenido reciclado."
        }
    ])
    st.dataframe(df_reg, use_container_width=True, hide_index=True)

    st.markdown("---")

    # =========================================================================
    # 4. AGENDA DE CONTROL Y VALIDACIÓN PREVIA PARA DIRECCIÓN
    # =========================================================================
    st.subheader(f"4. Agenda de Diligencia Previa y Control: {empresa_activa['razon_social']}")
    st.caption("Puntos de contraste recomendados para el equipo directivo antes de comités de dirección o procesos de auditoría.")

    st.markdown(f"""
    <div class="executive-card">
        <h4>PUNTO 1: Política de Repercusión de la Contribución RAP (RD 1055/2022)</h4>
        <p><strong>Cuestión Clave:</strong> Bajo una estimación de ~{reg['toneladas_estimadas']:,.0f} toneladas anuales procesadas, la contribución a un sistema colectivo (SCRAP) representa un importe modelizado de entre <strong>{reg['rap_rango_min']:,.0f} EUR y {reg['rap_rango_max']:,.0f} EUR anuales</strong>.</p>
        <p><strong>Acción de Control Interno:</strong> Verificar con el departamento de administración y comercial si la contribución al SCRAP se identifica separadamente en factura o si se está absorbiendo involuntariamente en el margen bruto de las operaciones comerciales.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="executive-card">
        <h4>PUNTO 2: Blindaje de Suministros por Restricción PFAS (Reglamento UE 2025/40)</h4>
        <p><strong>Cuestión Clave:</strong> El Artículo 5 del Reglamento (UE) 2025/40 establece límites estrictos (25 ppb / 250 ppb) para envases en contacto con alimentos grasos y húmedos.</p>
        <p><strong>Acción de Control Interno:</strong> Instruir a la dirección técnica para auditar las Declaraciones de Conformidad (DoC) de los proveedores de papel y cartón con recubrimiento barrera, identificando qué referencias dependen de tratamientos fluorados para anticipar alternativas homologadas.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="executive-card">
        <h4>PUNTO 3: Gestión Contractual del Capital Circulante y Clientes Clave</h4>
        <p><strong>Cuestión Clave:</strong> La brecha de DSO de <strong>+{circ['dias_brecha_dso']} días</strong> respecto a la mediana del sector (59 días) representa un volumen de tesorería inmovilizado de <strong>{circ['potencial_dso_eur']:,.0f} EUR</strong>.</p>
        <p><strong>Acción de Control Interno:</strong> Analizar la concentración de saldos con la gran distribución para evaluar si el coste financiero de un eventual anticipo de facturas resulta asumible frente a la política de negociación de plazos de pago de las cuentas clave.</p>
    </div>
    """, unsafe_allow_html=True)

    # =========================================================================
    # BOTÓN DE DESCARGA: DOSSIER ESTRUCTURADO
    # =========================================================================
    st.markdown("---")
    fecha_informe = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    documento_markdown = f"""# KROMA ENTERPRISE — OUTSIDE-IN INTELLIGENCE SCAN
**Protocolo:** Diagnóstico Financiero y Exposición Regulatoria (CNAE 1721)
**Fecha:** {fecha_informe}
**Entidad:** {empresa_activa['razon_social']} (CIF: {empresa_activa['cif']})
**Sede:** {empresa_activa['comunidad_autonoma']} | **Subsector Observable:** {empresa_activa['subsector']}

---

## 1. RADIOGRAFÍA FINANCIERA REGISTRAL
- Cifra Neta de Negocios: {ratios['ventas']:,.0f} EUR
- EBITDA Oficial: {ratios['ebitda']:,.0f} EUR (Margen: {ratios['ebitda_pct']}%)
- Deuda Financiera Neta: {deuda_neta:,.0f} EUR (Ratio DFN/EBITDA: {ratio_dfn_ebitda}x | Corto Plazo: {deuda_cp:,.0f} EUR)
- Ciclo de Conversión de Efectivo (CCC): {ratios['ciclo_caja_dias']} días (DSO: {ratios['dso']} d | DIO: {ratios['dio']} d | DPO: {ratios['dpo']} d)

### Comparación frente a Cohorte de Referencia (50 Empresas CNAE 1721)
- Periodo Medio de Cobro: {ratios['dso']} días (Mediana sectorial: {peer['dso_mediana']} d | Brecha: +{circ['dias_brecha_dso']} d)
- Permanencia de Stock: {ratios['dio']} días (Mediana sectorial: {peer['dio_mediana']} d | Brecha: +{circ['dias_brecha_dio']} d)
- Pago a Proveedores: {ratios['dpo']} días (Mediana sectorial: {peer['dpo_mediana']} d)
- **Capital circulante potencialmente optimizable (NWC neto):** ~{circ['circulante_liberable_neto']:,.0f} EUR

---

## 2. ESCENARIOS DE SENSIBILIDAD DE MARGEN (STRESS TEST BOBINA)
Base de aprovisionamiento auditada: {consumo_base:,.0f} EUR
- Subida 5% con Pass-through 0% (Absorción): Sobrecoste +{consumo_base * 0.05:,.0f} EUR | EBITDA: {max(0, ebitda_base - consumo_base * 0.05):,.0f} EUR (-{((consumo_base * 0.05) / ebitda_base) * 100:.1f}%)
- Subida 5% con Pass-through 50% (Parcial): Sobrecoste +{consumo_base * 0.025:,.0f} EUR | EBITDA: {max(0, ebitda_base - consumo_base * 0.025):,.0f} EUR (-{((consumo_base * 0.025) / ebitda_base) * 100:.1f}%)
- Subida 5% con Pass-through 100% (Indexación): Sobrecoste 0 EUR | Margen protegido

---

## 3. EXPOSICIÓN REGULATORIA Y MARCO DE APLICACIÓN
- **RD 1055/2022 (RAP Comercial):** Adhesión obligatoria a SCRAP. Exposición modelizada sobre ~{reg['toneladas_estimadas']:,.0f} t: entre {reg['rap_rango_min']:,.0f} € y {reg['rap_rango_max']:,.0f} € anuales.
- **Reglamento (UE) 2025/40 Art. 5 (PFAS):** Prohibición en contacto alimentario sujeta a límites de 25 ppb / 250 ppb. Requiere contraste de DoC con suministradores de bobina barrera.
- **Reglamento (UE) 2025/40 Art. 24 (Espacio Vacío):** Máximo 50% de aire aplicable a embalajes agrupados, de transporte y e-commerce (no aplica de forma universal a venta unitaria).
- **Ley 7/2022 (Impuesto Plástico):** 0,45 €/kg sobre polímero no reciclado. Exige certificado UNE-EN 15343 para acreditar exención.

---

## 4. AGENDA DE CONTROL Y VALIDACIÓN INTERNA
1. **Comercial / RAP:** Contrastar si la cuota SCRAP se factura explícitamente o se asume en margen.
2. **Técnica / PFAS:** Auditar certificados DoC de bobinas barrera ante el marco del Reglamento (UE) 2025/40.
3. **Financiera / Circulante:** Evaluar margen de maniobra en plazos de cobro frente a concentración de cuentas clave.

---
*Dossier generado bajo metodología KROMA Outside-In Intelligence. Prohibida su reproducción sin autorización.*
"""

    st.download_button(
        label="📥 Descargar Dossier Estratégico (.md)",
        data=documento_markdown,
        file_name=f"Dossier_KROMA_{empresa_activa['cif']}_{datetime.now().strftime('%Y%m%d')}.md",
        mime="text/markdown",
        use_container_width=True
    )
