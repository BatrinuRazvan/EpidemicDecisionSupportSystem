import dash
from dash import html, dcc, Output, Input, callback
import plotly.express as px
import mysql.connector
import pandas as pd
import subprocess
from dash.exceptions import PreventUpdate
from backend import helperfunctions

def fetch_data():
    try:
        # db_config = {
        #     'host': 'localhost',
        #     'user': 'root',
        #     'password': '1234',
        #     'database': 'edss'
        # }
        # conn = mysql.connector.connect(**db_config)
        conn = helperfunctions.get_db_connection()
        query = "SELECT DAY_ID, TOTAL, CURED, DEAD, SICK FROM status"
        df = pd.read_sql(query, conn)
        data_list = df.to_dict('records')  # Convert DataFrame to list of dicts
        print("Data fetched successfully:")
        print(data_list)  # Print the entire list
        conn.close()
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of an error


layout = html.Div([
    html.H1('Simulation'),
    dcc.Graph(id='real-time-graph'),
    dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0),
    html.Button('Run PowerShell Script', id='ps-button', n_clicks=0),
    html.Div(id='dummy-output', style={'display': 'none'})
])


@callback(Output('real-time-graph', 'figure'), [Input('interval-component', 'n_intervals')])


def update_graph(n):
    df = fetch_data()
    if df.empty:
        print("No data retrieved from the database.")
        return px.area()  # Return an empty graph if no data is retrieved

    try:
        fig = px.area(df, x='DAY_ID', y=['DEAD', 'CURED', 'SICK', 'TOTAL'],
                      color_discrete_map={'TOTAL': 'aquamarine', 'CURED': 'green', 'DEAD': 'gray', 'SICK': 'red'})
        return fig
    except Exception as e:
        print(f"Error creating graph: {e}")
        return {}

@callback(
    Output('dummy-output', 'children'),  # You can use a dummy output if you don't need to update the layout
    [Input('ps-button', 'n_clicks')]
)

def run_ps_script(n_clicks):
    if n_clicks == 0:
        raise PreventUpdate

    try:
        # Full path to your PowerShell script
        ps_script_path = "D:\\Licenta\\EDSS\\EpidemicDecisionalSupportSystem\\backend\\startSim.ps1"
        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_script_path], check=True)
        print("PowerShell script executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute PowerShell script: {e}")

    return None


dash.register_page(__name__, path='/')