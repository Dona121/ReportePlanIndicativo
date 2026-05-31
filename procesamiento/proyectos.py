"""
Extracción y preparación del inventario de proyectos/gestiones a partir
de la columna de texto del Plan Indicativo.

El Plan tiene cuatro columnas candidatas con texto libre:
    - PROYECTOS 2024
    - PROYECTOS 2025
    - PROYECTOS 2026                          (ejecutados / en ejecución)
    - PROYECTOS/GESTIONES PROGRAMADAS 2026    (programados de la vigencia)

Funciones expuestas:
    - construir_proyectos(datos, vigencia, modo='en_ejecucion'|'programados')
    - construir_dataframe_proyectos_listo(_datos, vigencia, modo=...)
    - columna_proyectos(vigencia, modo): resuelve la columna fuente.
"""
import streamlit as st
import polars as pl
import pandas as pd


# =========================================================================
# Resolución de la columna fuente según vigencia + modo
# =========================================================================
def columna_proyectos(vigencia: str, modo: str = "en_ejecucion") -> str:
    """Devuelve el nombre de columna del Plan Indicativo a usar.

    Para 2026 existen dos modos:
        - 'en_ejecucion' -> 'PROYECTOS 2026'
        - 'programados'  -> 'PROYECTOS/GESTIONES PROGRAMADAS 2026'

    Para 2024, 2025 y 2027 sólo existe 'PROYECTOS {vigencia}'.
    """
    if vigencia == "2026" and modo == "programados":
        return "PROYECTOS/GESTIONES PROGRAMADAS 2026"
    return f"PROYECTOS {vigencia}"


# =========================================================================
# Helpers privados
# =========================================================================
def _extraer_regex(expr: pl.Expr, patron: str) -> pl.Expr:
    """Extrae el primer grupo de captura del patrón ``patron`` y limpia espacios."""
    return expr.str.extract(patron, group_index=1).str.strip_chars()


def _normalizar_numero(expr: pl.Expr, col_fuente: str) -> pl.Expr:
    """Normaliza una cadena numérica extraída del texto del Plan Indicativo.

    Replica la versión nueva del notebook: para ``PROYECTOS 2025`` los valores
    ya vienen en formato US (punto decimal, sin separador de miles), así que
    se castean tal cual. Para cualquier otra vigencia (incluido
    ``PROYECTOS/GESTIONES PROGRAMADAS 2026``) se aplica un reemplazo masivo:
    coma decimal → punto y se eliminan los puntos de miles, convirtiendo
    "1.234,56" → "1234.56".
    """
    limpio = expr.str.strip_chars().str.replace_all(r"\s+", "")
    if col_fuente == "PROYECTOS 2025":
        valor = limpio
    else:
        valor = limpio.str.replace_many({",": ".", ".": ""})
    return valor.cast(pl.Float64, strict=False)


