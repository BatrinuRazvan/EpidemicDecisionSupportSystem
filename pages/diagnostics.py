import dash
from dash import callback, html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objs as go
from backend import helperfunctions
import pandas as pd
from constants import COLUMN_NAME_MAPPING

dash.register_page(__name__, path='/diagnostics')

disease_data = helperfunctions.fetch_data_for_table('diagnostics')

df_disease = pd.DataFrame(disease_data, columns=["NAME", "TOTAL"])

fig_pie = px.pie(df_disease, names="NAME", values="TOTAL")
fig_pie.update_traces(textposition='inside', textinfo='percent+label')
fig_pie.update_layout(
    font=dict(family="Arial", size=20),
)

layout = html.Div([
    html.H1("Diagnostics and Cases", style={'text-align': 'center', 'font-size': '32px'}),
    dcc.Graph(id="pie-chart", figure=fig_pie, style={"marginLeft": "2%"}),
    html.Div(id="symptoms-output", style={"marginTop": 20, "textAlign": "center"}),
    dcc.Graph(id="time-series-chart")
], style={"fontFamily": "Arial"})


@callback(
    Output("pie-chart", "figure"),
    Input("url", "pathname")  # Assuming you have dcc.Location component on your page
)
def update_pie_chart(pathname):
    disease_data = helperfunctions.fetch_data_for_table('diagnostics')
    df_disease = pd.DataFrame(disease_data, columns=["NAME", "TOTAL"])
    fig_pie = px.pie(df_disease, names="NAME", values="TOTAL")
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(
        font=dict(family="Arial", size=20),
    )
    return fig_pie

@callback(
    [Output("symptoms-output", "children"),
     Output("time-series-chart", "figure")],
    [Input("pie-chart", "clickData")]
)
def update_output(clickData):
    if clickData is None:
        return html.Div("Please select a diagnostic from the pie chart.", style={"textAlign": "center", "fontSize": "16px"}), go.Figure()

    selected_disease = clickData["points"][0]["label"]

    try:
        symptoms_data = helperfunctions.fetch_data_for_diagnostic('symptoms', selected_disease)

        if symptoms_data.empty:
            symptoms_list = html.Div(f"Diagnostic: {selected_disease} - No symptoms data available", style={"textAlign": "center"})
        else:
            symptoms_list = [
                html.Div([
                    html.Div(f"Diagnostic: {selected_disease}",
                             style={"textAlign": "left", "marginLeft": "46%", "fontSize": "25px", "fontWeight": "bold"}),
                    html.Div([
                        "Symptoms:",
                        html.Ul([html.Li(symptom["SYMPTOM"], style={"fontSize": "18px"}) for _, symptom in symptoms_data.iterrows()],
                                style={"listStyleType": "disc", "paddingLeft": "40px", "marginTop": "5px"})
                    ], style={"textAlign": "left", "marginLeft": "46%", "marginRight": "20%", "fontSize": "25px", "fontWeight": "bold", "marginTop": "1%"})
                ], style={"fontFamily": "Arial"})
            ]

        timestamp_data = helperfunctions.fetch_data_for_diagnostic('diagnostics_timestamps', selected_disease)

        if timestamp_data.empty:
            fig_time_series = go.Figure()
        else:
            df_timestamp = pd.DataFrame(timestamp_data)
            df_timestamp['TIMESTAMP'] = pd.to_datetime(df_timestamp['TIMESTAMP'])
            fig_time_series = px.line(df_timestamp, x="TIMESTAMP", y="REGISTERED",
                                      labels={
                                          "TIMESTAMP": COLUMN_NAME_MAPPING.get("TIMESTAMP", "Over Time"),
                                          "REGISTERED": COLUMN_NAME_MAPPING.get("REGISTERED", "Cases Registered")
                                      },
                                      title=f"Reported cases of {selected_disease} over time")

        return symptoms_list, fig_time_series

    except Exception as e:
        return html.Div(f"An error occurred: {e}", style={"textAlign": "center", "color": "red"}), go.Figure()
