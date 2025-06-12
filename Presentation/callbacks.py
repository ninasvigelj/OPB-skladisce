from dash import Input, Output
import plotly.express as px
from PRESENTATION.charts import graf_BDP_delovno_stanovanja_po_regiji  

def register_callbacks(app, df):
    """
    Registriramo povratne klice za Dash aplikacijo.
    """

    # Posodobimo graf glede na izbor regije
    @app.callback(
        Output("bdp-delovno-stanovanja", "figure"),
        Input("regija-dropdown", "value")
    )
    def update_chart(selected_region):
        fig = graf_BDP_delovno_stanovanja_po_regiji(df, selected_region)
        return fig
