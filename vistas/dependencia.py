"""
Pestaña 04 — Ejecución por Dependencia.

Lista el desempeño de cada secretaría o dependencia con metas en la
vigencia, junto con su avance acumulado del cuatrienio.
"""
import streamlit as st

from utils.ui import seccion, render_table


def render_dependencia(filtro_vigencia: str, ejec_dependencia) -> None:
    """Renderiza la pestaña de Ejecución por Dependencia."""
    seccion(
        "04", "Ejecución por Dependencia",
        "Desempeño de las dependencias responsables de la ejecución del Plan de Desarrollo.",
        tooltip=(
            "Para cada secretaría o dependencia se reporta cuántas metas "
            "tiene programadas en la vigencia, cuántas alcanzaron el 100% "
            "(categoría 'Superior'), su avance promedio en la vigencia y su "
            "avance promedio acumulado del cuatrienio. Las dependencias se "
            "homologan según la tabla oficial del Plan Indicativo, que "
            "permite agrupar variantes de nombre y, cuando aplica, marcar "
            "responsabilidades compartidas entre varias secretarías."
        ),
    )

    df_dep = ejec_dependencia.to_pandas()

    varias_opciones = sorted([x for x in df_dep["Varias Secretarías"].dropna().unique()])
    if varias_opciones:
        filtro_sec = st.multiselect(
            "Filtrar por agrupación (Varias Secretarías)",
            options=varias_opciones, default=[],
        )
        if filtro_sec:
            df_dep = df_dep[df_dep["Varias Secretarías"].isin(filtro_sec)]

    if df_dep.empty:
        st.info("No hay dependencias con metas programadas en la vigencia seleccionada.")
        return

    # Ordenamos por avance descendente para que la tabla se lea de mejor a peor
    df_dep = df_dep.sort_values(
        f"Porcentaje de Ejecución {filtro_vigencia}",
        ascending=False, na_position="last",
    )

    columnas_dep = [
        {"key": "Dependencia Responsable", "label": "Dependencia", "type": "text"},
        {"key": f"Metas Programadas {filtro_vigencia}", "label": f"Programadas {filtro_vigencia}", "type": "int"},
        {"key": f"Metas Cumplidas al 100% {filtro_vigencia}", "label": "Cumplidas 100%", "type": "int"},
        {"key": f"Porcentaje de Ejecución {filtro_vigencia}", "label": f"Avance {filtro_vigencia}", "type": "pctbar"},
        {"key": "Porcentaje de Ejecución Acumulada", "label": "Avance acumulado", "type": "pctbar"},
    ]
    render_table(df_dep, columnas_dep)
