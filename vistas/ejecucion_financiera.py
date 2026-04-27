"""
Pestaña 02 — Ejecución Financiera.

Compara los recursos programados contra los efectivamente pagados para
la vigencia seleccionada y para todo el cuatrienio, desagregando por
fuente y por categorías del Plan de Desarrollo.
"""
import streamlit as st
import plotly.graph_objects as go

from config.styles import COLORS
from config.tooltips import TOOLTIPS
from utils.formato import formato_pesos, formato_porcentaje
from utils.ui import seccion, render_vista, selector_vista


def render_ejecucion_financiera(
    filtro_vigencia: str,
    ejec_financ_tipo,
    ejec_acumulada_tipo,
    categorias_pdd,
    prog_vig: float,
    ejec_vig: float,
    pct_vig: float,
    prog_cuatri: float,
    ejec_acum: float,
    pct_cuatri: float,
) -> None:
    """Renderiza la pestaña de Ejecución Financiera (sub-tabs vigencia/cuatrienio)."""
    seccion(
        "02", "Ejecución Financiera",
        "Comportamiento de recursos programados frente a ejecutados por fuente y categoría del PDD.",
        tooltip=(
            "Compara los recursos presupuestados frente a los efectivamente "
            "pagados. La programación reúne las diez fuentes de financiación "
            "del Plan (recursos propios, SGP, Regalías, cofinanciaciones, "
            "crédito y otras). La ejecución consolida los reportes de "
            "Hacienda, Regalías y, para 2025, también los de Aguas de Sucre, "
            "Gestiones, PDET, Fondo Mixto e Indersucre. El % de ejecución "
            "indica qué tanto se ha utilizado de cada fuente."
        ),
    )

    sub_v, sub_c = st.tabs([f"Vigencia {filtro_vigencia}", "Cuatrienio"])

    with sub_v:
        _render_sub_vigencia(
            filtro_vigencia, ejec_financ_tipo, categorias_pdd,
            prog_vig, ejec_vig, pct_vig,
        )

    with sub_c:
        _render_sub_cuatrienio(
            ejec_acumulada_tipo, prog_cuatri, ejec_acum, pct_cuatri,
        )


