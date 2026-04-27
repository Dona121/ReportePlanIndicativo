"""
Pie de página corporativo.
"""
import streamlit as st

from config.styles import COLORS, FONT_MONO


def render_footer() -> None:
    """Renderiza el pie de página del dashboard."""
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style='display: flex; justify-content: space-between; align-items: center;
                    padding: 0.6rem 0 1.2rem 0; font-size: 0.75rem; color: {COLORS["blue_dark"]};
                    font-family: {FONT_MONO}, monospace; letter-spacing: 0.08em;
                    border-top: 1px solid #e3e3e1;'>
            <span>Plan Indicativo · Sistema de Seguimiento 2024—2027</span>
            <span>Construido con Streamlit · Polars · Plotly</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
