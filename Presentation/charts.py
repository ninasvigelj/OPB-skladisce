import plotly.express as px
import pandas as pd

def graf_BDP_delovno_stanovanja_po_regiji(df: pd.DataFrame, selected_region: str):
    dff = df[df["regija"] == selected_region]

    if dff.empty:
        return px.line(title="Ni podatkov za izbrano regijo.")

    # Pretvori leto v datetime (če ni že)
    dff["leto"] = pd.to_datetime(dff["leto"], format="%Y")

    # Preoblikuj podatke v long (tidy) obliko, da lahko z isto X osjo prikažemo več Y-jev
    df_long = dff.melt(
        id_vars=["leto"],
        value_vars=["bdp", "stevilo_stanovanj", "delovno_aktivno"],
        var_name="indikator",
        value_name="vrednost"
    )

    # Nariši črte za vsak indikator posebej (različna barva)
    fig = px.line(
        df_long,
        x="leto",
        y="vrednost",
        color="indikator",
        title=f"BDP, stanovanja in delovno aktivno prebivalstvo po letih za regijo: {selected_region}",
        markers=True
    )

    fig.update_layout(margin={"t": 40, "l": 40, "r": 20, "b": 30})
    return fig