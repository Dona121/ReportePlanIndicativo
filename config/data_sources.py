"""
URLs de los archivos en GitHub y agrupación por tipo de carga.

- ARCHIVOS_CERRADOS: vigencias 2024 y 2025 (no cambian, siempre del repo).
- ARCHIVOS_ACTUALIZABLES: Plan Indicativo + 2026 (el usuario puede subirlos).
"""

GH = {
    "pi":  "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/Plan%20Indicativo%202024-2027.xlsx",
    "h24": "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/EJECUCION%20INVERSION%20A%20DICIEMBRE%2031%20DEL%202024%20ENERO%2010%202025.xlsx",
    "r24": "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/INFORME%20FINANCIERO%20REGALIAS%20A%2031%20DE%20DICIEMBRE%20DE%202024.xlsx",
    "h25": "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/EJECUCION%20INVERSION%20DE%20ENERO%20A%20DICIEMBRE%202025.xlsx",
    "r25": "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/PAGOS%20REGALIAS%20ENERO%20-%20DICIEMBRE%202025.xlsx",
    # Fuentes adicionales 2025 (vigencia cerrada)
    "ads_rp_25":     "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/RELACION%20DE%20PAGOS%20ENERO%20A%20DICIEMBRE%20ADS.xlsx",
    "ads_reg_25":    "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/PAGOS%20REGALIAS%202025%20ADS.xlsx",
    "gestiones_25":  "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/EjecucionFinancieraGestiones_20260210.xlsx",
    "fondo_mixto_25":"https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/CONTRATOS%20Y%20CONVENIOS%202025%20-%20FONDO%20MIXTO.xlsx",
    "inder_25":      "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/EjecucionIndersucre_Territorial_Regalias_202602010.xlsx",
    # Archivos actualizables
    "h26": "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/EJECUCION%20INVERSION%20DE%20HACIENDA%20PRUEBA%202026.xlsx",
    "r26": "https://raw.githubusercontent.com/Dona121/Plan-Indicativo/main/data/CG-cttos_04_marzo_20260304.xlsx",
}

# Vigencias cerradas (siempre se descargan del repo)
ARCHIVOS_CERRADOS = [
    "h24", "r24", "h25", "r25",
    "ads_rp_25", "ads_reg_25", "gestiones_25", "fondo_mixto_25", "inder_25",
]

# Archivos que el usuario puede actualizar manualmente
ARCHIVOS_ACTUALIZABLES = ["pi", "h26", "r26"]