# =========================================================================
# Sub-pestaña: Vigencia
# =========================================================================
def _render_sub_vigencia(
    filtro_vigencia, ejec_financ_tipo, categorias_pdd,
    prog_vig, ejec_vig, pct_vig,
):
    k1, k2, k3 = st.columns(3)
    k1.metric("Programación", formato_pesos(prog_vig), help=TOOLTIPS["prog_vigencia"])
    k2.metric("Ejecución", formato_pesos(ejec_vig), help=TOOLTIPS["ejec_vigencia"])
    k3.metric("Avance", formato_porcentaje(pct_vig), help=TOOLTIPS["avance_vigencia"])

    # --- Por clasificación de recursos ---
    st.markdown("##### Por Clasificación de Recursos")
    vista = selector_vista("vista_fin_vig_tipo")
    df_tipo = ejec_financ_tipo.to_pandas()

    def fig_tipo():
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Programación", x=df_tipo["Clasificación Recursos"],
            y=df_tipo[f"Programación Financiera {filtro_vigencia}"],
            marker=dict(color=COLORS["blue_dark"], line=dict(color="#fff", width=1)),
        ))
        fig.add_trace(go.Bar(
            name="Ejecución", x=df_tipo["Clasificación Recursos"],
            y=df_tipo[f"Ejecución Financiera {filtro_vigencia}"],
            marker=dict(color=COLORS["orange_deep"], line=dict(color="#fff", width=1)),
        ))
        fig.update_layout(
            barmode="group", height=460,
            title=f"Programación vs Ejecución por Fuente — {filtro_vigencia}",
            yaxis_title="Valor (COP)", xaxis_tickangle=-25, bargap=0.25,
        )
        return fig

    columnas_tipo = [
        {"key": "Clasificación Recursos", "label": "Fuente", "type": "text"},
        {"key": "Tipo Fuente", "label": "Tipo", "type": "text"},
        {"key": f"Programación Financiera {filtro_vigencia}", "label": f"Programación {filtro_vigencia}", "type": "money"},
        {"key": f"Ejecución Financiera {filtro_vigencia}", "label": f"Ejecución {filtro_vigencia}", "type": "money"},
        {"key": "Porcentaje de Ejecución Financiera", "label": "Avance", "type": "pctbar"},
    ]
    totales_tipo = {
        f"Programación Financiera {filtro_vigencia}": df_tipo[f"Programación Financiera {filtro_vigencia}"].sum(),
        f"Ejecución Financiera {filtro_vigencia}": df_tipo[f"Ejecución Financiera {filtro_vigencia}"].sum(),
        "Porcentaje de Ejecución Financiera": (
            df_tipo[f"Ejecución Financiera {filtro_vigencia}"].sum()
            / df_tipo[f"Programación Financiera {filtro_vigencia}"].sum()
            if df_tipo[f"Programación Financiera {filtro_vigencia}"].sum() else 0
        ),
    }
    render_vista(vista, fig_factory=fig_tipo, df_tabla=df_tipo,
                 columnas=columnas_tipo, totales=totales_tipo)

    # --- Por categorías del PDD ---
    st.markdown("##### Por Categorías del Plan de Desarrollo")
    cat1, cat2, cat3 = st.tabs(["Líneas Estratégicas", "Sectores PDD", "Programas PDD"])

    def fig_cat(df, col_cat, titulo):
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Programación", x=df[col_cat],
            y=df[f"Programación Financiera {filtro_vigencia}"],
            marker_color=COLORS["blue_dark"],
        ))
        fig.add_trace(go.Bar(
            name="Ejecución", x=df[col_cat],
            y=df[f"Ejecución Financiera {filtro_vigencia}"],
            marker_color=COLORS["orange_deep"],
        ))
        fig.update_layout(barmode="group", height=480,
                          title=titulo, xaxis_tickangle=-30)
        return fig

    def _totales(df):
        prog = df[f"Programación Financiera {filtro_vigencia}"].sum()
        ejec = df[f"Ejecución Financiera {filtro_vigencia}"].sum()
        return {
            f"Programación Financiera {filtro_vigencia}": prog,
            f"Ejecución Financiera {filtro_vigencia}": ejec,
            "Porcentaje de Ejecución Financiera": (ejec / prog) if prog else 0,
        }

    with cat1:
        vista = selector_vista("vista_fin_cat_lineas")
        df = categorias_pdd["lineas"].to_pandas()
        columnas = [
            {"key": "Línea Estratégica", "label": "Línea Estratégica", "type": "text"},
            {"key": f"Programación Financiera {filtro_vigencia}", "label": "Programación", "type": "money"},
            {"key": f"Ejecución Financiera {filtro_vigencia}", "label": "Ejecución", "type": "money"},
            {"key": "Porcentaje de Ejecución Financiera", "label": "Avance", "type": "pctbar"},
        ]
        render_vista(
            vista,
            fig_factory=lambda: fig_cat(df, "Línea Estratégica",
                                        f"Programación vs Ejecución por Línea — {filtro_vigencia}"),
            df_tabla=df, columnas=columnas, totales=_totales(df),
        )

    with cat2:
        vista = selector_vista("vista_fin_cat_sectores")
        df = categorias_pdd["sectores"].to_pandas()
        columnas = [
            {"key": "Sector PDD", "label": "Sector PDD", "type": "text"},
            {"key": f"Programación Financiera {filtro_vigencia}", "label": "Programación", "type": "money"},
            {"key": f"Ejecución Financiera {filtro_vigencia}", "label": "Ejecución", "type": "money"},
            {"key": "Porcentaje de Ejecución Financiera", "label": "Avance", "type": "pctbar"},
        ]
        render_vista(
            vista,
            fig_factory=lambda: fig_cat(df, "Sector PDD",
                                        f"Programación vs Ejecución por Sector — {filtro_vigencia}"),
            df_tabla=df, columnas=columnas, totales=_totales(df),
        )

    with cat3:
        vista = selector_vista("vista_fin_cat_programas")
        df = categorias_pdd["programas"].to_pandas()
        columnas = [
            {"key": "Programa PDD", "label": "Programa PDD", "type": "text"},
            {"key": f"Programación Financiera {filtro_vigencia}", "label": "Programación", "type": "money"},
            {"key": f"Ejecución Financiera {filtro_vigencia}", "label": "Ejecución", "type": "money"},
            {"key": "Porcentaje de Ejecución Financiera", "label": "Avance", "type": "pctbar"},
        ]

        def fig_programas():
            df_top = df.sort_values(f"Ejecución Financiera {filtro_vigencia}", ascending=True).tail(20)
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Programación", y=df_top["Programa PDD"],
                x=df_top[f"Programación Financiera {filtro_vigencia}"],
                orientation="h",
                marker_color=COLORS["blue_dark"],
            ))
            fig.add_trace(go.Bar(
                name="Ejecución", y=df_top["Programa PDD"],
                x=df_top[f"Ejecución Financiera {filtro_vigencia}"],
                orientation="h",
                marker_color=COLORS["orange_deep"],
            ))
            fig.update_layout(
                barmode="group", height=650,
                title=f"Top 20 programas por ejecución — {filtro_vigencia}",
                xaxis_title="Valor (COP)",
            )
            return fig

        render_vista(vista, fig_factory=fig_programas,
                     df_tabla=df, columnas=columnas, totales=_totales(df))


