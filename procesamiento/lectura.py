"""
Lectura de los archivos Excel del Plan Indicativo y vigencias asociadas, y
construcción de la base unificada utilizada por el dashboard.

Las funciones expuestas son:
    - programacion_financiera(vigencia): expresión polars que suma las diez
      fuentes de financiación para una vigencia dada.
    - procesar_datos(...): lee los Excel desde sus bytes y devuelve un dict
      con los DataFrames listos para alimentar los reportes.

La función está cacheada con st.cache_data para evitar relecturas costosas.
"""
import io

import streamlit as st
import polars as pl
import polars.selectors as cs


def programacion_financiera(vigencia: str) -> pl.Expr:
    """Suma las diez fuentes de programación financiera para la vigencia dada.

    El parámetro ``vigencia`` debe ser ``"24"``, ``"25"``, ``"26"`` o ``"27"``
    (los dos últimos dígitos del año), tal como aparecen en las columnas del
    Plan Indicativo.
    """
    return (
        pl.col("programación recursos propios icld" + vigencia)
        + pl.col("programación recursos propios icde" + vigencia)
        + pl.col("programación sgp educación" + vigencia)
        + pl.col("programación sgp salud" + vigencia)
        + pl.col("programación sgp apsb" + vigencia)
        + pl.col("programación cofinanciación municipio" + vigencia)
        + pl.col("programación cofinanciación nación" + vigencia)
        + pl.col("programación crédito" + vigencia)
        + pl.col("programación regalías" + vigencia)
        + pl.col("programación otras fuentes" + vigencia)
    )


