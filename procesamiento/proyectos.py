"""
Extracción y preparación del inventario de proyectos/gestiones a partir
de la columna de texto del Plan Indicativo.

Funciones expuestas:
    - construir_proyectos(datos, vigencia)
    - construir_dataframe_proyectos_listo(_datos, vigencia)
"""
import streamlit as st
import polars as pl
import pandas as pd


# =========================================================================
# Helpers privados
# =========================================================================
def _extraer_regex(expr: pl.Expr, patron: str) -> pl.Expr:
    """Extrae el primer grupo de captura del patrón ``patron`` y limpia espacios."""
    return expr.str.extract(patron, group_index=1).str.strip_chars()


def _normalizar_numero(expr: pl.Expr) -> pl.Expr:
    """Normaliza una cadena numérica con separadores variados a Float64."""
    x = expr.str.strip_chars().str.replace_all(r"\s+", "")
    return (
        pl.when(x.is_null() | (x == ""))
        .then(pl.lit(None))
        .when(x.str.contains(r"^\d{1,3}(?:\.\d{3})+,\d+$"))
        .then(x.str.replace_all(r"\.", "").str.replace_all(",", "."))
        .when(x.str.contains(r"^\d{1,3}(?:,\d{3})+\.\d+$"))
        .then(x.str.replace_all(",", ""))
        .when(x.str.contains(r"^\d{1,3}(?:\.\d{3})+$"))
        .then(x.str.replace_all(r"\.", ""))
        .when(x.str.contains(r"^\d{1,3}(?:,\d{3})+$"))
        .then(x.str.replace_all(",", ""))
        .when(x.str.contains(r",") & ~x.str.contains(r"\."))
        .then(x.str.replace_all(",", "."))
        .otherwise(x)
        .cast(pl.Float64, strict=False)
    )


# =========================================================================
# Construcción del inventario
# =========================================================================
def construir_proyectos(datos: dict, vigencia: str) -> pl.DataFrame:
    """Extrae proyectos/gestiones desde la columna de texto del Plan Indicativo."""
    prog_ff = datos["prog_fisica_financiera"]

    # La vigencia 2026 tiene dos columnas candidatas; se prefiere la que contenga datos.
    col_proyecto = f"PROYECTOS {vigencia}"
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
            "Indicador de producto principal", "código de indicador principal",
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
            _normalizar_numero(_extraer_regex(texto, patron_meta)).alias("Meta"),
            _normalizar_numero(_extraer_regex(texto, patron_ejecutado)).alias("Ejecutado"),
            _extraer_regex(texto, patron_estado).alias("Estado en portafolio"),
        )
        .drop(col_proyecto)
    )


@st.cache_data(show_spinner=False)
def construir_dataframe_proyectos_listo(_datos: dict, vigencia: str) -> pd.DataFrame:
    """Toma construir_proyectos y agrega columnas calculadas (Indicador, Avance)
    en el formato listo para mostrar/exportar.

    El parámetro _datos lleva underscore para indicar a Streamlit que no debe
    intentar hashearlo (es un dict de polars DataFrames, no hashable).
    El cache se invalida automáticamente cuando cambian los datos porque la
    función procesar_datos también está cacheada y retorna un nuevo objeto.
    """
    df = construir_proyectos(_datos, vigencia).to_pandas()
    if df.empty:
        return df

    df["Avance"] = df.apply(
        lambda r: (r["Ejecutado"] / r["Meta"])
        if pd.notna(r["Meta"]) and pd.notna(r["Ejecutado"]) and r["Meta"] != 0
        else None,
        axis=1,
    )

    def _fmt(row):
        codigo = row.get("código de indicador principal")
        nombre = row.get("Indicador de producto principal")
        codigo = "" if pd.isna(codigo) else str(codigo).strip()
        nombre = "" if pd.isna(nombre) else str(nombre).strip()
        if codigo and nombre:
            return f"{codigo} — {nombre}"
        return codigo or nombre or ""

    df["Indicador"] = df.apply(_fmt, axis=1)
    return df
