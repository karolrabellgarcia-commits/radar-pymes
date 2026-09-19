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
# 1. CONFIGURACIÓN Y CLIENTE IA
# ==============================================================================
st.set_page_config(
    page_title="KROMA TrendRadar | Inteligencia Estratégica e Innovación",
    layout="wide"
)

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY and "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]

if API_KEY:
    genai.configure(api_key=API_KEY)
    ai_model = genai.GenerativeModel("gemini-1.5-pro-latest")
else:
    ai_model = None

# ==============================================================================
# 2. MOTOR DE PROSPECCIÓN Y RADAR DE TENDENCIAS (GEMINI 1.5 PRO)
# ==============================================================================
def generar_radar_innovacion(perfil: dict) -> dict:
    if not ai_model:
        return {
            "resumen_vision": "Configura tu GEMINI_API_KEY para activar el radar de inteligencia de mercado e innovación.",
            "macrotendencias": [],
            "tecnologias_aplicadas": [],
            "nuevos_modelos_negocio": [],
            "matriz_priorizacion": [],
            "pilotos_accion": []
        }

    prompt = f"""
    Actúa como Socio Director de una agencia de prospección estratégica global de primer nivel (estilo Trendone, Gartner, Board of Innovation).
    Tu misión es realizar un Radar de Tendencias, Scouting Tecnológico y Oportunidades de Innovación Disruptiva para la siguiente pyme:

    PERFIL DEL NEGOCIO:
    - Empresa: {perfil.get('nombre_empresa')}
    - Sector y Nicho Exacto: {perfil.get('sector_nicho')}
    - Modelo Actual y Clientes: {perfil.get('modelo_actual')}
    - Mayor Fortaleza / Activo Actual: {perfil.get('fortaleza')}
    - Grado de Ambición de Innovación: {perfil.get('ambicion')}
    - Desafío o Amenaza Percibida: {perfil.get('amenaza')}

    INSTRUCCIONES DE ALTO NIVEL:
    - Nada de respuestas genéricas de consultoría básica ni consejos obvios ("usa redes sociales", "haz una web", "usa ChatGPT").
    - Enfócate en tendencias emergentes reales, tecnologías aplicadas concretas a su cadena de valor y nuevos modelos de ingresos.
    - Sé exhaustivo, técnico, inspirador y accionable.

    GENERA EXCLUSIVAMENTE UN OBJETO JSON VÁLIDO CON ESTA ESTRUCTURA (sin bloques markdown de código ```json ni texto adicional):
    {{
        "resumen_vision": "Visión de futuro para esta empresa en los próximos 3 años (1 párrafo denso y directivo)...",
        "macrotendencias": [
            {{
                "nombre": "Nombre de la Macro/Micro Tendencia",
                "horizonte": "Inmediato (0-12m) / Medio (1-3 años) / Largo (3-5 años)",
                "impacto_sector": "Cómo transforma las reglas del juego de su mercado",
                "oportunidad_pyme": "Qué oportunidad concreta abre para esta empresa específica"
            }},
            {{
                "nombre": "Segunda Tendencia",
                "horizonte": "...",
                "impacto_sector": "...",
                "oportunidad_pyme": "..."
            }},
            {{
                "nombre": "Tercera Tendencia",
                "horizonte": "...",
                "impacto_sector": "...",
                "oportunidad_pyme": "..."
            }}
        ],
        "tecnologias_aplicadas": [
            {{
                "tecnologia": "Nombre de la Tecnología / Caso de Uso IA",
                "madurez": "Emergente / En Aceleración / Consolidada",
                "caso_uso_real": "Aplicación quirúrgica en sus operaciones, producto o canal de venta",
                "ejemplo_mercado": "Qué startup o empresa puntera ya lo está haciendo en el mundo"
            }},
            {{
                "tecnologia": "Segunda Tecnología",
                "madurez": "...",
                "caso_uso_real": "...",
                "ejemplo_mercado": "..."
            }},
            {{
                "tecnologia": "Tercera Tecnología",
                "madurez": "...",
                "caso_uso_real": "...",
                "ejemplo_mercado": "..."
            }}
        ],
        "nuevos_modelos_negocio": [
            {{
                "concepto": "Nombre del Nuevo Modelo (ej. Servitización, Suscripción B2B, Marketplace, etc.)",
                "mecanismo_ingreso": "Cómo se monetiza y de dónde proviene el margen",
                "ventaja_defensiva": "Por qué blindará al negocio frente a competidores tradicionales"
            }},
            {{
                "concepto": "Segundo Modelo",
                "mecanismo_ingreso": "...",
                "ventaja_defensiva": "..."
            }}
        ],
        "matriz_priorizacion": [
            {{
                "iniciativa": "Nombre de la iniciativa",
                "categoria": "Quick Win (Impacto Alto, Complejidad Baja) / Apuesta Estratégica (Impacto Alto, Complejidad Alta) / Experimento Rápido (Impacto Medio, Complejidad Baja)",
                "impacto_negocio": "Alto / Medio / Radical",
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
                "plazo": "Fase 1: 30 Días (Exploración & Prototipado)",
                "accion": "Experimento de bajo coste y validación rápida...",
                "kpi_exito": "Métrica clave de validación"
            }},
            {{
                "plazo": "Fase 2: 90 Días (Piloto de Mercado)",
                "accion": "Primer lanzamiento controlado con clientes diana...",
                "kpi_exito": "Métrica de tracción inicial"
            }},
            {{
                "plazo": "Fase 3: 180 Días (Escalado & Integración)",
                "accion": "Consolidación en la propuesta comercial principal...",
                "kpi_exito": "Métrica de volumen / facturación"
            }}
        ]
    }}
    """
    try:
        res = ai_model.generate_content(prompt)
        t = res.text.strip()
        if t.startswith("```json"):
            t = t[7:]
        if t.startswith("```"):
            t = t[3:]
        if t.endswith("```"):
            t = t[:-3]
        return json.loads(t.strip())
    except Exception as e:
        return {
            "resumen_vision": f"Error al procesar radar: {str(e)}",
            "macrotendencias": [],
            "tecnologias_aplicadas": [],
            "nuevos_modelos_negocio": [],
            "matriz_priorizacion": [],
            "pilotos_accion": []
        }

