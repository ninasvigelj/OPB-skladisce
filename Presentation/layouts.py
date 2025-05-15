from dash import html, dcc


def create_layout(dropdown_options, default_value):
    """
    Ustvari glavno postavitev za vizualizacijo prodaje po produktnih linijah.
    """
    return html.Div([
        html.H1("Prodaja po produktnih linijah"),
        html.Div([
            html.Label("Izberite trgovino:"),
            dcc.Dropdown(
                id="product-line-dropdown",
                options=dropdown_options,
                value=default_value,
                clearable=False
            )
        ], style={"width": "30%", "margin-bottom": "1rem"}),
        html.Div([
        dcc.Graph(id="income-by-branch"),
        dcc.Graph(id="income-by-month")
    ], style={
        "display": "flex",
        "justifyContent": "flex-start",  # or 'center', 'flex-start'
        "gap": "2rem",  # adds space between charts
    })
        #dcc.Graph(id="income-by-branch")
    ])