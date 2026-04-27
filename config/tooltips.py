"""
Diccionario centralizado de tooltips para las métricas y secciones del dashboard.

Cada clave corresponde a una métrica visible en la app. El usuario verá estos
textos al pasar el mouse sobre el ícono "?" o sobre los labels de las métricas.
"""

TOOLTIPS = {
    # KPIs de cabecera
    "prog_vigencia": (
        "Total de recursos que el Plan Indicativo tiene presupuestados para la "
        "vigencia, sumando todas las fuentes de financiación: recursos propios "
        "(ICLD e ICDE), Sistema General de Participaciones (Educación, Salud y "
        "APSB), Regalías, cofinanciación de la Nación y de Municipios, crédito "
        "y otras fuentes."
    ),
    "ejec_vigencia": (
        "Recursos efectivamente pagados durante la vigencia. Consolida la "
        "información de Hacienda, Regalías y entidades adscritas. Para 2025 "
        "se incluyen además Aguas de Sucre, Gestiones, PDET, Fondo Mixto e "
        "Indersucre, que reportan su ejecución por separado."
    ),
    "avance_vigencia": (
        "Qué porcentaje del presupuesto programado se ha pagado efectivamente "
        "en la vigencia. Es la relación entre lo ejecutado y lo programado."
    ),
    "prog_cuatrienio": (
        "Recursos totales que el Plan Indicativo proyecta invertir en los "
        "cuatro años del Plan de Desarrollo (2024-2027), considerando todas "
        "las fuentes de financiación."
    ),
    "ejec_acumulada": (
        "Suma de los recursos pagados desde el inicio del Plan hasta la "
        "vigencia actual. Acumula la ejecución de 2024, 2025 y 2026. No "
        "incluye 2027 porque aún no ha iniciado."
    ),
    "avance_cuatrienio": (
        "Qué porcentaje del Plan de Desarrollo se ha ejecutado financieramente "
        "hasta el momento. Compara la ejecución acumulada contra la "
        "programación total del cuatrienio."
    ),

    # Avances físicos
    "avance_vig_ponderado": (
        "Mide qué tanto se han cumplido las metas del Plan en la vigencia. "
        "Es un promedio ponderado donde cada programa aporta según el número "
        "de metas que tiene programadas; los programas con más metas pesan "
        "proporcionalmente más en el resultado global."
    ),
    "avance_cuatrienio_ponderado": (
        "Cumplimiento global de las metas físicas del Plan considerando todo "
        "el cuatrienio, no solo la vigencia actual. Cada programa aporta "
        "según el peso que tiene dentro del Plan."
    ),
    "eficacia_operativa": (
        "Mide qué tan eficientes son las líneas y sectores en cumplir sus "
        "metas, ajustando por su tamaño relativo. Permite comparar de forma "
        "justa dependencias con muchas metas frente a otras con pocas: una "
        "línea con pocas metas pero alto cumplimiento puede tener mejor "
        "eficacia operativa que otra con muchas metas y bajo cumplimiento."
    ),
    "aporte_pdd": (
        "Cuánto contribuye una Línea Estratégica o un Sector al cumplimiento "
        "global del Plan de Desarrollo. Combina el nivel de avance de la "
        "agrupación con su peso dentro del total de metas."
    ),

    # Tablas financieras
    "ejec_clasif_recursos": (
        "Recursos pagados durante la vigencia, agrupados por el tipo de "
        "fuente que los financia (ICLD, ICDE, SGP, Regalías, Cofinanciación, "
        "Crédito u Otras Fuentes)."
    ),
    "porcentaje_ejecucion_financiera": (
        "Qué tanto se ha utilizado cada tipo de recurso en relación con lo "
        "que se tenía programado."
    ),

    # Distribución
    "distribucion_metas": (
        "Indica cómo está repartida la programación física del Plan entre "
        "los cuatro años. Compara cuánto se planea cumplir en cada vigencia "
        "frente a la meta total del cuatrienio."
    ),

    # Dependencia
    "metas_programadas": (
        "Cantidad de metas físicas que la dependencia tiene asignadas y para "
        "las cuales hay un valor a cumplir en la vigencia."
    ),
    "metas_cumplidas_100": (
        "Metas que alcanzaron o superaron el 100% del avance esperado en la "
        "vigencia (categoría 'Superior')."
    ),
    "porcentaje_ejec_dependencia": (
        "Avance promedio de las metas asignadas a la dependencia en la "
        "vigencia. Considera solo las metas con programación para ese año."
    ),
    "porcentaje_ejec_acumulada_dependencia": (
        "Avance promedio acumulado (cuatrienio) de todas las metas asignadas "
        "a la dependencia, considerando los años transcurridos del Plan."
    ),

    # Proyectos
    "total_proyectos_gestiones": (
        "Cantidad de proyectos y gestiones registrados en el Plan Indicativo "
        "para la vigencia. Incluye iniciativas tanto de ejecución directa "
        "como de gestión de recursos."
    ),
    "avance_proyecto": (
        "Porcentaje de cumplimiento físico del proyecto: qué tanto se ha "
        "ejecutado frente a la meta planeada (en unidades físicas, no en pesos)."
    ),
}
