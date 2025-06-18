from dash import html, dcc

def create_layout_regije(dropdown_options, default_value, default_leva, default_desna):
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
            html.Label("Izberi obdobje:"),
            dcc.RangeSlider(
                id="leto-obdobje",
                min=2008,
                max=2023,
                step=1,
                value=[2008, 2023],
                marks={leto: str(leto) for leto in range(2008, 2024)},
                tooltip={"placement": "bottom", "always_visible": True},
                allowCross=False
            )
        ], style={"margin-bottom": "1.5rem"}),

        html.Div([
            html.Label("Leva os:", style={"margin-right": "10px"}),
            dcc.Dropdown(
                id="leva-os-dropdown",
                options=[
                    {"label": "BDP", "value": "bdp"},
                    {"label": "Število stanovanj", "value": "stevilo_stanovanj"},
                    {"label": "Število podjetij", "value": "stevilo_podjetij"},
                    {"label": "Delovno aktivno prebivalstvo", "value": "delovno_aktivno"},
                ],
                value=default_leva,
                placeholder="Izberite podatke:",
                style={"width": "200px"},
                clearable=False
            )
        ], style={"display": "inline-block", "margin-right": "30px"}),

        html.Div([
            html.Label("Desna os:", style={"margin-right": "10px"}),
            dcc.Dropdown(
                id="desna-os-dropdown",
                options=[
                    {"label": "BDP", "value": "bdp"},
                    {"label": "Število stanovanj", "value": "stevilo_stanovanj"},
                    {"label": "Število podjetij", "value": "stevilo_podjetij"},
                    {"label": "Delovno aktivno prebivalstvo", "value": "delovno_aktivno"},
                ],
                value=default_desna,
                placeholder="Izberite podatke:",
                style={"width": "200px"},
                clearable=False
            )
        ], style={"display": "inline-block"}),

        html.Div(id="leto-warning", style={"color": "red", "margin-bottom": "1rem"}),

        dcc.Graph(id="bdp-delovno-stanovanja-podjetja"),

        dcc.Graph(id="graf-stanovanja"),

        dcc.Graph(id="graf-stanovanja-pie"),

        html.Div([
            html.Label("Izberi podatek in leto za zemljevid občin:"),
            
            dcc.Dropdown(
                id="izberi-podatek",
                options=[
                    {"label": "Delovno aktivni", "value": "delovno_aktivno"},
                    {"label": "Podjetja", "value": "stevilo_podjetij"},
                    {"label": "Stanovanja", "value": "stevilo_stanovanj"}
                ],
                value="delovno_aktivno",
                clearable=False,
                style={"margin-bottom": "10px"}
            ),

            dcc.Dropdown(
                id="izberi-leto-zemljevid",
                options=[{"label": str(leto), "value": leto} for leto in range(2008, 2024)],
                value=2023,
                clearable=False,
                style={"margin-bottom": "30px"}
            ),

            dcc.Graph(id="zemljevid-obcin", style={"height": "600px"})
        ])

    ], style={"padding": "2rem"})
