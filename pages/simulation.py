import dash
from dash import html, dcc, Output, Input, callback, State
import plotly.express as px
import requests
from dash.exceptions import PreventUpdate
from backend import helperfunctions
from constants import *

dash.register_page(__name__)

input_size = '70px'

main_parameters = [
    html.Div([
        html.Label(SIMULATION_LABELS['numberOfAgentsParam']),
        dcc.Input(id='numberOfAgentsParam', type='number', value=100000, style={'width': input_size})
    ]),
    html.Div([
        html.Label(SIMULATION_LABELS['numberOfSickAtStartParam']),
        dcc.Input(id='numberOfSickAtStartParam', type='number', value=100, style={'width': input_size})
    ]),
    html.Div([
        html.Label(SIMULATION_LABELS['simPeriodParam']),
        dcc.Input(id='simPeriodParam', type='number', value=3, style={'width': input_size})
    ]),
]

disease_parameters = [
    html.Div([
        html.Label(SIMULATION_LABELS['standardIncubationTimeDiseaseParam']),
        dcc.Input(id='standardIncubationTimeDiseaseParam', type='number', value=6, style={'width': input_size})
    ]),
    html.Div([
        html.Label(SIMULATION_LABELS['chanceToTransmitDiseaseParam']),
        dcc.Slider(id='chanceToTransmitDiseaseParam', min=0, max=100, step=1, value=20, marks={i: str(i) for i in range(0, 101, 10)})
    ]),
    html.Div([
        html.Label(SIMULATION_LABELS['healingTimeDiseaseParam']),
        dcc.Input(id='healingTimeDiseaseParam', type='number', value=15, style={'width': input_size})
    ]),
    html.Div([
        html.Label(SIMULATION_LABELS['initialChanceToHealParam']),
        dcc.Slider(id='initialChanceToHealParam', min=0, max=50, step=1, value=0, marks={i: str(i) for i in range(0, 51, 5)})
    ]),
    html.Div([
        html.Label(SIMULATION_LABELS['initialChanceToKillParam']),
        dcc.Slider(id='initialChanceToKillParam', min=0, max=1, step=0.01, value=0, marks={i: str(i) for i in [0, 0.25, 0.5, 0.75, 1]})
    ]),
    html.Div([
        html.Label(SIMULATION_LABELS['chanceForAsymptomaticParam']),
        dcc.Slider(id='chanceForAsymptomaticParam', min=0, max=25, step=1, value=5, marks={i: str(i) for i in range(0, 101, 10)})
    ]),
]

agent_parameters = [
    html.Div([
        html.Label(SIMULATION_LABELS['chanceToGoOutParam']),
        dcc.Slider(id='chanceToGoOutParam', min=0, max=100, step=1, value=40, marks={i: str(i) for i in range(0, 101, 10)})
    ]),
    html.Div([
        html.Label(SIMULATION_LABELS['chanceToSelfQuarantineParam']),
        dcc.Slider(id='chanceToSelfQuarantineParam', min=0, max=100, step=1, value=95, marks={i: str(i) for i in range(0, 101, 10)})
    ]),
    html.Div([
        html.Label(SIMULATION_LABELS['agentsAtCentralLocation_atSameTimeParam']),
        dcc.Input(id='agentsAtCentralLocation_atSameTimeParam', type='number', value=100, style={'width': input_size})
    ]),
]

mask_parameters = [
    html.Div([
        html.Label(SIMULATION_LABELS['maskDistributionTimeParam']),
        dcc.Input(id='maskDistributionTimeParam', type='number', value=45, style={'width': input_size})
    ]),
    html.Div([
        html.Label(SIMULATION_LABELS['maskCooldownTimeParam']),
        dcc.Input(id='maskCooldownTimeParam', type='number', value=25, style={'width': input_size})
    ]),
    html.Div([
        html.Label(SIMULATION_LABELS['maskUse']),
        dcc.Checklist(id='maskUse', options=[{'label': '', 'value': 'maskUse'}], value=[])
    ]),
]

vaccine_parameters = [
    html.Div([
        html.Label(SIMULATION_LABELS['vaccineDistributionTimeParam']),
        dcc.Input(id='vaccineDistributionTimeParam', type='number', value=50, style={'width': input_size})
    ]),
    html.Div([
        html.Label(SIMULATION_LABELS['vaccineEnforced']),
        dcc.Checklist(id='vaccineEnforced', options=[{'label': '', 'value': 'vaccineEnforced'}], value=[])
    ]),
]

