import streamlit as st
import pandas as pd
import io
import os
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
import google.generativeai as genai

# ==============================================================================
# 1. CONFIGURACION Y CLIENTE IA
# ==============================================================================
st.set_page_config(
    page_title="KROMA TrendRadar | Inteligencia Estrategica e Innovacion",
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
    st.caption("La clave se mantiene activa durante toda la sesion.")

ai_model = None
if api_key_input:
    genai.configure(api_key=api_key_input)
    modelos_candidatos = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash"]
    for m_name in modelos_candidatos:
        try:
            ai_model = genai.GenerativeModel(m_name)
            break
        except Exception:
            continue

# ==============================================================================
# 2. MOTOR DE PROSPECCION Y RADAR DE TENDENCIAS
# ==============================================================================
def generar_radar_innovacion(perfil: dict) -> dict:
    if not api_key_input:
        return {
            "error": "Falta la clave API. Introduzca su clave en el panel lateral para iniciar el analisis."
        }

    prompt = f"""
    Actua como Socio Director de una firma global de prospeccion e inteligencia estrategica (metodologia Trendone, Gartner, Board of Innovation).
    Tu mision es elaborar un Radar de Tendencias, Scouting Tecnologico y Oportunidades de Innovacion Disruptiva para la siguiente pyme:

    PERFIL CORPORATIVO:
    - Entidad: {perfil.get('nombre_empresa')}
    - Sector y Nicho Especifico: {perfil.get('sector_nicho')}
    - Propuesta Actual y Segmento de Clientes: {perfil.get('modelo_actual')}
    - Ventaja Competitiva Actual / Fortaleza: {perfil.get('fortaleza')}
    - Nivel de Ambicion Estrategica: {perfil.get('ambicion')}
    - Amenaza de Mercado Identificada: {perfil.get('amenaza')}

    CRITERIOS DE RIGOR ESTRATEGICO:
    - Evita cualquier generalidad o recomendacion superficial (como uso de redes sociales o digitalizacion generica).
    - Centrate en tendencias de mercado emergentes comprobadas, aplicaciones tecnologicas de impacto directo en su cadena de valor y modelos de negocio de alto margen.
    - El tono debe ser analitico, ejecutivo, preciso y cuantitativamente orientativo.
    - No utilices emoticonos ni iconos decorativos en las respuestas.

    RESPONDE EXCLUSIVAMENTE CON UN OBJETO JSON VALIDO CON ESTA ESTRUCTURA EXACTA (sin bloques markdown de codigo ni texto complementario):
    {{
        "resumen_vision": "Sintesis prospectiva sobre la evolucion estrategica de la entidad a tres anos vista...",
        "macrotendencias": [
            {{
                "nombre": "Nombre formal de la tendencia",
                "horizonte": "Inmediato (0-12m) / Medio Plazo (1-3 anos) / Largo Plazo (3-5 anos)",
                "impacto_sector": "Transformacion estructural del entorno competitivo",
                "oportunidad_pyme": "Oportunidad de captura de valor aplicable para esta empresa"
            }},
            {{
                "nombre": "Segunda tendencia",
                "horizonte": "...",
                "impacto_sector": "...",
                "oportunidad_pyme": "..."
            }},
            {{
                "nombre": "Tercera tendencia",
                "horizonte": "...",
                "impacto_sector": "...",
                "oportunidad_pyme": "..."
            }}
        ],
        "tecnologias_aplicadas": [
            {{
                "tecnologia": "Nombre de la tecnologia o solucion de IA",
                "madurez": "Emergente / En Crecimiento / Madura",
                "caso_uso_real": "Caso de aplicacion directa en producto, canal u operaciones",
                "ejemplo_mercado": "Referencia de empresa o entidad pionera a nivel global"
            }},
            {{
                "tecnologia": "Segunda tecnologia",
                "madurez": "...",
                "caso_uso_real": "...",
                "ejemplo_mercado": "..."
            }},
            {{
                "tecnologia": "Tercera tecnologia",
                "madurez": "...",
                "caso_uso_real": "...",
                "ejemplo_mercado": "..."
            }}
        ],
        "nuevos_modelos_negocio": [
            {{
                "concepto": "Denominacion del modelo de negocio",
                "mecanismo_ingreso": "Estructura de monetizacion y origen del margen",
                "ventaja_defensiva": "Barrera de entrada y proteccion frente a competidores"
            }},
            {{
                "concepto": "Segundo modelo",
                "mecanismo_ingreso": "...",
                "ventaja_defensiva": "..."
            }}
        ],
        "matriz_priorizacion": [
            {{
                "iniciativa": "Denominacion del proyecto",
                "categoria": "Ganancia Inmediata / Apuesta Estrategica / Experimento Agil",
                "impacto_negocio": "Alto / Medio / Transformador",
                "complejidad": "Baja / Media / Alta"
            }},
            {{
                "iniciativa": "Segunda iniciativa",
                "categoria": "...",
                "impacto_negocio": "...",
                "complejidad": "..."
            }},
            {{
                "iniciativa": "Tercera iniciativa",
                "categoria": "...",
                "impacto_negocio": "...",
                "complejidad": "..."
            }},
            {{
                "iniciativa": "Cuarta iniciativa",
                "categoria": "...",
                "impacto_negocio": "...",
                "complejidad": "..."
            }}
        ],
        "pilotos_accion": [
            {{
                "plazo": "Fase 1: 30 Dias (Definicion y Prototipado)",
                "accion": "Prueba de concepto de bajo coste y validacion rapida",
                "kpi_exito": "Indicador cuantitativo de validacion"
            }},
            {{
                "plazo": "Fase 2: 90 Dias (Despliegue Controlado)",
                "accion": "Piloto de mercado con clientes cualificados",
                "kpi_exito": "Metrica de traccion inicial"
            }},
            {{
                "plazo": "Fase 3: 180 Dias (Escalado e Integracion)",
                "accion": "Incorporacion al portafolio comercial estandar",
                "kpi_exito": "Metrica de contribucion a ingresos"
            }}
        ]
    }}
    """
    
    modelos_a_probar = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash"]
    ultimo_error = ""
    for nom_mod in modelos_a_probar:
        try:
            m = genai.GenerativeModel(nom_mod)
            res = m.generate_content(prompt)
            t = res.text.strip()
            if t.startswith("```json"):
                t = t[7:]
            if t.startswith("```"):
                t = t[3:]
            if t.endswith("```"):
                t = t[:-3]
            return json.loads(t.strip())
        except Exception as e:
            ultimo_error = str(e)
            continue

    return {"error": f"Error al generar con Gemini: {ultimo_error}"}

# ==============================================================================
# 3. GENERADOR DE DOSSIER EDITORIAL EN PDF
# ==============================================================================
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#0F172A"))
        self.drawString(45, 804, "KROMA TRENDRADAR | DOSSIER DE INTELIGENCIA ESTRATEGICA")
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(45, 796, 550, 796)
        self.line(45, 42, 550, 42)
        self.drawString(45, 30, "INFORME DE INNOVACION Y PROSPECTIVA SECTORIAL - CONFIDENCIAL")
        self.drawRightString(550, 30, f"Pagina {self._pageNumber} de {page_count}")
        self.restoreState()

def generar_pdf_trendradar(perfil: dict, radar: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=45,
        rightMargin=45,
        topMargin=55,
        bottomMargin=55
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=colors.HexColor("#0F172A"), spaceAfter=4)
    sub_style = ParagraphStyle('DocSub', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=11, textColor=colors.HexColor("#64748B"), spaceAfter=10)
    h1 = ParagraphStyle('H1', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10.5, leading=14, textColor=colors.HexColor("#0F172A"), spaceBefore=10, spaceAfter=5)
    body = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor("#334155"), spaceAfter=5)
    callout = ParagraphStyle('Callout', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8.5, leading=12, textColor=colors.HexColor("#1E293B"))

    story = []
    story.append(Paragraph("RADAR DE TENDENCIAS Y HOJA DE RUTA DE INNOVACION", title_style))
    story.append(Paragraph(f"<b>Entidad:</b> {perfil.get('nombre_empresa')} | <b>Sector:</b> {perfil.get('sector_nicho')} | <b>Ambicion:</b> {perfil.get('ambicion')}", sub_style))

    story.append(Paragraph("1. VISION ESTRATEGICA DE FUTURO", h1))
    story.append(Paragraph(radar.get("resumen_vision", ""), callout))
    story.append(Spacer(1, 6))

    story.append(Paragraph("2. RADAR DE MACRO Y MICRO TENDENCIAS SECTORIALES", h1))
    t_tend_data = [["Tendencia", "Horizonte", "Transformacion del Mercado", "Oportunidad para la Entidad"]]
    for item in radar.get("macrotendencias", []):
        t_tend_data.append([
            item.get("nombre", ""),
            item.get("horizonte", ""),
            item.get("impacto_sector", ""),
            item.get("oportunidad_pyme", "")
        ])
    t_tend = Table(t_tend_data, colWidths=[110, 80, 160, 155])
    t_tend.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_tend)
    story.append(Spacer(1, 6))

    story.append(Paragraph("3. SCOUTING TECNOLOGICO Y CASOS DE USO DE IA", h1))
    t_tec_data = [["Tecnologia / IA", "Madurez", "Caso de Uso Aplicado al Negocio", "Benchmark Global"]]
    for item in radar.get("tecnologias_aplicadas", []):
        t_tec_data.append([
            item.get("tecnologia", ""),
            item.get("madurez", ""),
            item.get("caso_uso_real", ""),
            item.get("ejemplo_mercado", "")
        ])
    t_tec = Table(t_tec_data, colWidths=[115, 75, 175, 140])
    t_tec.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_tec)
    story.append(Spacer(1, 6))

    story.append(Paragraph("4. NUEVOS MODELOS DE NEGOCIO Y MONETIZACION", h1))
    for mb in radar.get("nuevos_modelos_negocio", []):
        story.append(Paragraph(f"<b>{mb.get('concepto')}:</b> {mb.get('mecanismo_ingreso')}", body))
        story.append(Paragraph(f"<i>Ventaja defensiva:</i> {mb.get('ventaja_defensiva')}", body))
    story.append(Spacer(1, 4))

    story.append(Paragraph("5. HOJA DE RUTA DE EXPERIMENTACION Y PILOTOS", h1))
    for p in radar.get("pilotos_accion", []):
        story.append(Paragraph(f"<b>{p.get('plazo')}:</b> {p.get('accion')}", body))
        story.append(Paragraph(f"<b>Metrica de Exito (KPI):</b> {p.get('kpi_exito')}", body))

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()

# ==============================================================================
# 4. ENTRADA DE DATOS
# ==============================================================================
st.title("KROMA TrendRadar — Inteligencia de Mercado e Innovacion")
st.caption("Radar de tendencias emergentes, prospeccion tecnologica y nuevos modelos de negocio para pymes.")

with st.expander("Configurar Perfil de la Empresa a Prospectar", expanded=True):
    with st.