# ==============================================================================
# 3. GENERADOR DE DOSSIER EDITORIAL EN PDF (ESTILO TREND REPORT)
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
        self.drawString(45, 804, "KROMA TRENDRADAR | DOSSIER DE INTELIGENCIA ESTRATÉGICA")
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(45, 796, 550, 796)
        self.line(45, 42, 550, 42)
        self.drawString(45, 30, "INFORME DE INNOVACIÓN Y PROSPECTIVA SECTORIAL - CONFIDENCIAL")
        self.drawRightString(550, 30, f"Página {self._pageNumber} de {page_count}")
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
    story.append(Paragraph("RADAR DE TENDENCIAS & HOJA DE RUTA DE INNOVACIÓN", title_style))
    story.append(Paragraph(f"<b>Entidad:</b> {perfil.get('nombre_empresa')} | <b>Sector:</b> {perfil.get('sector_nicho')} | <b>Ambición:</b> {perfil.get('ambicion')}", sub_style))

    # Visión Ejecutiva
    story.append(Paragraph("1. VISIÓN ESTRATÉGICA DE FUTURO", h1))
    story.append(Paragraph(radar.get("resumen_vision", ""), callout))
    story.append(Spacer(1, 6))

    # Macrotendencias
    story.append(Paragraph("2. RADAR DE MACRO & MICRO TENDENCIAS SECTORIALES", h1))
    t_tend_data = [["Tendencia", "Horizonte", "Transformación del Mercado", "Oportunidad para la Empresa"]]
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

    # Tecnologías & IA
    story.append(Paragraph("3. SCOUTING TECNOLÓGICO & CASOS DE USO DE IA", h1))
    t_tec_data = [["Tecnología / IA", "Madurez", "Caso de Uso Aplicado al Negocio", "Benchmark Global"]]
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

    # Modelos de Negocio
    story.append(Paragraph("4. NUEVOS MODELOS DE NEGOCIO & MONETIZACIÓN", h1))
    for mb in radar.get("nuevos_modelos_negocio", []):
        story.append(Paragraph(f"• <b>{mb.get('concepto')}:</b> {mb.get('mecanismo_ingreso')}", body))
        story.append(Paragraph(f"  <i>Ventaja defensiva:</i> {mb.get('ventaja_defensiva')}", body))
    story.append(Spacer(1, 4))

    # Hoja de Ruta de Pilotos
    story.append(Paragraph("5. HOJA DE RUTA DE EXPERIMENTACIÓN & PILOTOS", h1))
    for p in radar.get("pilotos_accion", []):
        story.append(Paragraph(f"• <b>{p.get('plazo')}:</b> {p.get('accion')}", body))
        story.append(Paragraph(f"  <b>Métrica de Éxito (KPI):</b> {p.get('kpi_exito')}", body))

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()

# ==============================================================================
# 4. INTERFAZ STREAMLIT (ÁGIL, DIRECTA Y PRECARGADA)
# ==============================================================================
st.title("KROMA TrendRadar — Inteligencia de Mercado & Innovación")
st.caption("Radar de tendencias, scouting de tecnologías emergentes y diseño de nuevos modelos de negocio para pymes.")

