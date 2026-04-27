"""
Constructores de reportes por vigencia a partir de la base unificada que
devuelve ``procesamiento.lectura.procesar_datos``.

Cada función expuesta replica fielmente la lógica del notebook original:
    - construir_ejecucion_financ_tipo(datos, vigencia)
    - construir_ejecucion_acumulada_tipo(datos)
    - construir_prog_financ_categorias(datos, vigencia)
    - construir_ejec_por_dependencia(datos, vigencia)
    - construir_avances_fisicos(datos, vigencia)
"""
import polars as pl


def construir_ejecucion_financ_tipo(datos: dict, vigencia: str) -> pl.DataFrame:
    """Ejecución por clasificación de recursos para la vigencia filtrada.

    En 2025 se aplica str.split(" | ").explode() ANTES de agrupar, igual que
    en el bloque acumulado. Esto garantiza que los KPIs y la tabla de
    'Por Clasificación de Recursos' reflejen el RP tras explode (la cifra
    real validada con el notebook).
    """
    ejecuciones = datos["ejecuciones_financieras"][vigencia]
    orden_fuentes = datos["orden_fuentes"]
    prog_financ_tipo = datos["prog_financ_tipo"]

    concat_ejec = pl.concat(ejecuciones, how="diagonal")
    if vigencia == "2025":
        concat_ejec = concat_ejec.with_columns(pl.col("CODIGO META").str.split(" | ")).explode("CODIGO META")

    return (
        orden_fuentes.join(
            concat_ejec,
            left_on="Clasificación Recursos", right_on="CLASIFICACIÓN RECURSOS", how="left",
        )
        .group_by("Clasificación Recursos").agg(pl.col("RP").sum().alias(f"Ejecución Financiera {vigencia}"))
        .join(orden_fuentes, on="Clasificación Recursos", how="inner")
        .join(prog_financ_tipo, on="Clasificación Recursos", how="inner")
        .select("Orden", "Tipo Fuente", "Clasificación Recursos",
                f"Programación Financiera {vigencia}", f"Ejecución Financiera {vigencia}")
        .with_columns(
            (pl.when(pl.col(f"Programación Financiera {vigencia}") == 0)
             .then(pl.lit(0))
             .otherwise(pl.col(f"Ejecución Financiera {vigencia}") / pl.col(f"Programación Financiera {vigencia}"))
             ).alias("Porcentaje de Ejecución Financiera")
        )
        .sort(by="Orden")
    )


def construir_ejecucion_acumulada_tipo(datos: dict) -> pl.DataFrame:
    """Acumulado por CLASIFICACIÓN RECURSOS para todo el cuatrienio.

    Replica exactamente la lógica del notebook (bloque ejecucion_2024_agrp,
    ejecucion_2025_agrp, ejecucion_2026_agrp). En 2025 se hace explode por
    " | " antes de agrupar — el notebook lo hace así y la app lo replica.
    """
    orden_fuentes = datos["orden_fuentes"]
    prog_financ_tipo = datos["prog_financ_tipo"]

    agrp = {}
    for v in ["2024", "2025", "2026"]:
        concat = pl.concat(datos["ejecuciones_financieras"][v], how="diagonal")
        if v == "2025":
            concat = concat.with_columns(pl.col("CODIGO META").str.split(" | ")).explode("CODIGO META")
        agrp[v] = (
            concat.group_by("CLASIFICACIÓN RECURSOS")
            .agg(pl.col("RP").sum().alias(f"Ejecución Financiera {v}"))
        )

    return (
        orden_fuentes
        .join(agrp["2024"], left_on="Clasificación Recursos", right_on="CLASIFICACIÓN RECURSOS", how="left")
        .join(agrp["2025"], left_on="Clasificación Recursos", right_on="CLASIFICACIÓN RECURSOS", how="left")
        .join(agrp["2026"], left_on="Clasificación Recursos", right_on="CLASIFICACIÓN RECURSOS", how="left")
        .join(prog_financ_tipo, on="Clasificación Recursos")
        .with_columns(
            pl.col("Ejecución Financiera 2024", "Ejecución Financiera 2025", "Ejecución Financiera 2026").fill_null(pl.lit(0))
        )
        .with_columns(
            (pl.col("Ejecución Financiera 2024") + pl.col("Ejecución Financiera 2025")
             + pl.col("Ejecución Financiera 2026")).alias("Ejecución Financiera Acumulada"),
            (pl.col("Programación Financiera 2024") + pl.col("Programación Financiera 2025")
             + pl.col("Programación Financiera 2026") + pl.col("Programación Financiera 2027")
             ).alias("Programación Cuatrienio"),
        )
        .select("Orden", "Tipo Fuente", "Clasificación Recursos",
                "Programación Financiera 2024", "Programación Financiera 2025", "Programación Financiera 2026",
                "Ejecución Financiera 2024", "Ejecución Financiera 2025", "Ejecución Financiera 2026",
                "Programación Cuatrienio", "Ejecución Financiera Acumulada")
        .sort(by="Orden")
    )


