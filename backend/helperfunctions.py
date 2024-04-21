import mysql.connector
from decouple import config
import pandas as pd
import requests

API_BASE_URL = "http://localhost:8080"


def get_db_connection():
    dbHost = config('HOST')
    dbUser = config('USER')
    dbPassword = config('PASSWORD')
    dbDatabase = config('DATABASE')
    return mysql.connector.connect(
        host=dbHost,
        user=dbUser,
        password=dbPassword,
        database=dbDatabase
    )

def fetch_data_for_simulation():
    try:
        conn = get_db_connection()
        query = "SELECT DAY_INCREMENT, TOTAL_HOSPITALIZATIONS, TOTAL_RECOVERED, TOTAL_DEATHS, DAILY_CASES FROM simulation"
        df = pd.read_sql(query, conn)
        data_list = df.to_dict('records')
        print("Data fetched successfully:")
        print(data_list)
        conn.close()
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()


def fetch_data_for_table(selected_table):
    try:
        conn = get_db_connection()

        if selected_table == 'covid19_tm':
            query = "SELECT * FROM covid19_tm"
        elif selected_table == 'status':
            query = "SELECT DATE_ID, TOTAL, CURED, DEAD, SICK FROM status"
        elif selected_table == 'covid_global':
            query = "SELECT * FROM covid_global"
        elif selected_table == 'covid_romania':
            query = "SELECT * FROM covid_romania"
        elif selected_table == 'simulation':
            query = "SELECT * FROM simulation"
        else:
            # Add more tables as needed
            print(f"Invalid table name: {selected_table}")
            return pd.DataFrame()

        df = pd.read_sql(query, conn)
        data_list = df.to_dict('records')
        print("Data fetched successfully:")
        print(data_list)
        conn.close()
        return df
    except Exception as e:
        print(f"Error fetching data for table {selected_table}: {e}")
        return pd.DataFrame()


def post_message(city, title, gravity, range_km, description, color):
    # Your existing code to post the message, modified to include 'color'
    data = {
        "city": city,
        "title": title,
        "severity": gravity,  # Assuming 'gravity' is used as 'severity'
        "range": range_km,
        "description": description,
        "color": color  # Include the color in the data sent to the server
    }
    requests.post(f'{API_BASE_URL}/messages/addNotification', json=data)


def get_messages():
    response = requests.get(f'{API_BASE_URL}/messages/getMessages')
    return response.json()


def get_citiesAndMarkers():
    response = requests.get(f'{API_BASE_URL}/cities')
    city_markers = {marker["cityName"]: {"lat": marker["latitude"], "lon": marker["longitude"]} for marker in response.json()}
    return city_markers


def get_decisionResponses():
    response = requests.get(f'{API_BASE_URL}/messages/getDecisionResponses')
    return response.json()


def fetch_and_summarize_simulation_data():
    response = requests.get(f"{API_BASE_URL}/getSimulationData")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        # Sample or summarize your data here. As an example, we'll randomly select 100 entries if the data is large.
        if len(df) > 100:
            df_sampled = df.sample(n=100)
        else:
            df_sampled = df
        return df_sampled.to_json(orient='split')
    else:
        print(f"Failed to fetch simulation data: {response.status_code}")
        return None


def getOpenApiKey():
    return config('OPENAPIKEY')
