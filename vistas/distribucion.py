"""
Pestaña 03 — Distribución de Metas.

Muestra cómo se reparte la programación física del Plan entre las cuatro
vigencias del cuatrienio. Permite:
    - Vista general (todas las metas del Plan).
    - Filtro por una o varias dependencias responsables (homologadas en
      la tabla 'HomologacionSecretarias' del Plan Indicativo).
    - Comparación lado a lado: distribución general vs distribución de
      la selección.

El join entre prog_fisica_financiera y la homologación replica el del
notebook: ``left`` desde ``Responsable`` (con strip_chars) hacia
``Responsable en PI``.
"""
import pandas as pd
import polars as pl
import streamlit as st
import plotly.graph_objects as go

from config.styles import COLORS, FONT_HEADING, FONT_MONO
from utils.formato import formato_entero
from utils.ui import seccion, render_table, selector_vista


# Vigencias del cuatrienio
_VIGENCIAS = ["2024", "2025", "2026", "2027"]
_PALETA_VIGENCIA = {
    "2024": COLORS["blue_dark"],
    "2025": COLORS["cyan"],
    "2026": COLORS["orange_deep"],
    "2027": COLORS["brown"],
}

# Tooltip explicativo del cálculo
_TOOLTIP_FORMULA = (
    "Para cada vigencia: distribución = "
    "(Σ Meta Física Esperada de la vigencia) / (Σ Meta de cuatrienio). "
    "El denominador siempre es la meta total del cuatrienio del subconjunto "
    "considerado: si filtras por dependencia, se recalcula con sólo esas "
    "metas. Algunas metas son acumulativas y otras se reinician cada año, "
    "por eso la suma de los cuatro porcentajes puede no dar exactamente 100%."
)


# =========================================================================
# Cálculo de la distribución (general o filtrada)
# =========================================================================
def _calcular_distribucion(
    prog_ff: pl.DataFrame,
    homologacion: pl.DataFrame,
    dependencias_filtro: list[str] | None,
) -> tuple[pd.DataFrame, int]:
    """Devuelve (df con columnas Vigencia / Suma / Distribución, n_metas).

    Si ``dependencias_filtro`` está vacío o es None, usa todo el universo de
    metas. En caso contrario hace left join contra la homologación de
    secretarías (igual que el notebook) y filtra por las dependencias
    seleccionadas.
    """
    df = prog_ff
    if dependencias_filtro:
        df = (
            prog_ff
            .with_columns(pl.col("Responsable").str.strip_chars())
            .join(
                homologacion,
                left_on="Responsable", right_on="Responsable en PI", how="left",
            )
            .filter(pl.col("Dependencia Responsable").is_in(dependencias_filtro))
        )

    n_metas = df.get_column("Codigo Meta").count()
    total_cuatrienio = df.select(pl.col("Meta de cuatrienio").sum()).item() or 0

    filas = []
    for v in _VIGENCIAS:
        suma = df.select(pl.col(f"Meta Física Esperada {v}").sum()).item() or 0
        pct = (suma / total_cuatrienio) if total_cuatrienio else 0
        filas.append({"Vigencia": v, "Metas físicas": suma, "Distribución": pct})

    return pd.DataFrame(filas), n_metas


# =========================================================================
# Gráficos
# =========================================================================
def _fig_donut(df: pd.DataFrame, titulo: str) -> go.Figure:
    """Donut interactivo con la distribución por vigencia."""
    fig = go.Figure(data=[go.Pie(
        labels=df["Vigencia"],
        values=df["Distribución"],
        hole=0.6,
        marker=dict(
            colors=[_PALETA_VIGENCIA[v] for v in df["Vigencia"]],
            line=dict(color="#fff", width=2),
        ),
        textinfo="label+percent",
        textfont=dict(family=FONT_HEADING, size=14, color="#fff"),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Distribución: %{percent}<br>"
            "Metas físicas: %{customdata:,.0f}"
            "<extra></extra>"
        ),
        customdata=df["Metas físicas"],
        sort=False,
    )])
    fig.update_layout(
        height=440, showlegend=False,
        title=dict(text=titulo, x=0.0, xanchor="left"),
        margin=dict(t=60, b=20, l=20, r=20),
    )
    return fig


def _fig_comparativa(
    df_general: pd.DataFrame,
    df_seleccion: pd.DataFrame,
    etiqueta_seleccion: str,
) -> go.Figure:
    """Barras agrupadas: distribución general vs selección, por vigencia."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Plan completo",
        x=df_general["Vigencia"],
        y=df_general["Distribución"],
        marker_color=COLORS["blue_dark"],
        text=[f"{v*100:.1f}%" for v in df_general["Distribución"]],
        textposition="outside",
        hovertemplate=(
            "<b>Plan completo · %{x}</b><br>"
            "Distribución: %{y:.2%}<extra></extra>"
        ),
    ))
    fig.add_trace(go.Bar(
        name=etiqueta_seleccion,
        x=df_seleccion["Vigencia"],
        y=df_seleccion["Distribución"],
        marker_color=COLORS["orange_deep"],
        text=[f"{v*100:.1f}%" for v in df_seleccion["Distribución"]],
        textposition="outside",
        hovertemplate=(
            "<b>" + etiqueta_seleccion + " · %{x}</b><br>"
            "Distribución: %{y:.2%}<extra></extra>"
        ),
    ))
    fig.update_layout(
        height=460, barmode="group", bargap=0.28, bargroupgap=0.08,
        title=dict(
            text="Distribución por Vigencia · Plan vs Selección",
            x=0.0, xanchor="left",
        ),
        yaxis=dict(tickformat=".0%", title=None),
        xaxis=dict(title=None),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0),
        margin=dict(t=70, b=40, l=40, r=20),
    )
    return fig


# =========================================================================
# Bloque "chip" con el resumen de la selección
# =========================================================================
def _render_chip_resumen(etiqueta: str, n_dependencias: int, n_metas: int) -> None:
    """Indicador editorial del subconjunto que se está visualizando."""
    if n_dependencias == 0:
        chip_label = "Vista general"
        valor = f"{n_metas:,} metas del Plan"
    else:
        chip_label = etiqueta
        sufijo = "dependencia" if n_dependencias == 1 else "dependencias"
        valor = f"{n_metas:,} metas · {n_dependencias} {sufijo}"

    st.markdown(
        f"""
        <div style="background:#fff; border:1px solid var(--hairline);
                    border-left: 3px solid {COLORS['orange_deep']};
                    padding: 0.7rem 1rem 0.75rem 1rem; border-radius: 2px;
                    margin: 0.4rem 0 1rem 0;">
            <div style="font-family: {FONT_MONO}, monospace; font-size: 0.65rem;
                        letter-spacing: 0.18em; text-transform: uppercase;
                        color: {COLORS['orange_deep']}; font-weight: 600;
                        margin-bottom: 0.25rem;">
                {chip_label}
            </div>
            <div style="font-family: {FONT_HEADING}, sans-serif; font-size: 0.95rem;
                        color: var(--ink); font-weight: 500;">
                {valor}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================================
