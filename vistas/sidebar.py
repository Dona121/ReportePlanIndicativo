"""
Sidebar del dashboard.

Ofrece:
    - botón global para recargar datos del repositorio (limpia caché y rerun);
    - selector de modo de carga (repo vs subir archivos);
    - file uploaders para Plan Indicativo y archivos 2026;
    - selectbox de vigencia de análisis.

Devuelve una tupla ``(archivos_bytes, filtro_vigencia)``.
"""
import streamlit as st

from config.styles import COLORS, FONT_DISPLAY, FONT_HEADING, FONT_BODY, FONT_MONO
from config.data_sources import GH, ARCHIVOS_CERRADOS, ARCHIVOS_ACTUALIZABLES
from utils.github import descargar_desde_github


def render_sidebar() -> tuple[dict, str]:
    """Renderiza la sidebar y devuelve los bytes de cada archivo y la vigencia."""
    st.sidebar.markdown(
        f"""
        <div style='padding: 0.8rem 0 1.2rem 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 1rem;'>
            <div style='font-family: {FONT_MONO}, monospace; font-size: 0.68rem; letter-spacing: 0.22em;
                        color: {COLORS["orange"]}; text-transform: uppercase;'>
                Plan de Desarrollo
            </div>
            <div style='font-family: {FONT_DISPLAY}, {FONT_HEADING}, sans-serif; font-size: 2rem;
                        font-weight: 400; color: #fff; line-height: 1; margin-top: 0.25rem;'>
                2024<span style='color: {COLORS["orange"]}'>—</span>2027
            </div>
            <div style='font-family: {FONT_HEADING}, sans-serif; font-size: 0.7rem;
                        color: #b9c6d6; margin-top: 0.5rem; letter-spacing: 0.14em;
                        text-transform: uppercase; font-weight: 500;'>
                Sistema de Seguimiento
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("### Archivos actualizables")
    st.sidebar.markdown(
        f"""
        <div style='font-family: {FONT_BODY}, sans-serif; font-size: 0.78rem;
                    color: #b9c6d6; margin: -0.4rem 0 0.8rem 0; line-height: 1.5;'>
            Las vigencias 2024 y 2025 ya cerraron y se consultan del repositorio.
            Sube aquí los archivos de 2026 y el Plan Indicativo.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Botón global de recarga: siempre visible, independiente del modo de carga.
    # Limpia toda la caché (descargas + procesamiento) para forzar lectura fresca.
    if st.sidebar.button(
        "Recargar datos del repositorio",
        use_container_width=True,
        help="Limpia la caché y vuelve a descargar los archivos desde GitHub",
    ):
        st.cache_data.clear()
        # Limpia también el archivo Excel pre-generado, por si la vigencia cambia
        st.session_state.pop("xlsx_bytes", None)
        st.session_state.pop("xlsx_vigencia", None)
        st.rerun()

    modo_carga = st.sidebar.radio(
        "Modo",
        options=["Usar datos del repositorio", "Subir archivos 2026 y Plan Indicativo"],
        index=0,
        label_visibility="collapsed",
    )

    archivos_bytes: dict = {}

    # Vigencias cerradas: siempre del repo
    try:
        with st.spinner("Cargando vigencias cerradas (2024-2025)..."):
            for key in ARCHIVOS_CERRADOS:
                archivos_bytes[key] = descargar_desde_github(GH[key])
    except Exception as e:
        st.sidebar.error(f"Error al cargar vigencias cerradas: {e}")
        st.stop()

    # Archivos actualizables
    if modo_carga == "Usar datos del repositorio":
        try:
            with st.spinner("Descargando Plan Indicativo y archivos 2026..."):
                for key in ARCHIVOS_ACTUALIZABLES:
                    archivos_bytes[key] = descargar_desde_github(GH[key])
        except Exception as e:
            st.sidebar.error(f"Error al descargar: {e}")
            st.stop()
    else:
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Plan Indicativo**")
        pi_file = st.sidebar.file_uploader(
            "Plan Indicativo 2024-2027",
            type=["xlsx"], key="pi_upload",
            label_visibility="collapsed",
        )

        st.sidebar.markdown("**Hacienda 2026**")
        h26_file = st.sidebar.file_uploader(
            "Ejecución Hacienda 2026",
            type=["xlsx"], key="h26_upload",
            label_visibility="collapsed",
        )

        st.sidebar.markdown("**Regalías 2026**")
        r26_file = st.sidebar.file_uploader(
            "Pagos Regalías 2026",
            type=["xlsx"], key="r26_upload",
            label_visibility="collapsed",
        )

        if not (pi_file and h26_file and r26_file):
            st.warning(
                "Sube los tres archivos requeridos: Plan Indicativo, Hacienda 2026 y Regalías 2026."
            )
            st.stop()

        archivos_bytes["pi"] = pi_file.getvalue()
        archivos_bytes["h26"] = h26_file.getvalue()
        archivos_bytes["r26"] = r26_file.getvalue()

    st.sidebar.markdown("### Vigencia de análisis")
    filtro_vigencia = st.sidebar.selectbox(
        "Vigencia",
        options=["2024", "2025", "2026"],
        index=2,
        label_visibility="collapsed",
    )

    return archivos_bytes, filtro_vigencia
