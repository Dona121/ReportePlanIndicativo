"""
Dashboard — Plan Indicativo 2024-2027.

Orquestador principal del tablero de seguimiento. Este archivo se mantiene
intencionalmente delgado: sólo configura la página, inyecta el CSS y el
tema Plotly, carga los datos vía la sidebar, calcula los reportes y delega
cada bloque visual a un módulo de ``vistas/``.

Estructura del proyecto:
    config/         -> paleta, fuentes, CSS, tema Plotly, tooltips, URLs.
    procesamiento/  -> lectura de Excel y agregaciones por vigencia.
    exportaciones/  -> generadores de Excel formateados corporativamente.
    utils/          -> helpers transversales (formato, tablas, GitHub).
    vistas/         -> bloques de UI (sidebar, masthead, pestañas, footer).
"""
import polars as pl
import streamlit as st

# ---- Configuración base ------------------------------------------------
# st.set_page_config DEBE invocarse antes de cualquier otra llamada a st.*
st.set_page_config(
    page_title="Plan Indicativo 2024-2027",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Identidad visual --------------------------------------------------
from config.styles import inyectar_css
from config.plotly_theme import configurar_tema_plotly

inyectar_css()
configurar_tema_plotly()

# ---- Procesamiento y reportes ------------------------------------------
from procesamiento import (
    procesar_datos,
    construir_ejecucion_financ_tipo,
    construir_ejecucion_acumulada_tipo,
    construir_prog_financ_categorias,
    construir_ejec_por_dependencia,
    construir_avances_fisicos,
)

# ---- Vistas ------------------------------------------------------------
from vistas import (
    render_sidebar,
    render_masthead,
    render_kpis_cabecera,
    render_ejecucion_fisica,
    render_ejecucion_financiera,
    render_distribucion,
    render_dependencia,
    render_proyectos,
    render_exportar,
    render_footer,
)


# =========================================================================
# 1. Sidebar — carga de archivos + selector de vigencia
# =========================================================================
archivos_bytes, filtro_vigencia = render_sidebar()

# =========================================================================
# 2. Procesamiento
# =========================================================================
try:
    datos = procesar_datos(
        archivos_bytes["pi"], archivos_bytes["h24"], archivos_bytes["r24"],
        archivos_bytes["h25"], archivos_bytes["r25"],
        archivos_bytes["ads_rp_25"], archivos_bytes["ads_reg_25"],
        archivos_bytes["gestiones_25"], archivos_bytes["fondo_mixto_25"],
        archivos_bytes["inder_25"],
        archivos_bytes["h26"], archivos_bytes["r26"],
    )
except Exception as e:
    st.error(f"Error procesando los archivos: {e}")
    st.exception(e)
    st.stop()

# =========================================================================
# 3. Reportes derivados (cacheados implícitamente vía datos)
# =========================================================================
ejec_financ_tipo    = construir_ejecucion_financ_tipo(datos, filtro_vigencia)
ejec_acumulada_tipo = construir_ejecucion_acumulada_tipo(datos)
categorias_pdd      = construir_prog_financ_categorias(datos, filtro_vigencia)
ejec_dependencia    = construir_ejec_por_dependencia(datos, filtro_vigencia)
avances_fisicos     = construir_avances_fisicos(datos, filtro_vigencia)

# =========================================================================
# 4. KPIs de cabecera
# =========================================================================
prog_vig    = ejec_financ_tipo.select(pl.col(f"Programación Financiera {filtro_vigencia}").sum()).item() or 0
ejec_vig    = ejec_financ_tipo.select(pl.col(f"Ejecución Financiera {filtro_vigencia}").sum()).item() or 0
pct_vig     = (ejec_vig / prog_vig) if prog_vig else 0

prog_cuatri = ejec_acumulada_tipo.select(pl.col("Programación Cuatrienio").sum()).item() or 0
ejec_acum   = ejec_acumulada_tipo.select(pl.col("Ejecución Financiera Acumulada").sum()).item() or 0
pct_cuatri  = (ejec_acum / prog_cuatri) if prog_cuatri else 0

# =========================================================================
# 5. Render principal
# =========================================================================
render_masthead(filtro_vigencia)
render_kpis_cabecera(
    filtro_vigencia,
    prog_vig, ejec_vig, pct_vig,
    prog_cuatri, ejec_acum, pct_cuatri,
)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Ejecución Física",
    "Ejecución Financiera",
    "Distribución de Metas",
    "Ejecución por Dependencia",
    "Proyectos",
    "Exportar",
])

with tab1:
    render_ejecucion_fisica(filtro_vigencia, avances_fisicos)

with tab2:
    render_ejecucion_financiera(
        filtro_vigencia,
        ejec_financ_tipo, ejec_acumulada_tipo, categorias_pdd,
        prog_vig, ejec_vig, pct_vig,
        prog_cuatri, ejec_acum, pct_cuatri,
    )

with tab3:
    render_distribucion(filtro_vigencia, datos, avances_fisicos)

with tab4:
    render_dependencia(filtro_vigencia, ejec_dependencia)

with tab5:
    render_proyectos(filtro_vigencia, datos)

with tab6:
    render_exportar(
        filtro_vigencia, datos,
        ejec_financ_tipo, ejec_acumulada_tipo, categorias_pdd,
        ejec_dependencia, avances_fisicos,
    )

render_footer()
