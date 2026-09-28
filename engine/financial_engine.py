"""
KROMA Enterprise Analytics
Motor determinista de cálculo financiero y modelización de escenarios para CNAE 1721.
Alineado con principios de evidencia: separa datos observados de modelos de sensibilidad.
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
            return "Tramo P75 - P90 (Demora Elevada)"
        else:
            return "Tramo > P90 (Extremo Superior)"

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
        dpo_bench = bench_ind.get("dpo_dias_pago", {"mediana": 60.0})
        ebitda_bench = bench_ind.get("margen_ebitda", {})

        posicion_dso = FinancialEngine.calcular_posicion_distribucion(
            dso, dso_bench["p25"], dso_bench["mediana"], dso_bench["p75"], dso_bench["p90"]
        )
        posicion_dio = FinancialEngine.calcular_posicion_distribucion(
            dio, dio_bench["p25"], dio_bench["mediana"], dio_bench["p75"], dio_bench["p90"]
        )

        # Cálculo riguroso de exceso de Working Capital frente a medianas sectoriales:
        # Exceso Clientes = (DSO actual - DSO mediana) * Ventas diarias
        dias_brecha_dso = max(0.0, dso - dso_bench["mediana"])
        caja_potencial_dso = dias_brecha_dso * ventas_dia

        # Exceso Stock = (DIO actual - DIO mediana) * Coste diario
        dias_brecha_dio = max(0.0, dio - dio_bench["mediana"])
        caja_potencial_dio = dias_brecha_dio * coste_dia

        # Efecto Proveedores frente a mediana sectorial (60 días)
        efecto_proveedores_eur = (dpo - dpo_bench["mediana"]) * coste_dia

        # Capital Circulante Neto Potencialmente Optimizable (Metodología NWC estándar)
        # NWC_actual - NWC_objetivo = (Clientes_actual - Clientes_obj) + (Stock_actual - Stock_obj) - (Prov_actual - Prov_obj)
        circulante_liberable_neto = caja_potencial_dso + caja_potencial_dio - max(0.0, efecto_proveedores_eur)

        # Estimación de toneladas procesadas basada en ratio sectorial de aprovisionamiento
        # Precio medio ponderado bobina virgen/reciclada (~1.300 €/t)
        toneladas_estimadas = coste_materiales / 1300.0 if coste_materiales > 0 else 0.0

        # Rango de exposición RAP Industrial (RD 1055/2022) según tarifas habituales de SCRAP (100 € - 140 €/t)
        rap_rango_min = toneladas_estimadas * 100.0
        rap_rango_max = toneladas_estimadas * 140.0

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
                "dio_mediana": dio_bench["mediana"],
                "dio_p90": dio_bench["p90"],
                "posicion_dio": posicion_dio,
                "dpo_mediana": dpo_bench["mediana"],
                "ebitda_mediana": ebitda_bench["mediana"],
                "ebitda_p75": ebitda_bench["p75"]
            },
            "potencial_circulante": {
                "potencial_dso_eur": round(caja_potencial_dso, 2),
                "potencial_dio_eur": round(caja_potencial_dio, 2),
                "efecto_proveedores_eur": round(efecto_proveedores_eur, 2),
                "circulante_liberable_neto": round(circulante_liberable_neto, 2),
                "dias_brecha_dso": round(dias_brecha_dso, 1),
                "dias_brecha_dio": round(dias_brecha_dio, 1)
            },
            "modelizacion_regulatoria": {
                "toneladas_estimadas": round(toneladas_estimadas, 1),
                "rap_rango_min": round(rap_rango_min, 2),
                "rap_rango_max": round(rap_rango_max, 2)
            }
        }
