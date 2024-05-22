import dash
from dash import html, dcc, Output, Input, callback, State
import plotly.express as px
import requests
from dash.exceptions import PreventUpdate
from backend import helperfunctions
import openai
from constants import SIMULATION_LABELS

dash.register_page(__name__)

main_parameters = [
    html.Div([
        html.Label(SIMULATION_LABELS['numberOfAgentsParam']),
        dcc.Input(id='numberOfAgentsParam', type='number', value=1000)
    ]),
    html.Div([
        html.Label(SIMULATION_LABELS['numberOfSickAtStartParam']),
        dcc.Input(id='numberOfSickAtStartParam', type='number', value=100)
    ]),
    html.Div([
        html.Label(SIMULATION_LABELS['simPeriodParam']),
        dcc.Input(id='simPeriodParam', type='number', value=3)
    ]),
]

# Define input elements for the dropdown categories with labels, default values, and sliders
disease_parameters = [
    html.Div([
        html.Label(SIMULATION_LABELS['standardIncubationTimeDiseaseParam']),
        dcc.Input(id='standardIncubationTimeDiseaseParam', type='number', value=5)
    ]),
    html.Div([
        html.Label(SIMULATION_LABELS['chanceToTransmitDiseaseParam']),
        dcc.Slider(id='chanceToTransmitDiseaseParam', min=0, max=100, step=1, value=50, marks={i: str(i) for i in range(0, 101, 10)})
    ]),
    html.Div([
        html.Label(SIMULATION_LABELS['healingTimeDiseaseParam']),
        dcc.Input(id='healingTimeDiseaseParam', type='number', value=10)
    ]),
    html.Div([
        html.Label(SIMULATION_LABELS['initialChanceToHealParam']),
        dcc.Slider(id='initialChanceToHealParam', min=0, max=50, step=1, value=25, marks={i: str(i) for i in range(0, 51, 5)})
    ]),
    html.Div([
        html.Label(SIMULATION_LABELS['initialChanceToKillParam']),
        dcc.Slider(id='initialChanceToKillParam', min=0, max=1, step=0.01, value=0.1, marks={i: str(i) for i in [0, 0.25, 0.5, 0.75, 1]})
    ]),
    html.Div([
        html.Label(SIMULATION_LABELS['chanceForAsymptomaticParam']),
        dcc.Slider(id='chanceForAsymptomaticParam', min=0, max=100, step=1, value=50, marks={i: str(i) for i in range(0, 101, 10)})
    ]),
]

agent_parameters = [
    html.Div([
        html.Label(SIMULATION_LABELS['chanceToGoOutParam']),
        dcc.Input(id='chanceToGoOutParam', type='number', value=30)
    ]),
    html.Div([
        html.Label(SIMULATION_LABELS['chanceToSelfQuarantineParam']),
        dcc.Input(id='chanceToSelfQuarantineParam', type='number', value=50)
    ]),
    html.Div([
        html.Label(SIMULATION_LABELS['agentsAtCentralLocation_atSameTimeParam']),
        dcc.Input(id='agentsAtCentralLocation_atSameTimeParam', type='number', value=100)
    ]),
]

mask_parameters = [
    html.Div([
        html.Label(SIMULATION_LABELS['maskDistributionTimeParam']),
        dcc.Input(id='maskDistributionTimeParam', type='number', value=7)
    ]),
    html.Div([
        html.Label(SIMULATION_LABELS['maskCooldownTimeParam']),
        dcc.Input(id='maskCooldownTimeParam', type='number', value=14)
    ]),
    html.Div([
        html.Label(SIMULATION_LABELS['maskUse']),
        dcc.Checklist(id='maskUse', options=[{'label': '', 'value': 'maskUse'}], value=[])
    ]),
]

vaccine_parameters = [
    html.Div([
        html.Label(SIMULATION_LABELS['vaccineDistributionTimeParam']),
        dcc.Input(id='vaccineDistributionTimeParam', type='number', value=30)
    ]),
    html.Div([
        html.Label(SIMULATION_LABELS['vaccineEnforced']),
        dcc.Checklist(id='vaccineEnforced', options=[{'label': '', 'value': 'vaccineEnforced'}], value=[])
    ]),
]

