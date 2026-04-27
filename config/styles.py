"""
Identidad visual del dashboard: paleta corporativa, fuentes y CSS institucional.

Uso:
    from config.styles import COLORS, FONT_DISPLAY, FONT_HEADING, FONT_BODY, FONT_MONO
    from config.styles import inyectar_css

    inyectar_css()  # llamar UNA vez tras st.set_page_config
"""
import streamlit as st

# =========================================================================
# Paleta corporativa
# =========================================================================
COLORS = {
    "green_light":  "#17743d",
    "green_dark":   "#005931",
    "cyan":         "#47b1d5",
    "blue":         "#1754ab",
    "blue_dark":    "#003d6c",
    "orange":       "#d88c16",
    "orange_deep":  "#cf7000",
    "amber":        "#d37e00",
    "brown":        "#9b5b1e",
    "coral":        "#e68878",
}

# Fuentes oficiales:
#   Alkaline   -> fuente de display / titulares (carácter institucional)
#   Montserrat -> encabezados y UI
#   Open Sans  -> cuerpo, datos, formularios
FONT_DISPLAY = "Alkaline"
FONT_HEADING = "Montserrat"
FONT_BODY    = "Open Sans"
FONT_MONO    = "JetBrains Mono"  # apoyo para metadatos pequeños