# =========================================================================
# Construcción del inventario
# =========================================================================
def construir_proyectos(
    datos: dict,
    vigencia: str,
    modo: str = "en_ejecucion",
) -> pl.DataFrame:
    """Extrae proyectos/gestiones desde la columna de texto del Plan Indicativo.

    Args:
        datos: dict que devuelve procesar_datos.
        vigencia: '2024' | '2025' | '2026' | '2027'.
        modo: 'en_ejecucion' (default) o 'programados'. Solo cambia el
              comportamiento cuando vigencia='2026'.
    """
    prog_ff = datos["prog_fisica_financiera"]
    col_proyecto = columna_proyectos(vigencia, modo)

    if col_proyecto not in prog_ff.columns:
        return pl.DataFrame()

    texto = pl.col(col_proyecto)

    patron_bpin = r"\((?i:bpin)\s*:\s*([^()]+?)\s*\)"
    patron_tipo_banco = r"\((?i:tipo\s+de\s+banco)\s*:\s*([^()]+?)\s*\)"
    patron_meta = (
        r"\((?i:(?:"
        r"meta\s+del\s+proyecto|"
        r"meta\s+de\s+la\s+gesti(?:ón|on)|"
        r"meta\s+total\s+del\s+indicador|"
        r"meta\s+total\s+de\s+la\s+vigencia|"
        r"meta\s+total\s+del\s+proyecto|"
        r"meta\s+programada|"
        r"meta\s+de\s+la\s+vigencia"
        r"))\s*:\s*([^()]+?)\s*\)"
    )
    # NOTA: el notebook usa literal "2024" en este patrón.
    # Aquí lo generalizamos a \d{4} para que también funcione en 2025/2026.
    patron_ejecutado = (
        r"\((?i:(?:"
        r"ejecuci(?:ón|on)\s+\d{4}|"
        r"ejecutado|"
        r"ejecuci(?:ón|on)"
        r"))\s*:\s*([^()]+?)\s*\)"
    )
    patron_estado = r"\((?i:estado\s+en\s+portafolio)\s*:\s*([^()]+?)\s*\)"
    patron_bloques_info = (
        r"\((?i:(?:"
        r"bpin|"
        r"tipo\s+de\s+banco|"
        r"meta\s+del\s+proyecto|"
        r"meta\s+de\s+la\s+gesti(?:ón|on)|"
        r"meta\s+total\s+del\s+indicador|"
        r"meta\s+total\s+de\s+la\s+vigencia|"
        r"meta\s+total\s+del\s+proyecto|"
        r"meta\s+programada|"
        r"meta\s+de\s+la\s+vigencia|"
        r"ejecuci(?:ón|on)\s+\d{4}|"
        r"ejecutado|"
        r"ejecuci(?:ón|on)|"
        r"estado\s+en\s+portafolio"
        r"))\s*:\s*[^()]+?\s*\)"
    )

    return (
        prog_ff
        .select(
            "Codigo Meta", "Línea Estratégica", "Sector PDD", "Programa PDD",
            "Indicador de producto principal", "Código del indicador principal",
            col_proyecto,
        )
        .with_columns(
            pl.col(col_proyecto).fill_null("").cast(pl.String).alias(col_proyecto)
        )
        .filter(pl.col(col_proyecto) != "", pl.col(col_proyecto) != "0")
        .with_columns(
            pl.col(col_proyecto)
            .str.replace_all(r"\n\s*\n+", "\n\n")
            .str.split("\n\n")
            .alias(col_proyecto)
        )
        .explode(col_proyecto)
        .with_columns(pl.col(col_proyecto).str.strip_chars().alias(col_proyecto))
        .filter(pl.col(col_proyecto) != "", pl.col(col_proyecto) != "0")
        .with_columns(
            texto.str.replace_all(patron_bloques_info, "")
                 .str.replace_all(r"\s+", " ")
                 .str.strip_chars()
                 .alias("Nombre del Proyecto"),
            _extraer_regex(texto, patron_bpin).alias("BPIN"),
            _extraer_regex(texto, patron_tipo_banco).alias("Tipo de Banco"),
            _normalizar_numero(_extraer_regex(texto, patron_meta), col_proyecto).alias("Meta"),
            _normalizar_numero(_extraer_regex(texto, patron_ejecutado), col_proyecto).alias("Ejecutado"),
            _extraer_regex(texto, patron_estado).alias("Estado en portafolio"),
        )
        .drop(col_proyecto)
    )


@st.cache_data(show_spinner=False)
def construir_dataframe_proyectos_listo(
    _datos: dict,
    vigencia: str,
    modo: str = "en_ejecucion",
) -> pd.DataFrame:
    """Toma construir_proyectos y agrega columnas calculadas (Indicador, Avance)
    en el formato listo para mostrar/exportar.

    El parámetro _datos lleva underscore para indicar a Streamlit que no debe
    intentar hashearlo (es un dict de polars DataFrames, no hashable).
    El cache se invalida automáticamente cuando cambian los datos porque la
    función procesar_datos también está cacheada y retorna un nuevo objeto.
    """
    df = construir_proyectos(_datos, vigencia, modo).to_pandas()
    if df.empty:
        return df

    df["Avance"] = df.apply(
        lambda r: (r["Ejecutado"] / r["Meta"])
        if pd.notna(r["Meta"]) and pd.notna(r["Ejecutado"]) and r["Meta"] != 0
        else None,
        axis=1,
    )

    def _fmt(row):
        codigo = row.get("Código del indicador principal")
        nombre = row.get("Indicador de producto principal")
        codigo = "" if pd.isna(codigo) else str(codigo).strip()
        nombre = "" if pd.isna(nombre) else str(nombre).strip()
        if codigo and nombre:
            return f"{codigo} — {nombre}"
        return codigo or nombre or ""

    df["Indicador"] = df.apply(_fmt, axis=1)
    return df
