"""
Pestaña 06 — Exportar.

Permite generar y descargar un Excel consolidado con toda la información
del tablero, formateado con la identidad visual corporativa.
"""
import streamlit as st

from config.styles import COLORS, FONT_BODY, FONT_DISPLAY, FONT_HEADING, FONT_MONO
from utils.ui import seccion
from exportaciones.excel_reporte import generar_reporte_excel


def render_exportar(
    filtro_vigencia: str,
    datos: dict,
    ejec_financ_tipo,
    ejec_acumulada_tipo,
    categorias_pdd,
    ejec_dependencia,
    avances_fisicos,
) -> None:
    """Renderiza la pestaña de Exportar."""
    seccion(
        "06", "Exportar",
        "Descarga un archivo Excel consolidado con toda la información del tablero, "
        "formateado con la identidad visual corporativa.",
    )

    # Tarjeta descriptiva de lo que incluye el archivo
    st.markdown(
        f"""
        <div style='background:#fff; border:1px solid var(--hairline);
                    border-left: 3px solid {COLORS["orange_deep"]};
                    padding: 1.2rem 1.4rem; border-radius: 2px; margin-bottom: 1.2rem;'>
            <div style='font-family: {FONT_HEADING}, sans-serif; font-size: 0.72rem;
                        text-transform: uppercase; letter-spacing: 0.14em;
                        color: {COLORS["orange_deep"]}; font-weight: 700; margin-bottom: 0.5rem;'>
                Contenido del archivo
            </div>
            <div style='font-family: {FONT_BODY}, sans-serif; font-size: 0.9rem;
                        color: var(--ink); line-height: 1.7;'>
                El archivo incluye ocho hojas: <strong>Portada</strong> con los indicadores
                clave de la vigencia, <strong>Financiera por Fuente</strong>,
                <strong>Financiera Cuatrienio</strong>, <strong>Por Categoría PDD</strong>
                (líneas, sectores y programas), <strong>Ejecución Física</strong> con
                los avances por línea y sector, <strong>Por Dependencia</strong>,
                <strong>Detalle por Meta</strong> y <strong>Proyectos</strong>.
                Todas las tablas se entregan con la paleta corporativa, tipografías
                Montserrat y Open Sans, y formatos numéricos listos para imprimir.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_gen, col_info = st.columns([1, 2])
    with col_gen:
        st.markdown(
            f"""
            <div style='font-family: {FONT_HEADING}, sans-serif; font-size: 0.72rem;
                        text-transform: uppercase; letter-spacing: 0.14em;
                        color: var(--ink-mute); font-weight: 600; margin-bottom: 0.6rem;'>
                Vigencia a exportar
            </div>
            <div style='font-family: {FONT_DISPLAY}, {FONT_HEADING}, sans-serif;
                        font-size: 2.4rem; color: {COLORS["blue_dark"]}; font-weight: 700;
                        line-height: 1;'>
                {filtro_vigencia}
            </div>
            <div style='font-family: {FONT_MONO}, monospace; font-size: 0.72rem;
                        color: var(--ink-mute); margin-top: 0.4rem;'>
                Cambia la vigencia desde la barra lateral.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_info:
        # Botón de generación y descarga
        if st.button("Generar archivo Excel", use_container_width=False, key="gen_xlsx"):
            with st.spinner("Generando archivo Excel con formato corporativo..."):
                try:
                    xlsx_bytes = generar_reporte_excel(
                        datos, filtro_vigencia,
                        ejec_financ_tipo, ejec_acumulada_tipo, categorias_pdd,
                        ejec_dependencia, avances_fisicos,
                    )
                    st.session_state["xlsx_bytes"] = xlsx_bytes
                    st.session_state["xlsx_vigencia"] = filtro_vigencia
                    st.success("Archivo generado correctamente. Usa el botón de descarga.")
                except Exception as e:
                    st.error(f"Error al generar el archivo: {e}")
                    st.exception(e)

        if (
            st.session_state.get("xlsx_bytes")
            and st.session_state.get("xlsx_vigencia") == filtro_vigencia
        ):
            st.download_button(
                "Descargar archivo Excel",
                data=st.session_state["xlsx_bytes"],
                file_name=f"Plan_Indicativo_{filtro_vigencia}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=False,
                key="dl_xlsx",
            )