layout = html.Div([
    html.H1('Epidemic Simulation'),
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
    html.H3('Disease Parameters'),
    html.Button('▼', id='toggle-disease-parameters', n_clicks=0, style={'border': 'none', 'background': 'none', 'font-size': '24px', 'color': '#007bff'}),
    html.Div(disease_parameters, id='disease-parameters', style={'display': 'none'}),
    html.Div([
        html.H3('Agent Parameters'),
        html.Button('Agent Parameters ▼', id='toggle-agent-parameters', n_clicks=0,
                    style={'border': 'none', 'background': 'none', 'font-size': '24px'}),
    ]),
    html.Div(agent_parameters, id='agent-parameters', style={'display': 'none'}),
    html.H3('Mask Parameters'),
    html.Button('▼', id='toggle-mask-parameters', n_clicks=0, style={'border': 'none', 'background': 'none', 'font-size': '24px', 'color': '#007bff'}),
    html.Div(mask_parameters, id='mask-parameters', style={'display': 'none'}),
    html.H3('Vaccine Parameters'),
    html.Button('▼', id='toggle-vaccine-parameters', n_clicks=0, style={'border': 'none', 'background': 'none', 'font-size': '24px', 'color': '#007bff'}),
    html.Div(vaccine_parameters, id='vaccine-parameters', style={'display': 'none'}),
    html.Button('Analyze Simulation', id='analyze-simulation-button', n_clicks=0, style={'border-radius': '20px', 'background-color': '#007bff', 'color': 'white', 'font-size': '20px', 'margin': '10px', 'marginTop': '1%'}),
    html.Div(id='analysis-output'),
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
        fig = px.area(df, x='DAY_INCREMENT', y=['TOTAL_DEATHS', 'TOTAL_RECOVERED', 'DAILY_CASES', 'TOTAL_HOSPITALIZATIONS'],
                      color_discrete_map={'TOTAL_HOSPITALIZATIONS': 'aquamarine', 'TOTAL_RECOVERED': 'green', 'TOTAL_DEATHS': 'gray', 'DAILY_CASES': 'red'})
        return fig
    except Exception as e:
        print(f"Error creating graph: {e}")
        return {}

@callback(
    Output('dummy-output', 'children'),
    [Input('start-simulation-button', 'n_clicks'),
     Input('pause-simulation-button', 'n_clicks'),
     Input('resume-simulation-button', 'n_clicks'),
     Input('reset-simulation-button', 'n_clicks'),
     State('numberOfAgentsParam', 'value'),
     State('numberOfSickAtStartParam', 'value'),
     State('simPeriodParam', 'value'),
     State('standardIncubationTimeDiseaseParam', 'value'),
     State('chanceToTransmitDiseaseParam', 'value'),
     State('healingTimeDiseaseParam', 'value'),
     State('initialChanceToHealParam', 'value'),
     State('initialChanceToKillParam', 'value'),
     State('chanceForAsymptomaticParam', 'value'),
     State('chanceToGoOutParam', 'value'),
     State('chanceToSelfQuarantineParam', 'value'),
     State('agentsAtCentralLocation_atSameTimeParam', 'value'),
     State('maskDistributionTimeParam', 'value'),
     State('maskCooldownTimeParam', 'value'),
     State('maskUse', 'value'),
     State('vaccineDistributionTimeParam', 'value'),
     State('vaccineEnforced', 'value')]
)
def control_simulation_and_submit_parameters(start_clicks, pause_clicks, resume_clicks, reset_clicks, *args):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    parameter_values = {
        'numberOfAgentsParam': args[0],
        'numberOfSickAtStartParam': args[1],
        'simPeriodParam': args[2],
        'standardIncubationTimeDiseaseParam': args[3],
        'chanceToTransmitDiseaseParam': args[4],
        'healingTimeDiseaseParam': args[5],
        'initialChanceToHealParam': args[6],
        'initialChanceToKillParam': args[7],
        'chanceForAsymptomaticParam': args[8],
        'chanceToGoOutParam': args[9],
        'chanceToSelfQuarantineParam': args[10],
        'agentsAtCentralLocation_atSameTimeParam': args[11],
        'maskDistributionTimeParam': args[12],
        'maskCooldownTimeParam': args[13],
        'maskUse': 'maskUse' in args[14],
        'vaccineDistributionTimeParam': args[15],
        'vaccineEnforced': 'vaccineEnforced' in args[16]
    }

    try:
        response = requests.post('http://localhost:8080/updateParameters', json=parameter_values)
        if response.status_code == 200:
            print("Parameters submitted successfully.")
        else:
            print(f"Failed to submit parameters: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error during parameters submission: {e}")

    if 'start-simulation-button' in changed_id and start_clicks > 0:
        try:
            requests.post('http://localhost:8080/startSimulation')
            print("Simulation started successfully.")
        except requests.RequestException as e:
            print(f"Failed to start simulation: {e}")

    elif 'pause-simulation-button' in changed_id and pause_clicks > 0:
        try:
            requests.post('http://localhost:8080/pauseSimulation')
            print("Simulation paused.")
        except requests.RequestException as e:
            print(f"Failed to pause simulation: {e}")

    elif 'resume-simulation-button' in changed_id and resume_clicks > 0:
        try:
            requests.post('http://localhost:8080/resumeSimulation')
            print("Simulation resumed.")
        except requests.RequestException as e:
            print(f"Failed to resume simulation: {e}")

    elif 'reset-simulation-button' in changed_id and reset_clicks > 0:
        try:
            requests.post('http://localhost:8080/resetSimulation')
            print("Simulation reset.")
        except requests.RequestException as e:
            print(f"Failed to reset simulation: {e}")

    return None

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
            try:
                api_key = helperfunctions.getOpenApiKey()
                client = openai.OpenAI(api_key=api_key)

                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": f"Analyze this summarized simulation data: {summarized_data}. "
                                       f"Using your data, what epidemic/ pandemic that you know of does this data resemble?",
                        }
                    ],
                    model="gpt-3.5-turbo",
                )

                try:
                    analysis = chat_completion.choices[0].message.content
                except AttributeError:
                    print("Failed to extract analysis from the response.")
                    analysis = "Analysis could not be performed."

                return analysis
            except Exception as e:
                print(f"Error during OpenAI chat completion request: {e}")
                return "An error occurred during analysis."
        else:
            return "No data available for analysis."
    else:
        raise PreventUpdate

dash.register_page(__name__, path='/')