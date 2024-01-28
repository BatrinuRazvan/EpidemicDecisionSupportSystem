import dash
from dash import html, dcc, Output, Input, callback
import plotly.express as px
from backend import helperfunctions
import pandas as pd

def fetch_data():
    try:
        # db_config = {
        #     'host': 'localhost',
        #     'user': 'root',
        #     'password': '1234',
        #     'database': 'edss'
        # } # Put this in a separate file to reuse everywhere implementing DRY
        # conn = mysql.connector.connect(**db_config)
        conn = helperfunctions.get_db_connection()
        query = "SELECT data, cazuri, decese FROM covid19_tm"
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
    html.H1('Covid19 Real-Life Comparison'),
    dcc.Graph(id='covid19-graph'),
    dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0),
])


@callback(Output('covid19-graph', 'figure'), [Input('interval-component', 'n_intervals')])


def update_graph(n):
    df = fetch_data()
    if df.empty:
        print("No data retrieved from the database.")
        return px.area()  # Return an empty graph if no data is retrieved

    try:
        fig = px.area(df, x='data', y=['cazuri', 'decese'],
                      color_discrete_map={'cazuri': 'red', 'decese': 'gray'})
        return fig
    except Exception as e:
        print(f"Error creating graph: {e}")
        return {}


dash.register_page(__name__, path='/real_life_comparison')