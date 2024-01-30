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
            {'label': table, 'value': table} for table in ['covid_global', 'covid_romania', 'covid19_tm', 'status']
        ],
        value=['covid_global', 'covid_romania', 'covid19_tm', 'status'][0] if ['covid_global', 'covid_romania', 'covid19_tm', 'status'] else None,
        style={'width': '50%'}
    ),
    dcc.Dropdown(
        id='column-dropdown-1',
        options=[],
        value=['SUM_DEATHS'],
        multi=True,
        style={'width': '50%'}
    ),
    dcc.RangeSlider(
        id='time-range-slider-1',
        min=1,
        max=10,
        step=1,
        marks={i: str(i) for i in range(11)},
        value=[1, 10],
    ),
    dcc.Dropdown(
        id='table-dropdown-2',
        options=[
            {'label': table, 'value': table} for table in ['covid_global', 'covid_romania', 'covid19_tm', 'status']
        ],
        value=['covid_global', 'covid_romania', 'covid19_tm', 'status'][0] if ['covid_global', 'covid_romania', 'covid19_tm', 'status'] else None,
        style={'width': '50%'}
    ),
    dcc.Dropdown(
        id='column-dropdown-2',
        options=[],
        value=['SUM_CASES'],
        multi=True,
        style={'width': '50%'}
    ),
    dcc.RangeSlider(
        id='time-range-slider-2',
        min=1,
        max=10,
        step=1,
        marks={i: str(i) for i in range(11)},
        value=[1, 10],
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
    [Input('table-dropdown-1', 'value'),  # Ensure these inputs are correct
     Input('column-dropdown-1', 'value'),
     Input('table-dropdown-2', 'value'),
     Input('column-dropdown-2', 'value'),
     Input('time-range-slider-1', 'value'),
     Input('time-range-slider-2', 'value'),
     Input('plot-button', 'n_clicks')]
)
def plot_side_by_side(table1_name, columns_table1, table2_name, columns_table2, time_range_1, time_range_2, n_clicks):
    try:
        if n_clicks is None:
            return dash.no_update, time_range_1, time_range_2

        df_table1 = helperfunctions.fetch_data_for_table(table1_name)
        df_table2 = helperfunctions.fetch_data_for_table(table2_name)

        # Filter data based on the range slider values
        df_table1_filtered = df_table1[df_table1['DAY_INCREMENT'].between(time_range_1[0], time_range_1[1])]
        df_table2_filtered = df_table2[df_table2['DAY_INCREMENT'].between(time_range_2[0], time_range_2[1])]

        if not df_table1_filtered.empty and not df_table2_filtered.empty:
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

            # Use the filtered dataframes for plotting
            traces_table1 = [go.Scatter(x=df_table1_filtered['DAY_INCREMENT'], y=df_table1_filtered[col], mode='lines',
                                        name=f'{table1_name} - {col}') for col in columns_table1]
            traces_table2 = [go.Scatter(x=df_table2_filtered['DAY_INCREMENT'], y=df_table2_filtered[col], mode='lines',
                                        name=f'{table2_name} - {col}') for col in columns_table2]

            layout = go.Layout(
                title=f'Side-by-Side Comparison of {", ".join(columns_table1)} for {table1_name} and {", ".join(columns_table2)} for {table2_name}',
                xaxis={'title': 'DAY_INCREMENT'},
                yaxis={'title': 'Values'}
            )
            fig = go.Figure(data=traces_table1 + traces_table2, layout=layout)

            # Make sure to return a value for each Output listed in the decorator
            return fig, min_time_1, max_time_1, interval_marks_1, time_range_1, min_time_2, max_time_2, interval_marks_2, time_range_2

    except Exception as e:

        print(f"Error in callback: {str(e)}")

        # Ensure to return the correct number of values, even in case of error

        return dash.no_update, 0, 1, {}, [0, 1], 0, 1, {}, [0, 1]