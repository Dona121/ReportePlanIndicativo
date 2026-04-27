"""
Helpers de interfaz: encabezados de sección, tablas institucionales y
selector de vista (gráfico vs tabla).
"""
import pandas as pd
import streamlit as st

from utils.formato import (
    formato_entero,
    formato_numero_decimal,
    formato_pesos_completo,
    formato_porcentaje,
)


# =========================================================================
# Encabezado de sección numerado
# =========================================================================
def seccion(numero: str, titulo: str, kicker: str = "", tooltip: str = ""):
    """Renderiza un encabezado de sección numerado.

    Si se pasa ``tooltip``, aparece un ícono '?' al lado del título que muestra
    la explicación detallada al pasar el mouse encima.
    """
    icono = ""
    if tooltip:
        # El atributo title de HTML produce un tooltip nativo del navegador,
        # ligero y consistente con la estética minimalista del dashboard.
        tooltip_safe = tooltip.replace('"', "&quot;")
        icono = f'<span class="seccion-info" title="{tooltip_safe}">?</span>'
    st.markdown(
        f'<div class="section-title"><span class="num">{numero}</span>{titulo}{icono}</div>',
        unsafe_allow_html=True,
    )
    if kicker:
        st.markdown(f'<div class="section-kicker">{kicker}</div>', unsafe_allow_html=True)


# =========================================================================
# Tabla institucional (HTML)
# =========================================================================
def pct_class(valor: float) -> str:
    """Clase CSS según el rango del porcentaje (0-1)."""
    if pd.isna(valor) or valor is None:
        return ""
    v = float(valor)
    if v < 0.25:
        return "low"
    if v < 0.5:
        return "mid"
    if v < 0.85:
        return "high"
    return "top"


def render_table(df: pd.DataFrame, columnas: list, totales: dict | None = None):
    """Renderiza una tabla institucional en HTML.

    Args:
        df: DataFrame con los datos.
        columnas: lista de dicts ``{'key', 'label', 'type'}``.
            ``type`` ∈ {'text', 'money', 'pct', 'int', 'num2', 'pctbar'}.
        totales: dict opcional ``{key: valor}`` para la fila de totales.
    """
    html = ['<table class="institutional-table">']

    # Encabezado
    html.append("<thead><tr>")
    for col in columnas:
        cls = "num" if col["type"] in ("money", "pct", "int", "num2", "pctbar") else ""
        html.append(f'<th class="{cls}">{col["label"]}</th>')
    html.append("</tr></thead>")

    # Cuerpo
    html.append("<tbody>")
    for _, row in df.iterrows():
        html.append("<tr>")
        for col in columnas:
            v = row.get(col["key"])
            t = col["type"]
            if t == "money":
                cell = formato_pesos_completo(v) if pd.notna(v) else "—"
                html.append(f'<td class="num">{cell}</td>')
            elif t == "pct":
                cell = formato_porcentaje(v) if pd.notna(v) else "—"
                html.append(f'<td class="num">{cell}</td>')
            elif t == "pctbar":
                if pd.notna(v):
                    pct = max(0.0, min(1.0, float(v)))
                    klass = pct_class(v)
                    bar = int(pct * 100)
                    cell = (
                        f'<div class="pct-cell {klass}">'
                        f'<div class="bar"><span style="width:{bar}%"></span></div>'
                        f'<div class="value">{v*100:.1f}%</div>'
                        f'</div>'
                    )
                else:
                    cell = '<div class="pct-cell"><div class="value">—</div></div>'
                html.append(f'<td class="num">{cell}</td>')
            elif t == "int":
                cell = formato_entero(v) if pd.notna(v) else "—"
                html.append(f'<td class="num">{cell}</td>')
            elif t == "num2":
                cell = formato_numero_decimal(v) if pd.notna(v) else "—"
                html.append(f'<td class="num">{cell}</td>')
            else:
                cell = "" if pd.isna(v) or v is None else str(v)
                html.append(f"<td>{cell}</td>")
        html.append("</tr>")
    html.append("</tbody>")

    # Totales
    if totales:
        html.append("<tfoot><tr>")
        for i, col in enumerate(columnas):
            if i == 0 and col["key"] not in totales:
                html.append("<td>Total</td>")
                continue
            v = totales.get(col["key"])
            if v is None:
                cls = "num" if col["type"] in ("money", "pct", "int", "num2", "pctbar") else ""
                html.append(f'<td class="{cls}"></td>')
                continue
            t = col["type"]
            if t == "money":
                html.append(f'<td class="num">{formato_pesos_completo(v)}</td>')
            elif t == "pct" or t == "pctbar":
                html.append(f'<td class="num">{formato_porcentaje(v)}</td>')
            elif t == "int":
                html.append(f'<td class="num">{formato_entero(v)}</td>')
            elif t == "num2":
                html.append(f'<td class="num">{formato_numero_decimal(v)}</td>')
            else:
                html.append(f"<td>{v}</td>")
        html.append("</tr></tfoot>")

    html.append("</table>")
    st.markdown("".join(html), unsafe_allow_html=True)


# =========================================================================
# Selector de vista (gráfico/tabla) y renderizador unificado
# =========================================================================
def render_vista(
    tipo_vista: str,
    fig_factory,
    df_tabla: pd.DataFrame,
    columnas: list,
    totales: dict | None = None,
):
    """Renderiza gráfico o tabla según la selección del usuario."""
    if tipo_vista == "Tabla":
        render_table(df_tabla, columnas, totales)
    else:
        st.plotly_chart(fig_factory(), use_container_width=True)


def selector_vista(key: str) -> str:
    """Radio horizontal para elegir entre 'Gráfico' y 'Tabla'."""
    return st.radio(
        "Vista",
        options=["Gráfico", "Tabla"],
        horizontal=True,
        key=key,
        label_visibility="collapsed",
    )
