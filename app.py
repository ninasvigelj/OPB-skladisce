import pandas as pd
from dash import Dash

from SERVICES.statistics_service import StatisticsService
from PRESENTATION.layouts import create_layout_regije 
from PRESENTATION.callbacks import register_callbacks

# Pridobi podatke
service = StatisticsService()
df = service.bdp_delovno_stanovanja_po_regijah()

# Pripravi možnosti za dropdown
regije = df["regija"].sort_values().unique()
dropdown_options = [{"label": reg, "value": reg} for reg in regije]

# Ustvari Dash aplikacijo
app = Dash(__name__, external_stylesheets=[
    "https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css"
])

# Nastavi postavitev
app.layout = create_layout_regije(
    dropdown_options=dropdown_options,
    default_value=regije[0]
)

# Registriraj povratne klice
register_callbacks(app, df)

# Zaženi aplikacijo
if __name__ == "__main__":
    app.run(debug=True)