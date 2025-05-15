from dash import Input, Output
import plotly.express as px

from Presentation.charts import stolpicni_diagram_linija, prodaja_po_mesecih


def register_callbacks(app, df):
    """
    Registriramo povratne klice za Dash aplikacijo.
    """

    # Posodobimo prikaz prodaje glede na izbor trgovine
    @app.callback(
        Output("income-by-branch", "figure"),
        Input("product-line-dropdown", "value")
    )
    def update_income_chart(selected_branch):
      fig = stolpicni_diagram_linija(df, selected_branch)
      return fig
    
    @app.callback(
        Output("income-by-month", "figure"),
        Input("product-line-dropdown", "value")
    )
    def update_line_chart(selected_branch):
      fig = prodaja_po_mesecih(df, selected_branch)
      return fig