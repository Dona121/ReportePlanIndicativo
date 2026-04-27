"""
Descarga de archivos desde el repositorio en GitHub.

- ttl=3600: la caché expira automáticamente cada hora, así que si subes un
  archivo nuevo al repo basta con esperar (o usar el botón "Recargar datos").
- El cache-buster `_t=...` se añade en la URL al pulsar el botón para
  forzar bypass del CDN de GitHub raw.
"""
import streamlit as st
import requests


@st.cache_data(show_spinner=False, ttl=3600)
def descargar_desde_github(url: str) -> bytes:
    """Descarga el contenido binario de un archivo público en GitHub raw."""
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return r.content
