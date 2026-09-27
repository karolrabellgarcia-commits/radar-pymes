import json

class DossierGenerator:
    def __init__(self, ai_model):
        self.model = ai_model

    def generar_capitulo_vulnerabilidad(self, empresa: dict, fin_data: dict, normativas: list) -> str:
        prompt = f"""
        Actúa como Socio Director de Auditoría Estratégica Industrial en Packaging (CNAE 1721).
        Redacta el ANÁLISIS DE VULNERABILIDAD NORMATIVA Y AMENAZAS DEL CATÁLOGO ACTUAL.

        EMPRESA: {empresa['razon_social']} | Ventas: {fin_data['ratios_empresa']['ventas']:,.0f} € | Margen EBITDA: {fin_data['ratios_empresa']['ebitda_pct']}%
        Subsector: {empresa['subsector']}

        NORMATIVAS REALES VIGENTES:
        {json.dumps(normativas, ensure_ascii=False, indent=2)}

        Analiza qué productos quedan fuera de mercado por PPWR (Art. 5, 9, 26) y Ley 7/2022. Sé severo, técnico y cuantitativo. Sin emoticonos.
        """
        res = self.model.generate_content(prompt)
        return res.text.strip()

    def generar_capitulo_circulante(self, fin_data: dict, benchmark: dict) -> str:
        ratios = fin_data["ratios_empresa"]
        caja = fin_data["caja_inmovilizada"]

        prompt = f"""
        Actúa como Director de Finanzas Corporativas de Turnaround Industrial.
        Redacta la RADIOGRAFÍA DEL FONDO DE MANIOBRA Y ESTRÉS DE CIRCULANTE.

        DATOS AUDITADOS FRENTE A 50 RIVALES (CNAE 1721):
        - DSO: {ratios['dso']} días vs Sector {benchmark['indicadores']['dso_dias_cobro']['mediana']} días.
        - DIO: {ratios['dio']} días vs Sector {benchmark['indicadores']['dio_dias_inventario']['mediana']} días.
        - Caja atrapada en clientes: {caja['caja_atrapada_clientes']:,.0f} €.
        - Caja inmovilizada en stock: {caja['caja_atrapada_stock']:,.0f} €.
        - TOTAL CAJA INMOVILIZADA: {caja['total_caja_liberable']:,.0f} €.

        Explica cómo la empresa financia gratis a sus clientes a costa de pólizas bancarias. Lenguaje directo y corporativo. Sin emoticonos.
        """
        res = self.model.generate_content(prompt)
        return res.text.strip()

    def generar_hoja_ruta_ejecucion(self, tech_sel: dict, fin_sim: dict, subv_sel: dict) -> list:
        prompt = f"""
        Genera la HOJA DE RUTA DE EJECUCIÓN TÉCNICA A 30, 60, 90 Y 180 DÍAS para implantar:
        Tecnología: {tech_sel['nombre']} ({tech_sel['capex_llave_en_mano']:,.0f} €).
        Financiación: Vendor Finance ({fin_sim['cuota_mensual_renting']} €/mes) frente a ahorro de merma ({fin_sim['ahorro_mensual']} €/mes).
        Subvención: {subv_sel['organismo']} ({fin_sim['subvencion_estimada']:,.0f} €).

        Responde EXCLUSIVAMENTE con un JSON válido con este formato:
        [
          {{
            "periodo": "Fase 1: Días 1 a 30 (Homologación y Solicitud Pública)",
            "actuacion_tecnica": "Acción técnica concreta...",
            "entregable_comite": "Documento o resguardo oficial..."
          }},
          {{
            "periodo": "Fase 2: Días 31 a 60 (Instalación Técnica y Puesta a Punto)",
            "actuacion_tecnica": "Acción en planta...",
            "entregable_comite": "Acta de recepción..."
          }},
          {{
            "periodo": "Fase 3: Días 61 a 90 (Calibración y Control de Scrap)",
            "actuacion_tecnica": "Auditoría de merma...",
            "entregable_comite": "Certificado de reducción..."
          }},
          {{
            "periodo": "Fase 4: Días 91 a 180 (Escalado y Negociación de Cobro)",
            "actuacion_tecnica": "Convergencia de cobros...",
            "entregable_comite": "DSO a 60 días..."
          }}
        ]
        """
        res = self.model.generate_content(prompt)
        t = res.text.strip()
        if t.startswith("```json"):
            t = t[7:]
        if t.startswith("```"):
            t = t[3:]
        if t.endswith("```"):
            t = t[:-3]
        return json.loads(t.strip())
