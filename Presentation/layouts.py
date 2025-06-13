from dash import html, dcc

def create_layout_regije(dropdown_options, default_value):
    """
    Ustvari postavitev za prikaz BDP, delovno aktivnih in stanovanj po letih za izbrano regijo.
    """
    return html.Div([
        html.H1("BDP, delovno aktivni in stanovanja po regijah"),

        html.Div([
            html.Label("Izberite regijo:"),
            dcc.Dropdown(
                id="regija-dropdown",
                options=dropdown_options,
                value=default_value,
                multi=True,
                clearable=True
            )
        ], style={"width": "40%", "margin-bottom": "1.5rem"}),

        dcc.Graph(id="bdp-delovno-stanovanja")
    ], style={"padding": "2rem"})


