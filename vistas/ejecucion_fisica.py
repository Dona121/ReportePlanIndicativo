"""
Pestaña 01 — Ejecución Física.

Muestra el avance ponderado por línea estratégica y por sector PDD,
diferenciando vigencia y cuatrienio.
"""
import streamlit as st
import plotly.express as px

from config.styles import COLORS
from config.plotly_theme import SCALE_BLUE, SCALE_GREEN
from config.tooltips import TOOLTIPS
from utils.formato import formato_porcentaje
from utils.ui import seccion, render_vista, selector_vista


_COLUMNAS_LINEAS = [
    {"key": "Línea Estratégica", "label": "Línea Estratégica", "type": "text"},
    {"key": "% Aporte Cumplimiento PDD", "label": "Aporte PDD", "type": "pct"},
    {"key": "Sobre Numero Total de Indicadores", "label": "Peso relativo", "type": "pct"},
    {"key": "% Eficacia Operativa", "label": "Eficacia Operativa", "type": "pctbar"},
]
_COLUMNAS_SECTORES = [
    {"key": "Sector PDD", "label": "Sector PDD", "type": "text"},
    {"key": "% Aporte Cumplimiento PDD", "label": "Aporte PDD", "type": "pct"},
    {"key": "Sobre Numero Total de Indicadores", "label": "Peso relativo", "type": "pct"},
    {"key": "% Eficacia Operativa", "label": "Eficacia Operativa", "type": "pctbar"},
]


def _fig_bar_horizontal(df, cat_col, val_col, titulo, color_scale):
    df2 = df.sort_values(val_col, ascending=True)
    fig = px.bar(
        df2, x=val_col, y=cat_col,
        orientation="h", text=val_col,
        color=val_col, color_continuous_scale=color_scale,
        title=titulo,
    )
    fig.update_traces(
        texttemplate="%{text:.1%}", textposition="outside",
        marker_line_color=COLORS["blue_dark"], marker_line_width=0.5,
    )
    fig.update_layout(
        xaxis_tickformat=".0%",
        height=max(450, len(df2) * 32),
        showlegend=False, coloraxis_showscale=False, bargap=0.3,
    )
    return fig


def render_ejecucion_fisica(filtro_vigencia: str, avances_fisicos: dict) -> None:
    """Renderiza la pestaña de Ejecución Física."""
    seccion(
        "01", "Ejecución Física",
        "Avance ponderado del cumplimiento de metas físicas del Plan de Desarrollo.",
        tooltip=(
            "Mide qué tanto se han cumplido las metas del Plan en términos "
            "físicos, no monetarios. El avance global se construye combinando "
            "el desempeño de cada programa con su peso dentro del Plan: los "
            "programas con más metas pesan más en el resultado. La 'Eficacia "
            "Operativa' permite comparar líneas y sectores ajustando por su "
            "tamaño relativo, de modo que dependencias pequeñas con buen "
            "desempeño no quedan invisibilizadas frente a las más grandes."
        ),
    )

    k1, k2 = st.columns(2)
    k1.metric(
        f"Avance ponderado — Vigencia {filtro_vigencia}",
        formato_porcentaje(avances_fisicos["avance_vig_ponderado"] or 0),
        help=TOOLTIPS["avance_vig_ponderado"],
    )
    k2.metric(
        "Avance ponderado — Cuatrienio",
        formato_porcentaje(avances_fisicos["avance_cuatrienio_total"] or 0),
        help=TOOLTIPS["avance_cuatrienio_ponderado"],
    )

    st.markdown(" ")
    sub_v, sub_c = st.tabs([f"Vigencia {filtro_vigencia}", "Cuatrienio"])

    with sub_v:
        st.markdown("##### Por Línea Estratégica")
        vista = selector_vista("vista_fis_vig_lineas")
        df = avances_fisicos["avance_vig_lineas"].to_pandas()
        if not df.empty:
            render_vista(
                vista,
                fig_factory=lambda: _fig_bar_horizontal(
                    df, "Línea Estratégica", "% Eficacia Operativa",
                    f"Eficacia Operativa por Línea Estratégica — {filtro_vigencia}", SCALE_BLUE),
                df_tabla=df,
                columnas=_COLUMNAS_LINEAS,
            )
        else:
            st.info("Sin datos para la vigencia seleccionada.")

        st.markdown("##### Por Sector PDD")
        vista = selector_vista("vista_fis_vig_sectores")
        df = avances_fisicos["avance_vig_sectores"].to_pandas()
        if not df.empty:
            render_vista(
                vista,
                fig_factory=lambda: _fig_bar_horizontal(
                    df, "Sector PDD", "% Eficacia Operativa",
                    f"Eficacia Operativa por Sector PDD — {filtro_vigencia}", SCALE_BLUE),
                df_tabla=df,
                columnas=_COLUMNAS_SECTORES,
            )

    with sub_c:
        st.markdown("##### Por Línea Estratégica")
        vista = selector_vista("vista_fis_cuatri_lineas")
        df = avances_fisicos["avance_cuatri_lineas"].to_pandas()
        render_vista(
            vista,
            fig_factory=lambda: _fig_bar_horizontal(
                df, "Línea Estratégica", "% Eficacia Operativa",
                "Eficacia Operativa por Línea Estratégica — Cuatrienio", SCALE_GREEN),
            df_tabla=df,
            columnas=_COLUMNAS_LINEAS,
        )

        st.markdown("##### Por Sector PDD")
        vista = selector_vista("vista_fis_cuatri_sectores")
        df = avances_fisicos["avance_cuatri_sectores"].to_pandas()
        render_vista(
            vista,
            fig_factory=lambda: _fig_bar_horizontal(
                df, "Sector PDD", "% Eficacia Operativa",
                "Eficacia Operativa por Sector PDD — Cuatrienio", SCALE_GREEN),
            df_tabla=df,
            columnas=_COLUMNAS_SECTORES,
        )
