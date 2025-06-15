from dash import Input, Output
from PRESENTATION.charts import graf_vse_po_regijah, graf_stanovanja_po_regijah

def register_callbacks(app, df):
    @app.callback(
        Output("bdp-delovno-stanovanja-podjetja", "figure"),
        Output("leto-warning", "children"),
        Input("regija-dropdown", "value"),
        Input("leto-od", "value"),
        Input("leto-do", "value")
    )
    def update_chart(selected_regions, leto_od, leto_do):
        if not selected_regions or leto_od is None or leto_do is None:
            return {}, "Prosimo, izpolnite vsa polja in pri tem pazite, da izberete obdobje med 2008 in 2023."

        if leto_od > leto_do:
            return {}, "Leto 'od' ne sme biti večje od leta 'do'."

        fig = graf_vse_po_regijah(df, selected_regions, leto_od, leto_do)
        return fig, ""
    
        fig2 = graf_stanovanja_po_regijah(df, selected_regions, leto_od, leto_do)
        return fig2, ""
