import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def graf_vse_po_regijah(df: pd.DataFrame, selected_regions: list, leto_od: int, leto_do: int):
    dff = df[df["regija"].isin(selected_regions)].copy()

    if dff.empty:
        return go.Figure().update_layout(title="Ni podatkov za izbrane regije.")

    dff["leto"] = pd.to_datetime(dff["leto"], format="%Y")
    dff = dff[(dff["leto"].dt.year >= leto_od) & (dff["leto"].dt.year <= leto_do)]

    if dff.empty:
        return go.Figure().update_layout(title="Ni podatkov za izbrana leta.")

    df_grouped = dff.groupby("leto").agg({
        "bdp": "sum",
        "stevilo_stanovanj": "sum",
        "stevilo_podjetij": "sum",
        "delovno_aktivno": "sum"
    }).reset_index()

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(x=df_grouped["leto"], y=df_grouped["bdp"],
                   name="BDP v mio. EUR", mode="lines+markers"),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(x=df_grouped["leto"], y=df_grouped["stevilo_stanovanj"],
                   name="Št. stanovanj", mode="lines+markers"),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(x=df_grouped["leto"], y=df_grouped["stevilo_podjetij"],
                   name="Št. podjetij", mode="lines+markers"),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(x=df_grouped["leto"], y=df_grouped["delovno_aktivno"],
                   name="Delovno aktivno", mode="lines+markers"),
        secondary_y=True
    )

    fig.update_layout(
        title=f"Podatki za izbrane regije za obdobje {leto_od} do {leto_do}",
        xaxis_title="Leto",
        yaxis_title="BDP / št. stanovanj / št. podjetij",
        margin={"t": 40, "l": 40, "r": 20, "b": 30}
    )

    fig.update_yaxes(title_text="Delovno aktivno prebivalstvo", secondary_y=True)

    return fig