# Vista principal
# =========================================================================
def render_distribucion(filtro_vigencia: str, datos: dict, avances_fisicos: dict) -> None:
    """Renderiza la pestaña de Distribución de Metas con filtro por dependencia."""
    seccion(
        "03", "Distribución de Metas",
        "Peso relativo de la programación física en cada vigencia del cuatrienio.",
        tooltip=_TOOLTIPVISTA(),
    )

    prog_ff = datos["prog_fisica_financiera"]
    homologacion = datos["homologacion_secretarias"]

    # ---- Filtro por dependencia ----
    dependencias_disponibles = sorted(
        homologacion
        .select(pl.col("Dependencia Responsable").drop_nulls().unique())
        .to_series()
        .to_list()
    )

    seleccion = st.multiselect(
        "Filtrar por dependencia responsable",
        options=dependencias_disponibles,
        default=[],
        placeholder="Selecciona una o varias dependencias para acotar la vista",
        help=(
            "Las dependencias provienen de la tabla HomologacionSecretarias "
            "del Plan Indicativo. Si dejas el filtro vacío, se muestran las "
            "metas de todo el Plan."
        ),
    )

    # ---- Cálculos ----
    df_general, n_total = _calcular_distribucion(prog_ff, homologacion, None)
    df_sel, n_sel = _calcular_distribucion(prog_ff, homologacion, seleccion or None)

    # Etiqueta legible
    if seleccion:
        if len(seleccion) == 1:
            etiqueta_sel = seleccion[0]
        else:
            etiqueta_sel = f"{len(seleccion)} dependencias seleccionadas"
    else:
        etiqueta_sel = "Plan completo"

    _render_chip_resumen(etiqueta_sel, len(seleccion), n_sel)

    # Si hay filtro pero la selección no tiene metas, lo advertimos
    if seleccion and n_sel == 0:
        st.warning(
            "La selección no tiene metas físicas registradas en el Plan Indicativo."
        )
        return

    # ---- Selector de vista ----
    vista = selector_vista("vista_distr")

    if vista == "Tabla":
        # Solo porcentajes — sin la columna de suma
        if seleccion:
            df_tabla = pd.DataFrame({
                "Vigencia": df_general["Vigencia"],
                "Plan completo": df_general["Distribución"].values,
                etiqueta_sel: df_sel["Distribución"].values,
            })
            columnas = [
                {"key": "Vigencia",       "label": "Vigencia",       "type": "text"},
                {"key": "Plan completo",  "label": "Plan completo",  "type": "pctbar"},
                {"key": etiqueta_sel,     "label": etiqueta_sel,     "type": "pctbar"},
            ]
        else:
            df_tabla = pd.DataFrame({
                "Vigencia": df_general["Vigencia"],
                "Distribución": df_general["Distribución"].values,
            })
            columnas = [
                {"key": "Vigencia",     "label": "Vigencia",     "type": "text"},
                {"key": "Distribución", "label": "Distribución", "type": "pctbar"},
            ]
        render_table(df_tabla, columnas)
    else:
        # Gráfico interactivo
        if seleccion:
            # Comparativo: barras Plan completo vs selección
            st.plotly_chart(
                _fig_comparativa(df_general, df_sel, etiqueta_sel),
                use_container_width=True,
            )
            with st.expander("Ver donut de la selección", expanded=False):
                st.plotly_chart(
                    _fig_donut(df_sel, f"Distribución — {etiqueta_sel}"),
                    use_container_width=True,
                )
        else:
            st.plotly_chart(
                _fig_donut(df_general, "Distribución por Vigencia"),
                use_container_width=True,
            )

    # ---- Conteo de metas (siempre visible al final) ----
    st.markdown(" ")
    st.markdown("##### Conteo de Metas")
    a, b = st.columns(2)
    a.metric(
        "Total de indicadores de producto",
        formato_entero(avances_fisicos["numero_total_metas"]),
    )
    b.metric(
        f"Indicadores con programación en {filtro_vigencia}",
        formato_entero(avances_fisicos["numero_metas_prog_vigencia"]),
    )


# Se define después por claridad: tooltip del título de sección.
def _TOOLTIPVISTA() -> str:
    return (
        "Muestra cómo se reparte la programación física entre las cuatro "
        "vigencias del cuatrienio. " + _TOOLTIP_FORMULA
    )