# =========================================================================
# CSS institucional
# =========================================================================
CSS = f"""
<style>
/* Montserrat y Open Sans oficiales desde Google Fonts.
   Alkaline no está disponible en Google Fonts, se carga desde un CDN libre;
   si falla, el stack hace fallback a Montserrat + serif. */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&family=Open+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

@font-face {{
    font-family: 'Alkaline';
    src: url('https://cdn.jsdelivr.net/gh/gogolapse/fonts@main/Alkaline/Alkaline.otf') format('opentype');
    font-weight: 400;
    font-style: normal;
    font-display: swap;
}}

:root {{
    --green-light: {COLORS["green_light"]};
    --green-dark:  {COLORS["green_dark"]};
    --cyan:        {COLORS["cyan"]};
    --blue:        {COLORS["blue"]};
    --blue-dark:   {COLORS["blue_dark"]};
    --orange:      {COLORS["orange"]};
    --orange-deep: {COLORS["orange_deep"]};
    --amber:       {COLORS["amber"]};
    --brown:       {COLORS["brown"]};
    --coral:       {COLORS["coral"]};

    --paper:       #ffffff;
    --ink:         #0d1b2a;
    --ink-mute:    #4a5a6a;
    --hairline:    #e3e3e1;
    --chip-bg:     #f1f1ef;
}}

/* Base tipográfica */
html, body, [class*="css"], .stApp {{
    font-family: '{FONT_BODY}', system-ui, sans-serif !important;
    color: var(--ink);
}}

.stApp {{
    background: var(--paper);
}}

/* Encabezados H1..H6 con Montserrat (institucional, geométrica) */
h1, h2, h3, h4, h5, h6 {{
    font-family: '{FONT_HEADING}', Helvetica, sans-serif !important;
    color: var(--ink);
    letter-spacing: -0.01em;
}}
h1 {{ font-weight: 800 !important; }}
h2, h3 {{ font-weight: 700 !important; }}
h4, h5, h6 {{ font-weight: 600 !important; }}

/* Footer oculto. NO tocamos el header ni el toolbar: Streamlit usa esos
   contenedores para el botón de reabrir la sidebar cuando está colapsada
   y para el menú de opciones (tres puntos), y cualquier regla que los
   afecte rompe esa interacción. */
footer {{ visibility: hidden; }}

/* Reducir el padding del contenedor principal para aprovechar más el ancho.
   Streamlit usa por defecto ~6rem de padding lateral, demasiado para una
   pantalla con sidebar lateral. Lo bajamos para que las tarjetas KPI no
   queden estrechas y los gráficos respiren mejor. */
.main .block-container,
[data-testid="stMain"] .block-container,
[data-testid="stAppViewContainer"] .block-container {{
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    padding-top: 2rem !important;
    max-width: 100% !important;
}}

/* Sidebar */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, var(--blue-dark) 0%, #00284a 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}}
[data-testid="stSidebar"] * {{ color: #e9eef5 !important; }}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{ color: #fff !important; font-family: '{FONT_HEADING}', sans-serif !important; }}
[data-testid="stSidebar"] label {{
    font-family: '{FONT_HEADING}', sans-serif !important;
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: #b9c6d6 !important;
    font-weight: 600 !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    color: #fff !important;
}}
[data-testid="stSidebar"] button {{
    background: var(--orange-deep) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 2px !important;
    font-family: '{FONT_HEADING}', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    font-size: 0.75rem !important;
    transition: background 0.2s ease;
}}
[data-testid="stSidebar"] button:hover {{
    background: var(--amber) !important;
}}
[data-testid="stSidebar"] [data-testid="stFileUploader"] section {{
    background: rgba(255,255,255,0.04) !important;
    border: 1px dashed rgba(255,255,255,0.25) !important;
    border-radius: 2px !important;
}}
[data-testid="stSidebar"] [data-testid="stFileUploader"] small {{
    color: #b9c6d6 !important;
}}

/* KPIs */
[data-testid="stMetric"] {{
    background: #fff;
    border: 1px solid var(--hairline);
    border-left: 3px solid var(--blue);
    padding: 0.9rem 1rem;
    border-radius: 2px;
    box-shadow: 0 1px 0 rgba(13,27,42,0.03);
    overflow: hidden;
}}
[data-testid="stMetric"] [data-testid="stMetricLabel"] {{
    font-family: '{FONT_HEADING}', sans-serif !important;
    font-size: 0.68rem !important;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: var(--ink-mute) !important;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    font-family: '{FONT_DISPLAY}', '{FONT_HEADING}', Helvetica, sans-serif !important;
    font-weight: 400 !important;
    font-size: 1.7rem !important;
    color: var(--ink) !important;
    letter-spacing: -0.015em;
    line-height: 1.05;
    white-space: nowrap;
    overflow: visible;
}}
[data-testid="stMetric"] [data-testid="stMetricValue"] > div {{
    overflow: visible !important;
}}
[data-testid="stMetric"] [data-testid="stMetricDelta"] {{
    font-family: '{FONT_MONO}', monospace !important;
    font-size: 0.78rem !important;
    color: var(--green-light) !important;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    gap: 0;
    border-bottom: 1px solid var(--hairline);
    background: transparent;
}}
.stTabs [data-baseweb="tab"] {{
    height: 48px;
    padding: 0 1.3rem;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    color: var(--ink-mute) !important;
    font-family: '{FONT_HEADING}', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    transition: color 0.2s ease, border-color 0.2s ease;
}}
.stTabs [data-baseweb="tab"]:hover {{
    color: var(--blue) !important;
}}
.stTabs [aria-selected="true"] {{
    color: var(--blue-dark) !important;
    border-bottom: 2px solid var(--orange-deep) !important;
    background: transparent !important;
}}

/* Toggle gráfico/tabla */
div[data-testid="stRadio"] > label {{
    font-family: '{FONT_HEADING}', sans-serif !important;
    font-size: 0.7rem !important;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: var(--ink-mute) !important;
    font-weight: 600 !important;
}}

/* Tablas nativas de Streamlit */
.stDataFrame, [data-testid="stDataFrame"] {{
    border: 1px solid var(--hairline);
    border-radius: 2px;
}}

/* Alertas */
.stAlert {{
    border-radius: 2px !important;
    border-left: 3px solid var(--blue) !important;
}}

/* Selects */
[data-baseweb="select"] > div {{
    border-radius: 2px !important;
    border-color: var(--hairline) !important;
}}

/* Botón de descarga */
.stDownloadButton button {{
    background: var(--blue-dark) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 2px !important;
    font-family: '{FONT_HEADING}', sans-serif !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    font-size: 0.78rem !important;
    padding: 0.55rem 1.1rem !important;
}}
.stDownloadButton button:hover {{
    background: var(--blue) !important;
}}

/* Encabezado editorial */
.masthead {{
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    padding: 1.2rem 0 0.4rem 0;
    border-bottom: 1px solid var(--ink);
    margin-bottom: 0.4rem;
}}
.masthead .eyebrow {{
    font-family: '{FONT_MONO}', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--orange-deep);
    margin-bottom: 0.4rem;
}}
.masthead h1 {{
    font-family: '{FONT_DISPLAY}', '{FONT_HEADING}', Helvetica, sans-serif !important;
    font-size: 4rem !important;
    line-height: 0.95 !important;
    margin: 0 !important;
    font-weight: 400 !important;
    color: var(--ink);
}}
.masthead h1 em {{
    font-style: normal;
    color: var(--orange-deep);
}}
.masthead .edition {{
    font-family: '{FONT_MONO}', monospace;
    font-size: 0.72rem;
    color: var(--ink-mute);
    text-align: right;
    letter-spacing: 0.08em;
    line-height: 1.55;
}}
.masthead .edition strong {{
    color: var(--ink);
    font-weight: 700;
    font-family: '{FONT_HEADING}', sans-serif;
    letter-spacing: 0.06em;
}}

.subhead {{
    font-family: '{FONT_BODY}', sans-serif;
    font-size: 0.92rem;
    color: var(--ink-mute);
    font-style: italic;
    border-bottom: 1px solid var(--hairline);
    padding-bottom: 1.2rem;
    margin-bottom: 1.6rem;
    letter-spacing: 0.01em;
    line-height: 1.5;
}}

/* Títulos de sección numerados */
.section-title {{
    font-family: '{FONT_HEADING}', sans-serif;
    font-size: 1.7rem;
    font-weight: 700;
    color: var(--ink);
    margin: 1.2rem 0 0.2rem 0;
    letter-spacing: -0.015em;
}}
.section-title .num {{
    font-family: '{FONT_MONO}', monospace;
    font-size: 0.75rem;
    color: var(--orange-deep);
    letter-spacing: 0.2em;
    vertical-align: middle;
    margin-right: 0.8rem;
    font-weight: 500;
}}
.section-title .seccion-info {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: var(--blue-dark);
    color: #fff;
    font-family: '{FONT_HEADING}', sans-serif;
    font-size: 0.8rem;
    font-weight: 700;
    margin-left: 0.7rem;
    cursor: help;
    vertical-align: middle;
    transition: background 0.18s ease;
}}
.section-title .seccion-info:hover {{
    background: var(--orange-deep);
}}
.section-kicker {{
    font-family: '{FONT_BODY}', sans-serif;
    font-size: 0.83rem;
    color: var(--ink-mute);
    font-style: italic;
    margin-bottom: 1rem;
    border-bottom: 1px dotted var(--hairline);
    padding-bottom: 0.8rem;
}}

/* Separador */
hr {{
    border: none !important;
    border-top: 1px solid var(--hairline) !important;
    margin: 2rem 0 !important;
}}

/* Caption */
[data-testid="stCaptionContainer"], .stCaption {{
    color: var(--ink-mute) !important;
    font-style: italic;
    font-size: 0.82rem !important;
    font-family: '{FONT_BODY}', sans-serif !important;
}}

/* Plotly containers */
.js-plotly-plot {{
    border: 1px solid var(--hairline);
    border-radius: 2px;
    background: #fff;
    padding: 0.6rem;
}}

/* Radio del sidebar */
[data-testid="stSidebar"] [role="radiogroup"] label {{
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    padding: 0.5rem 0.75rem;
    border-radius: 2px;
    margin-bottom: 0.3rem;
    text-transform: none;
    letter-spacing: 0;
    font-size: 0.85rem !important;
}}

/* Multiselect chips */
[data-baseweb="tag"] {{
    background: var(--blue-dark) !important;
    color: #fff !important;
    border-radius: 2px !important;
    font-family: '{FONT_HEADING}', sans-serif !important;
}}

/* =====================================================================
   Tabla institucional custom (.institutional-table)
   ===================================================================== */
.institutional-table {{
    width: 100%;
    border-collapse: collapse;
    font-family: '{FONT_BODY}', sans-serif;
    font-size: 0.85rem;
    background: #fff;
    border: 1px solid var(--hairline);
    border-radius: 2px;
    overflow: hidden;
    margin: 0.3rem 0 1.2rem 0;
}}
.institutional-table thead tr {{
    background: var(--blue-dark);
}}
.institutional-table thead th {{
    font-family: '{FONT_HEADING}', sans-serif;
    color: #fff;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    font-size: 0.7rem;
    text-align: left;
    padding: 0.8rem 0.9rem;
    border-bottom: 2px solid var(--orange-deep);
    white-space: nowrap;
}}
.institutional-table thead th.num {{
    text-align: right;
}}
.institutional-table tbody td {{
    padding: 0.65rem 0.9rem;
    border-bottom: 1px solid var(--hairline);
    color: var(--ink);
    vertical-align: middle;
}}
.institutional-table tbody td.num {{
    text-align: right;
    font-variant-numeric: tabular-nums;
    font-family: '{FONT_MONO}', monospace;
    font-size: 0.82rem;
    color: var(--ink);
}}
.institutional-table tbody tr:nth-child(even) {{
    background: #f6f6f5;
}}
.institutional-table tbody tr:hover {{
    background: #ededeb;
}}
.institutional-table tbody tr:last-child td {{
    border-bottom: none;
}}
.institutional-table tfoot td {{
    font-family: '{FONT_HEADING}', sans-serif;
    font-weight: 700;
    background: #ededeb;
    padding: 0.75rem 0.9rem;
    border-top: 2px solid var(--blue-dark);
    color: var(--blue-dark);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-size: 0.78rem;
}}
.institutional-table tfoot td.num {{
    font-family: '{FONT_MONO}', monospace;
    font-size: 0.82rem;
    text-align: right;
    color: var(--blue-dark);
}}

/* Barra de progreso inline en celdas de porcentaje */
.pct-cell {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
    justify-content: flex-end;
}}
.pct-cell .bar {{
    position: relative;
    width: 60px;
    height: 6px;
    background: var(--chip-bg);
    border-radius: 1px;
    overflow: hidden;
    flex-shrink: 0;
}}
.pct-cell .bar > span {{
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    background: var(--blue);
    border-radius: 1px;
}}
.pct-cell.low    .bar > span {{ background: var(--coral); }}
.pct-cell.mid    .bar > span {{ background: var(--amber); }}
.pct-cell.high   .bar > span {{ background: var(--green-light); }}
.pct-cell.top    .bar > span {{ background: var(--green-dark); }}

.pct-cell .value {{
    font-family: '{FONT_MONO}', monospace;
    font-size: 0.82rem;
    min-width: 55px;
    text-align: right;
    color: var(--ink);
}}
</style>
"""


def inyectar_css() -> None:
    """Inserta el CSS institucional en el documento.

    Debe llamarse UNA vez, después de st.set_page_config y antes de cualquier
    elemento renderizado del dashboard.
    """
    st.markdown(CSS, unsafe_allow_html=True)
