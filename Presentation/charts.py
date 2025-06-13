import plotly.express as px
import pandas as pd

def graf_BDP_delovno_stanovanja_po_regiji(df: pd.DataFrame, selected_regions: list):
    dff = df[df["regija"].isin(selected_regions)]

    if dff.empty:
        return px.line(title="Ni podatkov za izbrane regije.")

    dff["leto"] = pd.to_datetime(dff["leto"], format="%Y")

    df_grouped = dff.groupby("leto").agg({
        "bdp": "sum",
        "stevilo_stanovanj": "sum",
        "delovno_aktivno": "sum"
    }).reset_index()

    df_long = df_grouped.melt(
        id_vars=["leto"],
        value_vars=["bdp", "stevilo_stanovanj", "delovno_aktivno"],
        var_name="indikator",
        value_name="vrednost"
    )

    fig = px.line(
        df_long,
        x="leto",
        y="vrednost",
        color="indikator",
        title=f"Skupno za regije: {', '.join(selected_regions)}",
        markers=True
    )

    fig.update_layout(margin={"t": 40, "l": 40, "r": 20, "b": 30})
    return fig