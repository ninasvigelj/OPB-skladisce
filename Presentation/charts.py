import plotly.express as px
import pandas as pd

def graf_BDP_delovno_stanovanja_po_regiji(df: pd.DataFrame, selected_region: str):
    dff = df[df["regija"] == selected_region]

    dff["leto"] = pd.to_datetime(df["leto"], format="%Y")

    fig = px.line(
        dff,
        x="leto",
        y="BDP",
        title="Skupna prodaja po mesecih"
    )
    fig.update_traces(mode="lines+markers")
    fig.update_layout(margin={"t": 40, "l": 40, "r": 20, "b": 30})
    return fig

