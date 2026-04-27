"""
Pestaña 03 — Distribución de Metas.

Muestra el peso relativo de la programación física en cada vigencia
del cuatrienio.
"""
import pandas as pd
import polars as pl
import streamlit as st
import plotly.graph_objects as go

from config.styles import COLORS, FONT_HEADING
from utils.formato import formato_entero
from utils.ui import seccion, render_vista, selector_vista


def render_distribucion(filtro_vigencia: str, datos: dict, avances_fisicos: dict) -> None:
    """Renderiza la pestaña de Distribución de Metas."""
    seccion(
        "03", "Distribución de Metas",
        "Peso relativo de la programación física en cada vigencia del cuatrienio.",
        tooltip=(
            "Muestra cómo se reparte el cumplimiento físico del Plan entre "
            "los cuatro años: cuánto se planea cumplir cada vigencia frente "
            "a la meta total del cuatrienio. La suma de los porcentajes "
            "puede no dar exactamente 100% porque algunas metas son "
            "acumulativas y otras corresponden a flujos que se reinician "
            "cada año."
        ),
    )

    prog_ff = datos["prog_fisica_financiera"]
    programacion_cuatrienio = prog_ff.select(pl.col("Meta de cuatrenio").sum()).item() or 1

    distribucion = {}
    for v in ["2024", "2025", "2026", "2027"]:
        suma = prog_ff.select(pl.col(f"Meta Física Esperada {v}").sum()).item() or 0
        distribucion[v] = (suma / programacion_cuatrienio, suma)

    df_dist = pd.DataFrame({
        "Vigencia": list(distribucion.keys()),
        "Suma metas físicas": [v[1] for v in distribucion.values()],
        "Distribución": [v[0] for v in distribucion.values()],
    })

    vista = selector_vista("vista_distr")

    def fig_distr():
        fig = go.Figure(data=[go.Pie(
            labels=df_dist["Vigencia"], values=df_dist["Distribución"],
            hole=0.55,
            marker=dict(
                colors=[COLORS["blue_dark"], COLORS["cyan"],
                        COLORS["orange_deep"], COLORS["brown"]],
                line=dict(color="#fff", width=2),
            ),
            textinfo="label+percent",
            textfont=dict(family=FONT_HEADING, size=14, color="#fff"),
        )])
        fig.update_layout(height=470, showlegend=False,
                          title="Distribución por Vigencia")
        return fig

    columnas_dist = [
        {"key": "Vigencia", "label": "Vigencia", "type": "text"},
        {"key": "Suma metas físicas", "label": "Metas físicas programadas", "type": "int"},
        {"key": "Distribución", "label": "Distribución", "type": "pctbar"},
    ]
    totales_dist = {
        "Suma metas físicas": df_dist["Suma metas físicas"].sum(),
        "Distribución": df_dist["Distribución"].sum(),
    }
    render_vista(vista, fig_factory=fig_distr,
                 df_tabla=df_dist, columnas=columnas_dist, totales=totales_dist)

    st.markdown(" ")
    st.markdown("##### Conteo de Metas")
    a, b = st.columns(2)
    a.metric("Total de indicadores de producto",
             formato_entero(avances_fisicos["numero_total_metas"]))
    b.metric(f"Indicadores con programación en {filtro_vigencia}",
             formato_entero(avances_fisicos["numero_metas_prog_vigencia"]))