# =========================================================================
# Sub-pestaña: Cuatrienio
# =========================================================================
def _render_sub_cuatrienio(ejec_acumulada_tipo, prog_cuatri, ejec_acum, pct_cuatri):
    k1, k2, k3 = st.columns(3)
    k1.metric("Programación Cuatrienio", formato_pesos(prog_cuatri),
              help=TOOLTIPS["prog_cuatrienio"])
    k2.metric("Ejecución Acumulada", formato_pesos(ejec_acum),
              help=TOOLTIPS["ejec_acumulada"])
    k3.metric("Avance", formato_porcentaje(pct_cuatri),
              help=TOOLTIPS["avance_cuatrienio"])

    vista = selector_vista("vista_fin_cuatri")
    df_acum = ejec_acumulada_tipo.to_pandas()

    def fig_acum():
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Ejecución 2024", x=df_acum["Clasificación Recursos"],
                             y=df_acum["Ejecución Financiera 2024"], marker_color=COLORS["green_light"]))
        fig.add_trace(go.Bar(name="Ejecución 2025", x=df_acum["Clasificación Recursos"],
                             y=df_acum["Ejecución Financiera 2025"], marker_color=COLORS["blue"]))
        fig.add_trace(go.Bar(name="Ejecución 2026", x=df_acum["Clasificación Recursos"],
                             y=df_acum["Ejecución Financiera 2026"], marker_color=COLORS["orange_deep"]))
        fig.update_layout(barmode="stack", height=520,
                          title="Ejecución Acumulada por Fuente (2024-2026)",
                          yaxis_title="Valor (COP)", xaxis_tickangle=-25, bargap=0.25)
        return fig

    # Calcular % de avance cuatrienio por fuente
    df_acum_tabla = df_acum.copy()
    df_acum_tabla["% Avance Cuatrienio"] = df_acum_tabla.apply(
        lambda r: (r["Ejecución Financiera Acumulada"] / r["Programación Cuatrienio"])
        if r["Programación Cuatrienio"] else 0, axis=1
    )

    columnas_acum = [
        {"key": "Clasificación Recursos", "label": "Fuente", "type": "text"},
        {"key": "Programación Cuatrienio", "label": "Programación Cuatrienio", "type": "money"},
        {"key": "Ejecución Financiera 2024", "label": "Ejec. 2024", "type": "money"},
        {"key": "Ejecución Financiera 2025", "label": "Ejec. 2025", "type": "money"},
        {"key": "Ejecución Financiera 2026", "label": "Ejec. 2026", "type": "money"},
        {"key": "Ejecución Financiera Acumulada", "label": "Ejec. Acumulada", "type": "money"},
        {"key": "% Avance Cuatrienio", "label": "Avance", "type": "pctbar"},
    ]
    totales_acum = {
        "Programación Cuatrienio": df_acum_tabla["Programación Cuatrienio"].sum(),
        "Ejecución Financiera 2024": df_acum_tabla["Ejecución Financiera 2024"].sum(),
        "Ejecución Financiera 2025": df_acum_tabla["Ejecución Financiera 2025"].sum(),
        "Ejecución Financiera 2026": df_acum_tabla["Ejecución Financiera 2026"].sum(),
        "Ejecución Financiera Acumulada": df_acum_tabla["Ejecución Financiera Acumulada"].sum(),
        "% Avance Cuatrienio": (
            df_acum_tabla["Ejecución Financiera Acumulada"].sum()
            / df_acum_tabla["Programación Cuatrienio"].sum()
            if df_acum_tabla["Programación Cuatrienio"].sum() else 0
        ),
    }
    render_vista(vista, fig_factory=fig_acum, df_tabla=df_acum_tabla,
                 columnas=columnas_acum, totales=totales_acum)
