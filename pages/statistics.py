import dash
from dash import html, dcc, Output, Input, callback
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
from backend import helperfunctions

dash.register_page(__name__)

layout = html.Div([
    html.H1('Statistics'),
    dcc.Graph(id='dynamic-statistics'),
    html.Div([
        html.Button('DEAD', id='btn-dead', n_clicks=0),
        html.Button('CURED', id='btn-cured', n_clicks=0),
        html.Button('SICK', id='btn-sick', n_clicks=0),
        html.Button('TOTAL', id='btn-total', n_clicks=0),
        html.Button('Clear All', id='btn-clear-all', n_clicks=0),
    ]),
])

# Initialize an empty list to store selected areas
selected_areas = []

@callback(Output('dynamic-statistics', 'figure'),
          [Input('btn-dead', 'n_clicks'),
           Input('btn-cured', 'n_clicks'),
           Input('btn-sick', 'n_clicks'),
           Input('btn-total', 'n_clicks'),
           Input('btn-clear-all', 'n_clicks')])
def update_statistics_graph(n_clicks_dead, n_clicks_cured, n_clicks_sick, n_clicks_total, n_clicks_clear_all):
    ctx = dash.callback_context

    if not ctx.triggered_id:
        raise PreventUpdate

    button_id = ctx.triggered_id.split('.')[0]

    if button_id == 'btn-clear-all':
        # Clear all selected areas and show the original graph
        selected_areas.clear()
        df = helperfunctions.fetch_data()
        if df is None or df.empty:
            print("No data retrieved from the database.")
            return go.Figure()  # Return an empty figure if no data is retrieved
    else:
        # Add the selected area to the list
        selected_area = button_id.replace('btn-', '').upper()
        if selected_area not in selected_areas:
            selected_areas.append(selected_area)

        # Fetch data and create graph based on selected areas
        df = helperfunctions.fetch_data()
        if df is None or df.empty:
            print("No data retrieved from the database.")
            return go.Figure()  # Return an empty figure if no data is retrieved

        # Select only the columns that are in the selected_areas list
        selected_df = df[['DAY_ID'] + selected_areas]

    try:
        fig = go.Figure()

        for area in selected_areas:
            fig.add_trace(go.Scatter(x=selected_df['DAY_ID'], y=selected_df[area], mode='lines', fill='tozeroy', name=area))
            # fig.add_trace(go.Scatter(x=selected_df['DAY_ID'], y=selected_df[area], mode='lines', fill='tonexty', name=area))

        fig.update_layout(title='Dynamic Statistics', xaxis_title='Day', yaxis_title='Value')

        return fig
    except Exception as e:
        print(f"Error creating graph: {e}")
        return go.Figure()

# You can keep the fetch_data function from your original app.py file
# and the create_graph function if you have one. Make sure to import them.

# Also, keep the callback for run_ps_script if you need it in this file.

# Make sure to update the import statements accordingly.
