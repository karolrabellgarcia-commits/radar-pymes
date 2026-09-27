"""
Motor analítico financiero determinista para pymes industriales.
Calcula ratios, percentiles frente al benchmark de 50 rivales y potencial de caja liberable.
"""
from typing import Dict, Any

class FinancialEngine:
    @staticmethod
    def calcular_percentil(valor: float, p25: float, mediana: float, p75: float, p90: float) -> str:
        if valor <= p25:
            return "Percentil <= P25 (Cuartil Superior Eficiente)"
        elif valor <= mediana:
            return "Entre P25 y Mediana (Rango Medio Alto)"
        elif valor <= p75:
            return "Entre Mediana y P75 (Rango Medio Bajo)"
        elif valor <= p90:
            return "Entre P75 y P90 (Tercil Crítico)"
        else:
            return "Percentil > P90 (Extremo Superior de Riesgo)"

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

        posicion_dso = FinancialEngine.calcular_percentil(
            dso, dso_bench["p25"], dso_bench["mediana"], dso_bench["p75"], dso_bench["p90"]
        )
        posicion_dio = FinancialEngine.calcular_percentil(
            dio, dio_bench["p25"], dio_bench["mediana"], dio_bench["p75"], dio_bench["p90"]
        )

        dias_exceso_dso = max(0.0, dso - dso_bench["mediana"])
        caja_potencial_clientes = dias_exceso_dso * ventas_dia

        dias_exceso_dio = max(0.0, dio - dio_bench["mediana"])
        caja_potencial_stock = dias_exceso_dio * coste_dia

        total_potencial_caja = caja_potencial_clientes + caja_potencial_stock

        return {
            "ratios_empresa": {
                "ventas": ventas,
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
                "potencial_clientes": round(caja_potencial_clientes, 2),
                "potencial_stock": round(caja_potencial_stock, 2),
                "total_potencial_liberable": round(total_potencial_caja, 2),
                "dias_brecha_dso": round(dias_exceso_dso, 1),
                "dias_brecha_dio": round(dias_exceso_dio, 1)
            }
        }

    @staticmethod
    def simular_vendor_finance(capex_bruto: float, ahorro_anual: float, pct_subvencion: float, plazo_meses: int = 36) -> Dict[str, Any]:
        subvencion_estimada = capex_bruto * pct_subvencion
        coste_neto_adquisicion = capex_bruto - subvencion_estimada
        
        coeficiente = 0.0315 if plazo_meses == 36 else 0.0245
        cuota_mensual = capex_bruto * coeficiente
        ahorro_mensual = ahorro_anual / 12.0
        cash_flow_neto_mensual = ahorro_mensual - cuota_mensual
        cobertura_servicio = ahorro_mensual / cuota_mensual if cuota_mensual > 0 else 0.0
        payback_meses = (capex_bruto / ahorro_anual) * 12.0 if ahorro_anual > 0 else 999.0

        return {
            "capex_bruto": capex_bruto,
            "subvencion_estimada": round(subvencion_estimada, 2),
            "coste_neto_adquisicion": round(coste_neto_adquisicion, 2),
            "cuota_mensual_renting": round(cuota_mensual, 2),
            "ahorro_mensual": round(ahorro_mensual, 2),
            "cash_flow_neto_mensual": round(cash_flow_neto_mensual, 2),
            "cobertura_servicio_cuota": round(cobertura_servicio, 2),
            "payback_meses": round(payback_meses, 1),
            "cash_flow_positivo_inmediato": cash_flow_neto_mensual > 0
        }