def construir_prog_financ_categorias(datos: dict, vigencia: str) -> dict:
    """Programación vs ejecución agrupadas por línea, sector y programa."""
    prog_ff = datos["prog_fisica_financiera"]
    orden_lineas = datos["orden_lineas_pdd"]
    orden_sectores = datos["orden_sectores_pdd"]
    orden_programas = datos["orden_programas_pdd"]

    def agregar(grupo, orden_df, col_orden):
        return (
            prog_ff.group_by(grupo).agg(
                pl.col(f"Programación Financiera {vigencia}").sum(),
                pl.col(f"Ejecución Financiera {vigencia}").sum(),
            )
            .join(orden_df, on=grupo, how="inner")
            .with_columns(
                (pl.when(pl.col(f"Programación Financiera {vigencia}") == 0)
                 .then(pl.lit(0))
                 .otherwise(pl.col(f"Ejecución Financiera {vigencia}") / pl.col(f"Programación Financiera {vigencia}"))
                 ).alias("Porcentaje de Ejecución Financiera")
            )
            .sort(col_orden)
            .select(col_orden, grupo, f"Programación Financiera {vigencia}",
                    f"Ejecución Financiera {vigencia}", "Porcentaje de Ejecución Financiera")
        )

    return {
        "lineas": agregar("Línea Estratégica", orden_lineas, "Orden Linea"),
        "sectores": agregar("Sector PDD", orden_sectores, "Orden Sector"),
        "programas": agregar("Programa PDD", orden_programas, "Orden Programa PDD"),
    }


def construir_ejec_por_dependencia(datos: dict, vigencia: str) -> pl.DataFrame:
    """Replica exactamente 'ejecucion_por_dependencia' del notebook.

    Usa join 'left' con la homologación de secretarías, igual que el notebook.
    El otro DataFrame del notebook ('avance_por_dependencia') usa inner pero
    no es el que alimenta esta tabla principal.
    """
    prog_ff = datos["prog_fisica_financiera"]
    homologacion = datos["homologacion_secretarias"]

    ejec_acumulada = (
        prog_ff.select(pl.col("Responsable").str.strip_chars(), "PORCENTAJE DE EJECUCIÓN ACUMULADA")
        .group_by("Responsable")
        .agg(pl.col("PORCENTAJE DE EJECUCIÓN ACUMULADA").fill_null(pl.lit(0)).mean().alias("Porcentaje de Ejecución Acumulada"))
    )

    return (
        prog_ff.select(
            pl.col("Responsable").str.strip_chars(), f"Meta Física Esperada {vigencia}",
            f"PORCENTAJE DE EJECUCIÓN {vigencia}", f"CATEGORÍA DE EJECUCIÓN FÍSICA {vigencia}"
        )
        .filter(pl.col(f"Meta Física Esperada {vigencia}").fill_null(pl.lit(0)) != 0)
        .with_columns(
            (pl.when(pl.col(f"Meta Física Esperada {vigencia}") != 0).then(pl.lit(1)).otherwise(pl.lit(0))
             ).alias(f"Metas Programadas {vigencia}"),
            (pl.when(pl.col(f"CATEGORÍA DE EJECUCIÓN FÍSICA {vigencia}") == "Superior").then(pl.lit(1)).otherwise(pl.lit(0))
             ).alias(f"Metas Cumplidas al 100% {vigencia}"),
        )
        .group_by("Responsable").agg(
            pl.col(f"PORCENTAJE DE EJECUCIÓN {vigencia}").fill_null(pl.lit(0)).mean().alias(f"Porcentaje de Ejecución {vigencia}"),
            pl.col(f"Metas Programadas {vigencia}").sum(),
            pl.col(f"Metas Cumplidas al 100% {vigencia}").sum(),
        )
        .join(homologacion, left_on="Responsable", right_on="Responsable en PI", how="left")
        .join(ejec_acumulada, on="Responsable", how="left")
        .select("Varias Secretarías", "Dependencia Responsable",
                f"Metas Programadas {vigencia}", f"Metas Cumplidas al 100% {vigencia}",
                f"Porcentaje de Ejecución {vigencia}", "Porcentaje de Ejecución Acumulada")
    )


