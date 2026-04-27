"""
Pestaña 05 — Proyectos.

Lista los proyectos y gestiones extraídos del texto del Plan Indicativo
para la vigencia y permite descargar el inventario en Excel.
"""
import pandas as pd
import streamlit as st

from config.tooltips import TOOLTIPS
from utils.formato import formato_entero
from utils.ui import seccion, render_table
from procesamiento.proyectos import construir_dataframe_proyectos_listo
from exportaciones.excel_proyectos import generar_excel_proyectos


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

    df_proy = construir_dataframe_proyectos_listo(datos, filtro_vigencia)

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
            xlsx_vig = generar_excel_proyectos(
                df_export_vig,
                titulo=f"Proyectos y Gestiones — Vigencia {filtro_vigencia}",
                subtitulo="Inventario completo extraído del Plan Indicativo",
            )
            st.download_button(
                f"Descargar vigencia {filtro_vigencia}",
                data=xlsx_vig,
                file_name=f"proyectos_{filtro_vigencia}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_proy_vig",
                use_container_width=True,
            )
        else:
            st.button(f"Descargar vigencia {filtro_vigencia}", disabled=True,
                      use_container_width=True, key="dl_proy_vig_disabled")

    with dl2:
        # Consolidado de las cuatro vigencias del Plan
        try:
            partes = []
            for v in ["2024", "2025", "2026", "2027"]:
                df_v = construir_dataframe_proyectos_listo(datos, v)
                if not df_v.empty:
                    df_v = df_v.copy()
                    df_v.insert(0, "Vigencia PI", v)
                    partes.append(df_v)
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
                    subtitulo="Inventario unificado de todas las vigencias del Plan (2024–2027)",
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
        st.info(f"No hay proyectos ni gestiones registrados para la vigencia {filtro_vigencia}.")
        return

    # ---- Conteo por tipo de banco (sustituye a las tarjetas monetarias) ----
    total_registros = len(df_proy)

    conteo_bancos = (
        df_proy["Tipo de Banco"].fillna("Sin clasificar")
        .replace("", "Sin clasificar")
        .value_counts()
    )
    # Tomamos los tres tipos de banco con más registros + total general
    tipos_top = conteo_bancos.head(3)

    columnas_kpi = st.columns(1 + len(tipos_top))
    columnas_kpi[0].metric(
        "Total proyectos/gestiones", formato_entero(total_registros),
        help=TOOLTIPS["total_proyectos_gestiones"],
    )
    for i, (banco, conteo) in enumerate(tipos_top.items(), start=1):
        columnas_kpi[i].metric(banco, formato_entero(conteo))

    st.markdown(" ")

    # ---- Filtros ----
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
