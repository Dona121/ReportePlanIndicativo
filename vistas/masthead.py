"""
Masthead editorial y KPIs de cabecera.
"""
import streamlit as st

from config.tooltips import TOOLTIPS
from utils.formato import formato_pesos, formato_porcentaje


def render_masthead(filtro_vigencia: str) -> None:
    """Renderiza el bloque editorial principal del dashboard."""
    st.markdown(
        f"""
        <div class="masthead">
            <div>
                <div class="eyebrow">Informe de Seguimiento  /  Vigencia {filtro_vigencia}</div>
                <h1>Plan <em>Indicativo</em></h1>
            </div>
            <div class="edition">
                <strong>Vigencia en análisis</strong><br/>
                {filtro_vigencia} · Cuatrienio 2024—2027<br/>
                Ejecución física y financiera
            </div>
        </div>
        <div class="subhead">
            Instrumento de seguimiento al cumplimiento de metas del Plan de Desarrollo.
            Consolida la programación y ejecución de los indicadores de producto y sus fuentes de financiación.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpis_cabecera(
    filtro_vigencia: str,
    prog_vig: float,
    ejec_vig: float,
    pct_vig: float,
    prog_cuatri: float,
    ejec_acum: float,
    pct_cuatri: float,
) -> None:
    """Tarjetas KPI principales bajo el masthead."""
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        f"Programación {filtro_vigencia}",
        formato_pesos(prog_vig),
        help=TOOLTIPS["prog_vigencia"],
    )
    c2.metric(
        f"Ejecución {filtro_vigencia}",
        formato_pesos(ejec_vig),
        formato_porcentaje(pct_vig),
        help=TOOLTIPS["ejec_vigencia"],
    )
    c3.metric(
        "Programación Cuatrienio",
        formato_pesos(prog_cuatri),
        help=TOOLTIPS["prog_cuatrienio"],
    )
    c4.metric(
        "Ejecución Acumulada",
        formato_pesos(ejec_acum),
        formato_porcentaje(pct_cuatri),
        help=TOOLTIPS["ejec_acumulada"],
    )

    st.markdown("<hr/>", unsafe_allow_html=True)
