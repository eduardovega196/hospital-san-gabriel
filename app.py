"""
app.py - Sistema de Gestión de Insumos Hospitalarios
Plataforma de gestión preventiva con IA para hospitales chilenos.

Requisitos:
    pip install streamlit pandas plotly scikit-learn requests

Uso:
    1. python bbdd.py          (genera la base de datos)
    2. streamlit run app.py    (inicia la aplicación)
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
import os
import requests

# ─────────────────────────────────────────────
# CONFIGURACIÓN INICIAL
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="MedStock · Gestión de Insumos",
    page_icon="assets/favicon.png" if os.path.exists("assets/favicon.png") else None,
    layout="wide",
    initial_sidebar_state="expanded",
)
# ─────────────────────────────────────────────
# CONTROL DE ACCESO (LANDING VS DASHBOARD)
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
# CONTROL DE ACCESO (LANDING VS DASHBOARD)
# ─────────────────────────────────────────────

# Si la URL no tiene "?app=true", mostramos solo el Landing Page
# Si la URL no tiene "?app=true", mostramos solo el Landing Page
if "app" not in st.query_params:
    st.markdown("""
        <style>
            /* 1. Ocultar interfaz nativa de Streamlit */
            [data-testid="stSidebar"], [data-testid="collapsedControl"], header, footer { 
                display: none !important; 
            }
            
            /* 2. Forzar fondo oscuro sin bloquear el scroll */
            html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
                background-color: #050d1f !important;
                padding: 0 !important;
                margin: 0 !important;
            }
            
            .block-container {
                padding: 0 !important;
                margin: 0 !important;
                max-width: 100% !important;
                width: 100% !important;
            }
            
            /* 3. Posición absoluta para el iframe */
            /* 3. Posición FIJA para anclar el iframe directamente a los bordes de la pantalla */
            iframe {
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                width: 100vw !important;
                height: 100vh !important;
                border: none !important;
                margin: 0 !important;
                padding: 0 !important;
                background-color: #050d1f !important;
                z-index: 1; /* Nos aseguramos de que el iframe esté en el fondo */
            }
            
            /* ─── BOTÓN FLOTANTE NATIVO ─── */
            .btn-flotante-container {
                position: fixed;
                top: 25px;
                right: 35px;
                z-index: 999999;
            }
            .btn-flotante {
                background-color: #8DC63F;
                color: #122860 !important;
                padding: 0.8rem 1.8rem;
                text-decoration: none !important;
                font-family: 'Montserrat', sans-serif;
                font-weight: 800;
                font-size: 0.85rem;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                border-radius: 50px;
                box-shadow: 0 4px 15px rgba(141,198,63,0.3);
                transition: transform 0.3s, box-shadow 0.3s;
                display: inline-block;
            }
            .btn-flotante:hover {
                transform: scale(1.05);
                box-shadow: 0 8px 25px rgba(141,198,63,0.5);
                color: #122860 !important;
            }

            /* ─── SCROLLBAR OSCURO MODO NUCLEAR ─── */
            /* El asterisco fuerza a cualquier contenedor de Streamlit a obedecer */
            *::-webkit-scrollbar {
                width: 10px !important;
                background-color: #050d1f !important;
            }
            *::-webkit-scrollbar-track {
                background-color: #050d1f !important; 
                border-left: 1px solid rgba(255,255,255,0.02) !important;
            }
            *::-webkit-scrollbar-thumb {
                background-color: #1B3A7A !important; 
                border-radius: 10px !important;
                border: 2px solid #050d1f !important; 
            }
            *::-webkit-scrollbar-thumb:hover {
                background-color: #8DC63F !important; 
            }
        </style>
        
        <div class="btn-flotante-container">
            <a href="?app=true" target="_self" class="btn-flotante">INGRESAR AL DASHBOARD ➔</a>
        </div>
    """, unsafe_allow_html=True)

    # Cargar el contenido del landing original
    landing_path = os.path.join(os.path.dirname(__file__), "landing.html")
    if os.path.exists(landing_path):
        with open(landing_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        import streamlit.components.v1 as components
        components.html(html_content, scrolling=True)
    else:
        st.error("No se encontró landing.html")

    st.stop()

# =======================================================
# SI EL CÓDIGO PASA DE AQUÍ, ES PORQUE EL USUARIO YA 
# ESTÁ EN EL DASHBOARD (?app=true)
# =======================================================
# ─────────────────────────────────────────────
# ESTILOS GLOBALES
# ─────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');

/* ── Variables — paleta Clínica Las Condes ──── */
:root {
    --navy:       #1B3A7A;
    --navy-mid:   #254d9e;
    --navy-dark:  #122860;
    --lime:       #8DC63F;
    --lime-dark:  #6fa32e;
    --lime-lt:    #F1F8E6;
    --accent:     #1B3A7A;
    --accent-lt:  #E8EEFA;
    --danger:     #C0392B;
    --danger-lt:  #FDEEEC;
    --warn:       #E67E22;
    --warn-lt:    #FEF4EC;
    --border:     #DDE3EE;
    --text:       #1A2640;
    --muted:      #5E708A;
    --bg:         #F5F7FB;
    --white:      #FFFFFF;
    --radius:     5px;

    /* ── Sistema tipográfico Montserrat ── */
    --font:           'Montserrat', sans-serif;
    --fw-regular:     400;
    --fw-medium:      500;
    --fw-semibold:    600;
    --fw-bold:        700;
    --fw-extrabold:   800;
}

/* ── Reset / Base ───────────────────────────── */
html, body, [class*="css"] {
    font-family: var(--font);
    color: var(--text);
    background: var(--bg);
    font-weight: var(--fw-regular);
    font-size: 14px;
    -webkit-font-smoothing: antialiased;
}

/* ── Sidebar ────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: var(--navy-dark) !important;
    border-right: none;
}
section[data-testid="stSidebar"] * {
    color: #D6E0F5 !important;
    font-family: var(--font);
    font-size: 0.8rem;
}

/* Logo — grande, bold, mayúsculas */
section[data-testid="stSidebar"] .sidebar-logo {
    color: #FFFFFF !important;
    font-family: var(--font);
    font-size: 1.25rem;
    font-weight: var(--fw-extrabold);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    line-height: 1.2;
    display: block;
    margin-bottom: 0.15rem;
}

/* Subtítulo — pequeño, medium, mayúsculas */
section[data-testid="stSidebar"] .sidebar-sub {
    color: #A0B9DE !important;
    font-size: 0.62rem;
    font-weight: var(--fw-medium);
    text-transform: uppercase;
    letter-spacing: 0.15em;
    display: block;
    margin-bottom: 1.4rem;
}

/* Ítems del menú — medium, mayúsculas */
section[data-testid="stSidebar"] .stRadio label {
    padding: 0.5rem 0.75rem;
    border-radius: var(--radius);
    transition: background 0.15s, color 0.15s;
    display: block;
    color: #D6E0F5 !important;
    border-left: 3px solid transparent;
    font-weight: var(--fw-medium);
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.07);
    color: #FFFFFF !important;
    border-left-color: var(--lime);
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.15) !important;
    margin: 1rem 0;
}

/* Etiquetas de sección sidebar — bold, mayúsculas, pequeño */
section[data-testid="stSidebar"] .sidebar-section-label {
    color: #8AB4F8 !important;
    font-size: 0.6rem;
    font-weight: var(--fw-bold);
    text-transform: uppercase;
    letter-spacing: 0.15em;
    display: block;
    margin-bottom: 0.5rem;
}

/* Tarjetas de estado */
section[data-testid="stSidebar"] .sidebar-stat {
    background: rgba(255,255,255,0.05);
    border-left: 3px solid rgba(255,255,255,0.1);
    border-radius: 0 var(--radius) var(--radius) 0;
    padding: 0.6rem 0.8rem;
    margin-bottom: 0.4rem;
}
section[data-testid="stSidebar"] .sidebar-stat-num {
    font-size: 1.4rem;
    font-weight: var(--fw-extrabold);
    color: #FFFFFF !important;
    line-height: 1;
    display: block;
    letter-spacing: -0.02em;
}
section[data-testid="stSidebar"] .sidebar-stat-label {
    font-size: 0.65rem;
    font-weight: var(--fw-regular);
    color: #A0B9DE !important;
    display: block;
    margin-top: 0.15rem;
    letter-spacing: 0.02em;
}
section[data-testid="stSidebar"] .sidebar-stat.danger { border-left-color: #E57373; }
section[data-testid="stSidebar"] .sidebar-stat.danger .sidebar-stat-num { color: #FFCDD2 !important; }
section[data-testid="stSidebar"] .sidebar-stat.warn   { border-left-color: var(--lime); }
section[data-testid="stSidebar"] .sidebar-stat.warn   .sidebar-stat-num { color: #D4EDAA !important; }

section[data-testid="stSidebar"] .stSelectbox * {
    color: #1A2640 !important;
    font-family: var(--font);
}

/* ── Page header ────────────────────────────── */
.page-header {
    padding: 1.4rem 0 1.1rem 0;
    margin-bottom: 1.4rem;
    border-bottom: 2px solid var(--navy);
}
.page-header .page-badge {
    display: inline-block;
    background: var(--lime);
    color: #FFFFFF;
    font-size: 0.6rem;
    font-weight: var(--fw-bold);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    margin-bottom: 0.6rem;
}
.page-header h1 {
    font-family: var(--font);
    font-size: 1.45rem;
    font-weight: var(--fw-extrabold);
    color: var(--navy);
    margin: 0 0 0.25rem 0;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}
.page-header p {
    color: var(--muted);
    font-size: 0.8rem;
    font-weight: var(--fw-regular);
    margin: 0;
    letter-spacing: 0.01em;
}

/* ── Section label — bold, mayúsculas ────────── */
.section-label {
    font-size: 0.65rem;
    font-weight: var(--fw-bold);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--navy);
    margin-bottom: 0.75rem;
    padding-bottom: 0.45rem;
    border-bottom: 2px solid var(--lime);
    display: block;
}

/* ── KPI cards ──────────────────────────────── */
.kpi-card {
    background: var(--white);
    border: 1px solid var(--border);
    border-top: 3px solid var(--navy);
    border-radius: var(--radius);
    padding: 1.1rem 1.25rem 1rem;
    position: relative;
}
.kpi-card.danger { border-top-color: var(--danger); }
.kpi-card.warn   { border-top-color: var(--warn);   }
.kpi-card.ok     { border-top-color: var(--lime);   }

.kpi-number {
    font-size: 2rem;
    font-weight: var(--fw-extrabold);
    line-height: 1;
    color: var(--navy);
    letter-spacing: -0.03em;
    display: block;
}
.kpi-number.danger { color: var(--danger); }
.kpi-number.warn   { color: var(--warn); }
.kpi-number.ok     { color: var(--lime-dark); }

.kpi-label {
    font-size: 0.62rem;
    font-weight: var(--fw-bold);
    color: var(--muted);
    margin-top: 0.4rem;
    display: block;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* ── Alert rows ─────────────────────────────── */
.alert-row {
    background: var(--white);
    border: 1px solid var(--border);
    border-left: 4px solid var(--navy);
    border-radius: var(--radius);
    padding: 0.7rem 1rem;
    margin-bottom: 0.45rem;
    font-size: 0.8rem;
    font-weight: var(--fw-regular);
    display: flex;
    align-items: baseline;
    gap: 0.5rem;
    flex-wrap: wrap;
    line-height: 1.5;
}
.alert-row.danger { border-left-color: var(--danger); background: var(--danger-lt); }
.alert-row.warn   { border-left-color: var(--warn);   background: var(--warn-lt);   }
.alert-row.ok     { border-left-color: var(--lime);   background: var(--lime-lt);   }
.alert-row strong { font-weight: var(--fw-semibold); }

/* Tags de alerta — bold, mayúsculas, píldora */
.alert-tag {
    display: inline-block;
    font-size: 0.58rem;
    font-weight: var(--fw-bold);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    white-space: nowrap;
}
.alert-tag.danger { background: #FADDDA; color: var(--danger); }
.alert-tag.warn   { background: #FAE8D5; color: #A04000; }
.alert-tag.ok     { background: #D8EDBC; color: #4A6B1A; }
.alert-tag.info   { background: var(--accent-lt); color: var(--navy); }

/* ── FEFO box ───────────────────────────────── */
.fefo-box {
    background: var(--accent-lt);
    border: 1px solid #C0CEED;
    border-left: 4px solid var(--navy);
    border-radius: var(--radius);
    padding: 0.9rem 1.1rem;
    font-size: 0.8rem;
    font-weight: var(--fw-regular);
    margin-bottom: 1rem;
    color: var(--text);
    line-height: 1.7;
}
.fefo-box strong {
    color: var(--navy);
    font-weight: var(--fw-semibold);
}

/* ── Chat ───────────────────────────────────── */
.chat-user {
    background: var(--navy);
    color: #D6E0F5;
    padding: 0.7rem 1rem;
    border-radius: 10px 10px 2px 10px;
    margin: 0.6rem 0 0.6rem 20%;
    font-size: 0.82rem;
    font-weight: var(--fw-medium);
    line-height: 1.6;
}
.chat-bot {
    background: var(--white);
    border: 1px solid var(--border);
    border-left: 3px solid var(--lime);
    color: var(--text);
    padding: 0.7rem 1rem;
    border-radius: 10px 10px 10px 2px;
    margin: 0.6rem 20% 0.6rem 0;
    font-size: 0.82rem;
    font-weight: var(--fw-regular);
    line-height: 1.7;
}

/* ── Streamlit overrides ────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 2px solid var(--navy);
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    font-family: var(--font);
    font-size: 0.72rem;
    font-weight: var(--fw-semibold);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 0.6rem 1.3rem;
    color: var(--muted);
    border: none;
    background: transparent;
}
.stTabs [aria-selected="true"] {
    color: #FFFFFF !important;
    background: var(--lime) !important;
    border-radius: var(--radius) var(--radius) 0 0;
}

.stButton > button[kind="primary"] {
    font-family: var(--font);
    font-size: 0.75rem;
    font-weight: var(--fw-semibold);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    background: var(--navy);
    border: none;
    border-radius: 20px;
    padding: 0.55rem 1.4rem;
    color: #FFFFFF;
}
.stButton > button[kind="primary"]:hover { background: var(--navy-mid); }

.stButton > button:not([kind="primary"]) {
    font-family: var(--font);
    font-size: 0.75rem;
    font-weight: var(--fw-medium);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    border: 1.5px solid var(--border);
    border-radius: 20px;
    padding: 0.5rem 1.2rem;
    color: var(--navy);
}
.stButton > button:not([kind="primary"]):hover {
    border-color: var(--navy);
    background: var(--accent-lt);
}

div[data-testid="stMetric"] {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 0.8rem 1rem;
}
div[data-testid="stMetricValue"] {
    font-family: var(--font) !important;
    font-size: 1.5rem !important;
    font-weight: var(--fw-extrabold) !important;
    color: var(--navy) !important;
    letter-spacing: -0.02em;
}
div[data-testid="stMetricLabel"] {
    font-family: var(--font) !important;
    font-size: 0.62rem !important;
    font-weight: var(--fw-bold) !important;
    color: var(--muted) !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.stTextInput input, .stSelectbox > div, .stMultiSelect > div {
    font-family: var(--font) !important;
    font-size: 0.82rem !important;
    font-weight: var(--fw-regular) !important;
}

.stTextInput label, .stSelectbox label,
.stMultiSelect label, .stNumberInput label {
    font-family: var(--font) !important;
    font-size: 0.65rem !important;
    font-weight: var(--fw-bold) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: var(--navy) !important;
}

.stDataFrame {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    font-family: var(--font) !important;
    font-size: 0.78rem !important;
}

footer, #MainMenu { visibility: hidden; height: 0; }
.block-container { padding-top: 1.5rem !important; }

[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
}

/* ═══════════════════════════════════════════════════════════
   FIX ÍCONOS: restaurar la fuente Material Symbols de Streamlit.
   Las reglas font-family:Montserrat (incl. el "*" del sidebar)
   sobreescribían esta fuente y los íconos salían como texto
   (keyboard_double_arrow_left, keyboard_arrow_down, etc.).
   ═══════════════════════════════════════════════════════════ */
[data-testid="stIconMaterial"],
span[data-testid="stIconMaterial"],
section[data-testid="stSidebar"] [data-testid="stIconMaterial"],
[data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"],
[data-testid="stExpanderIcon"] {
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
    font-feature-settings: 'liga' !important;
    -webkit-font-feature-settings: 'liga' !important;
    font-weight: normal !important;
    letter-spacing: normal !important;
    text-transform: none !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# INICIALIZACIÓN
# ─────────────────────────────────────────────

DB_PATH = "hospital_insumos.db"

def verificar_bbdd():
    if not os.path.exists(DB_PATH):
        from bbdd import generar_base_de_datos
        generar_base_de_datos(n_registros=2000, db_path=DB_PATH)

verificar_bbdd()

try:
    from bbdd import (
        cargar_insumos, cargar_historial, cargar_movimientos,
        cargar_consumo_combinado,
        registrar_movimiento, registrar_ajuste, get_kpis, UBICACIONES
    )
except ImportError:
    st.error("No se puede importar bbdd.py. Ambos archivos deben estar en la misma carpeta.")
    st.stop()


# ─────────────────────────────────────────────
# CACHÉ
# ─────────────────────────────────────────────

@st.cache_data(ttl=60)
def obtener_insumos():     return cargar_insumos()

@st.cache_data(ttl=120)
def obtener_historial():   return cargar_historial()

@st.cache_data(ttl=60)
def obtener_consumo():     return cargar_consumo_combinado()

@st.cache_data(ttl=60)
def obtener_movimientos(): return cargar_movimientos()

@st.cache_data(ttl=60)
def obtener_kpis():        return get_kpis()

# Colores Plotly — paleta institucional
PLOT_COLORS = {
    "VENCIDO":  "#C0392B",
    "CRÍTICO":  "#E67E22",
    "ALERTA":   "#F0C040",
    "OK":       "#8DC63F",
    "AGOTADO":  "#922B21",
    "BAJO":     "#F0C040",
    "NORMAL":   "#8DC63F",
    "accent":   "#1B3A7A",
}
PLOT_BLUES = ["#1B3A7A","#2E5AA8","#4A7BC8","#7BA3DC","#AABFE8","#D0DCF2"]


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown('<span class="sidebar-logo">MedStock</span>', unsafe_allow_html=True)
    st.markdown('<span class="sidebar-sub">Gestión de Insumos · v2.0</span>', unsafe_allow_html=True)

    pagina = st.radio(
        "Módulo",
        [
            "Dashboard",
            "Alertas Críticas",
            "Registrar Movimiento",
            "Inventario",
            "Proyección Predictiva",
            "Asistente IA",
            "Movimientos",
        ],
        label_visibility="collapsed",
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<span class="sidebar-section-label">Sesión activa</span>', unsafe_allow_html=True)

    # Lista dinámica de profesionales
    if "profesionales" not in st.session_state:
        st.session_state.profesionales = [
            "Dr. Eduardo Vega",
            "Dr. Félix Fauré",
            "Klga. Jessica Berton",
            "Farm. Christian Norambuena",
            "Enf. Claudia Manquelipe",
        ]

    usuario = st.selectbox(
        "Usuario",
        st.session_state.profesionales,
        label_visibility="collapsed",
    )

    with st.expander("Gestionar profesionales"):
        nuevo = st.text_input("Agregar profesional", placeholder="Ej: Dr. Cristian Ulloa", key="input_nuevo_prof")
        if st.button("Agregar", key="btn_agregar_prof", use_container_width=True):
            nombre = nuevo.strip()
            if nombre and nombre not in st.session_state.profesionales:
                st.session_state.profesionales.append(nombre)
                st.success(f"'{nombre}' agregado.")
                st.rerun()
            elif nombre in st.session_state.profesionales:
                st.warning("Ese profesional ya existe.")
            else:
                st.warning("Escribe un nombre.")

        if len(st.session_state.profesionales) > 1:
            a_eliminar = st.selectbox(
                "Eliminar profesional",
                st.session_state.profesionales,
                key="sel_eliminar_prof",
            )
            if st.button("Eliminar", key="btn_eliminar_prof", use_container_width=True, type="primary"):
                st.session_state.profesionales.remove(a_eliminar)
                st.success(f"'{a_eliminar}' eliminado.")
                st.rerun()

    try:
        kpis = obtener_kpis()
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<span class="sidebar-section-label">Estado del inventario</span>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="sidebar-stat danger">
            <span class="sidebar-stat-num">{kpis['stock_critico']}</span>
            <span class="sidebar-stat-label">Stock crítico o agotado</span>
        </div>
        <div class="sidebar-stat warn">
            <span class="sidebar-stat-num">{kpis['por_vencer_30']}</span>
            <span class="sidebar-stat-label">Vencen en menos de 30 días</span>
        </div>
        <div class="sidebar-stat">
            <span class="sidebar-stat-num">{kpis['vencidos']}</span>
            <span class="sidebar-stat-label">Productos vencidos</span>
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        pass

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        f'<span style="color:#3D5A73;font-size:0.7rem;">'
        f'{datetime.now().strftime("%d %b %Y · %H:%M")}</span>',
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def page_header(badge: str, title: str, subtitle: str):
    st.markdown(f"""
    <div class="page-header">
        <span class="page-badge">{badge}</span>
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def section_label(text: str):
    st.markdown(f'<span class="section-label">{text}</span>', unsafe_allow_html=True)


