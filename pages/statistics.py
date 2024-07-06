import dash
from dash import html, dcc, Output, Input, callback, State
import plotly.graph_objects as go
from backend import helperfunctions
from constants import *
import pandas as pd

dash.register_page(__name__)

df = helperfunctions.fetch_data_for_simulation()
available_columns = [col for col in df.columns if col not in [BY_ID, BY_DATE]]
mapped_columns = {col: COLUMN_NAME_MAPPING.get(col, col) for col in available_columns}

layout = html.Div([
    html.H1('Statistics for Current Epidemic', style={'text-align': 'center'}),
    html.H2('Chart Type:', style={'marginLeft': '5%'}),
    dcc.Dropdown(
        id='chart-type-dropdown',
        options=[
            {'label': 'Line Chart', 'value': 'line'},
            {'label': 'Bar Chart', 'value': 'bar'},
            {'label': 'Area Chart', 'value': 'area'}
        ],
        value='line',
        style={'width': '30%', 'marginLeft': '3%'}
    ),
    html.H2('Statistic Display:', style={'marginLeft': '5%'}),
    dcc.Dropdown(
        id='statistic-display-dropdown',
        options=[
            {'label': 'Daily', 'value': 'daily'},
            {'label': 'Weekly', 'value': 'weekly'},
            {'label': 'Monthly', 'value': 'monthly'},
            {'label': 'Yearly', 'value': 'yearly'}
        ],
        value='daily',
        style={'width': '30%', 'marginLeft': '3%'}
    ),
    dcc.Graph(id='dynamic-statistics'),
    html.Div([
        html.Button(mapped_columns[stat], id=f"btn-{stat.lower()}", n_clicks=0,
                    style={'background-color': 'blue', 'border-radius': '20px', 'color': 'white',
                           'padding': '10px 20px', 'font-size': '16px', 'margin': '5px'})
        for stat in mapped_columns
    ] + [
        html.Button('Clear All', id='btn-clear-all', n_clicks=0,
                    style={'background-color': 'red', 'border-radius': '20px', 'color': 'white',
                           'padding': '10px 20px', 'font-size': '16px', 'margin': '5px'})
    ], style={'display': 'flex', 'justify-content': 'center', 'gap': '10px'}),
], style={'fontFamily': 'Arial'})

selected_areas = []


def update_selected_areas(button_id):
    selected_area = button_id.replace('btn-', '').upper()
    if selected_area not in selected_areas:
        selected_areas.append(selected_area)


def clear_all():
    selected_areas.clear()


@callback(
    [Output(f"btn-{stat.lower()}", 'style') for stat in mapped_columns] +
    [Output('dynamic-statistics', 'figure')],
    [Input(f"btn-{stat.lower()}", 'n_clicks_timestamp') for stat in mapped_columns] +
    [Input('btn-clear-all', 'n_clicks_timestamp'),
     Input('chart-type-dropdown', 'value'),
     Input('statistic-display-dropdown', 'value')],
    [State(f"btn-{stat.lower()}", 'id') for stat in mapped_columns] +
    [State('chart-type-dropdown', 'value'),
     State('statistic-display-dropdown', 'value')]
)
def update_dashboard(*args):
    ctx = dash.callback_context
    inputs = ctx.inputs
    states = ctx.states

    button_styles = [
        {'background-color': 'blue', 'border-radius': '20px', 'color': 'white',
         'padding': '10px 20px', 'font-size': '16px', 'margin': '5px'} for _ in mapped_columns
    ]

    button_id = ''
    latest_click = -1

    timestamp_inputs = {key: value for key, value in inputs.items() if 'n_clicks_timestamp' in key and value is not None}

    for inp_id, timestamp in timestamp_inputs.items():
        if timestamp:
            current_timestamp = int(timestamp)
            if latest_click < current_timestamp:
                latest_click = current_timestamp
                button_id = inp_id.split('.')[0]

    chart_type = states['chart-type-dropdown.value']
    statistic_display = states['statistic-display-dropdown.value']
    if button_id == 'btn-clear-all':
        clear_all()
    elif 'btn' in button_id:
        update_selected_areas(button_id)
        index = [f"btn-{stat.lower()}" for stat in mapped_columns].index(button_id)
        button_styles[index] = {'background-color': 'orange', 'border-radius': '20px', 'color': 'white',
                                'padding': '10px 20px', 'font-size': '16px', 'margin': '5px'}

    df = helperfunctions.fetch_data_for_simulation()
    if df is None or df.empty:
        print("No data retrieved from the database.")
        return [*button_styles, go.Figure()]

    if statistic_display == 'daily':
        df['INTERVAL'] = df[BY_ID]
    elif statistic_display == 'weekly':
        df['INTERVAL'] = df[BY_ID] // 7
    elif statistic_display == 'monthly':
        df['INTERVAL'] = df[BY_ID] // 30
    elif statistic_display == 'yearly':
        df['INTERVAL'] = df[BY_ID] // 365

    numeric_df = df.select_dtypes(include='number')

    df_resampled = numeric_df.groupby('INTERVAL').sum().reset_index()

    selected_df = df_resampled[['INTERVAL'] + selected_areas]

    try:
        fig = go.Figure()

        for area in selected_areas:
            area_label = COLUMN_NAME_MAPPING.get(area, area)
            if chart_type == 'line' or chart_type == 'area':
                fig.add_trace(go.Scatter(x=selected_df['INTERVAL'], y=selected_df[area], mode='lines', fill='tozeroy' if chart_type == 'area' else None, name=area_label))
            elif chart_type == 'bar':
                fig.add_trace(go.Bar(x=selected_df['INTERVAL'], y=selected_df[area], name=area_label))

        fig.update_layout(title='Dynamic Statistics', xaxis_title='Interval', yaxis_title='Value')

        return [*button_styles, fig]
    except Exception as e:
        print(f"Error creating graph: {e}")
        return [*button_styles, go.Figure()]

