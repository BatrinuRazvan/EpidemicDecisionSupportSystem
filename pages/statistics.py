import dash
from dash import html, dcc, Output, Input, callback, State
import plotly.graph_objects as go
from backend import helperfunctions
from constants import *

dash.register_page(__name__)

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
    dcc.Graph(id='dynamic-statistics'),
    html.Div([
        html.Button(stat['label'], id=f"btn-{stat['value'].lower()}", n_clicks=0,
                    style={'background-color': 'blue', 'border-radius': '20px', 'color': 'white',
                           'padding': '10px 20px', 'font-size': '16px', 'margin': '5px'})
        for stat in TABLE_OPTIONz
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
    [Output(f"btn-{stat['value'].lower()}", 'style') for stat in TABLE_OPTIONz] +
    [Output('dynamic-statistics', 'figure')],
    [Input(f"btn-{stat['value'].lower()}", 'n_clicks_timestamp') for stat in TABLE_OPTIONz] +
    [Input('btn-clear-all', 'n_clicks_timestamp'),
     Input('chart-type-dropdown', 'value')],
    [State(f"btn-{stat['value'].lower()}", 'id') for stat in TABLE_OPTIONz] +
    [State('chart-type-dropdown', 'value')]
)
def update_dashboard(*args):
    ctx = dash.callback_context
    inputs = ctx.inputs
    states = ctx.states

    button_styles = [
        {'background-color': 'blue', 'border-radius': '20px', 'color': 'white',
         'padding': '10px 20px', 'font-size': '16px', 'margin': '5px'} for _ in TABLE_OPTIONz
    ]  # Default styles for all buttons

    button_id = ''
    latest_click = -1  # Initialize as a large negative number

    # Filter out non-timestamp inputs
    timestamp_inputs = {key: value for key, value in inputs.items() if 'n_clicks_timestamp' in key and value is not None}

    # Find the button that was last clicked
    for inp_id, timestamp in timestamp_inputs.items():
        if timestamp:
            current_timestamp = int(timestamp)  # Convert timestamp safely
            if latest_click < current_timestamp:
                latest_click = current_timestamp
                button_id = inp_id.split('.')[0]

    chart_type = states['chart-type-dropdown.value']
    if button_id == 'btn-clear-all':
        clear_all()
    elif 'btn' in button_id:
        update_selected_areas(button_id)
        index = [f"btn-{stat['value'].lower()}" for stat in TABLE_OPTIONz].index(button_id)
        button_styles[index] = {'background-color': 'orange', 'border-radius': '20px', 'color': 'white',
                                'padding': '10px 20px', 'font-size': '16px', 'margin': '5px'}  # Change style for clicked button

    df = helperfunctions.fetch_data_for_simulation()
    if df is None or df.empty:
        print("No data retrieved from the database.")
        return [*button_styles, go.Figure()]

    selected_df = df[['DAY_INCREMENT'] + selected_areas]

    try:
        fig = go.Figure()

        for area in selected_areas:
            if chart_type == 'line' or chart_type == 'area':
                fig.add_trace(go.Scatter(x=selected_df['DAY_INCREMENT'], y=selected_df[area], mode='lines', fill='tozeroy' if chart_type == 'area' else None, name=area))
            elif chart_type == 'bar':
                fig.add_trace(go.Bar(x=selected_df['DAY_INCREMENT'], y=selected_df[area], name=area))

        fig.update_layout(title='Dynamic Statistics', xaxis_title='Day', yaxis_title='Value')

        return [*button_styles, fig]
    except Exception as e:
        print(f"Error creating graph: {e}")
        return [*button_styles, go.Figure()]
