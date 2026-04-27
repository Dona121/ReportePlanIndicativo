"""
Tema corporativo para Plotly y escalas de color reutilizables.

Uso:
    from config.plotly_theme import configurar_tema_plotly, SCALE_BLUE
    configurar_tema_plotly()  # llamar una vez al inicio del script
"""
import plotly.graph_objects as go
import plotly.io as pio

from config.styles import COLORS, FONT_BODY, FONT_HEADING


CORPORATE_SEQUENCE = [
    COLORS["blue_dark"], COLORS["orange_deep"], COLORS["green_light"],
    COLORS["cyan"], COLORS["brown"], COLORS["blue"],
    COLORS["coral"], COLORS["amber"], COLORS["green_dark"], COLORS["orange"],
]

SCALE_BLUE = [
    [0.0, "#e8eef6"], [0.25, "#a9bedb"],
    [0.5, "#5f85b8"], [0.75, COLORS["blue"]], [1.0, COLORS["blue_dark"]],
]
SCALE_ORANGE = [
    [0.0, "#fbecd4"], [0.25, "#f3c77a"],
    [0.5, COLORS["orange"]], [0.75, COLORS["orange_deep"]], [1.0, COLORS["brown"]],
]
SCALE_GREEN = [
    [0.0, "#e1eee4"], [0.25, "#8ebfa0"],
    [0.5, COLORS["green_light"]], [0.75, COLORS["green_dark"]], [1.0, "#003d22"],
]


def configurar_tema_plotly() -> None:
    """Registra el template 'corporate' y lo activa como default."""
    corporate_template = go.layout.Template()
    corporate_template.layout = go.Layout(
        font=dict(family=f"{FONT_BODY}, sans-serif", color=COLORS["blue_dark"], size=12),
        title=dict(font=dict(family=f"{FONT_HEADING}, sans-serif", size=15, color="#0d1b2a")),
        paper_bgcolor="white",
        plot_bgcolor="white",
        colorway=CORPORATE_SEQUENCE,
        xaxis=dict(
            gridcolor="#ececea", linecolor="#c8c8c5", zerolinecolor="#ececea",
            ticks="outside", tickfont=dict(size=11, color="#4a5a6a"),
            title=dict(font=dict(size=11, color="#4a5a6a")),
        ),
        yaxis=dict(
            gridcolor="#ececea", linecolor="#c8c8c5", zerolinecolor="#ececea",
            ticks="outside", tickfont=dict(size=11, color="#4a5a6a"),
            title=dict(font=dict(size=11, color="#4a5a6a")),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)", bordercolor="#e3e3e1", borderwidth=1,
            font=dict(size=11, color="#0d1b2a"),
        ),
        margin=dict(l=60, r=30, t=60, b=60),
    )
    pio.templates["corporate"] = corporate_template
    pio.templates.default = "corporate"
