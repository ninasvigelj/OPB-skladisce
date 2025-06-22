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
                    {"label": "Število dokončanih stanovanj", "value": "stevilo_stanovanj"},
                    {"label": "Število podjetij", "value": "stevilo_podjetij"},
                    {"label": "Delovno aktivno prebivalstvo", "value": "delovno_aktivno"},
                ],
                value=default_leva,
                placeholder="Izberite podatke:",
                style={"width": "250px"},
                clearable=False
            )
        ], style={"display": "inline-block", "margin-right": "30px"}),

        html.Div([
            html.Label("Desna os:", style={"margin-right": "10px"}),
            dcc.Dropdown(
                id="desna-os-dropdown",
                options=[
                    {"label": "BDP", "value": "bdp"},
                    {"label": "Število dokončanih stanovanj", "value": "stevilo_stanovanj"},
                    {"label": "Število podjetij", "value": "stevilo_podjetij"},
                    {"label": "Delovno aktivno prebivalstvo", "value": "delovno_aktivno"},
                ],
                value=default_desna,
                placeholder="Izberite podatke:",
                style={"width": "250px"},
                clearable=False
            )
        ], style={"display": "inline-block"}),

        html.Div(id="leto-warning", style={"color": "red", "margin-bottom": "1rem"}),

        dcc.Graph(id="bdp-delovno-stanovanja-podjetja"),
        html.P("Graf prikazuje podatke izbranih regij - če imamo izranih več regij, graf prikazuje vsoto določene količine za vse izbrane regije-" \
        " skozi čas (izbrano obdobje) za izbrane indikatorje (npr. BDP, število podjetij, itd.). Na grafu lahko za izbrano obdobje opazujemo, kako so se gibali izbrani podatki. Pri analizi s pomočjo tega grafa moramo "
        "biti pozorni na to katere podatke smo izbrali na levi in katere na desni osi in da te dve ne prikazujeta nujno primerljivih številk."
        , style={"margin-bottom": "2rem"}),

        html.Hr(style={"margin": "2rem 0"}),

        html.H2("Število dokončanih stanovanj po regijah in izbranih letih po številu sob"),

        html.Div([
            html.Div([
                dcc.Graph(id="graf-stanovanja")
            ], style={"width": "70%", "padding-right": "1rem"}),

            html.Div([
                dcc.Graph(id="graf-stanovanja-pie")
            ], style={"width": "30%"})
        ], style={"display": "flex", "margin-bottom": "2rem"}),

        html.P("Levi graf prikazuje podatke o številu dokončanih stanovanj v izbranih regijah po posameznih letih v izbranem obdobju. Desni graf pa nam prikazuje kako" \
        " so vsa dokočana stanovanja v določenem odbobju (gledamo torej vsoto po letih) razdeljena glede na število sob oziroma kolikšen del dokončanih stanovanj ima določeno število sob." \
        " Podatki v obeh grafih se seštevajo glede na izbrane regije.", style={"margin-bottom": "2rem"}),

        html.Hr(style={"margin": "2rem 0"}),

        html.H2("Prikaz podatkov za izbrane parametre po občinah"),


        html.Div([
            html.Label("Izberi podatek in leto za zemljevid občin:"),
            
            dcc.Dropdown(
                id="izberi-podatek",
                options=[
                    {"label": "Delovno aktivno prebivalstvo", "value": "delovno_aktivno"},
                    {"label": "Število podjetij", "value": "stevilo_podjetij"},
                    {"label": "Število dokončanih stanovanj", "value": "stevilo_stanovanj"}
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

            dcc.Graph(id="zemljevid-obcin", style={"height": "600px"}),
            html.P("Graf prikazuje izbrane podatke po občinah za izbrani leto." \
            " Na levi strani lahko vidimo barvno lestvico ki prikazuje vrednosti izbranega indikatorja." \
            " Opomba*: občina Mirna obstaja od leta 2009, občina Ankaran pa od leta 2015 naprej, zato so zemljevidi" \
            " v teh letih zemljevidi malo drugačni. ", style={"margin-bottom": "2rem"})

        ])

    ], style={"padding": "2rem"})
