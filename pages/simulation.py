import dash
from dash import html, dcc, Output, Input, callback
import plotly.express as px
import subprocess
from dash.exceptions import PreventUpdate
from backend import helperfunctions


layout = html.Div([
    html.H1('Simulation'),
    dcc.Graph(id='real-time-graph'),
    html.Div([
        dcc.Input(id='nb-of-people', type='number', value=1000, placeholder='Number of People'),
        dcc.Input(id='number_of_months', type='number', value=3, placeholder='Number of Months'),
        dcc.Input(id='number_of_days', type='number', value=0, placeholder="Number of Days"),
        dcc.Input(id='start_sick', type='number', value=100, placeholder="Start Sick"),
        dcc.Input(id='sleepTime', type='number', value=8, placeholder="Sleep Time"),
        dcc.Input(id='average_time_of_encounters', type='number', value=3, placeholder="Average Time Of Encounters"),
        dcc.Input(id='max_chances_going_outside', type='number', value=60, placeholder="Maximum Chances Of Going Outside"),
        dcc.Input(id='time_incubating', type='number', placeholder="Time Incubating", min=0, max=8),
        dcc.Input(id='time_before_infectious', type='number', value=1, placeholder="Time Before Infectious"),
        dcc.Input(id='max_infectuosity', type='number', value=160, placeholder="Maximum Infectious"),
        dcc.Input(id='max_lethality', type='number', value=10, placeholder="Maximum Lethality"),
        dcc.Input(id='days_before_possible_healing', type='number', value=0, placeholder="Days Before Healing"),
        dcc.Input(id='healing_chances', type='number', value=45, placeholder="Healing Chance"),
        dcc.Input(id='immunity_bounds', type='number', placeholder="Immunity Bounds", min=0, max=100),
        dcc.Input(id='immunity_ri_start', type='number', value=20, placeholder="Immunity Ri Start"),
        dcc.Input(id='immunity_modifier', type='number', value=50, placeholder="Immunity Modifier")
    ]),
    dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0),
    html.Button('Start Simulation', id='ps-button', n_clicks=0),
    html.Div(id='dummy-output', style={'display': 'none'})
])


@callback(Output('real-time-graph', 'figure'), [Input('interval-component', 'n_intervals')])
def update_graph(n):
    df = helperfunctions.fetch_data()
    if df.empty:
        print("No data retrieved from the database.")
        return px.area()

    try:
        fig = px.area(df, x='DAY_ID', y=['DEAD', 'CURED', 'SICK', 'TOTAL'],
                      color_discrete_map={'TOTAL': 'aquamarine', 'CURED': 'green', 'DEAD': 'gray', 'SICK': 'red'})
        return fig
    except Exception as e:
        print(f"Error creating graph: {e}")
        return {}


@callback(
    Output('dummy-output', 'children'),
    [Input('ps-button', 'n_clicks')]
)
def run_ps_script(n_clicks):
    if n_clicks == 0:
        raise PreventUpdate

    try:
        ps_script_path = "E:\\Programming Projects\\Python\\EpidemicDecisionSupportSystem\\backend\\startSim.ps1"
        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_script_path], check=True)
        print("PowerShell script executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute PowerShell script: {e}")

    return None


dash.register_page(__name__, path='/')
