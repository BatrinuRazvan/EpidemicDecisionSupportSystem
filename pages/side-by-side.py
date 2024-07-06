from dash.dependencies import Input, Output
import dash
from dash import dcc, html, callback
import plotly.graph_objs as go
from backend import helperfunctions
from dash.exceptions import PreventUpdate
from constants import *

dash.register_page(__name__)

layout = html.Div([
    html.H2("Choose the data you want to plot", style={'textAlign': 'center', 'marginBottom': '20px', 'color': '#2c3e50'}),

    dcc.Dropdown(
        id='table-dropdown-1',
        options=TABLE_OPTIONS,
        value=TABLE_OPTIONS[0]['value'],
        style={'width': '50%', 'margin': '0 auto 20px'}
    ),
    dcc.Dropdown(
        id='column-dropdown-1',
        options=[],
        multi=True,
        style={'width': '50%', 'margin': '0 auto 20px'}
    ),
    html.Div(
        dcc.RangeSlider(
            id='time-range-slider-1',
            min=1,
            max=10,
            step=1,
            marks={i: str(i) for i in range(11)},
            value=[1, 10],
        ),
        style={'width': '80%', 'margin': '20px auto'}
    ),

    dcc.Dropdown(
        id='table-dropdown-2',
        options=TABLE_OPTIONS,
        value=TABLE_OPTIONS[0]['value'],
        style={'width': '50%', 'margin': '0 auto 20px'}
    ),
    dcc.Dropdown(
        id='column-dropdown-2',
        options=[],
        multi=True,
        style={'width': '50%', 'margin': '0 auto 20px'}
    ),
    html.Div(
        dcc.RangeSlider(
            id='time-range-slider-2',
            min=1,
            max=10,
            step=1,
            marks={i: str(i) for i in range(11)},
            value=[1, 10],
        ),
        style={'width': '80%', 'margin': '20px auto'}
    ),

    html.Button('Plot Side-by-Side', id='plot-button', style={
        'display': 'block', 'margin': '30px auto', 'fontSize': '18px',
        'padding': '10px 20px', 'borderRadius': '50px', 'border': 'none', 'color': 'white',
        'backgroundColor': '#3498db', 'cursor': 'pointer'
    }),

    dcc.Graph(id='side-by-side-graph', style={'margin-top': '20px'})
])

@callback(
    [Output('column-dropdown-1', 'options'),
     Output('column-dropdown-2', 'options')],
    [Input('table-dropdown-1', 'value'),
     Input('table-dropdown-2', 'value')]
)
def update_column_dropdown(table1, table2):
    columns_table1 = [col for col in helperfunctions.fetch_data_for_table(table1) if col not in ['DAY_INCREMENT', 'DATE_ID']]
    columns_table2 = [col for col in helperfunctions.fetch_data_for_table(table2) if col not in ['DAY_INCREMENT', 'DATE_ID']]
    options_table1 = [{'label': COLUMN_NAME_MAPPING.get(col, col), 'value': col} for col in columns_table1]
    options_table2 = [{'label': COLUMN_NAME_MAPPING.get(col, col), 'value': col} for col in columns_table2]
    return options_table1, options_table2


@callback(
    [
        Output('side-by-side-graph', 'figure'),
        Output('time-range-slider-1', 'min'),
        Output('time-range-slider-1', 'max'),
        Output('time-range-slider-1', 'marks'),
        Output('time-range-slider-1', 'value'),
        Output('time-range-slider-2', 'min'),
        Output('time-range-slider-2', 'max'),
        Output('time-range-slider-2', 'marks'),
        Output('time-range-slider-2', 'value')
    ],
    [
        Input('table-dropdown-1', 'value'),
        Input('column-dropdown-1', 'value'),
        Input('table-dropdown-2', 'value'),
        Input('column-dropdown-2', 'value'),
        Input('time-range-slider-1', 'value'),
        Input('time-range-slider-2', 'value'),
        Input('plot-button', 'n_clicks')
    ]
)
def plot_side_by_side(table1_name, columns_table1, table2_name, columns_table2, time_range_1, time_range_2, n_clicks):
    if n_clicks is None:
        raise PreventUpdate

    df_table1 = helperfunctions.fetch_data_for_table(table1_name)
    df_table2 = helperfunctions.fetch_data_for_table(table2_name)

    if df_table1.empty or df_table2.empty:
        raise PreventUpdate

    min_time_1, max_time_1 = df_table1['DAY_INCREMENT'].min(), df_table1['DAY_INCREMENT'].max()
    min_time_2, max_time_2 = df_table2['DAY_INCREMENT'].min(), df_table2['DAY_INCREMENT'].max()

    def create_marks(min_val, max_val):
        step = (max_val - min_val) // 10
        if step == 0:
            step = 1
        return {i: {'label': str(i), 'style': {'transform': 'rotate(-45deg)', 'white-space': 'nowrap'}} for i in range(min_val, max_val + 1, step)}

    marks_time_1 = create_marks(min_time_1, max_time_1)
    marks_time_2 = create_marks(min_time_2, max_time_2)

    valid_range_1 = [max(min_time_1, time_range_1[0]), min(max_time_1, time_range_1[1])]
    valid_range_2 = [max(min_time_2, time_range_2[0]), min(max_time_2, time_range_2[1])]

    df_table1_filtered = df_table1[df_table1['DAY_INCREMENT'].between(*valid_range_1)]
    df_table2_filtered = df_table2[df_table2['DAY_INCREMENT'].between(*valid_range_2)]

    traces_table1 = [
        go.Scatter(
            x=df_table1_filtered['DAY_INCREMENT'],
            y=df_table1_filtered[col],
            mode='lines',
            name=f'{COLUMN_NAME_MAPPING.get(table1_name, table1_name)} - {COLUMN_NAME_MAPPING.get(col, col)}'
        ) for col in columns_table1
    ]
    traces_table2 = [
        go.Scatter(
            x=df_table2_filtered['DAY_INCREMENT'],
            y=df_table2_filtered[col],
            mode='lines',
            name=f'{COLUMN_NAME_MAPPING.get(table2_name, table2_name)} - {COLUMN_NAME_MAPPING.get(col, col)}'
        ) for col in columns_table2
    ]

    layout = go.Layout(
        title=f'Side-by-Side Comparison of {", ".join([COLUMN_NAME_MAPPING.get(col, col) for col in columns_table1])} and {", ".join([COLUMN_NAME_MAPPING.get(col, col) for col in columns_table2])}',
        xaxis={'title': 'DAYS'},
        yaxis={'title': 'Values'}
    )

    fig = go.Figure(data=traces_table1 + traces_table2, layout=layout)

    return fig, min_time_1, max_time_1, marks_time_1, valid_range_1, min_time_2, max_time_2, marks_time_2, valid_range_2
