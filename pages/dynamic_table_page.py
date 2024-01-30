import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output, State
import plotly.express as px
from backend import helperfunctions

# Initialize Dash app
dash.register_page(__name__)

# Define your app layout
layout = html.Div([
    dcc.Dropdown(
        id='table-dropdown',
        options=[
            {'label': 'Covid19_TM', 'value': 'covid19_tm'},
            {'label': 'Status', 'value': 'status'},
            # Add more tables as needed
        ],
        value='covid19_tm',  # Default selected value
        style={'width': '50%'}
    ),
    dcc.Dropdown(
        id='column-dropdown',
        options=[],  # To be populated dynamically based on the selected table
        multi=True,  # Allow multiple selections
        style={'width': '50%'}
    ),
    html.Button('Plot', id='plot-button'),
    html.Button('Clear Graph', id='clear-button'),
    dcc.Graph(id='graph')
])

# Define callback to update column dropdown options based on selected table
@callback(
    Output('column-dropdown', 'options'),
    [Input('table-dropdown', 'value')]
)
def update_column_dropdown(selected_table):
    if selected_table == 'covid19_tm':
        columns = ['CAZURI', 'DECESE']
    elif selected_table == 'status':
        columns = ['TOTAL', 'CURED', 'DEAD', 'SICK']
    else:
        # Add more tables as needed
        columns = []
    options = [{'label': col, 'value': col} for col in columns]
    return options

# Define callback to fetch data based on selected table and column
@callback(
    Output('graph', 'figure'),
    [Input('table-dropdown', 'value'),
     Input('column-dropdown', 'value'),
     Input('plot-button', 'n_clicks'),
     Input('clear-button', 'n_clicks')],
    [State('graph', 'relayoutData')]
)
def update_graph(selected_table, selected_columns, n_clicks_plot, n_clicks_clear, relayout_data):
    if n_clicks_plot is None and n_clicks_clear is None:
        return dash.no_update

    ctx = dash.callback_context
    if ctx.triggered_id == 'clear-button':
        # If the "Clear Graph" button is clicked, return an empty figure
        return px.line()

    df = helperfunctions.fetch_data_for_table(selected_table)
    if not df.empty:
        fig = px.line(df, x='DATE_ID', y=selected_columns, title=f'{", ".join(selected_columns)} for {selected_table}')
        return fig
    else:
        return dash.no_update

