"""
KROMA Enterprise Analytics
Motor determinista de cálculo cuantitativo, estrés financiero y exposición regulatoria.
Sector Packaging y Fabricación de Cartón Ondulado (CNAE 1721 / 2222).
"""
from typing import Dict, Any

class FinancialEngine:
    @staticmethod
    def calcular_posicion_distribucion(valor: float, p25: float, mediana: float, p75: float, p90: float) -> str:
        if valor <= p25:
            return "Tramo <= P25 (Cuartil Superior Eficiente)"
        elif valor <= mediana:
            return "Tramo P25 - Mediana"
        elif valor <= p75:
            return "Tramo Mediana - P75"
        elif valor <= p90:
            return "Tramo P75 - P90 (Tercil Superior de Demora)"
        else:
            return "Tramo > P90 (Extremo Superior de la Distribución)"

    @staticmethod
    def calcular_diagnostico_completo(balance: Dict[str, Any], benchmark: Dict[str, Any]) -> Dict[str, Any]:
        ventas = float(balance.get("ventas", 0.0))
        coste_materiales = float(balance.get("coste_materiales_consumos", 0.0))
        ebitda = float(balance.get("ebitda", 0.0))
        clientes = float(balance.get("clientes_cobro_pendiente", 0.0))
        stock = float(balance.get("existencias_stock", 0.0))
        proveedores = float(balance.get("proveedores_deuda", 0.0))
        caja = float(balance.get("tesoreria_disponible", 0.0))
        deuda = float(balance.get("deuda_bancaria_total", 0.0))
        plantilla = int(balance.get("plantilla", 20))

        ebitda_pct = (ebitda / ventas) * 100.0 if ventas > 0 else 0.0
        ventas_dia = ventas / 365.0 if ventas > 0 else 0.0
        coste_dia = coste_materiales / 365.0 if coste_materiales > 0 else 0.0

        # Ratios de rotación del circulante
        dso = (clientes / ventas) * 365.0 if ventas > 0 else 0.0
        dio = (stock / coste_materiales) * 365.0 if coste_materiales > 0 else 0.0
        dpo = (proveedores / coste_materiales) * 365.0 if coste_materiales > 0 else 0.0
        ciclo_caja_dias = dso + dio - dpo
        ventas_empleado = ventas / plantilla if plantilla > 0 else 0.0
        ratio_deuda_ebitda = deuda / ebitda if ebitda > 0 else 99.0

        bench_ind = benchmark.get("indicadores", {})
        dso_bench = bench_ind.get("dso_dias_cobro", {})
        dio_bench = bench_ind.get("dio_dias_inventario", {})
        ebitda_bench = bench_ind.get("margen_ebitda", {})

        posicion_dso = FinancialEngine.calcular_posicion_distribucion(
            dso, dso_bench["p25"], dso_bench["mediana"], dso_bench["p75"], dso_bench["p90"]
        )
        posicion_dio = FinancialEngine.calcular_posicion_distribucion(
            dio, dio_bench["p25"], dio_bench["mediana"], dio_bench["p75"], dio_bench["p90"]
        )

        dias_brecha_dso = max(0.0, dso - dso_bench["mediana"])
        caja_potencial_dso = dias_brecha_dso * ventas_dia

        dias_brecha_dio = max(0.0, dio - dio_bench["mediana"])
        caja_potencial_dio = dias_brecha_dio * coste_dia

        potencial_teorico_total = caja_potencial_dso + caja_potencial_dio

        # Estimación cuantitativa industrial del consumo de materia prima
        # En packaging celulósico, precio medio ponderado bobina virgen/reciclada ~1.300 €/t
        toneladas_procesadas = coste_materiales / 1300.0 if coste_materiales > 0 else 0.0
        tarifa_scrap_tonelada = 120.0  # Cuota media de ecotasa industrial SCRAP (Envalora / Pro Circular)
        impacto_anual_scrap = toneladas_procesadas * tarifa_scrap_tonelada

        # Impuesto al plástico (Ley 7/2022 o Ley Foral a 0,45 €/kg): estimado en un 2,5% de polímero virgen en mix
        toneladas_plastico_virgen = toneladas_procesadas * 0.025
        impacto_impuesto_plastico = toneladas_plastico_virgen * 1000.0 * 0.45

        # Mix en riesgo por PFAS (Reglamento UE 2025/40 Art. 5): estimado en un 30% del catálogo alimentario
        volumen_ventas_riesgo_pfas = ventas * 0.30

        return {
            "ratios_empresa": {
                "ventas": ventas,
                "coste_materiales": coste_materiales,
                "ebitda": ebitda,
                "ebitda_pct": round(ebitda_pct, 2),
                "dso": round(dso, 1),
                "dio": round(dio, 1),
                "dpo": round(dpo, 1),
                "ciclo_caja_dias": round(ciclo_caja_dias, 1),
                "ventas_empleado": round(ventas_empleado, 2),
                "deuda_ebitda": round(ratio_deuda_ebitda, 2),
                "tesoreria": caja
            },
            "benchmark_peer": {
                "dso_p25": dso_bench["p25"],
                "dso_mediana": dso_bench["mediana"],
                "dso_p75": dso_bench["p75"],
                "dso_p90": dso_bench["p90"],
                "posicion_dso": posicion_dso,
                "dio_p25": dio_bench["p25"],
                "dio_mediana": dio_bench["mediana"],
                "dio_p75": dio_bench["p75"],
                "dio_p90": dio_bench["p90"],
                "posicion_dio": posicion_dio,
                "ebitda_mediana": ebitda_bench["mediana"],
                "ebitda_p75": ebitda_bench["p75"]
            },
            "potencial_circulante": {
                "potencial_dso_eur": round(caja_potencial_dso, 2),
                "potencial_dio_eur": round(caja_potencial_dio, 2),
                "potencial_teorico_total": round(potencial_teorico_total, 2),
                "dias_brecha_dso": round(dias_brecha_dso, 1),
                "dias_brecha_dio": round(dias_brecha_dio, 1)
            },
            "cuantificacion_regulatoria": {
                "toneladas_procesadas": round(toneladas_procesadas, 1),
                "impacto_anual_scrap": round(impacto_anual_scrap, 2),
                "impacto_impuesto_plastico": round(impacto_impuesto_plastico, 2),
                "volumen_ventas_riesgo_pfas": round(volumen_ventas_riesgo_pfas, 2),
                "coste_regulatorio_directo_anual": round(impacto_anual_scrap + impacto_impuesto_plastico, 2)
            }
        }

    @staticmethod
    def simular_escenario_tecnologico_dinamico(
        capex_bruto: float, 
        coste_materiales_anual: float, 
        tasa_recuperacion_merma: float = 0.022, 
        pct_subvencion: float = 0.40, 
        plazo_meses: int = 36
    ) -> Dict[str, Any]:
        subvencion_proyectada = capex_bruto * pct_subvencion
        inversion_neta_proyectada = capex_bruto - subvencion_proyectada
        
        coeficiente_renting = 0.0315 if plazo_meses == 36 else 0.0245
        cuota_mensual_estimada = capex_bruto * coeficiente_renting
        
        ahorro_anual_estimado = coste_materiales_anual * tasa_recuperacion_merma
        ahorro_mensual_teorico = ahorro_anual_estimado / 12.0
        diferencial_mensual_proyectado = ahorro_mensual_teorico - cuota_mensual_estimada

        return {
            "capex_bruto": capex_bruto,
            "subvencion_proyectada": round(subvencion_proyectada, 2),
            "inversion_neta_proyectada": round(inversion_neta_proyectada, 2),
            "cuota_mensual_estimada": round(cuota_mensual_estimada, 2),
            "ahorro_mensual_teorico": round(ahorro_mensual_teorico, 2),
            "diferencial_mensual_proyectado": round(diferencial_mensual_proyectado, 2),
            "pct_merma_modelizado": round(tasa_recuperacion_merma * 100, 1),
            "base_consumo_anual": coste_materiales_anual
        }