def construir_avances_fisicos(datos: dict, vigencia: str) -> dict:
    """Calcula avances físicos ponderados por línea, sector y programa."""
    prog_ff = datos["prog_fisica_financiera"]

    numero_total_metas = prog_ff.get_column("Codigo Meta").count()
    numero_metas_prog_vigencia = (
        prog_ff.filter(pl.col(f"Meta Física Esperada {vigencia}") != 0).get_column("Codigo Meta").count()
    )

    promedio_programas = (
        prog_ff.filter(pl.col(f"Meta Física Esperada {vigencia}") != 0)
        .group_by("Programa PDD").agg(pl.col(f"PORCENTAJE DE EJECUCIÓN {vigencia}").mean())
        .rename({f"PORCENTAJE DE EJECUCIÓN {vigencia}": "Promedio de avance de ejecución de la vigencia"})
    )

    num_metas_lineas_cp = (
        prog_ff.filter(pl.col(f"Meta Física Esperada {vigencia}") != 0)
        .group_by("Línea Estratégica").agg(pl.col("Codigo Meta").len())
        .rename({"Codigo Meta": "Total Indicadores de Producto con Programacion"})
    )
    num_metas_lineas = (
        prog_ff.group_by("Línea Estratégica").agg(pl.col("Codigo Meta").len())
        .rename({"Codigo Meta": "Total Indicadores de Producto"})
    )
    num_metas_sectores_cp = (
        prog_ff.filter(pl.col(f"Meta Física Esperada {vigencia}") != 0)
        .group_by("Sector PDD").agg(pl.col("Codigo Meta").len())
        .rename({"Codigo Meta": "Total Indicadores de Producto con Programacion"})
    )
    num_metas_sectores = (
        prog_ff.group_by("Sector PDD").agg(pl.col("Codigo Meta").len())
        .rename({"Codigo Meta": "Total Indicadores de Producto"})
    )
    num_metas_programas = (
        prog_ff.group_by("Programa PDD").agg(pl.col("Codigo Meta").len())
        .rename({"Codigo Meta": "Total Indicadores de Producto"})
    )

    ponderado_vigencia = (
        prog_ff
        .with_columns(
            (pl.when(pl.col(f"Meta Física Esperada {vigencia}") != 0).then(pl.lit(1)).otherwise(pl.lit(0))
             ).alias(f"Metas Programadas {vigencia}")
        )
        .group_by("Línea Estratégica", "Sector PDD", "Programa PDD")
        .agg(pl.col(f"Metas Programadas {vigencia}").sum())
        .with_columns(
            (pl.col(f"Metas Programadas {vigencia}") / max(numero_metas_prog_vigencia, 1)
             ).alias("Sobre Numero Total de Metas Programadas")
        )
        .join(promedio_programas, on="Programa PDD", how="left")
        .with_columns(pl.col("Promedio de avance de ejecución de la vigencia").fill_null(pl.lit(0)))
        .rename({f"Metas Programadas {vigencia}": "Total Indicadores de Producto Programados"})
    )

    ponderado_cuatrienio = (
        prog_ff.group_by("Línea Estratégica", "Sector PDD", "Programa PDD")
        .agg(pl.col("PORCENTAJE DE EJECUCIÓN ACUMULADA").fill_null(pl.lit(0)).mean())
        .join(num_metas_programas, on="Programa PDD")
        .with_columns((pl.col("Total Indicadores de Producto") / max(numero_total_metas, 1)).alias("Sobre Numero Total de Metas"))
        .rename({"PORCENTAJE DE EJECUCIÓN ACUMULADA": "Promedio de avance de ejecución acumulada"})
    )

    avance_vig_ponderado = ponderado_vigencia.select(
        pl.col("Promedio de avance de ejecución de la vigencia") * pl.col("Sobre Numero Total de Metas Programadas")
    ).sum().item()

    avance_cuatrienio_total = ponderado_cuatrienio.select(
        pl.col("Promedio de avance de ejecución acumulada") * pl.col("Sobre Numero Total de Metas")
    ).sum().item()

    def avance_por_dim(ponderado, grupo, num_metas_df, total, col_avance, col_metas):
        return (
            ponderado.group_by(grupo)
            .agg((pl.col(col_avance) * pl.col(col_metas)).sum())
            .rename({col_avance: "% Aporte Cumplimiento PDD"})
            .join(num_metas_df, on=grupo)
            .with_columns((pl.col(num_metas_df.columns[1]) / max(total, 1)).alias("Sobre Numero Total de Indicadores"))
            .with_columns(
                (pl.when(pl.col("Sobre Numero Total de Indicadores") == 0)
                 .then(pl.lit(0))
                 .otherwise(pl.col("% Aporte Cumplimiento PDD") / pl.col("Sobre Numero Total de Indicadores"))
                 ).alias("% Eficacia Operativa")
            )
        )

    return {
        "avance_vig_ponderado": avance_vig_ponderado,
        "avance_cuatrienio_total": avance_cuatrienio_total,
        "avance_vig_lineas": avance_por_dim(
            ponderado_vigencia, "Línea Estratégica", num_metas_lineas_cp, numero_metas_prog_vigencia,
            "Promedio de avance de ejecución de la vigencia", "Sobre Numero Total de Metas Programadas"),
        "avance_cuatri_lineas": avance_por_dim(
            ponderado_cuatrienio, "Línea Estratégica", num_metas_lineas, numero_total_metas,
            "Promedio de avance de ejecución acumulada", "Sobre Numero Total de Metas"),
        "avance_vig_sectores": avance_por_dim(
            ponderado_vigencia, "Sector PDD", num_metas_sectores_cp, numero_metas_prog_vigencia,
            "Promedio de avance de ejecución de la vigencia", "Sobre Numero Total de Metas Programadas"),
        "avance_cuatri_sectores": avance_por_dim(
            ponderado_cuatrienio, "Sector PDD", num_metas_sectores, numero_total_metas,
            "Promedio de avance de ejecución acumulada", "Sobre Numero Total de Metas"),
        "numero_total_metas": numero_total_metas,
        "numero_metas_prog_vigencia": numero_metas_prog_vigencia,
    }
