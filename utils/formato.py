"""
Formateadores de valores para la presentación en pantalla y tablas.
"""


def formato_pesos(valor):
    """Formato compacto: $1.23 MM, $1.5 M o $123 según magnitud."""
    if valor is None:
        return "—"
    try:
        v = float(valor)
        if v != v:  # NaN
            return "—"
        if abs(v) >= 1e9:
            return f"$ {v/1e9:,.2f} MM"
        if abs(v) >= 1e6:
            return f"$ {v/1e6:,.1f} M"
        return f"$ {v:,.0f}"
    except Exception:
        return "—"


def formato_porcentaje(valor):
    """Convierte una fracción [0,1] a string '12.34%'."""
    if valor is None:
        return "—"
    try:
        v = float(valor)
        if v != v:  # NaN
            return "—"
        return f"{v*100:,.2f}%"
    except Exception:
        return "—"


def formato_pesos_completo(valor):
    """Formato completo $ xxx,xxx,xxx para las tablas."""
    if valor is None:
        return "—"
    try:
        v = float(valor)
        if v != v:  # NaN
            return "—"
        return f"$ {v:,.0f}"
    except Exception:
        return "—"


def formato_entero(valor):
    """Convierte el valor a entero con separadores de miles."""
    if valor is None:
        return "—"
    try:
        v = float(valor)
        if v != v:  # NaN
            return "—"
        return f"{int(v):,}"
    except Exception:
        return "—"


def formato_numero_decimal(valor, decimales: int = 2):
    """Devuelve el número con ``decimales`` posiciones, omitidas si es entero."""
    if valor is None:
        return "—"
    try:
        v = float(valor)
        if v != v:  # NaN
            return "—"
        # Si es entero sin decimales significativos, muestra sin decimales
        if v == int(v):
            return f"{int(v):,}"
        return f"{v:,.{decimales}f}"
    except Exception:
        return "—"
