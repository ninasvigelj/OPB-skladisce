import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import json
import os

def graf_vse_po_regijah(df: pd.DataFrame, selected_regions: list, leto_obdobje: list, leva_os: str, desna_os: str):
    leto_od, leto_do = leto_obdobje

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

    if leva_os in df_grouped.columns:
        fig.add_trace(
            go.Scatter(x=df_grouped["leto"], y=df_grouped[leva_os],
                       name=leva_os.replace("_", " "), mode="lines+markers"),
            secondary_y=False
        )

    if desna_os in df_grouped.columns and desna_os != leva_os:
        fig.add_trace(
            go.Scatter(x=df_grouped["leto"], y=df_grouped[desna_os],
                       name=desna_os.replace("_", " "), mode="lines+markers"),
            secondary_y=True
        )

    # Poimenujmo osi
    imena_osi = {
        "bdp": "BDP (mio EUR)",
        "stevilo_stanovanj": "Število dokončanih stanovanj",
        "stevilo_podjetij": "Število podjetij",
        "delovno_aktivno": "Delovno aktivno prebivalstvo"
    }

    yaxis_title_leva = imena_osi.get(leva_os, leva_os.replace("_", " ").title())
    yaxis_title_desna = imena_osi.get(desna_os, desna_os.replace("_", " ").title())

    fig.update_layout(
        title=f"Podatki za izbrane regije za obdobje {leto_od} do {leto_do}",
        xaxis_title="Leto",
        yaxis_title=yaxis_title_leva,
        margin={"t": 40, "l": 40, "r": 20, "b": 30},
        plot_bgcolor="#ffffff",
        xaxis=dict(
            gridcolor="#e0e0e0"
        ),
        yaxis=dict(
            gridcolor="#e0e0e0"
        )
    )

    fig.update_yaxes(title_text=yaxis_title_desna, secondary_y=True)

    return fig



def graf_stanovanja_po_regijah(df: pd.DataFrame, selected_regije: list, leto_obdobje: list):
    leto_od, leto_do = leto_obdobje

    dff = df[df["regija"].isin(selected_regije)].copy()

    if dff.empty:
        return go.Figure().update_layout(title="Ni podatkov za izbrane regije.")

    dff["leto"] = pd.to_datetime(dff["leto"], format="%Y")
    dff = dff[(dff["leto"].dt.year >= leto_od) & (dff["leto"].dt.year <= leto_do)]

    if dff.empty:
        return go.Figure().update_layout(title="Ni podatkov za izbrana leta.")
    
    dff["leto_leto"] = dff["leto"].dt.year

    dff["sobe"] = dff["sobe"].astype(str)

    # Agregira po letu in številu sob (regije se združijo)
    df_agg = dff.groupby(["leto_leto", "sobe"], as_index=False)["stevilo"].sum()

    fig = px.bar(df_agg,
                x="leto_leto",
                y="stevilo",
                color="sobe",
                barmode="group", 
                title=f"Število stanovanj po občinah za obdobje {leto_od} do {leto_do}",
                labels={"stevilo": "Število stanovanj", "regija": "Regija"})

    fig.update_layout(
        barmode='group', 
        xaxis_title="Leto", 
        yaxis_title="Število stanovanj",
        plot_bgcolor="#ffffff",
        yaxis=dict(
            gridcolor="#e0e0e0"
        )
    )

    return fig

def graf_stanovanja_pie(df: pd.DataFrame, selected_regije: list, leto_obdobje: list):
    leto_od, leto_do = leto_obdobje
    dff = df[df["regija"].isin(selected_regije)].copy()

    if dff.empty:
        return go.Figure().update_layout(title="Ni podatkov za izbrane regije.")

    dff["leto"] = pd.to_datetime(dff["leto"], format="%Y")
    dff = dff[(dff["leto"].dt.year >= leto_od) & (dff["leto"].dt.year <= leto_do)]

    if dff.empty:
        return go.Figure().update_layout(title="Ni podatkov za izbrana leta.")

    df_grouped = dff.groupby("sobe")["stevilo"].sum().reset_index()

    fig = px.pie(df_grouped, values='stevilo', names='sobe', title='Porazdelitev stanovanj po številu sob')

    return fig

def graf_zemljevid_obcin(df: pd.DataFrame, podatek: str, leto: int, geojson_obcine: dict):
    df_filtered = df[df["leto"] == leto]

    if df_filtered.empty:
        return go.Figure().update_layout(title="Ni podatkov za izbrano leto.")

    moznosti_za_title = {
        "stevilo_stanovanj": "Število dokončanih stanovanj",
        "stevilo_podjetij": "Število podjetij",
        "delovno_aktivno": "Število delovno aktivnih prebivalcev (glede na prebivališče)"
    }

    fig = px.choropleth(
        data_frame=df_filtered,
        geojson=geojson_obcine,
        locations="obcina",
        featureidkey="properties.name",
        color=podatek,
        projection="mercator",
        title=f"{moznosti_za_title.get(podatek, podatek.replace('_', ' ').capitalize())} po občinah ({leto})",
        color_continuous_scale="Plasma_r" # same hude barve: https://plotly.com/python/builtin-colorscales/
    )
    fig.update_geos(fitbounds="locations", visible=False)

    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})

    return fig
