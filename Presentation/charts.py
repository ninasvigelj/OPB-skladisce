import plotly.express as px
import pandas as pd

def stolpicni_diagram_linija(df: pd.DataFrame, selected_branch):
    """
    """
    # Filter for the selected product line
    # Tukaj lahko filtriramo že direktno v bazi!

    dff = df[df["branch_name"] == selected_branch]
    # Aggregate gross income by branch
    agg = (
        dff
        .groupby(["product_line"], as_index=False)
        .gross_income
        .sum()
        .sort_values("gross_income", ascending=False)
    )
    # Build bar chart
    fig = px.bar(
        agg,
        x="product_line",
        y="gross_income",        
        title=f"Bruto prihodek za '{selected_branch}' po produktnih linijah",
        labels={"branch_name": "Poslovalnica", "gross_income": "Bruto prihodek"}
    )
    fig.update_layout(margin={"l": 40, "r": 20, "t": 50, "b": 40})
    return fig

def prodaja_po_mesecih(df: pd.DataFrame, selected_branch):
    """
    """
    # Filter for the selected product line
    # Tukaj lahko filtriramo že direktno v bazi!
    
    dff = df[df["branch_name"] == selected_branch]

    dff["invoice_date"] = pd.to_datetime(dff["invoice_date"])
  
    dff["month"] = dff["invoice_date"].dt.to_period("D").dt.to_timestamp()
    monthly_sales =  dff.groupby(["month"], as_index=False).agg({"gross_income": "sum"})

    fig = px.line(
        monthly_sales,
        x="month",
        y="gross_income",
        title="Skupna prodaja po mesecih",
        labels={"month": "Dan", "gross_income": "Bruto prihodek"}
    )
    fig.update_traces(mode="lines+markers")
    fig.update_layout(margin={"t": 40, "l": 40, "r": 20, "b": 30})
    return fig