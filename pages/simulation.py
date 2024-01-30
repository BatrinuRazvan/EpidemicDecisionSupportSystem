import dash
from dash import html, dcc, Output, Input, callback
import plotly.express as px
import subprocess
import json
from dash.exceptions import PreventUpdate
from backend import helperfunctions

dash.register_page(__name__)

input_elements = [
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
]

layout = html.Div([
    html.H1('Simulation'),
    dcc.Graph(id='real-time-graph'),
    dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0),
    html.Button('Start Simulation', id='ps-button', n_clicks=0),
    html.Div(id='dummy-output', style={'display': 'none'}),
    html.Div( input_elements, id='changable-parameters'),
])


@callback(Output('real-time-graph', 'figure'), [Input('interval-component', 'n_intervals')])
def update_graph(n):
    df = helperfunctions.fetch_data_for_simulation()
    if df.empty:
        print("No data retrieved from the database.")
        return px.area()

    try:
        fig = px.area(df, x='DATE_ID', y=['DEAD', 'CURED', 'SICK', 'TOTAL'],
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
        ps_script_path = "D:\\Licenta\\EDSS\\EpidemicDecisionalSupportSystem\\backend\\startSim.ps1"
        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_script_path], check=True)
        print("PowerShell script executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute PowerShell script: {e}")

    return None


@callback(
    [Output(input_id, 'value') for input_id in ['nb-of-people', 'number_of_months', 'number_of_days',
                                                'start_sick', 'sleepTime', 'average_time_of_encounters',
                                                'max_chances_going_outside', 'time_incubating',
                                                'time_before_infectious', 'max_infectuosity', 'max_lethality',
                                                'days_before_possible_healing', 'healing_chances',
                                                'immunity_bounds', 'immunity_ri_start', 'immunity_modifier']],
    [Input(input_id, 'value') for input_id in ['nb-of-people', 'number_of_months', 'number_of_days',
                                               'start_sick', 'sleepTime', 'average_time_of_encounters',
                                               'max_chances_going_outside', 'time_incubating',
                                               'time_before_infectious', 'max_infectuosity', 'max_lethality',
                                               'days_before_possible_healing', 'healing_chances',
                                               'immunity_bounds', 'immunity_ri_start', 'immunity_modifier']]
)
def update_input_values(*args):
    return args

@callback(
    Output('changable-parameters', 'children'),
    [Input('nb-of-people', 'value')] +  # Add other input IDs as needed
    [Input('number_of_months', 'value'),
     Input('number_of_days', 'value'),
     Input('start_sick', 'value'),
     Input('sleepTime', 'value'),
     Input('average_time_of_encounters', 'value'),
     Input('max_chances_going_outside', 'value'),
     Input('time_incubating', 'value'),
     Input('time_before_infectious', 'value'),
     Input('max_infectuosity', 'value'),
     Input('max_lethality', 'value'),
     Input('days_before_possible_healing', 'value'),
     Input('healing_chances', 'value'),
     Input('immunity_bounds', 'value'),
     Input('immunity_ri_start', 'value'),
     Input('immunity_modifier', 'value')]
)
def update_json(nb_of_people_value, *args):
    parameter_values = {input_id: value for input_id, value in zip(
        ['nb-of-people', 'number_of_months', 'number_of_days', 'start_sick', 'sleepTime', 'average_time_of_encounters',
         'max_chances_going_outside', 'time_incubating', 'time_before_infectious', 'max_infectuosity', 'max_lethality',
         'days_before_possible_healing', 'healing_chances', 'immunity_bounds', 'immunity_ri_start', 'immunity_modifier'],
        [nb_of_people_value] + list(args)
    )}

    with open('parameters.json', 'w') as json_file:
        json.dump(parameter_values, json_file)


    input_elements = [
        dcc.Input(id='nb-of-people', type='number', value=nb_of_people_value, placeholder='Number of People'),
        dcc.Input(id='number_of_months', type='number', value=args[0], placeholder='Number of Months'),
        dcc.Input(id='number_of_days', type='number', value=args[1], placeholder="Number of Days"),
        dcc.Input(id='start_sick', type='number', value=args[2], placeholder="Start Sick"),
        dcc.Input(id='sleepTime', type='number', value=args[3], placeholder="Sleep Time"),
        dcc.Input(id='average_time_of_encounters', type='number', value=args[4],
                  placeholder="Average Time Of Encounters"),
        dcc.Input(id='max_chances_going_outside', type='number', value=args[5],
                  placeholder="Maximum Chances Of Going Outside"),
        dcc.Input(id='time_incubating', type='number', value=args[6], placeholder="Time Incubating"),
        dcc.Input(id='time_before_infectious', type='number', value=args[7], placeholder="Time Before Infectious"),
        dcc.Input(id='max_infectuosity', type='number', value=args[8], placeholder="Maximum Infectious"),
        dcc.Input(id='max_lethality', type='number', value=args[9], placeholder="Maximum Lethality"),
        dcc.Input(id='days_before_possible_healing', type='number', value=args[10], placeholder="Days Before Healing"),
        dcc.Input(id='healing_chances', type='number', value=args[11], placeholder="Healing Chance"),
        dcc.Input(id='immunity_bounds', type='number', value=args[12], placeholder="Immunity Bounds"),
        dcc.Input(id='immunity_ri_start', type='number', value=args[13], placeholder="Immunity Ri Start"),
        dcc.Input(id='immunity_modifier', type='number', value=args[14], placeholder="Immunity Modifier")
            ]

    return input_elements

dash.register_page(__name__, path='/')
