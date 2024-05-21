import dash
import dash_core_components as dcc
import dash_html_components as html
from dash import callback
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
from backend import helperfunctions
import pandas as pd

dash.register_page(__name__, path='/real_life_comparison')

# Fetch the disease data
disease_data = helperfunctions.fetch_disease_table()

# Convert disease data to a DataFrame
df_disease = pd.DataFrame(disease_data, columns=["Disease", "Total"])

fig_pie = px.pie(df_disease, names="Disease", values="Total", title="Disease Distribution")

layout = html.Div([
    dcc.Graph(id="pie-chart", figure=fig_pie),
    html.Div(id="symptoms-output"),
    dcc.Graph(id="time-series-chart")
])


# Callback to update symptoms and time series chart based on pie chart selection
@callback(
    [Output("symptoms-output", "children"),
     Output("time-series-chart", "figure")],
    [Input("pie-chart", "clickData")]
)
def update_output(clickData):
    if clickData is None:
        return "", go.Figure()

    # Extract the clicked disease
    selected_disease = clickData["points"][0]["label"]

    # Fetch symptoms for the selected disease
    symptoms_data = helperfunctions.fetch_symptoms_table(selected_disease)

    # Convert symptoms data to a list of strings
    symptoms_list = [html.Div(["• ", symptom]) for symptom in symptoms_data]

    # Fetch disease timestamp data for the selected disease
    timestamp_data = helperfunctions.fetch_disease_timestamp_table(selected_disease)

    # Convert timestamp data to a DataFrame
    df_timestamp = pd.DataFrame(timestamp_data, columns=["Timestamp", "Total"])

    # Create the time series chart
    fig_time_series = px.line(df_timestamp, x="Timestamp", y="Total", title=f"Time Series for {selected_disease}")

    return symptoms_list, fig_time_series