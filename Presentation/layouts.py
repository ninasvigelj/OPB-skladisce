from dash import html, dcc

def create_layout_regije(dropdown_options, default_value):
    return html.Div([
        html.H1("Podatki po izbranih regijah"),

        html.Div([
            html.Label("Izberite regijo:"),
            dcc.Dropdown(
                id="regija-dropdown",
                options=dropdown_options,
                value=default_value,
                multi=True,
                clearable=True
            ),
        ], style={"width": "40%", "margin-bottom": "1rem"}),

        html.Div([
            html.Div([
                html.Label("Leto od:"),
                dcc.Input(
                    id="leto-od",
                    type="number",
                    min=2008,
                    max=2023,
                    step=1,
                    value=2008,
                    style={"width": "100px"}
                )
            ], style={"margin-right": "1.5rem"}),

            html.Div([
                html.Label("Leto do:"),
                dcc.Input(
                    id="leto-do",
                    type="number",
                    min=2008,
                    max=2023,
                    step=1,
                    value=2023,
                    style={"width": "100px"}
                )
            ])
        ], style={"display": "flex", "margin-bottom": "1.5rem"}),

        html.Div(id="leto-warning", style={"color": "red", "margin-bottom": "1rem"}),

        dcc.Graph(id="bdp-delovno-stanovanja-podjetja"),
        # Nov graf za stanovanja
        dcc.Graph(id="graf-stanovanja")
    ], style={"padding": "2rem"})
