from typing import Dict, Any

class FinancialEngine:
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
        dso_objetivo = float(bench_ind.get("dso_dias_cobro", {}).get("mediana", 58.0))
        dio_objetivo = float(bench_ind.get("dio_dias_inventario", {}).get("mediana", 32.0))
        ebitda_objetivo = float(bench_ind.get("margen_ebitda", {}).get("mediana", 12.0))
        ebitda_top25 = float(bench_ind.get("margen_ebitda", {}).get("p75_top", 15.0))

        dias_exceso_dso = max(0.0, dso - dso_objetivo)
        caja_atrapada_clientes = dias_exceso_dso * ventas_dia

        dias_exceso_dio = max(0.0, dio - dio_objetivo)
        caja_atrapada_stock = dias_exceso_dio * coste_dia

        caja_total_liberable = caja_atrapada_clientes + caja_atrapada_stock
        brecha_ebitda_pct = ebitda_objetivo - ebitda_pct
        ebitda_no_capturado_anual = max(0.0, (brecha_ebitda_pct / 100.0) * ventas)

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
            "comparativa_benchmark": {
                "dso_sector_mediana": dso_objetivo,
                "dio_sector_mediana": dio_objetivo,
                "ebitda_sector_mediana": ebitda_objetivo,
                "ebitda_sector_top25": ebitda_top25
            },
            "caja_inmovilizada": {
                "caja_atrapada_clientes": round(caja_atrapada_clientes, 2),
                "caja_atrapada_stock": round(caja_atrapada_stock, 2),
                "total_caja_liberable": round(caja_total_liberable, 2),
                "dias_exceso_cobro": round(dias_exceso_dso, 1),
                "dias_exceso_inventario": round(dias_exceso_dio, 1),
                "ebitda_no_capturado_anual": round(ebitda_no_capturado_anual, 2)
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
