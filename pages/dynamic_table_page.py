import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from backend import helperfunctions
from sklearn.linear_model import LinearRegression
from constants import TABLE_OPTIONS, BY_DATE, BY_ID

# Initialize Dash app
dash.register_page(__name__)

layout = html.Div([
    # Dropdowns for table and column selection
    html.H3("Select Incident"),
    dcc.Dropdown(
        id='table-dropdown',
        options=TABLE_OPTIONS,
        value='covid19_tm',  # Default selected table
        style={'width': '30%'}
    ),
    html.H3("Choose what to plot"),
    dcc.Dropdown(
        id='column-dropdown',
        options=[],
        multi=True,
        style={'width': '30%'}
    ),

    # Static Plot Section
    html.Div([
        html.H1("Analysis over time", style={'textAlign': 'center'}),
        dcc.Graph(id='static-graph'),
    ]),

    # Trend Graph Section
    html.Div([
        html.H1("Trend Graph", style={'textAlign': 'center'}),
        dcc.Dropdown(
            id='time-span-dropdown',
            options=[
                {'label': 'Daily', 'value': 'D'},
                {'label': 'Weekly', 'value': 'W'},
                {'label': 'Monthly', 'value': 'M'},
                {'label': 'Yearly', 'value': 'Y'}
            ],
            value='D',  # Default selected time span
            style={'width': '30%', 'margin-left': '13.5%'}
        ),
    ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}),

    dcc.Graph(id='trend-graph'),

    # Dynamic Chart Section
    html.Div([
        html.H1("Time-based Dynamic Charts", style={'textAlign': 'center'}),
        dcc.Dropdown(
            id='chart-type-dropdown',
            options=[
                {'label': 'Line Chart', 'value': 'line'},
                {'label': 'Bar Chart', 'value': 'bar'},
                {'label': 'Pie Chart', 'value': 'pie'},
                {'label': 'Area Chart', 'value': 'area'}
            ],
            value='line',  # Default chart type
            style={'width': '30%', 'margin-left': '13%'}
        ),
    ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}),

    dcc.Graph(id='dynamic-chart'),

], style={'fontFamily': 'Arial, sans-serif'})


# Callbacks for dynamic dropdowns and graph updates
@callback(
    Output('column-dropdown', 'options'),
    Input('table-dropdown', 'value')
)
def update_column_dropdown(selected_table):
    columns = helperfunctions.fetch_data_for_table(selected_table)
    options = [{'label': col, 'value': col} for col in columns if col not in [BY_ID, BY_DATE]]
    return options

# Callback to update the static graph
@callback(
    Output('static-graph', 'figure'),
    [Input('table-dropdown', 'value'),
     Input('column-dropdown', 'value')],
    prevent_initial_call=True
)
def update_static_graph(selected_table, selected_columns):
    if not selected_columns:
        # Return an empty figure if no columns are selected
        return go.Figure()

    # Fetch data
    df = helperfunctions.fetch_data_for_table(selected_table)
    if df.empty:
        # Return an empty figure if the data frame is empty
        return go.Figure()

    # Check if all selected columns are in the DataFrame
    missing_cols = [col for col in selected_columns if col not in df.columns]
    if missing_cols:
        print(f"Missing columns in DataFrame: {missing_cols}")
        return go.Figure()

    # Attempt to create a line plot
    try:
        fig = px.line(df, x=BY_DATE, y=selected_columns, title='Default Analysis')
        return fig
    except Exception as e:
        print(f"Error in plotting with selected columns {selected_columns}: {e}")
        return go.Figure()  # Return an empty figure in case of error

# Callback for Trend Analysis Graph
@callback(
    Output('trend-graph', 'figure'),
    [Input('table-dropdown', 'value'),
     Input('column-dropdown', 'value'),
     Input('time-span-dropdown', 'value')],
    prevent_initial_call=True
)
def update_trend_graph(selected_table, selected_columns, time_span):
    df = helperfunctions.fetch_data_for_table(selected_table)
    if df.empty or not selected_columns:
        return dash.no_update

    df['DATE_ID'] = pd.to_datetime(df['DATE_ID'])
    df.set_index('DATE_ID', inplace=True)

    trend_fig = go.Figure()
    for col in selected_columns:
        df_resampled = df[col].resample(time_span).mean().dropna().reset_index()
        df_resampled['Time'] = np.arange(len(df_resampled.index))
        X = df_resampled['Time'].values.reshape(-1, 1)
        y = df_resampled[col].values
        model = LinearRegression()
        model.fit(X, y)
        trend_line = model.predict(X)
        # Adding the trend line and actual data points to the figure
        trend_fig.add_trace(go.Scatter(x=df_resampled[BY_DATE], y=trend_line, mode='lines', name=f'{col} Trend'))
        trend_fig.add_trace(go.Scatter(x=df_resampled[BY_DATE], y=y, mode='markers', name=f'{col} Actual'))

    trend_fig.update_layout(title='Trend Analysis', xaxis_title='Date', yaxis_title='Value')
    return trend_fig

# Callback for Dynamic Chart
@callback(
    Output('dynamic-chart', 'figure'),
    [Input('table-dropdown', 'value'),
     Input('column-dropdown', 'value'),
     Input('time-span-dropdown', 'value'),
     Input('chart-type-dropdown', 'value')],
    prevent_initial_call=True
)
def update_dynamic_chart(selected_table, selected_columns, time_span, chart_type):
    df = helperfunctions.fetch_data_for_table(selected_table)
    if df.empty or not selected_columns:
        return dash.no_update

    df[BY_DATE] = pd.to_datetime(df[BY_DATE])
    df.set_index(BY_DATE, inplace=True)
    df_resampled = df[selected_columns].resample(time_span).sum().reset_index()

    if chart_type == 'line':
        fig = px.line(df_resampled, x=BY_DATE, y=selected_columns, title=' Line Chart')
    elif chart_type == 'bar':
        fig = px.bar(df_resampled, x=BY_DATE, y=selected_columns, title='Stacked Bar Chart', barmode='stack')
    elif chart_type == 'area':
        fig = px.area(df_resampled, x=BY_DATE, y=selected_columns, title='Area Chart')
    elif chart_type == 'pie':
        if len(selected_columns) == 1:
            fig = px.pie(df_resampled, names=BY_DATE, values=selected_columns[0], title='Pie Chart')
        else:
            return dash.no_update  # Pie chart requires exactly one column selection

    return fig
