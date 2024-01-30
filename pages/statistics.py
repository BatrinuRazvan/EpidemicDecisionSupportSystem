import dash
from dash import html, dcc, Output, Input, callback
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
from backend import helperfunctions

dash.register_page(__name__)

layout = html.Div([
    html.H1('Statistics for current Epidemic'),
    dcc.Graph(id='dynamic-statistics'),
    html.Div([
        html.Button(stat, id=f'btn-{stat.lower()}', n_clicks=0) for stat in ['DEAD', 'CURED', 'SICK', 'TOTAL']
    ] + [html.Button('Clear All', id='btn-clear-all', n_clicks=0)]),
])

selected_areas = []


def clear_all():
    selected_areas.clear()
    df = helperfunctions.fetch_data_for_simulation()
    if df is None or df.empty:
        print("No data retrieved from the database.")
        return go.Figure()


def update_selected_areas(button_id):
    selected_area = button_id.replace('btn-', '').upper()
    if selected_area not in selected_areas:
        selected_areas.append(selected_area)


@callback(Output('dynamic-statistics', 'figure'),
          [Input(f'btn-{stat.lower()}', 'n_clicks') for stat in ['DEAD', 'CURED', 'SICK', 'TOTAL']] +
          [Input('btn-clear-all', 'n_clicks')])
def update_statistics_graph(*args):
    ctx = dash.callback_context

    if not ctx.triggered_id:
        raise PreventUpdate

    button_id = ctx.triggered_id.split('.')[0]

    if button_id == 'btn-clear-all':
        clear_all()
    else:
        update_selected_areas(button_id)

    df = helperfunctions.fetch_data_for_simulation()
    if df is None or df.empty:
        print("No data retrieved from the database.")
        return go.Figure()

    selected_df = df[['DATE_ID'] + selected_areas]

    try:
        fig = go.Figure()

        for area in selected_areas:
            fig.add_trace(go.Scatter(x=selected_df['DATE_ID'], y=selected_df[area], mode='lines', fill='tozeroy', name=area))

        fig.update_layout(title='Dynamic Statistics', xaxis_title='Day', yaxis_title='Value')

        return fig
    except Exception as e:
        print(f"Error creating graph: {e}")
        return go.Figure()
