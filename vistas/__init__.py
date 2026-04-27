"""Bloques de interfaz del dashboard.

Cada submódulo expone una función `render_*` que se invoca desde el
orquestador principal (PlanIndicativo.py).
"""

from vistas.sidebar import render_sidebar
from vistas.masthead import render_masthead, render_kpis_cabecera
from vistas.ejecucion_fisica import render_ejecucion_fisica
from vistas.ejecucion_financiera import render_ejecucion_financiera
from vistas.distribucion import render_distribucion
from vistas.dependencia import render_dependencia
from vistas.proyectos import render_proyectos
from vistas.exportar import render_exportar
from vistas.footer import render_footer

__all__ = [
    "render_sidebar",
    "render_masthead",
    "render_kpis_cabecera",
    "render_ejecucion_fisica",
    "render_ejecucion_financiera",
    "render_distribucion",
    "render_dependencia",
    "render_proyectos",
    "render_exportar",
    "render_footer",
]
