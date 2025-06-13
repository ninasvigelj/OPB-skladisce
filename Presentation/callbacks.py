from dash import Input, Output
import plotly.express as px
from PRESENTATION.charts import graf_vse_po_regijah  

def register_callbacks(app, df):
    """
    Registriramo povratne klice za Dash aplikacijo.
    """

    @app.callback(
        Output("bdp-delovno-stanovanja-podjetja", "figure"),
        Input("regija-dropdown", "value")
    )
    def update_chart(selected_region):
        fig = graf_vse_po_regijah(df, selected_region)
        return fig