layout = html.Div([
    html.H1('Epidemic Simulation', style={'textAlign': 'center', 'fontSize': '40px', 'fontFamily': 'Arial'}),
    dcc.Graph(id='real-time-graph'),
    dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0),
    html.Div([
        html.Button('Start Simulation', id='start-simulation-button', n_clicks=0, style={'border-radius': '20px', 'background-color': '#007bff', 'color': 'white', 'font-size': '20px', 'margin': '10px'}),
        html.Button('Pause Simulation', id='pause-simulation-button', n_clicks=0, style={'border-radius': '20px', 'background-color': '#007bff', 'color': 'white', 'font-size': '20px', 'margin': '10px'}),
        html.Button('Resume Simulation', id='resume-simulation-button', n_clicks=0, style={'border-radius': '20px', 'background-color': '#007bff', 'color': 'white', 'font-size': '20px', 'margin': '10px'}),
        html.Button('Reset Simulation', id='reset-simulation-button', n_clicks=0, style={'border-radius': '20px', 'background-color': '#007bff', 'color': 'white', 'font-size': '20px', 'margin': '10px'}),
    ], style={'text-align': 'center'}),
    html.Div(id='dummy-output', style={'display': 'none'}),
    html.Div(main_parameters, id='main-parameters'),
    html.Div([
        html.H3('Disease Parameters'),
        html.Button('▼', id='toggle-disease-parameters', n_clicks=0, style={'border': 'none', 'background': 'none', 'font-size': '24px', 'color': '#007bff', 'margin-left': '10px'}),
    ], style={'display': 'flex', 'align-items': 'center'}),
    html.Div(disease_parameters, id='disease-parameters', style={'display': 'none'}),
    html.Div([
        html.H3('Agent Parameters'),
        html.Button('▼', id='toggle-agent-parameters', n_clicks=0, style={'border': 'none', 'background': 'none', 'font-size': '24px', 'color': '#007bff', 'margin-left': '10px'}),
    ], style={'display': 'flex', 'align-items': 'center'}),
    html.Div(agent_parameters, id='agent-parameters', style={'display': 'none'}),
    html.Div([
        html.H3('Mask Parameters'),
        html.Button('▼', id='toggle-mask-parameters', n_clicks=0, style={'border': 'none', 'background': 'none', 'font-size': '24px', 'color': '#007bff', 'margin-left': '10px'}),
    ], style={'display': 'flex', 'align-items': 'center'}),
    html.Div(mask_parameters, id='mask-parameters', style={'display': 'none'}),
    html.Div([
        html.H3('Vaccine Parameters'),
        html.Button('▼', id='toggle-vaccine-parameters', n_clicks=0, style={'border': 'none', 'background': 'none', 'font-size': '24px', 'color': '#007bff', 'margin-left': '10px'}),
    ], style={'display': 'flex', 'align-items': 'center'}),
    html.Div(vaccine_parameters, id='vaccine-parameters', style={'display': 'none'}),
    html.Button('Analyze Simulation', id='analyze-simulation-button', n_clicks=0, style={'border-radius': '20px', 'background-color': '#007bff', 'color': 'white', 'font-size': '20px', 'margin': '10px'}),
    html.Div(id='analysis-output', style={'marginLeft': '1%', 'marginTop': '1%', 'fontSize': '20px'}),
])