with st.expander("🎯 Configurar Perfil Estratégico de la Empresa (Caso de Innovación Precargado)", expanded=True):
    with st.form("form_radar"):
        col1, col2 = st.columns(2)
        with col1:
            nombre_empresa = st.text_input("Nombre de la Empresa", value="Actiuform Design S.L.")
            sector_nicho = st.text_input("Sector y Nicho Específico", value="Diseño, fabricación y distribución de mobiliario de oficina y contract")
            modelo_actual = st.text_input("Propuesta Actual y Clientes", value="Venta B2B de mobiliario estándar y a medida a través de distribuidores, arquitectos y licitaciones")
        with col2:
            fortaleza = st.text_input("Principal Activo / Fortaleza", value="Capacidad de fabricación flexible propia, red consolidada de arquitectos y control de calidad")
            ambicion = st.selectbox("Grado de Ambición Innovadora", [
                "Disruptiva: Nuevos modelos de negocio, servicios e IA aplicada",
                "Adyacente: Nuevos canales digitales, personalización y sostenibilidad",
                "Incremental: Digitalización de procesos y mejora de catálogo"
            ])
            amenaza = st.text_input("Mayor Amenaza / Desafío", value="Comoditización de precios por importaciones asiáticas y reducción del espacio de oficina tradicional por teletrabajo")

        submit_radar = st.form_submit_button("⚡ Generar Radar de Innovación & Scouting Tecnológico")

# ==============================================================================
# 5. RENDERIZADO INMEDIATO DEL RADAR
# ==============================================================================
perfil_actual = {
    "nombre_empresa": nombre_empresa,
    "sector_nicho": sector_nicho,
    "modelo_actual": modelo_actual,
    "fortaleza": fortaleza,
    "ambicion": ambicion,
    "amenaza": amenaza
}

with st.spinner("Escaneando macrotendencias globales, casos de uso de IA y modelos disruptivos para este nicho..."):
    radar_data = generar_radar_innovacion(perfil_actual)

# Resumen de Visión
st.markdown("---")
st.subheader("🔮 Visión Estratégica de Futuro")
st.info(radar_data.get("resumen_vision", ""))

# Pestañas de Alto Impacto
tab_tend, tab_tech, tab_biz, tab_matrix, tab_road = st.tabs([
    "📡 Radar de Tendencias",
    "🤖 Scouting Tecnológico & IA",
    "💡 Nuevos Modelos de Ingresos",
    "📊 Matriz de Priorización",
    "🚀 Hoja de Ruta de Pilotos"
])

with tab_tend:
    st.write("#### Fuerzas de Mercado que Transformarán su Nicho")
    for t in radar_data.get("macrotendencias", []):
        with st.container():
            st.markdown(f"##### 📌 {t.get('nombre')} — `{t.get('horizonte')}`")
            c_a, c_b = st.columns(2)
            c_a.write(f"**Impacto en el Sector:**\n{t.get('impacto_sector')}")
            c_b.success(f"**Oportunidad Concreta:**\n{t.get('oportunidad_pyme')}")
            st.divider()

with tab_tech:
    st.write("#### Tecnologías Emergentes & Aplicaciones Quirúrgicas de IA")
    for tc in radar_data.get("tecnologias_aplicadas", []):
        with st.container():
            st.markdown(f"##### ⚙️ {tc.get('tecnologia')} — *Madurez: {tc.get('madurez')}*")
            st.write(f"**Caso de Uso en la Empresa:** {tc.get('caso_uso_real')}")
            st.caption(f"🌍 **Benchmark / Quién lo está haciendo:** {tc.get('ejemplo_mercado')}")
            st.divider()

with tab_biz:
    st.write("#### Nuevas Vías de Monetización y Diversificación")
    for mb in radar_data.get("nuevos_modelos_negocio", []):
        with st.container():
            st.markdown(f"##### 💎 {mb.get('concepto')}")
            st.write(f"**Mecanismo de Ingresos:** {mb.get('mecanismo_ingreso')}")
            st.write(f"**Barrera Defensiva (Moat):** {mb.get('ventaja_defensiva')}")
            st.divider()

with tab_matrix:
    st.write("#### Matriz de Iniciativas: Impacto vs. Complejidad")
    df_mat = pd.DataFrame(radar_data.get("matriz_priorizacion", []))
    if not df_mat.empty:
        st.dataframe(df_mat, use_container_width=True)

with tab_road:
    st.write("#### Plan de Acción: De la Idea al Piloto Validado")
    for pl in radar_data.get("pilotos_accion", []):
        st.markdown(f"**{pl.get('plazo')}**")
        st.write(pl.get('accion'))
        st.info(f"🎯 **KPI de Validación:** {pl.get('kpi_exito')}")

st.markdown("---")
# Descarga de PDF Directiva
pdf_bytes = generar_pdf_trendradar(perfil_actual, radar_data)
st.download_button(
    label="📄 Descargar Dossier de Inteligencia & Innovación (PDF)",
    data=pdf_bytes,
    file_name=f"KROMA_TrendRadar_{perfil_actual['nombre_empresa'].replace(' ', '_')}.pdf",
    mime="application/pdf"
)
