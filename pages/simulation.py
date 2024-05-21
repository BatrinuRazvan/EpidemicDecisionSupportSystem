import dash
from dash import html, dcc, Output, Input, callback, State
import plotly.express as px
import requests
import json
from dash.exceptions import PreventUpdate
from backend import helperfunctions
import openai

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
    html.H1('Epidemic Simulation'),
    dcc.Graph(id='real-time-graph'),
    dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0),
    html.Div([
        html.Button('Start Simulation', id='start-simulation-button', n_clicks=0),
        html.Button('Pause Simulation', id='pause-simulation-button', n_clicks=0),
        html.Button('Resume Simulation', id='resume-simulation-button', n_clicks=0),
        html.Button('Reset Simulation', id='reset-simulation-button', n_clicks=0),
    ]),
    html.Div(id='dummy-output', style={'display': 'none'}),
    html.Div(input_elements, id='changable-parameters'),
    html.Button('Analyze Simulation', id='analyze-simulation-button', n_clicks=0),
    html.Div(id='analysis-output'),
])


@callback(Output('real-time-graph', 'figure'), [Input('interval-component', 'n_intervals')])
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
     Input('nb-of-people', 'value'),
     Input('number_of_months', 'value'),
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
def control_simulation_and_submit_parameters(start_clicks, pause_clicks, resume_clicks, reset_clicks, *args):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    parameter_values = {input_id: value for input_id, value in zip(
        ['nb-of-people', 'number_of_months', 'number_of_days', 'start_sick', 'sleepTime', 'average_time_of_encounters',
         'max_chances_going_outside', 'time_incubating', 'time_before_infectious', 'max_infectuosity', 'max_lethality',
         'days_before_possible_healing', 'healing_chances', 'immunity_bounds', 'immunity_ri_start', 'immunity_modifier'],
        args
    )}

    # Send parameters on every input change
    try:
        response = requests.post('http://localhost:8080/submitParameters', json=parameter_values)
        if response.status_code == 200:
            print("Parameters submitted successfully.")
        else:
            print(f"Failed to submit parameters: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error during parameters submission: {e}")

    # Control simulation based on button clicks
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