@callback(
    Output('real-time-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_graph(n):
    df = helperfunctions.fetch_data_for_simulation()
    if df.empty:
        print("No data retrieved from the database.")
        return px.area()

    try:
        available_columns = [col for col in df.columns if col not in [BY_ID, BY_DATE]]
        df_renamed = df.rename(columns=COLUMN_NAME_MAPPING)

        fig = px.area(df_renamed, x=COLUMN_NAME_MAPPING.get(BY_ID, BY_ID),
                      y=[COLUMN_NAME_MAPPING.get(col, col) for col in available_columns])
        fig.update_layout(legend_title_text='Metrics',
                          xaxis_title=COLUMN_NAME_MAPPING.get(BY_ID, BY_ID))

        return fig
    except Exception as e:
        print(f"Error creating graph: {e}")
        return {}


@callback(
    Output('dummy-output', 'children'),
    Output('numberOfAgentsParam', 'disabled'),
    Output('numberOfSickAtStartParam', 'disabled'),
    Output('simPeriodParam', 'disabled'),
    Input('start-simulation-button', 'n_clicks'),
    Input('pause-simulation-button', 'n_clicks'),
    Input('resume-simulation-button', 'n_clicks'),
    Input('reset-simulation-button', 'n_clicks'),
    Input('numberOfAgentsParam', 'value'),
    Input('numberOfSickAtStartParam', 'value'),
    Input('simPeriodParam', 'value'),
    Input('standardIncubationTimeDiseaseParam', 'value'),
    Input('chanceToTransmitDiseaseParam', 'value'),
    Input('healingTimeDiseaseParam', 'value'),
    Input('initialChanceToHealParam', 'value'),
    Input('initialChanceToKillParam', 'value'),
    Input('chanceForAsymptomaticParam', 'value'),
    Input('chanceToGoOutParam', 'value'),
    Input('chanceToSelfQuarantineParam', 'value'),
    Input('agentsAtCentralLocation_atSameTimeParam', 'value'),
    Input('maskDistributionTimeParam', 'value'),
    Input('maskCooldownTimeParam', 'value'),
    Input('maskUse', 'value'),
    Input('vaccineDistributionTimeParam', 'value'),
    Input('vaccineEnforced', 'value')
)
def control_simulation_and_submit_parameters(start_clicks, pause_clicks, resume_clicks, reset_clicks, *args):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    param_values = list(args)

    disable_main_params = 'start-simulation-button' in changed_id

    parameter_values = {
        'numberOfAgentsParam': param_values[0],
        'numberOfSickAtStartParam': param_values[1],
        'simPeriodParam': param_values[2],
        'standardIncubationTimeDiseaseParam': param_values[3],
        'chanceToTransmitDiseaseParam': param_values[4],
        'healingTimeDiseaseParam': param_values[5],
        'initialChanceToHealParam': param_values[6],
        'initialChanceToKillParam': param_values[7],
        'chanceForAsymptomaticParam': param_values[8],
        'chanceToGoOutParam': param_values[9],
        'chanceToSelfQuarantineParam': param_values[10],
        'agentsAtCentralLocation_atSameTimeParam': param_values[11],
        'maskDistributionTimeParam': param_values[12],
        'maskCooldownTimeParam': param_values[13],
        'maskUse': 'maskUse' in param_values[14],
        'vaccineDistributionTimeParam': param_values[15],
        'vaccineEnforced': 'vaccineEnforced' in param_values[16]
    }

    if changed_id:
        param_key = changed_id.split('.')[0]
        if param_key in parameter_values:
            try:
                response = requests.post('http://localhost:8080/updateParameters', json={param_key: parameter_values[param_key]})
                if response.status_code == 200:
                    print(f"Parameter {param_key} updated successfully.")
                else:
                    print(f"Failed to update parameter {param_key}: {response.status_code}")
            except requests.RequestException as e:
                print(f"Error during parameter update: {e}")

    if 'start-simulation-button' in changed_id:
        try:
            requests.post('http://localhost:8080/startSimulation')
            print("Simulation started successfully.")
        except requests.RequestException as e:
            print(f"Failed to start simulation: {e}")

    elif 'reset-simulation-button' in changed_id:
        try:
            requests.post('http://localhost:8080/resetSimulation')
            print("Simulation reset.")
        except requests.RequestException as e:
            print(f"Failed to reset simulation: {e}")

    elif 'pause-simulation-button' in changed_id:
        try:
            requests.post('http://localhost:8080/pauseSimulation')
            print("Simulation paused.")
        except requests.RequestException as e:
            print(f"Failed to pause simulation: {e}")

    elif 'resume-simulation-button' in changed_id:
        try:
            requests.post('http://localhost:8080/resumeSimulation')
            print("Simulation resumed.")
        except requests.RequestException as e:
            print(f"Failed to resume simulation: {e}")

    return None, disable_main_params, disable_main_params, disable_main_params


@callback(
    Output('disease-parameters', 'style'),
    Input('toggle-disease-parameters', 'n_clicks'),
    State('disease-parameters', 'style')
)
def toggle_disease_parameters(n_clicks, style):
    if n_clicks:
        if style['display'] == 'none':
            style['display'] = 'block'
        else:
            style['display'] = 'none'
    return style


@callback(
    Output('agent-parameters', 'style'),
    Input('toggle-agent-parameters', 'n_clicks'),
    State('agent-parameters', 'style')
)
def toggle_agent_parameters(n_clicks, style):
    if n_clicks:
        if style['display'] == 'none':
            style['display'] = 'block'
        else:
            style['display'] = 'none'
    return style


@callback(
    Output('mask-parameters', 'style'),
    Input('toggle-mask-parameters', 'n_clicks'),
    State('mask-parameters', 'style')
)
def toggle_mask_parameters(n_clicks, style):
    if n_clicks:
        if style['display'] == 'none':
            style['display'] = 'block'
        else:
            style['display'] = 'none'
    return style


@callback(
    Output('vaccine-parameters', 'style'),
    Input('toggle-vaccine-parameters', 'n_clicks'),
    State('vaccine-parameters', 'style')
)
def toggle_vaccine_parameters(n_clicks, style):
    if n_clicks:
        if style['display'] == 'none':
            style['display'] = 'block'
        else:
            style['display'] = 'none'
    return style

@callback(
    Output('analysis-output', 'children'),
    Input('analyze-simulation-button', 'n_clicks')
)
def analyze_simulation(n_clicks):
    if n_clicks > 0:
        summarized_data = helperfunctions.fetch_and_summarize_simulation_data()
        print(summarized_data)
        if summarized_data:
            return helperfunctions.analyze_simulation_data(summarized_data)
    else:
        raise PreventUpdate


dash.register_page(__name__, path='/')
