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
# 1. CONFIGURACIÓN Y CLIENTE IA (CON CASILLA LATERAL)
# ==============================================================================
st.set_page_config(
    page_title="KROMA TrendRadar | Inteligencia Estratégica e Innovación",
    layout="wide"
)

# Clave por defecto si existe en entorno o secrets
default_key = os.environ.get("GEMINI_API_KEY", "")
if not default_key and "GEMINI_API_KEY" in st.secrets:
    default_key = st.secrets["GEMINI_API_KEY"]

# Barra lateral para introducir la clave
with st.sidebar:
    st.header("🔑 Acceso y Configuración")
    api_key_input = st.text_input(
        "Introduce tu GEMINI_API_KEY:",
        value=default_key,
        type="password",
        help="Obtén tu clave en Google AI Studio (aistudio.google.com)"
    )
    st.caption("Introduce la clave una vez y quedará activa durante toda tu sesión.")

if api_key_input:
    genai.configure(api_key=api_key_input)
    ai_model = genai.GenerativeModel("gemini-1.5-pro-latest")
else:
    ai_model = None

# ==============================================================================
# 2. MOTOR DE PROSPECCIÓN Y RADAR DE TENDENCIAS
# ==============================================================================
def generar_radar_innovacion(perfil: dict) -> dict:
    if not ai_model:
        return {
            "error": "Falta la clave API. Introduce tu GEMINI_API_KEY en la barra lateral izquierda para generar el radar."
        }

    prompt = f"""
    Actúa como Socio Director de una firma global de prospección e inteligencia estratégica (estilo Trendone, Gartner, Board of Innovation).
    Tu misión es realizar un Radar de Tendencias, Scouting Tecnológico y Oportunidades de Innovación Disruptiva para la siguiente pyme:

    PERFIL DEL NEGOCIO:
    - Empresa: {perfil.get('nombre_empresa')}
    - Sector y Nicho Exacto: {perfil.get('sector_nicho')}
    - Propuesta Actual y Clientes: {perfil.get('modelo_actual')}
    - Mayor Fortaleza / Activo Actual: {perfil.get('fortaleza')}
    - Grado de Ambición de Innovación: {perfil.get('ambicion')}
    - Desafío o Amenaza Percibida: {perfil.get('amenaza')}

    INSTRUCCIONES DE RIGOR ESTRATÉGICO:
    - Nada de respuestas genéricas de consultoría básica ni consejos obvios ("usa redes sociales", "haz una web", "usa ChatGPT").
    - Enfócate en tendencias emergentes reales, tecnologías aplicadas concretas a su cadena de valor y nuevos modelos de ingresos.
    - Sé exhaustivo, técnico, inspirador y accionable.

    GENERA EXCLUSIVAMENTE UN OBJETO JSON VÁLIDO CON ESTA ESTRUCTURA (sin bloques markdown de código ```json ni texto adicional):
    {{
        "resumen_vision": "Visión de futuro para esta empresa en los próximos 3 años (1 párrafo denso, ambicioso y directivo)...",
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
                "categoria": "Quick Win / Apuesta Estratégica / Experimento Rápido",
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
        if t.endswith("
