"""
Pestaña 05 — Proyectos.

Lista los proyectos y gestiones extraídos del texto del Plan Indicativo
para la vigencia seleccionada. Para 2026 permite alternar entre el
listado de proyectos *en ejecución* (columna PROYECTOS 2026) y los
proyectos *programados* (columna PROYECTOS/GESTIONES PROGRAMADAS 2026).

Filtros disponibles: Línea Estratégica, Sector PDD y Tipo de Banco.
Botones de descarga: vigencia actual y consolidado del cuatrienio (que
ahora incluye una hoja extra con los programados 2026).
"""
import pandas as pd
import streamlit as st

from config.styles import COLORS, FONT_MONO
from config.tooltips import TOOLTIPS
from utils.formato import formato_entero
from utils.ui import seccion, render_table
from procesamiento.proyectos import (
    construir_dataframe_proyectos_listo,
    columna_proyectos,
)
from exportaciones.excel_proyectos import generar_excel_proyectos


# Etiquetas de los dos modos disponibles para 2026
_MODOS_2026 = {
    "En ejecución": "en_ejecucion",
    "Programados": "programados",
}


def _render_pildora_modo(modo_label: str, col_fuente: str) -> None:
    """Tarjeta pequeña que indica la columna fuente que se está leyendo."""
    st.markdown(
        f"""
        <div style="background:#fff; border:1px solid var(--hairline);
                    border-left: 3px solid {COLORS['blue']};
                    padding: 0.55rem 0.9rem; border-radius: 2px;
                    margin: 0.2rem 0 1rem 0; display: inline-block;">
            <span style="font-family: {FONT_MONO}, monospace; font-size: 0.66rem;
                         letter-spacing: 0.16em; text-transform: uppercase;
                         color: var(--ink-mute); margin-right: 0.5rem;">Fuente</span>
            <span style="font-family: {FONT_MONO}, monospace; font-size: 0.8rem;
                         color: var(--ink); font-weight: 600;">{modo_label}</span>
            <span style="font-family: {FONT_MONO}, monospace; font-size: 0.72rem;
                         color: var(--ink-mute); margin-left: 0.8rem;">{col_fuente}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_proyectos(filtro_vigencia: str, datos: dict) -> None:
    """Renderiza la pestaña de Proyectos."""
    seccion(
        "05", "Proyectos",
        "Inventario de proyectos y gestiones asociadas a las metas del Plan de Desarrollo, "
        "extraídos de la columna de texto del Plan Indicativo.",
        tooltip=(
            "Lista los proyectos y gestiones registrados para la vigencia "
            "en el Plan Indicativo. De cada uno se extraen el código BPIN, "
            "el indicador de producto al que aporta, el tipo de banco al "
            "que pertenece (Banco de Proyectos, Banco de Programas, etc.), "
            "la meta física comprometida y lo ejecutado. El avance se "
            "reporta en unidades físicas (no en pesos): qué tanto del "
            "producto o servicio comprometido se entregó."
        ),
    )

    # =====================================================================
    # Selector de modo (sólo aplica a 2026)
    # =====================================================================
    if filtro_vigencia == "2026":
        st.markdown("##### Tipo de listado")
        modo_label = st.radio(
            "Tipo de listado",
            options=list(_MODOS_2026.keys()),
            horizontal=True,
            key="proy_modo_2026",
            label_visibility="collapsed",
            help=(
                "**En ejecución** — Proyectos y gestiones que ya están "
                "corriendo (columna `PROYECTOS 2026`).\n\n"
                "**Programados** — Proyectos planificados para la vigencia "
                "que aún no inician (columna `PROYECTOS/GESTIONES "
                "PROGRAMADAS 2026`)."
            ),
        )
        modo = _MODOS_2026[modo_label]
    else:
        modo_label = "En ejecución"
        modo = "en_ejecucion"

    col_fuente = columna_proyectos(filtro_vigencia, modo)
    _render_pildora_modo(modo_label, col_fuente)

    # =====================================================================
    # Construcción del DataFrame de proyectos
    # =====================================================================
    df_proy = construir_dataframe_proyectos_listo(datos, filtro_vigencia, modo)

    # ---- Botones de descarga (siempre visibles arriba) ----
    st.markdown("##### Descargar inventario")
    dl1, dl2, _ = st.columns([1, 1, 2])

    with dl1:
        if not df_proy.empty:
            cols_export = [
                "Codigo Meta", "Línea Estratégica", "Sector PDD", "Programa PDD",
                "Nombre del Proyecto", "BPIN", "Indicador", "Tipo de Banco",
                "Meta", "Ejecutado", "Avance",
            ]
            df_export_vig = df_proy.reindex(columns=[c for c in cols_export if c in df_proy.columns])
            subtitulo_export = (
                f"Inventario completo extraído del Plan Indicativo · {modo_label}"
                if filtro_vigencia == "2026"
                else "Inventario completo extraído del Plan Indicativo"
            )
            xlsx_vig = generar_excel_proyectos(
                df_export_vig,
                titulo=f"Proyectos y Gestiones — Vigencia {filtro_vigencia}",
                subtitulo=subtitulo_export,
            )
            sufijo_archivo = "_programados" if (filtro_vigencia == "2026" and modo == "programados") else ""
            st.download_button(
                f"Descargar vigencia {filtro_vigencia}",
                data=xlsx_vig,
                file_name=f"proyectos_{filtro_vigencia}{sufijo_archivo}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_proy_vig",
                use_container_width=True,
            )
        else:
            st.button(f"Descargar vigencia {filtro_vigencia}", disabled=True,
                      use_container_width=True, key="dl_proy_vig_disabled")

    with dl2:
        # Consolidado: las cuatro vigencias + los programados 2026
        try:
            partes = []
            # PROYECTOS 2024..2027 (en ejecución / regular)
            for v in ["2024", "2025", "2026", "2027"]:
                df_v = construir_dataframe_proyectos_listo(datos, v, "en_ejecucion")
                if not df_v.empty:
                    df_v = df_v.copy()
                    df_v.insert(0, "Vigencia PI", v)
                    partes.append(df_v)
            # Programados 2026
            df_prog_2026 = construir_dataframe_proyectos_listo(datos, "2026", "programados")
            if not df_prog_2026.empty:
                df_prog_2026 = df_prog_2026.copy()
                df_prog_2026.insert(0, "Vigencia PI", "2026 (Programados)")
                partes.append(df_prog_2026)

            if partes:
                df_consol = pd.concat(partes, ignore_index=True)
                cols_consol = [
                    "Vigencia PI", "Codigo Meta", "Línea Estratégica", "Sector PDD",
                    "Programa PDD", "Nombre del Proyecto", "BPIN", "Indicador",
                    "Tipo de Banco", "Meta", "Ejecutado", "Avance",
                ]
                df_consol = df_consol.reindex(columns=[c for c in cols_consol if c in df_consol.columns])
                xlsx_all = generar_excel_proyectos(
                    df_consol,
                    titulo="Proyectos y Gestiones — Consolidado del Cuatrienio",
                    subtitulo=(
                        "Inventario unificado de todas las vigencias del Plan "
                        "(2024–2027) e incluye los Programados 2026."
                    ),
                )
                st.download_button(
                    "Descargar todas las vigencias",
                    data=xlsx_all,
                    file_name="proyectos_2024-2027.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_proy_all",
                    use_container_width=True,
                )
            else:
                st.button("Descargar todas las vigencias", disabled=True,
                          use_container_width=True, key="dl_proy_all_disabled")
        except Exception as e:
            st.error(f"No se pudo generar el consolidado: {e}")

    st.markdown("<hr/>", unsafe_allow_html=True)

    if df_proy.empty:
        st.info(
            f"No hay proyectos ni gestiones registrados para la vigencia "
            f"{filtro_vigencia} · {modo_label}."
        )
        return

    # =====================================================================
    # KPIs por tipo de banco
    # =====================================================================
    total_registros = len(df_proy)

    conteo_bancos = (
        df_proy["Tipo de Banco"].fillna("Sin clasificar")
        .replace("", "Sin clasificar")
        .value_counts()
    )
    tipos_top = conteo_bancos.head(3)

    columnas_kpi = st.columns(1 + len(tipos_top))
    columnas_kpi[0].metric(
        "Total proyectos/gestiones", formato_entero(total_registros),
        help=TOOLTIPS["total_proyectos_gestiones"],
    )
    for i, (banco, conteo) in enumerate(tipos_top.items(), start=1):
        columnas_kpi[i].metric(banco, formato_entero(conteo))

    st.markdown(" ")

    # =====================================================================
    # Filtros del usuario
    # =====================================================================
    fp1, fp2, fp3 = st.columns(3)
    with fp1:
        lineas_p = ["(Todas)"] + sorted(df_proy["Línea Estratégica"].dropna().unique().tolist())
        sel_linea_p = st.selectbox("Línea Estratégica", lineas_p, key="proy_linea")
    with fp2:
        df_tp = df_proy if sel_linea_p == "(Todas)" else df_proy[df_proy["Línea Estratégica"] == sel_linea_p]
        sectores_p = ["(Todos)"] + sorted(df_tp["Sector PDD"].dropna().unique().tolist())
        sel_sector_p = st.selectbox("Sector PDD", sectores_p, key="proy_sector")
    with fp3:
        df_tp2 = df_tp if sel_sector_p == "(Todos)" else df_tp[df_tp["Sector PDD"] == sel_sector_p]
        bancos = ["(Todos)"] + sorted([b for b in df_tp2["Tipo de Banco"].dropna().unique().tolist() if b])
        sel_banco = st.selectbox("Tipo de Banco", bancos, key="proy_banco")

    df_proy_f = df_proy.copy()
    if sel_linea_p != "(Todas)":
        df_proy_f = df_proy_f[df_proy_f["Línea Estratégica"] == sel_linea_p]
    if sel_sector_p != "(Todos)":
        df_proy_f = df_proy_f[df_proy_f["Sector PDD"] == sel_sector_p]
    if sel_banco != "(Todos)":
        df_proy_f = df_proy_f[df_proy_f["Tipo de Banco"] == sel_banco]

    st.caption(f"Mostrando {len(df_proy_f):,} proyectos/gestiones")

    columnas_proy = [
        {"key": "Codigo Meta", "label": "Meta", "type": "text"},
        {"key": "Nombre del Proyecto", "label": "Proyecto / Gestión", "type": "text"},
        {"key": "BPIN", "label": "BPIN", "type": "text"},
        {"key": "Indicador", "label": "Indicador de Producto", "type": "text"},
        {"key": "Tipo de Banco", "label": "Banco", "type": "text"},
        {"key": "Meta", "label": "Meta física", "type": "num2"},
        {"key": "Ejecutado", "label": "Ejecutado", "type": "num2"},
        {"key": "Avance", "label": "Avance", "type": "pctbar"},
    ]
    render_table(df_proy_f.head(200), columnas_proy)

    if len(df_proy_f) > 200:
        st.caption(
            "La tabla muestra los primeros 200 registros. "
            "Usa los botones de descarga para el listado completo."
        )
