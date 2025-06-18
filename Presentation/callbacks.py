from dash import Input, Output
from Presentation.charts import graf_vse_po_regijah, graf_stanovanja_po_regijah, graf_stanovanja_pie, graf_zemljevid_obcin

def register_callbacks(app, df, df2, df3, geojson_obcine):
    @app.callback(
        Output("bdp-delovno-stanovanja-podjetja", "figure"),
        Output("graf-stanovanja", "figure"),
        Output("graf-stanovanja-pie", "figure"),
        Output("leto-warning", "children"),
        Input("regija-dropdown", "value"),
        Input("leto-obdobje", "value"),
        Input("leva-os-dropdown", "value"),
        Input("desna-os-dropdown", "value")
    )
    def update_chart(selected_regions, leto_obdobje, leva_os, desna_os):
        if not selected_regions or leto_obdobje is None:
            return {}, {}, {}, "Prosimo, izpolnite vsa polja in pri tem pazite, da izberete obdobje med 2008 in 2023."

        leto_od, leto_do = leto_obdobje

        if leto_od > leto_do:
            return {}, {}, {}, "Leto 'od' ne sme biti večje od leta 'do'."

        fig1 = graf_vse_po_regijah(df, selected_regions, leto_obdobje, leva_os, desna_os)
        fig2 = graf_stanovanja_po_regijah(df2, selected_regions, leto_obdobje)
        fig3 = graf_stanovanja_pie(df2, selected_regions, leto_obdobje)

        return fig1, fig2, fig3, ""
    
    @app.callback(
        Output("zemljevid-obcin", "figure"),
        Input("izberi-podatek", "value"),
        Input("izberi-leto-zemljevid", "value")
    )
    def update_map(podatek, leto):
        return graf_zemljevid_obcin(df3, podatek, leto, geojson_obcine)