@st.cache_data(show_spinner="Procesando datos del Plan Indicativo...")
def procesar_datos(
    pi_bytes, h24_bytes, r24_bytes, h25_bytes, r25_bytes,
    ads_rp_25_bytes, ads_reg_25_bytes, gestiones_25_bytes,
    fondo_mixto_25_bytes, inder_25_bytes,
    h26_bytes, r26_bytes,
):
    """Lee los Excel y devuelve la base unificada para los reportes.

    Devuelve un dict con:
        plan_indicativo, orden_lineas_pdd, orden_sectores_pdd,
        orden_programas_pdd, homologacion_secretarias, orden_fuentes,
        prog_financ_tipo, ejecuciones_financieras, prog_fisica_financiera.
    """
    plan_indicativo = pl.read_excel(io.BytesIO(pi_bytes), table_name="tblPlanIndicativo_2")
    orden_lineas_pdd = pl.read_excel(io.BytesIO(pi_bytes), table_name="orden_lineas")
    orden_sectores_pdd = pl.read_excel(io.BytesIO(pi_bytes), table_name="orden_sectores")
    orden_programas_pdd = pl.read_excel(io.BytesIO(pi_bytes), table_name="orden_programas")
    homologacion_secretarias = pl.read_excel(io.BytesIO(pi_bytes), table_name="HomologacionSecretarias")

    columnas_prog_ejec_fisica = plan_indicativo.select(
        "Codigo Meta", "Línea Estratégica", "Sector PDD",
        "Numero Programa PDD", "Programa PDD",
        "Indicador de producto principal", "código de indicador principal",
        "Meta de cuatrenio",
        "Tipo de Acumulación", "Responsable", "Meta Física Esperada 2024",
        "Meta Física Esperada 2025", "Meta Física Esperada 2026", "Meta Física Esperada 2027",
        "PROYECTOS 2024", "PROYECTOS 2025", "PROYECTOS/GESTIONES PROGRAMADAS 2026", "PROYECTOS 2026",
        "PROYECTOS 2027", "EJECUCIÓN 2024", "PORCENTAJE DE EJECUCIÓN 2024", "CATEGORÍA DE EJECUCIÓN FÍSICA 2024",
        "EJECUCIÓN 2025", "PORCENTAJE DE EJECUCIÓN 2025", "CATEGORÍA DE EJECUCIÓN FÍSICA 2025",
        "EJECUCIÓN 2026", "PORCENTAJE DE EJECUCIÓN 2026", "CATEGORÍA DE EJECUCIÓN FÍSICA 2026",
        "EJECUCIÓN ACUMULADA", "PORCENTAJE DE EJECUCIÓN ACUMULADA", "CATEGORÍA DE EJECUCIÓN ACUMULADA",
    )

    # --- Ejecución 2024 ---
    ejecucion_regalias_2024 = (
        pl.read_excel(io.BytesIO(r24_bytes), table_name="EjecucionRegalias",
                      columns=["CODIGO META", "COMPROMISOS", "CLASIFICACIÓN RECURSOS"])
        .with_columns(pl.col("CODIGO META").fill_null(pl.lit("")))
        .filter(pl.col("CODIGO META") != "", pl.col("CODIGO META").str.starts_with("MT"))
        .rename({"COMPROMISOS": "RP"})
    )
    ejecucion_hacienda_2024 = (
        pl.read_excel(io.BytesIO(h24_bytes), table_name="EjecucionHaciendaDiciembre",
                      columns=["RP", "CODIGO META", "CLASIFICACIÓN RECURSOS"])
        .with_columns(pl.col("CODIGO META", "CLASIFICACIÓN RECURSOS").fill_null(pl.lit("")))
        .filter(pl.col("CODIGO META") != "", pl.col("CLASIFICACIÓN RECURSOS") != "")
    )

    # --- Ejecución 2025 (fuentes base) ---
    ejecucion_regalias_2025 = (
        pl.read_excel(io.BytesIO(r25_bytes), table_name="Pagos_Regalias_2025")
        .select("PAGOS REGALIAS", "CODIGO META", "CLASIFICACIÓN RECURSOS")
        .rename({"PAGOS REGALIAS": "RP"})
        .with_columns(pl.col("CODIGO META").fill_null(pl.lit("")))
        .filter(pl.col("CODIGO META") != "")
    )
    ejecucion_hacienda_2025 = (
        pl.read_excel(io.BytesIO(h25_bytes), table_name="EjecucionHaciendaDiciembre2025")
        .with_columns(
            pl.col("PROYECTO ARCHIVADO", "CODIGO META", "CLASIFICACIÓN RECURSOS", "SE VA A CARGAR EN PI").fill_null(pl.lit("")),
            pl.when(pl.col("DISTRIBUIR DE FORMA EQUITATIVA") == "SI").then(pl.col("RP") / 2).otherwise(pl.col("RP")),
        )
        .filter(pl.col("PROYECTO ARCHIVADO") == "", pl.col("CODIGO META") != "",
                pl.col("CLASIFICACIÓN RECURSOS") != "", pl.col("SE VA A CARGAR EN PI") == "")
        .select("CODIGO META", "CLASIFICACIÓN RECURSOS", "RP")
    )

    # --- Ejecución 2025 (fuentes adicionales) ---
    ejecucion_2025_ads_recursos_propios = (
        pl.read_excel(io.BytesIO(ads_rp_25_bytes), table_name="PagosAguasDeSucre")
        .select("VALOR DEL PAGO", "CLASIFICACIÓN RECURSOS", "CODIGO META")
        .with_columns(pl.col("CODIGO META").fill_null(pl.lit("")))
        .filter(pl.col("CODIGO META") != "")
        .rename({"VALOR DEL PAGO": "RP"})
    )

    ejecucion_2025_ads_regalias = (
        pl.read_excel(io.BytesIO(ads_reg_25_bytes), table_name="RegaliasAguasDeSucre")
        .select("CODIGO DE META", "CLASIFICACIÓN RECURSOS", "PAGOS")
        .rename({"CODIGO DE META": "CODIGO META", "PAGOS": "RP"})
        .with_columns(pl.col("CODIGO META").fill_null(pl.lit("")))
        .filter(pl.col("CODIGO META") != "")
    )

    ejecucion_2025_gestiones = (
        pl.read_excel(io.BytesIO(gestiones_25_bytes), table_name="EjecucionGestiones")
        .rename({"EJECUCION FINANCIERA": "RP"})
    )

    ejecucion_pdet_2025 = (
        pl.read_excel(io.BytesIO(h25_bytes), table_name="EjecucionPDET")
        .select("EJECUCION FINANCIERA", "CODIGO META", "CLASIFICACIÓN RECURSOS")
        .rename({"EJECUCION FINANCIERA": "RP"})
    )

    ejecucion_2025_fondo_mixto = (
        pl.read_excel(io.BytesIO(fondo_mixto_25_bytes), table_name="EjecucionFinancieraFondoMixto")
        .select("CLASIFICACIÓN RECURSOS", "EJECUCION FINANCIERA", "CODIGO META")
        .rename({"EJECUCION FINANCIERA": "RP"})
    )

    ejecucion_2025_indersucre_recursos_propios = (
        pl.read_excel(io.BytesIO(inder_25_bytes), table_name="EjecucionFinancieraINDERTerritorio")
        .rename({"EJECUCION FINANCIERA": "RP"})
    )

    ejecucion_2025_indersucre_regalias = (
        pl.read_excel(io.BytesIO(inder_25_bytes), table_name="EjecucionFinancieraINDERRegalias")
        .rename({"EJECUCION FINANCIERA": "RP"})
    )

    # --- Ejecución 2026 ---
    ejecucion_regalias_2026 = (
        pl.read_excel(io.BytesIO(r26_bytes), table_name="Pagos_Regalias_2026")
        .select(pl.all().name.map(lambda x: x.strip().upper().replace("_X0009_", "")))
        .filter(
            (pl.col("ULTIMA FECHA PAGO") >= pl.date(2026, 1, 1))
            & (pl.col("ULTIMA FECHA PAGO") <= pl.date(2026, 12, 31))
        )
        .select("PAGO EJECUTADO VALOR", "CODIGO META", "CLASIFICACIÓN RECURSOS")
        .rename({"PAGO EJECUTADO VALOR": "RP"})
        .with_columns(pl.col("CODIGO META").fill_null(pl.lit("")))
        .filter(pl.col("CODIGO META") != "")
    )
    ejecucion_hacienda_2026 = (
        pl.read_excel(io.BytesIO(h26_bytes), table_name="EjecucionHacienda2026")
        .with_columns(
            pl.col("PROYECTO ARCHIVADO", "CODIGO META", "CLASIFICACIÓN RECURSOS", "SE VA A CARGAR EN PI").fill_null(pl.lit("")),
            pl.when(pl.col("DISTRIBUIR DE FORMA EQUITATIVA") == "SI").then(pl.col("RP") / 2).otherwise(pl.col("RP")),
        )
        .filter(pl.col("PROYECTO ARCHIVADO") == "", pl.col("CODIGO META") != "",
                pl.col("CLASIFICACIÓN RECURSOS") != "", pl.col("SE VA A CARGAR EN PI") == "")
        .select("CODIGO META", "CLASIFICACIÓN RECURSOS", "RP")
    )

    # --- Agregados de ejecución por meta ---
    ejec_2024 = pl.concat([ejecucion_regalias_2024, ejecucion_hacienda_2024], how="diagonal") \
        .group_by("CODIGO META").agg(pl.col("RP").sum().alias("Ejecución Financiera 2024"))

    # 2025: las fuentes adicionales pueden traer códigos múltiples separados por " | ".
    # El notebook hace str.split(" | ").explode() SIN dividir el RP, por lo que cada
    # meta de un código múltiple recibe el RP completo de la fila original.
    # Esto puede inflar el total cuando se suma sobre todas las metas — pero es lo
    # que hace el notebook y la app debe reflejarlo fielmente.
    ejec_2025_full = (
        pl.concat([
            ejecucion_regalias_2025, ejecucion_hacienda_2025,
            ejecucion_2025_ads_recursos_propios, ejecucion_2025_ads_regalias,
            ejecucion_2025_gestiones, ejecucion_pdet_2025,
            ejecucion_2025_fondo_mixto,
            ejecucion_2025_indersucre_recursos_propios,
            ejecucion_2025_indersucre_regalias,
        ], how="diagonal")
        .with_columns(pl.col("CODIGO META").str.split(" | "))
        .explode("CODIGO META")
    )
    ejec_2025 = ejec_2025_full.group_by("CODIGO META").agg(
        pl.col("RP").sum().alias("Ejecución Financiera 2025")
    )

    ejec_2026 = pl.concat([ejecucion_regalias_2026, ejecucion_hacienda_2026], how="diagonal") \
        .group_by("CODIGO META").agg(pl.col("RP").sum().alias("Ejecución Financiera 2026"))

    columnas_programacion_financiera = (
        plan_indicativo.select("Codigo Meta", cs.starts_with("Programación").cast(pl.Float64))
        .select(pl.all().name.map(lambda x: x.strip().lower()))
        .select(
            "codigo meta",
            programacion_financiera("24").alias("Programación Financiera 2024"),
            programacion_financiera("25").alias("Programación Financiera 2025"),
            programacion_financiera("26").alias("Programación Financiera 2026"),
            programacion_financiera("27").alias("Programación Financiera 2027"),
        )
        .join(ejec_2024, left_on="codigo meta", right_on="CODIGO META", how="left")
        .join(ejec_2025, left_on="codigo meta", right_on="CODIGO META", how="left")
        .join(ejec_2026, left_on="codigo meta", right_on="CODIGO META", how="left")
        .with_columns(pl.col("Ejecución Financiera 2024", "Ejecución Financiera 2025", "Ejecución Financiera 2026").fill_null(pl.lit(0)))
    )

    orden_fuentes = pl.DataFrame({
        "Clasificación Recursos": ["COFINANCIACIÓN MUNICIPIO", "ICDE", "OTRAS FUENTES", "SGP APSB", "SGP SALUD",
                                   "SGP EDUCACION", "REGALÍAS", "COFINANCIACIÓN NACIÓN", "ICLD", "CREDITO"],
        "Orden": [1, 5, 3, 7, 9, 8, 10, 2, 6, 4],
        "Tipo Fuente": ["Otras Fuentes", "Recursos Propios", "Otras Fuentes",
                        "Sistema General de Participaciones (SGP)", "Sistema General de Participaciones (SGP)",
                        "Sistema General de Participaciones (SGP)", "Sistema General de Regalías",
                        "Otras Fuentes", "Recursos Propios", "Recursos del Crédito"],
    })

    prog_financ_tipo = (
        plan_indicativo.select(cs.starts_with("Programación"))
        .select(pl.all().name.map(lambda x: x.strip().lower()))
        .select(cs.exclude("programación total24", "programación total25", "programación total26", "programación total27"))
        .unpivot(on=cs.numeric(), variable_name="Clasificación Recursos", value_name="Programación financiera")
        .group_by("Clasificación Recursos").agg(pl.col("Programación financiera").sum())
        .with_columns(
            pl.col("Clasificación Recursos").str.slice(-2).alias("Vigencia"),
            pl.col("Clasificación Recursos").str.replace_all("programación ", "").str.replace_all(r"(24|25|26|27)", ""),
        )
        .with_columns((pl.lit("Programación Financiera 20") + pl.col("Vigencia")).alias("Vigencia"))
        .pivot(index="Clasificación Recursos", on="Vigencia", aggregate_function="sum")
        .with_columns(
            pl.col("Clasificación Recursos").str.replace_many(
                ["recursos propios icde", "cofinanciación nación", "sgp educación", "cofinanciación municipio",
                 "sgp salud", "sgp apsb", "otras fuentes", "regalías", "recursos propios icld", "crédito"],
                ["ICDE", "COFINANCIACIÓN NACIÓN", "SGP EDUCACION", "COFINANCIACIÓN MUNICIPIO",
                 "SGP SALUD", "SGP APSB", "OTRAS FUENTES", "REGALÍAS", "ICLD", "CREDITO"],
            )
        )
    )

    ejecuciones_financieras = {
        "2024": [ejecucion_regalias_2024, ejecucion_hacienda_2024],
        "2025": [
            ejecucion_regalias_2025, ejecucion_hacienda_2025,
            ejecucion_2025_ads_recursos_propios, ejecucion_2025_ads_regalias,
            ejecucion_2025_gestiones, ejecucion_pdet_2025,
            ejecucion_2025_fondo_mixto,
            ejecucion_2025_indersucre_recursos_propios,
            ejecucion_2025_indersucre_regalias,
        ],
        "2026": [ejecucion_regalias_2026, ejecucion_hacienda_2026],
    }

    prog_fisica_financiera = (
        columnas_prog_ejec_fisica.join(columnas_programacion_financiera, left_on="Codigo Meta", right_on="codigo meta", how="left")
        .with_columns(
            pl.col("Meta Física Esperada 2024", "Meta Física Esperada 2025",
                   "Meta Física Esperada 2026", "Meta Física Esperada 2027").fill_null(pl.lit(0))
        )
    )

    return {
        "plan_indicativo": plan_indicativo,
        "orden_lineas_pdd": orden_lineas_pdd,
        "orden_sectores_pdd": orden_sectores_pdd,
        "orden_programas_pdd": orden_programas_pdd,
        "homologacion_secretarias": homologacion_secretarias,
        "orden_fuentes": orden_fuentes,
        "prog_financ_tipo": prog_financ_tipo,
        "ejecuciones_financieras": ejecuciones_financieras,
        "prog_fisica_financiera": prog_fisica_financiera,
    }
