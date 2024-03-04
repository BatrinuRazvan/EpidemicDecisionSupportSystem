# side_by_side.py

import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from backend import helperfunctions

dash.register_page(__name__)

# Define your app layout for the side-by-side page
layout = html.Div([
    dcc.Dropdown(
        id='table-dropdown-1',
        options=[
            {'label': table, 'value': table} for table in ['covid_global', 'covid_romania', 'covid19_tm', 'simulation']
        ],
        value='table1',
        style={'width': '50%'}
    ),
    dcc.Dropdown(
        id='column-dropdown-1',
        options=[],
        multi=True,
        style={'width': '50%'}
    ),
    dcc.RangeSlider(
        id='time-range-slider-1',
        min=0,
        max=1,
        step=1,
        marks={},
        value=[0, 1],
    ),
    dcc.Dropdown(
        id='table-dropdown-2',
        options=[
            {'label': table, 'value': table} for table in ['covid19_tm', 'status', 'covid_romania', 'simulation']
        ],
        value='table2',
        style={'width': '50%'}
    ),
    dcc.Dropdown(
        id='column-dropdown-2',
        options=[],
        multi=True,
        style={'width': '50%'}
    ),
    dcc.RangeSlider(
        id='time-range-slider-2',
        min=0,
        max=1,
        step=1,
        marks={},
        value=[0, 1],
    ),
    html.Button('Plot Side-by-Side', id='plot-button'),
    dcc.Graph(id='side-by-side-graph')
])

# Define callback to update column dropdown options based on selected table
@callback(
    [Output('column-dropdown-1', 'options'),
     Output('column-dropdown-2', 'options')],
    [Input('table-dropdown-1', 'value'),
     Input('table-dropdown-2', 'value')]
)
def update_column_dropdown(table1, table2):
    columns_table1 = helperfunctions.fetch_data_for_table(table1)
    columns_table2 = helperfunctions.fetch_data_for_table(table2)
    options_table1 = [{'label': col, 'value': col} for col in columns_table1]
    options_table2 = [{'label': col, 'value': col} for col in columns_table2]
    return options_table1, options_table2

# Define callback to fetch and plot data based on selected tables and columns
@callback(
    [Output('side-by-side-graph', 'figure'),
     Output('time-range-slider-1', 'min'),
     Output('time-range-slider-1', 'max'),
     Output('time-range-slider-1', 'marks'),
     Output('time-range-slider-1', 'value'),
     Output('time-range-slider-2', 'min'),
     Output('time-range-slider-2', 'max'),
     Output('time-range-slider-2', 'marks'),
     Output('time-range-slider-2', 'value')],
    [Input('table-dropdown-1', 'value'),
     Input('column-dropdown-1', 'value'),
     Input('table-dropdown-2', 'value'),
     Input('column-dropdown-2', 'value'),
     Input('time-range-slider-1', 'value'),  # Include time range slider values as Input
     Input('time-range-slider-2', 'value'),
     Input('plot-button', 'n_clicks')]
)
def plot_side_by_side(table1, columns_table1, table2, columns_table2, time_range_1, time_range_2, n_clicks):
    try:
        if n_clicks is None:
            return dash.no_update

        df_table1 = helperfunctions.fetch_data_for_table(table1)
        df_table2 = helperfunctions.fetch_data_for_table(table2)

        print(f'Data for {table1}:')
        print(df_table1.head())

        print(f'Data for {table2}:')
        print(df_table2.head())

        print(f'Columns for {table1}: {columns_table1}')
        print(f'Columns for {table2}: {columns_table2}')

        if not df_table1.empty and not df_table2.empty:
            # Determine the range of the time sliders dynamically
            min_time_1, max_time_1 = int(df_table1['DAY_INCREMENT'].min()), int(df_table1['DAY_INCREMENT'].max())
            marks_time_1 = {i: str(i) for i in range(min_time_1, max_time_1 + 1)}

            min_time_2, max_time_2 = int(df_table2['DAY_INCREMENT'].min()), int(df_table2['DAY_INCREMENT'].max())
            marks_time_2 = {i: str(i) for i in range(min_time_2, max_time_2 + 1)}

            # Split the range into intervals
            num_intervals = 10
            interval_length_1 = (max_time_1 - min_time_1) // num_intervals
            interval_length_2 = (max_time_2 - min_time_2) // num_intervals

            interval_marks_1 = {min_time_1 + i * interval_length_1: str(min_time_1 + i * interval_length_1) for i in range(num_intervals + 1)}
            interval_marks_2 = {min_time_2 + i * interval_length_2: str(min_time_2 + i * interval_length_2) for i in range(num_intervals + 1)}

            initial_value_1 = min_time_1, min_time_1 + interval_length_1
            initial_value_2 = min_time_2, min_time_2 + interval_length_2

            traces_table1 = [go.Scatter(x=df_table1['DAY_INCREMENT'], y=df_table1[col], mode='lines', name=f'{table1} - {col}') for col in columns_table1]
            traces_table2 = [go.Scatter(x=df_table2['DAY_INCREMENT'], y=df_table2[col], mode='lines', name=f'{table2} - {col}') for col in columns_table2]

            print(f'time_range_1: {time_range_1}')
            print(f'time_range_2: {time_range_2}')
            layout = go.Layout(
                title=f'Side-by-Side Comparison of {", ".join(columns_table1)} for {table1} and {", ".join(columns_table2)} for {table2}',
                xaxis={'title': 'DAY_INCREMENT'},
                yaxis={'title': 'Values'}
            )
            fig = go.Figure(data=traces_table1 + traces_table2, layout=layout)

            return fig, min_time_1, max_time_1, interval_marks_1, initial_value_1, min_time_2, max_time_2, interval_marks_2, initial_value_2
        else:
            return dash.no_update

    except Exception as e:
        print(f"Error in callback: {str(e)}")
        return dash.no_update

