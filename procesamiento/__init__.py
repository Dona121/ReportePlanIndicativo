"""Capa de procesamiento de datos.

Submódulos:
    lectura    -> lectura de los Excel y construcción de la base unificada.
    reportes   -> agregaciones por vigencia (financieras y avances físicos).
    proyectos  -> extracción y preparación del inventario de proyectos.
"""

from procesamiento.lectura import procesar_datos, programacion_financiera
from procesamiento.reportes import (
    construir_ejecucion_financ_tipo,
    construir_ejecucion_acumulada_tipo,
    construir_prog_financ_categorias,
    construir_ejec_por_dependencia,
    construir_avances_fisicos,
)
from procesamiento.proyectos import (
    construir_proyectos,
    construir_dataframe_proyectos_listo,
)

__all__ = [
    "procesar_datos",
    "programacion_financiera",
    "construir_ejecucion_financ_tipo",
    "construir_ejecucion_acumulada_tipo",
    "construir_prog_financ_categorias",
    "construir_ejec_por_dependencia",
    "construir_avances_fisicos",
    "construir_proyectos",
    "construir_dataframe_proyectos_listo",
]