# ═════════════════════════════════════════════
# MÓDULO 0 · INICIO
# ═════════════════════════════════════════════

# ═════════════════════════════════════════════
# MÓDULO 0 · INICIO
# ═════════════════════════════════════════════

if pagina == "Inicio":
    # 1. CSS para eliminar el padding de Streamlit y hacer el iframe de ancho completo
    st.markdown("""
        <style>
            .block-container {
                padding-top: 0rem !important;
                padding-bottom: 0rem !important;
                padding-left: 0rem !important;
                padding-right: 0rem !important;
                max-width: 100% !important;
            }
            iframe {
                border: none !important;
                display: block;
            }
        </style>
    """, unsafe_allow_html=True)

    # 2. Cargar el HTML
    landing_path = os.path.join(os.path.dirname(__file__), "landing.html")
    if os.path.exists(landing_path):
        with open(landing_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        # Ajustamos el height para que cubra todo el scroll
        components.html(html_content, height=4000, scrolling=True)
    else:
        st.error("No se encontró el archivo landing.html. Asegúrese de que esté en la misma carpeta que app.py.")


# ═════════════════════════════════════════════
# MÓDULO 1 · DASHBOARD
# ═════════════════════════════════════════════

elif pagina == "Dashboard":
    page_header(
        "Resumen general",
        "Dashboard de Control",
        f"Estado del inventario al {datetime.now().strftime('%d de %B de %Y, %H:%M')}",
    )

    df   = obtener_insumos()
    kpis = obtener_kpis()

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <span class="kpi-number">{kpis['total_insumos']:,}</span>
            <span class="kpi-label">Registros totales</span>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card danger">
            <span class="kpi-number danger">{kpis['stock_critico']}</span>
            <span class="kpi-label">Stock crítico / agotado</span>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card danger">
            <span class="kpi-number danger">{kpis['vencidos']}</span>
            <span class="kpi-label">Productos vencidos</span>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="kpi-card warn">
            <span class="kpi-number warn">{kpis['por_vencer_30']}</span>
            <span class="kpi-label">Vencen en &lt; 30 días</span>
        </div>""", unsafe_allow_html=True)
    with c5:
        valor_fmt = f"${kpis['valor_total']/1_000_000:.1f} M"
        st.markdown(f"""
        <div class="kpi-card ok">
            <span class="kpi-number ok">{valor_fmt}</span>
            <span class="kpi-label">Valor inventario (CLP)</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1.2, 1, 1])

    with col_a:
        section_label("Estado de vencimientos")
        conteo_venc = df["Estado_Vencimiento"].value_counts().reset_index()
        conteo_venc.columns = ["Estado", "Cantidad"]
        fig = px.pie(
            conteo_venc, names="Estado", values="Cantidad",
            color="Estado",
            color_discrete_map={k: PLOT_COLORS[k] for k in PLOT_COLORS if k in conteo_venc["Estado"].values},
            hole=0.55,
        )
        fig.update_layout(
            margin=dict(t=10, b=10, l=0, r=0),
            legend=dict(orientation="h", y=-0.12, font_size=11),
            height=240,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_family="Montserrat",
        )
        fig.update_traces(textinfo="percent", textfont_size=11)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        section_label("Estado de stock")
        conteo_stock = df["Estado_Stock"].value_counts().reset_index()
        conteo_stock.columns = ["Estado", "Cantidad"]
        fig2 = px.bar(
            conteo_stock, x="Estado", y="Cantidad",
            color="Estado",
            color_discrete_map={k: PLOT_COLORS.get(k, "#94A3B8") for k in conteo_stock["Estado"]},
        )
        fig2.update_layout(
            margin=dict(t=5, b=5, l=0, r=0),
            showlegend=False, height=240,
            xaxis_title="", yaxis_title="",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_family="Montserrat",
            yaxis=dict(gridcolor="#E5E9EF"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col_c:
        section_label("Distribución por unidad")
        por_ubic = df.groupby("Ubicacion")["Stock_Actual"].sum().reset_index()
        fig3 = px.bar(
            por_ubic.sort_values("Stock_Actual", ascending=True),
            x="Stock_Actual", y="Ubicacion", orientation="h",
            color_discrete_sequence=["#1B3A7A"],
        )
        fig3.update_layout(
            margin=dict(t=5, b=5, l=0, r=0),
            showlegend=False, height=240,
            xaxis_title="", yaxis_title="",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_family="Montserrat",
            xaxis=dict(gridcolor="#E5E9EF"),
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section_label("Stock por categoría y unidad clínica")
    pivot = df.groupby(["Categoria", "Ubicacion"])["Stock_Actual"].sum().reset_index()
    fig4 = px.bar(
        pivot, x="Categoria", y="Stock_Actual", color="Ubicacion",
        barmode="group",
        color_discrete_sequence=PLOT_BLUES,
    )
    fig4.update_layout(
        margin=dict(t=5, b=5), height=280,
        xaxis_title="", yaxis_title="Unidades",
        legend=dict(orientation="h", y=1.08, font_size=11),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_family="Montserrat",
        yaxis=dict(gridcolor="#E5E9EF"),
    )
    st.plotly_chart(fig4, use_container_width=True)


# ═════════════════════════════════════════════
# MÓDULO 2 · ALERTAS CRÍTICAS
# ═════════════════════════════════════════════

elif pagina == "Alertas Críticas":
    page_header(
        "Requieren atención",
        "Alertas Críticas",
        "Productos vencidos, con stock insuficiente o próximos a expirar",
    )

    df = obtener_insumos()
    tab1, tab2, tab3 = st.tabs(["Vencidos", "Stock insuficiente", "Vencen en 30 – 60 días"])

    with tab1:
        vencidos = df[df["Estado_Vencimiento"] == "VENCIDO"].copy()
        vencidos["Días vencido"] = (
            pd.to_datetime(datetime.now().strftime("%Y-%m-%d")) -
            pd.to_datetime(vencidos["Fecha_Vencimiento"])
        ).dt.days
        st.markdown(f"**{len(vencidos)} productos vencidos** deben ser retirados del inventario de forma inmediata.")
        st.markdown("<br>", unsafe_allow_html=True)
        if len(vencidos) > 0:
            st.dataframe(
                vencidos[["ID_Insumo","Nombre_Producto","Categoria","Lote",
                           "Fecha_Vencimiento","Días vencido","Stock_Actual","Ubicacion"]]
                .sort_values("Días vencido", ascending=False),
                use_container_width=True, height=400,
            )
        else:
            st.success("No se registran productos vencidos.")

    with tab2:
        criticos = df[df["Estado_Stock"].isin(["AGOTADO", "CRÍTICO"])].copy()
        criticos["Déficit"] = criticos["Stock_Minimo"] - criticos["Stock_Actual"]
        st.markdown(f"**{len(criticos)} productos** presentan stock por debajo del nivel mínimo de seguridad.")
        st.markdown("<br>", unsafe_allow_html=True)
        peores = criticos.nlargest(10, "Déficit")
        for _, row in peores.iterrows():
            clase = "danger" if row["Estado_Stock"] == "AGOTADO" else "warn"
            tag   = "Agotado" if row["Estado_Stock"] == "AGOTADO" else "Crítico"
            st.markdown(f"""
            <div class="alert-row {clase}">
                <span class="alert-tag {clase}">{tag}</span>
                <strong>{row['Nombre_Producto']}</strong>
                &nbsp;&mdash;&nbsp;
                Stock actual: <strong>{row['Stock_Actual']}</strong> &nbsp;/&nbsp;
                Mínimo: <strong>{row['Stock_Minimo']}</strong> &nbsp;&mdash;&nbsp;
                Déficit: <strong>{int(row['Déficit'])}</strong> unidades &nbsp;|&nbsp;
                {row['Ubicacion']}
            </div>
            """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if len(criticos) > 0:
            st.dataframe(
                criticos[["ID_Insumo","Nombre_Producto","Categoria","Stock_Actual",
                           "Stock_Minimo","Déficit","Ubicacion","Estado_Stock"]]
                .sort_values("Déficit", ascending=False),
                use_container_width=True,
            )

    with tab3:
        alerta60 = df[df["Estado_Vencimiento"].isin(["CRÍTICO", "ALERTA"])].copy()
        alerta60["Días restantes"] = (
            pd.to_datetime(alerta60["Fecha_Vencimiento"]) -
            pd.to_datetime(datetime.now().strftime("%Y-%m-%d"))
        ).dt.days
        st.markdown(f"**{len(alerta60)} productos** vencen en los próximos 60 días.")
        st.markdown("<br>", unsafe_allow_html=True)
        fig = px.histogram(
            alerta60, x="Días restantes", nbins=20,
            color_discrete_sequence=["#E67E22"],
            labels={"Días restantes": "Días hasta vencimiento"},
        )
        fig.update_layout(
            height=240, margin=dict(t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_family="Montserrat",
            yaxis=dict(gridcolor="#E5E9EF"),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(
            alerta60[["ID_Insumo","Nombre_Producto","Categoria","Lote",
                       "Fecha_Vencimiento","Días restantes","Stock_Actual","Ubicacion"]]
            .sort_values("Días restantes"),
            use_container_width=True,
        )


# ═════════════════════════════════════════════
# MÓDULO 3 · TRASLADO A PABELLÓN (FEFO)
# ═════════════════════════════════════════════

elif pagina == "Registrar Movimiento":
    page_header(
        "Método FEFO",
        "Registrar Movimiento",
        "Registre salidas, traslados y entradas. El sistema sugiere el lote que vence primero para reducir mermas.",
    )

    df = obtener_insumos()
    col1, col2 = st.columns([1.5, 1])

    with col1:
        section_label("Registrar movimiento")
        categoria_sel = st.selectbox(
            "Categoría",
            ["Todas"] + sorted(df["Categoria"].unique().tolist())
        )
        df_filtrado   = df if categoria_sel == "Todas" else df[df["Categoria"] == categoria_sel]
        df_disponible = df_filtrado[df_filtrado["Stock_Actual"] > 0]

        nombre_sel = st.selectbox(
            "Producto",
            sorted(df_disponible["Nombre_Producto"].unique().tolist())
        )

        lotes_prod = df_disponible[
            df_disponible["Nombre_Producto"] == nombre_sel
        ].sort_values("Fecha_Vencimiento").reset_index(drop=True)

        if len(lotes_prod) > 0:
            # ── Sugerencia FEFO (registro que vence primero) ──
            primer_lote = lotes_prod.iloc[0]
            dias_venc   = (
                pd.to_datetime(primer_lote["Fecha_Vencimiento"]) -
                pd.to_datetime(datetime.now().strftime("%Y-%m-%d"))
            ).days
            clase_venc = "danger" if dias_venc < 30 else ("warn" if dias_venc < 60 else "info")
            st.markdown(f"""
            <div class="fefo-box">
                <span class="alert-tag {clase_venc}" style="margin-bottom:0.4rem;display:inline-block;">
                    Sugerencia FEFO
                </span><br>
                Lote <strong>{primer_lote['Lote']}</strong> &nbsp;&mdash;&nbsp;
                vence el <strong>{primer_lote['Fecha_Vencimiento']}</strong>
                ({dias_venc} días) &nbsp;&mdash;&nbsp;
                Ubicado en <strong>{primer_lote['Ubicacion']}</strong><br>
                Disponible: <strong>{primer_lote['Stock_Actual']} unidades</strong>
            </div>
            """, unsafe_allow_html=True)

            # ── Selector de registro específico (lote + ubicación) ──
            # Necesario porque un mismo lote puede existir en varias ubicaciones
            opciones_reg = {
                f"Lote {r['Lote']} · {r['Ubicacion']} · {int(r['Stock_Actual'])} disp.": int(r["ID_Insumo"])
                for _, r in lotes_prod.iterrows()
            }
            etiqueta_sel = st.selectbox("Lote / ubicación", list(opciones_reg.keys()))
            id_sel       = opciones_reg[etiqueta_sel]
            registro     = lotes_prod[lotes_prod["ID_Insumo"] == id_sel].iloc[0]
            lote_sel     = registro["Lote"]
            ubic_actual  = registro["Ubicacion"]
            stock_disp   = int(registro["Stock_Actual"])

            tipo_mov = st.selectbox("Tipo de movimiento", ["Traslado", "Salida", "Entrada"])

            # ── Origen / destino según el tipo ──
            if tipo_mov == "Traslado":
                st.caption(f"Origen: **{ubic_actual}** (ubicación actual del lote)")
                destinos = [u for u in UBICACIONES if u != ubic_actual]
                destino_sel = st.selectbox("Destino", destinos)
                mov_origen, mov_destino = ubic_actual, destino_sel
                cantidad = st.number_input(f"Cantidad a trasladar (máx. {stock_disp})", 1, stock_disp, 1)

            elif tipo_mov == "Salida":
                st.caption(f"Origen: **{ubic_actual}** — el insumo sale del inventario (consumo).")
                mov_origen, mov_destino = ubic_actual, "Consumo"
                cantidad = st.number_input(f"Cantidad a entregar (máx. {stock_disp})", 1, stock_disp, 1)

            else:  # Entrada
                st.caption(f"Ingreso de mercadería nueva a **{ubic_actual}**.")
                mov_origen, mov_destino = "Proveedor", ubic_actual
                cantidad = st.number_input("Cantidad recibida", 1, value=1)

            if st.button("Confirmar movimiento", type="primary", use_container_width=True):
                registrar_movimiento(
                    id_insumo=int(id_sel), nombre=nombre_sel, lote=lote_sel,
                    tipo=tipo_mov, cantidad=int(cantidad),
                    origen=mov_origen, destino=mov_destino, usuario=usuario,
                )
                if tipo_mov == "Traslado":
                    st.success(f"Traslado registrado: {cantidad} unidades de {nombre_sel} — {mov_origen} → {mov_destino}")
                elif tipo_mov == "Salida":
                    st.success(f"Salida registrada: {cantidad} unidades de {nombre_sel} desde {mov_origen}")
                else:
                    st.success(f"Entrada registrada: {cantidad} unidades de {nombre_sel} en {mov_destino}")
                st.cache_data.clear()
                st.rerun()

    with col2:
        section_label("Lotes disponibles del producto")
        if nombre_sel and len(lotes_prod) > 0:
            st.dataframe(
                lotes_prod[["Lote","Fecha_Vencimiento","Stock_Actual","Ubicacion","Estado_Vencimiento"]]
                .rename(columns={"Fecha_Vencimiento":"Vencimiento","Stock_Actual":"Stock","Estado_Vencimiento":"Estado"}),
                use_container_width=True, height=360,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    section_label("Distribución multibodega")
    pivot_ubic = df.groupby(["Ubicacion","Categoria"])["Stock_Actual"].sum().reset_index()
    fig = px.sunburst(
        pivot_ubic, path=["Ubicacion","Categoria"], values="Stock_Actual",
        color_discrete_sequence=PLOT_BLUES,
    )
    fig.update_layout(
        height=380, margin=dict(t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font_family="Montserrat",
    )
    st.plotly_chart(fig, use_container_width=True)


# ═════════════════════════════════════════════
# MÓDULO 4 · INVENTARIO
# ═════════════════════════════════════════════

# ═════════════════════════════════════════════
# MÓDULO 4 · INVENTARIO (con CRUD integrado)
# ═════════════════════════════════════════════
# Reemplaza el bloque "elif pagina == 'Inventario':" completo en tu app.py

elif pagina == "Inventario":
    page_header(
        "Consulta y exportación",
        "Inventario",
        "Filtre, busque y exporte el inventario completo de 2.000 registros",
    )

    import sqlite3
    from bbdd import calcular_estado_vencimiento, calcular_estado_stock, UBICACIONES, DB_PATH

    def _recalcular_estados(fecha_venc_str: str, stock_actual: int, stock_minimo: int):
        fecha = datetime.strptime(fecha_venc_str, "%Y-%m-%d")
        ev = calcular_estado_vencimiento(fecha)
        es = calcular_estado_stock(stock_actual, stock_minimo)
        return ev, es

    df = obtener_insumos()

    # ── Filtros ──────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    cat_f  = c1.multiselect("Categoría",    df["Categoria"].unique())
    ubic_f = c2.multiselect("Ubicación",    df["Ubicacion"].unique())
    estv_f = c3.multiselect("Estado Venc.", df["Estado_Vencimiento"].unique())
    ests_f = c4.multiselect("Estado Stock", df["Estado_Stock"].unique())
    buscar = st.text_input("Buscar por nombre de producto", "")

    df_view = df.copy()
    if cat_f:   df_view = df_view[df_view["Categoria"].isin(cat_f)]
    if ubic_f:  df_view = df_view[df_view["Ubicacion"].isin(ubic_f)]
    if estv_f:  df_view = df_view[df_view["Estado_Vencimiento"].isin(estv_f)]
    if ests_f:  df_view = df_view[df_view["Estado_Stock"].isin(ests_f)]
    if buscar:  df_view = df_view[df_view["Nombre_Producto"].str.contains(buscar, case=False, na=False)]

    st.caption(f"{len(df_view)} registros encontrados con los filtros aplicados.")
    st.dataframe(
        df_view[[
            "ID_Insumo","Nombre_Producto","Categoria","Lote","Proveedor",
            "Fecha_Vencimiento","Stock_Actual","Stock_Minimo",
            "Precio_Unitario","Ubicacion","Estado_Vencimiento","Estado_Stock",
        ]],
        use_container_width=True, height=400,
    )

    csv_bytes = df_view.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        "Exportar CSV",
        data=csv_bytes,
        file_name=f"inventario_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════
    # SECCIÓN CRUD — tres expanders independientes
    # ════════════════════════════════════════════════════════════════

    # ── AGREGAR ──────────────────────────────────────────────────────
    with st.expander("Agregar nuevo insumo"):
        st.markdown("<br>", unsafe_allow_html=True)
        a1, a2 = st.columns(2)
        with a1:
            a_nombre    = st.text_input("Nombre del producto *", key="a_nom",
                                        placeholder="Ej: Amoxicilina 250mg")
            a_categoria = st.selectbox("Categoría *", ["Fármaco", "Insumo Quirúrgico", "Implante"], key="a_cat")
            a_lote      = st.text_input("Lote *", key="a_lote", placeholder="Ej: LOT-202506-1234")
            a_proveedor = st.text_input("Proveedor", key="a_prov", placeholder="Ej: CENABAST")
            a_ubicacion = st.selectbox("Ubicación *", UBICACIONES, key="a_ubic")
        with a2:
            a_fecha_venc = st.date_input(
                "Fecha de vencimiento *", key="a_fv",
                value=datetime.now() + timedelta(days=365),
                min_value=datetime(2020, 1, 1).date(),
            )
            a_stock     = st.number_input("Stock actual *",         min_value=0,   value=100,    key="a_st")
            a_stock_min = st.number_input("Stock mínimo *",         min_value=1,   value=20,     key="a_sm")
            a_precio    = st.number_input("Precio unitario (CLP) *",min_value=0.0, value=1000.0,
                                          step=100.0, key="a_pr")
            a_fecha_ing = st.date_input("Fecha de ingreso", value=datetime.now().date(), key="a_fi")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Agregar insumo", type="primary", key="btn_agregar"):
            if not a_nombre.strip():
                st.error("El nombre del producto es obligatorio.")
            elif not a_lote.strip():
                st.error("El lote es obligatorio.")
            else:
                fv_str = a_fecha_venc.strftime("%Y-%m-%d")
                ev, es = _recalcular_estados(fv_str, int(a_stock), int(a_stock_min))
                conn = sqlite3.connect(DB_PATH)
                cur  = conn.cursor()
                cur.execute("SELECT COALESCE(MAX(ID_Insumo), 0) + 1 FROM insumos")
                next_id = cur.fetchone()[0]
                cur.execute("""
                    INSERT INTO insumos
                    (ID_Insumo, Nombre_Producto, Categoria, Lote, Proveedor,
                     Fecha_Vencimiento, Stock_Actual, Stock_Minimo, Precio_Unitario,
                     Ubicacion, Estado_Vencimiento, Estado_Stock, Fecha_Ingreso)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    next_id, a_nombre.strip(), a_categoria, a_lote.strip(),
                    a_proveedor.strip() or "Sin proveedor", fv_str,
                    int(a_stock), int(a_stock_min), round(float(a_precio), 2),
                    a_ubicacion, ev, es, a_fecha_ing.strftime("%Y-%m-%d"),
                ))
                conn.commit()
                conn.close()
                st.cache_data.clear()
                st.success(f"✅ **{a_nombre}** agregado con ID {next_id}.")
                st.rerun()

    # ── EDITAR ───────────────────────────────────────────────────────
    with st.expander("Editar insumo existente"):
        st.markdown("<br>", unsafe_allow_html=True)

        bc1, bc2 = st.columns([3, 1])
        busq_e  = bc1.text_input("Buscar por nombre", key="busq_e",
                                  placeholder="Escribe parte del nombre...")
        id_e    = bc2.number_input("O buscar por ID", min_value=0, value=0, step=1, key="id_e")

        if id_e > 0:
            df_e = df[df["ID_Insumo"] == id_e]
        elif busq_e:
            df_e = df[df["Nombre_Producto"].str.contains(busq_e, case=False, na=False)]
        else:
            df_e = pd.DataFrame()

        if len(df_e) == 0 and (busq_e or id_e > 0):
            st.warning("No se encontraron registros.")
        elif len(df_e) > 0:
            if len(df_e) > 1:
                opts_e = {
                    f"[{r['ID_Insumo']}] {r['Nombre_Producto']} — {r['Lote']} ({r['Ubicacion']})": r["ID_Insumo"]
                    for _, r in df_e.iterrows()
                }
                sel_e = st.selectbox("Selecciona el registro:", list(opts_e.keys()), key="sel_e")
                row_e = df[df["ID_Insumo"] == opts_e[sel_e]].iloc[0]
            else:
                row_e = df_e.iloc[0]

            st.caption(f"Editando ID {row_e['ID_Insumo']} · {row_e['Nombre_Producto']}")
            e1, e2 = st.columns(2)
            with e1:
                e_nom  = st.text_input("Nombre",    value=row_e["Nombre_Producto"], key="e_nom")
                e_cat  = st.selectbox("Categoría",
                    ["Fármaco", "Insumo Quirúrgico", "Implante"],
                    index=["Fármaco", "Insumo Quirúrgico", "Implante"].index(row_e["Categoria"])
                          if row_e["Categoria"] in ["Fármaco", "Insumo Quirúrgico", "Implante"] else 0,
                    key="e_cat")
                e_lote = st.text_input("Lote",      value=row_e["Lote"],      key="e_lote")
                e_prov = st.text_input("Proveedor", value=row_e["Proveedor"], key="e_prov")
                e_ubic = st.selectbox("Ubicación",  UBICACIONES,
                    index=UBICACIONES.index(row_e["Ubicacion"]) if row_e["Ubicacion"] in UBICACIONES else 0,
                    key="e_ubic")
            with e2:
                try:
                    fv_def = datetime.strptime(row_e["Fecha_Vencimiento"], "%Y-%m-%d").date()
                except Exception:
                    fv_def = datetime.now().date()
                e_fv  = st.date_input("Fecha vencimiento", value=fv_def, key="e_fv")
                e_st  = st.number_input("Stock actual",  min_value=0,   value=int(row_e["Stock_Actual"]),  key="e_st")
                e_sm  = st.number_input("Stock mínimo",  min_value=1,   value=int(row_e["Stock_Minimo"]),  key="e_sm")
                e_pr  = st.number_input("Precio (CLP)",  min_value=0.0, value=float(row_e["Precio_Unitario"]),
                                        step=100.0, key="e_pr")

            # Motivo del ajuste — solo se usa si cambia el stock actual
            stock_cambia = int(e_st) != int(row_e["Stock_Actual"])
            e_motivo = st.selectbox(
                "Motivo del ajuste de stock (si modificas el stock actual)",
                ["Recuento físico", "Merma / vencimiento", "Rotura / daño", "Corrección de error", "Otro"],
                key="e_motivo",
            )
            if stock_cambia:
                st.caption(
                    f"⚠️ Cambias el stock de {int(row_e['Stock_Actual'])} a {int(e_st)}. "
                    f"Se registrará un movimiento de **Ajuste** con motivo «{e_motivo}»."
                )

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Guardar cambios", type="primary", key="btn_editar"):
                stock_anterior = int(row_e["Stock_Actual"])
                fv_str = e_fv.strftime("%Y-%m-%d")
                ev, es = _recalcular_estados(fv_str, int(e_st), int(e_sm))
                conn = sqlite3.connect(DB_PATH)
                conn.execute("""
                    UPDATE insumos SET
                        Nombre_Producto=?, Categoria=?, Lote=?, Proveedor=?,
                        Ubicacion=?, Fecha_Vencimiento=?, Stock_Actual=?,
                        Stock_Minimo=?, Precio_Unitario=?,
                        Estado_Vencimiento=?, Estado_Stock=?
                    WHERE ID_Insumo=?
                """, (
                    e_nom.strip(), e_cat, e_lote.strip(), e_prov.strip(),
                    e_ubic, fv_str, int(e_st), int(e_sm), round(float(e_pr), 2),
                    ev, es, int(row_e["ID_Insumo"]),
                ))
                conn.commit()
                conn.close()

                # Si el stock cambió, dejar huella como movimiento de Ajuste
                if int(e_st) != stock_anterior:
                    registrar_ajuste(
                        id_insumo=int(row_e["ID_Insumo"]),
                        nombre=e_nom.strip(),
                        lote=e_lote.strip(),
                        ubicacion=e_ubic,
                        stock_anterior=stock_anterior,
                        stock_nuevo=int(e_st),
                        motivo=e_motivo,
                        usuario=usuario,
                    )

                st.cache_data.clear()
                if int(e_st) != stock_anterior:
                    st.success(
                        f"✅ ID {row_e['ID_Insumo']} actualizado. "
                        f"Ajuste de stock registrado en Movimientos ({stock_anterior} → {int(e_st)}, «{e_motivo}»)."
                    )
                else:
                    st.success(f"✅ ID {row_e['ID_Insumo']} actualizado correctamente.")
                st.rerun()

    # ── ELIMINAR ─────────────────────────────────────────────────────
    with st.expander("Eliminar insumo"):
        st.markdown("<br>", unsafe_allow_html=True)

        bd1, bd2 = st.columns([3, 1])
        busq_d  = bd1.text_input("Buscar por nombre", key="busq_d",
                                  placeholder="Escribe parte del nombre...")
        id_d    = bd2.number_input("O buscar por ID", min_value=0, value=0, step=1, key="id_d")

        if id_d > 0:
            df_d = df[df["ID_Insumo"] == id_d]
        elif busq_d:
            df_d = df[df["Nombre_Producto"].str.contains(busq_d, case=False, na=False)]
        else:
            df_d = pd.DataFrame()

        if len(df_d) == 0 and (busq_d or id_d > 0):
            st.warning("No se encontraron registros.")
        elif len(df_d) > 0:
            if len(df_d) > 1:
                opts_d = {
                    f"[{r['ID_Insumo']}] {r['Nombre_Producto']} — {r['Lote']} ({r['Ubicacion']})": r["ID_Insumo"]
                    for _, r in df_d.iterrows()
                }
                sel_d   = st.selectbox("Selecciona el registro:", list(opts_d.keys()), key="sel_d")
                row_d   = df[df["ID_Insumo"] == opts_d[sel_d]].iloc[0]
                id_borrar = int(opts_d[sel_d])
            else:
                row_d     = df_d.iloc[0]
                id_borrar = int(row_d["ID_Insumo"])

            st.markdown(f"""
            <div class="alert-row danger">
                <span class="alert-tag danger">⚠ Confirmar eliminación</span>
                <strong>ID {row_d['ID_Insumo']}</strong> &nbsp;·&nbsp;
                {row_d['Nombre_Producto']} &nbsp;·&nbsp;
                Lote: {row_d['Lote']} &nbsp;·&nbsp;
                Stock: {row_d['Stock_Actual']} ud &nbsp;·&nbsp;
                {row_d['Ubicacion']}
            </div>
            """, unsafe_allow_html=True)

            stock_a_borrar = int(row_d["Stock_Actual"])
            if stock_a_borrar > 0:
                d_motivo = st.selectbox(
                    "Motivo de la baja (este producto tiene stock que saldrá del sistema)",
                    ["Vencido y descartado", "Producto dado de baja", "Error de registro", "Otro"],
                    key="d_motivo",
                )
                st.caption(
                    f"⚠️ Al eliminar, {stock_a_borrar} unidades saldrán del inventario. "
                    f"Se registrará una **Baja** en Movimientos con motivo «{d_motivo}»."
                )
            else:
                d_motivo = None

            confirmar_d = st.checkbox(
                "Confirmo que deseo eliminar este registro de forma permanente",
                key="chk_del"
            )
            if confirmar_d:
                if st.button("Eliminar insumo", type="primary", key="btn_del"):
                    # Si el registro tiene stock, dejar huella como movimiento de Baja
                    # ANTES de borrarlo (la tabla de movimientos guarda nombre/lote como
                    # texto, así que el rastro sobrevive a la eliminación).
                    if stock_a_borrar > 0:
                        registrar_movimiento(
                            id_insumo=id_borrar,
                            nombre=row_d["Nombre_Producto"],
                            lote=row_d["Lote"],
                            tipo="Baja",
                            cantidad=stock_a_borrar,
                            origen=row_d["Ubicacion"],
                            destino="Descarte",
                            usuario=usuario,
                            motivo=f"{d_motivo} (registro eliminado con {stock_a_borrar} ud)",
                        )

                    conn = sqlite3.connect(DB_PATH)
                    conn.execute("DELETE FROM insumos WHERE ID_Insumo = ?", (id_borrar,))
                    conn.commit()
                    conn.close()
                    st.cache_data.clear()
                    if stock_a_borrar > 0:
                        st.success(
                            f"✅ ID {id_borrar} eliminado. "
                            f"Baja de {stock_a_borrar} unidades registrada en Movimientos («{d_motivo}»)."
                        )
                    else:
                        st.success(f"✅ ID {id_borrar} eliminado correctamente.")
                    st.rerun()


# ═════════════════════════════════════════════
# MÓDULO 5 · PROYECCIÓN PREDICTIVA
# ═════════════════════════════════════════════

elif pagina == "Proyección Predictiva":
    page_header(
        "Modelo predictivo",
        "Proyección de Quiebres",
        "Regresión lineal sobre el consumo (base histórica + salidas reales registradas) — anticipa el agotamiento antes de que ocurra",
    )

    try:
        from sklearn.linear_model import LinearRegression
        sklearn_ok = True
    except ImportError:
        sklearn_ok = False
        st.warning("scikit-learn no está instalado. Ejecute: pip install scikit-learn")

    df      = obtener_insumos()
    df_hist = obtener_consumo()

    if sklearn_ok and len(df_hist) > 0:

        df_mov_all = obtener_movimientos()
        n_salidas = int((df_mov_all["Tipo"] == "Salida").sum()) if "Tipo" in df_mov_all.columns else 0
        st.caption(
            f"El modelo combina la base histórica de consumo con **{n_salidas} salidas reales** "
            f"ya registradas. Cada nueva salida que registres se incorpora aquí y reajusta las proyecciones."
        )

        @st.cache_data(ttl=300)
        def calcular_proyecciones():
            resultados = []
            for id_ins in df_hist["ID_Insumo"].unique():
                hist = df_hist[df_hist["ID_Insumo"] == id_ins].sort_values("Fecha_Semana").reset_index(drop=True)
                if len(hist) < 4:
                    continue
                X = np.arange(len(hist)).reshape(-1, 1)
                y = hist["Consumo_Unidades"].values
                model = LinearRegression()
                model.fit(X, y)
                consumo_semanal = max(1, model.predict([[len(hist)]])[0])

                stock_row = df[df["ID_Insumo"] == id_ins]
                if len(stock_row) == 0:
                    continue
                stock_actual = stock_row.iloc[0]["Stock_Actual"]
                nombre       = stock_row.iloc[0]["Nombre_Producto"]
                ubicacion    = stock_row.iloc[0]["Ubicacion"]

                semanas_quiebre = stock_actual / consumo_semanal if consumo_semanal > 0 else 999
                dias_quiebre    = semanas_quiebre * 7
                fecha_quiebre   = datetime.now() + timedelta(days=dias_quiebre)

                resultados.append({
                    "Nombre":             nombre,
                    "Ubicación":          ubicacion,
                    "Stock actual":       stock_actual,
                    "Consumo / semana":   round(consumo_semanal, 1),
                    "Días hasta quiebre": round(dias_quiebre),
                    "Fecha estimada":     fecha_quiebre.strftime("%Y-%m-%d"),
                    "Nivel": (
                        "Urgente" if dias_quiebre <= 7  else
                        "Crítico" if dias_quiebre <= 14 else
                        "Alerta"  if dias_quiebre <= 30 else
                        "Normal"
                    ),
                })
            return pd.DataFrame(resultados).sort_values("Días hasta quiebre")

        df_proy  = calcular_proyecciones()
        urgentes = df_proy[df_proy["Nivel"] == "Urgente"]
        criticos = df_proy[df_proy["Nivel"] == "Crítico"]
        alertas  = df_proy[df_proy["Nivel"] == "Alerta"]

        ca, cb, cc = st.columns(3)
        with ca:
            st.markdown(f"""
            <div class="kpi-card danger">
                <span class="kpi-number danger">{len(urgentes)}</span>
                <span class="kpi-label">Se agotan esta semana</span>
            </div>""", unsafe_allow_html=True)
        with cb:
            st.markdown(f"""
            <div class="kpi-card warn">
                <span class="kpi-number warn">{len(criticos)}</span>
                <span class="kpi-label">Se agotan en 2 semanas</span>
            </div>""", unsafe_allow_html=True)
        with cc:
            st.markdown(f"""
            <div class="kpi-card">
                <span class="kpi-number">{len(alertas)}</span>
                <span class="kpi-label">Se agotan en 30 días</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        section_label("Avisos prioritarios")

        top10 = df_proy[df_proy["Días hasta quiebre"] <= 30].head(10)
        nivel_clase = {"Urgente": "danger", "Crítico": "warn", "Alerta": "warn"}
        for _, row in top10.iterrows():
            clase = nivel_clase.get(row["Nivel"], "info")
            st.markdown(f"""
            <div class="alert-row {clase}">
                <span class="alert-tag {clase}">{row['Nivel']}</span>
                <strong>{row['Nombre']}</strong>
                &nbsp;&mdash;&nbsp;
                A este ritmo de consumo ({row['Consumo / semana']} ud/sem), el stock se agotará
                el <strong>{row['Fecha estimada']}</strong> ({row['Días hasta quiebre']} días).
                Stock actual: <strong>{row['Stock actual']}</strong> &nbsp;|&nbsp; {row['Ubicación']}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        section_label("Tabla de proyecciones")
        st.dataframe(df_proy, use_container_width=True, height=400)

        section_label("Stock actual vs días hasta quiebre")
        fig = px.scatter(
            df_proy[df_proy["Días hasta quiebre"] < 365],
            x="Días hasta quiebre", y="Stock actual",
            color="Nivel", hover_name="Nombre",
            color_discrete_map={
                "Urgente": "#C0392B", "Crítico": "#E67E22",
                "Alerta":  "#F0C040", "Normal":  "#8DC63F",
            },
        )
        fig.add_vline(x=7,  line_dash="dot", line_color="#C0392B", annotation_text="7 d",  annotation_font_size=10)
        fig.add_vline(x=14, line_dash="dot", line_color="#E67E22", annotation_text="14 d", annotation_font_size=10)
        fig.add_vline(x=30, line_dash="dot", line_color="#F0C040", annotation_text="30 d", annotation_font_size=10)
        fig.update_layout(
            height=320, margin=dict(t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_family="Montserrat",
            yaxis=dict(gridcolor="#E5E9EF"),
            xaxis=dict(gridcolor="#E5E9EF"),
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Instale scikit-learn para habilitar el módulo predictivo: pip install scikit-learn")


# ═════════════════════════════════════════════
# MÓDULO 6 · ASISTENTE IA
# ═════════════════════════════════════════════

elif pagina == "Asistente IA":
    page_header(
        "Consulta en lenguaje natural",
        "Asistente de Decisión",
        "Formule preguntas sobre el inventario y obtenga respuestas basadas en los datos actuales",
    )

    with st.expander("Configurar API Key de Google Gemini", expanded=False):
        api_key = st.text_input(
            "API Key",
            type="password",
            placeholder="AIza...",
            help="Obtenga una gratis en aistudio.google.com → Get API Key",
        )
        st.caption("Sin API Key el asistente responde con lógica local. Gemini es gratuito (1.500 consultas/día).")

    df   = obtener_insumos()
    kpis = obtener_kpis()

    criticos_ctx = df[df["Estado_Stock"].isin(["AGOTADO","CRÍTICO"])].head(20)
    vencidos_ctx = df[df["Estado_Vencimiento"] == "VENCIDO"].head(10)
    por_venc_ctx = df[df["Estado_Vencimiento"] == "CRÍTICO"].head(15)

    contexto_bbdd = f"""
Eres un asistente de gestión de insumos hospitalarios. Tienes acceso al inventario actual de un hospital chileno.

RESUMEN DEL INVENTARIO:
- Total de registros: {kpis['total_insumos']}
- Productos con stock crítico/agotado: {kpis['stock_critico']}
- Productos vencidos: {kpis['vencidos']}
- Productos que vencen en menos de 30 días: {kpis['por_vencer_30']}
- Valor total del inventario: ${kpis['valor_total']:,.0f} CLP

TOP PRODUCTOS CON STOCK CRÍTICO O AGOTADO:
{criticos_ctx[['Nombre_Producto','Stock_Actual','Stock_Minimo','Ubicacion','Categoria']].to_string(index=False)}

PRODUCTOS VENCIDOS (muestra):
{vencidos_ctx[['Nombre_Producto','Fecha_Vencimiento','Stock_Actual','Ubicacion']].to_string(index=False)}

PRODUCTOS POR VENCER EN MENOS DE 30 DÍAS:
{por_venc_ctx[['Nombre_Producto','Fecha_Vencimiento','Stock_Actual','Ubicacion']].to_string(index=False)}

Responde siempre en español, de forma clara y directa. Sé conciso pero informativo.
Da recomendaciones prácticas basadas en los datos cuando sea pertinente.
"""

    if "mensajes_chat" not in st.session_state:
        st.session_state.mensajes_chat = []

    section_label("Consultas frecuentes")
    ejemplos = [
        "¿Qué insumos quirúrgicos están agotados?",
        "¿Qué fármacos debo reabastecer esta semana?",
        "¿Cuáles son los productos vencidos?",
        "¿Qué insumos de Pabellón 1 están en estado crítico?",
    ]
    cols_ej = st.columns(len(ejemplos))
    for i, ej in enumerate(ejemplos):
        if cols_ej[i].button(ej, use_container_width=True):
            st.session_state.mensajes_chat.append({"rol": "user", "texto": ej})
            api_key_val = locals().get("api_key", "") or os.environ.get("GEMINI_API_KEY", "")
            if api_key_val and len(api_key_val) > 10:
                with st.spinner("Procesando consulta..."):
                    try:
                        historial_gemini = []
                        for m in st.session_state.mensajes_chat[:-1]:
                            historial_gemini.append({
                                "role": "user" if m["rol"] == "user" else "model",
                                "parts": [{"text": m["texto"]}],
                            })
                        historial_gemini.append({"role": "user", "parts": [{"text": ej}]})
                        response = requests.post(
                            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
                            headers={"Content-Type": "application/json", "x-goog-api-key": api_key_val},
                            json={
                                "contents": [
                                    {"role": "user", "parts": [{"text": contexto_bbdd}]},
                                    {"role": "model", "parts": [{"text": "Entendido, estoy listo para responder consultas sobre el inventario."}]},
                                ] + historial_gemini,
                            },
                            timeout=30,
                        )
                        data = response.json()
                        if "candidates" in data:
                            respuesta_ia = data["candidates"][0]["content"]["parts"][0]["text"]
                        elif "error" in data:
                            respuesta_ia = f"Error de Gemini: {data['error']['message']}"
                        else:
                            respuesta_ia = f"Respuesta inesperada: {str(data)}"
                    except Exception as e:
                        respuesta_ia = f"Error al conectar con Gemini: {str(e)}"
            else:
                preg_lower = ej.lower()
                if any(w in preg_lower for w in ["agotado", "crítico", "falta", "quiebre"]):
                    top = df[df["Estado_Stock"].isin(["AGOTADO","CRÍTICO"])].head(5)
                    respuesta_ia = f"Hay {kpis['stock_critico']} productos con stock crítico o agotado. Los más urgentes:\n\n"
                    for _, r in top.iterrows():
                        respuesta_ia += f"· {r['Nombre_Producto']} — Stock: {r['Stock_Actual']} / Mínimo: {r['Stock_Minimo']} ({r['Ubicacion']})\n"
                    respuesta_ia += "\nConfigure una API Key de Gemini para respuestas detalladas."
                elif "vencid" in preg_lower:
                    top = df[df["Estado_Vencimiento"] == "VENCIDO"].head(5)
                    respuesta_ia = f"Hay {kpis['vencidos']} productos vencidos. Muestra:\n\n"
                    for _, r in top.iterrows():
                        respuesta_ia += f"· {r['Nombre_Producto']} — Venció el {r['Fecha_Vencimiento']} ({r['Ubicacion']})\n"
                else:
                    respuesta_ia = (
                        f"El inventario registra {kpis['total_insumos']} productos. "
                        f"Hay {kpis['stock_critico']} con stock crítico, "
                        f"{kpis['vencidos']} vencidos y "
                        f"{kpis['por_vencer_30']} que vencen en menos de 30 días."
                        f"\n\nConfigure una API Key de Gemini para respuestas específicas."
                    )
            st.session_state.mensajes_chat.append({"rol": "bot", "texto": respuesta_ia})
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    for msg in st.session_state.mensajes_chat:
        if msg["rol"] == "user":
            st.markdown(f'<div class="chat-user">{msg["texto"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bot">{msg["texto"]}</div>', unsafe_allow_html=True)

    with st.form("form_chat", clear_on_submit=True):
        col_inp, col_btn = st.columns([5, 1])
        pregunta = col_inp.text_input(
            "Consulta",
            placeholder="¿Qué insumos críticos necesito para las cirugías de traumatología de mañana?",
            label_visibility="collapsed",
        )
        enviar = col_btn.form_submit_button("Enviar", type="primary", use_container_width=True)

    if enviar and pregunta:
        st.session_state.mensajes_chat.append({"rol": "user", "texto": pregunta})
        api_key_val = locals().get("api_key", "") or os.environ.get("GEMINI_API_KEY", "")

        if api_key_val and len(api_key_val) > 10:
            with st.spinner("Procesando consulta..."):
                try:
                    historial_gemini = []
                    for m in st.session_state.mensajes_chat[:-1]:
                        historial_gemini.append({
                            "role": "user" if m["rol"] == "user" else "model",
                            "parts": [{"text": m["texto"]}],
                        })
                    historial_gemini.append({"role": "user", "parts": [{"text": pregunta}]})

                    response = requests.post(
                        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
                        headers={
                            "Content-Type": "application/json",
                            "x-goog-api-key": api_key_val,
                        },
                        json={
                            "contents": [
                                {"role": "user", "parts": [{"text": contexto_bbdd}]},
                                {"role": "model", "parts": [{"text": "Entendido, estoy listo para responder consultas sobre el inventario."}]},
                            ] + historial_gemini,
                        },
                        timeout=30,
                    )
                    data = response.json()
                    if "candidates" in data:
                        respuesta_ia = data["candidates"][0]["content"]["parts"][0]["text"]
                    elif "error" in data:
                        respuesta_ia = f"Error de Gemini: {data['error']['message']}"
                    else:
                        respuesta_ia = f"Respuesta inesperada: {str(data)}"
                except Exception as e:
                    respuesta_ia = f"Error al conectar con Gemini: {str(e)}"
        else:
            preg_lower = pregunta.lower()
            if any(w in preg_lower for w in ["agotado", "crítico", "falta", "quiebre"]):
                top = df[df["Estado_Stock"].isin(["AGOTADO","CRÍTICO"])].head(5)
                respuesta_ia = f"Hay {kpis['stock_critico']} productos con stock crítico o agotado. Los más urgentes:\n\n"
                for _, r in top.iterrows():
                    respuesta_ia += f"· {r['Nombre_Producto']} — Stock: {r['Stock_Actual']} / Mínimo: {r['Stock_Minimo']} ({r['Ubicacion']})\n"
                respuesta_ia += "\nConfigure una API Key de Gemini para respuestas detalladas."
            elif "vencid" in preg_lower:
                top = df[df["Estado_Vencimiento"] == "VENCIDO"].head(5)
                respuesta_ia = f"Hay {kpis['vencidos']} productos vencidos. Muestra:\n\n"
                for _, r in top.iterrows():
                    respuesta_ia += f"· {r['Nombre_Producto']} — Venció el {r['Fecha_Vencimiento']} ({r['Ubicacion']})\n"
            else:
                respuesta_ia = (
                    f"El inventario registra {kpis['total_insumos']} productos. "
                    f"Hay {kpis['stock_critico']} con stock crítico, "
                    f"{kpis['vencidos']} vencidos y "
                    f"{kpis['por_vencer_30']} que vencen en menos de 30 días."
                    f"\n\nConfigure una API Key de Gemini para respuestas específicas."
                )

        st.session_state.mensajes_chat.append({"rol": "bot", "texto": respuesta_ia})
        st.rerun()

    if st.button("Limpiar conversación"):
        st.session_state.mensajes_chat = []
        st.rerun()


# ═════════════════════════════════════════════
# MÓDULO 7 · MOVIMIENTOS
# ═════════════════════════════════════════════

elif pagina == "Movimientos":
    page_header(
        "Trazabilidad",
        "Historial de Movimientos",
        "Registro cronológico de traslados, entradas y salidas de insumos",
    )

    df_mov = obtener_movimientos()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <span class="kpi-number">{len(df_mov)}</span>
            <span class="kpi-label">Movimientos totales</span>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <span class="kpi-number">{len(df_mov[df_mov['Tipo']=='Traslado'])}</span>
            <span class="kpi-label">Traslados</span>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card">
            <span class="kpi-number">{len(df_mov[df_mov['Tipo']=='Salida'])}</span>
            <span class="kpi-label">Salidas a pabellón</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tipo_f = st.multiselect("Filtrar por tipo de movimiento:", df_mov["Tipo"].unique())
    if tipo_f:
        df_mov = df_mov[df_mov["Tipo"].isin(tipo_f)]

    st.dataframe(df_mov, use_container_width=True, height=500)

    section_label("Distribución por tipo")
    conteo = df_mov["Tipo"].value_counts().reset_index()
    conteo.columns = ["Tipo", "Cantidad"]
    fig = px.pie(
        conteo, names="Tipo", values="Cantidad",
        color_discrete_sequence=["#1B3A7A","#8DC63F","#E67E22"],
        hole=0.45,
    )
    fig.update_layout(
        height=260, margin=dict(t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font_family="Montserrat",
        legend=dict(orientation="h", y=-0.1),
    )
    st.plotly_chart(fig, use_container_width=True)