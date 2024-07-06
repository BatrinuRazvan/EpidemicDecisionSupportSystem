import mysql.connector
from decouple import config
import pandas as pd
import requests
import openai
import time

API_BASE_URL = "http://localhost:8080"


def get_db_connection():
    db_config = {
        'host': config('HOST'),
        'user': config('USER'),
        'password': config('PASSWORD'),
        'database': config('DATABASE')
    }
    return mysql.connector.connect(**db_config)


def fetch_data_for_simulation():
    try:
        conn = get_db_connection()
        query = "SELECT * FROM simulation"
        df = pd.read_sql(query, conn)
        data_list = df.to_dict('records')
        print("Data fetched successfully:")
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
        elif selected_table == 'diagnostics':
            query = "SELECT * FROM DIAGNOSTICS"
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
    data = {
        "city": city,
        "title": title,
        "severity": gravity,
        "range": range_km,
        "description": description,
        "color": color
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


def fetch_data_for_diagnostic(selected_table, diagnosticName):
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        query = f"SELECT * FROM {selected_table} WHERE DIAGNOSTICNAME = %s"
        cursor.execute(query, (diagnosticName,))
        data_list = cursor.fetchall()
        if data_list:
            columns = [col[0] for col in cursor.description]
            df = pd.DataFrame(data_list, columns=columns)
            print("Data fetched successfully:", df)
        else:
            df = pd.DataFrame()
        return df


def analyze_simulation_data(summarized_data):
    api_key = getOpenApiKey()
    client = openai.OpenAI(api_key=api_key)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Analyze this summarized simulation data: {summarized_data}. "
                           f"Using your data, what epidemic/pandemic that you know of does this data resemble?",
            }
        ],
        model="gpt-3.5-turbo",
    )

    try:
        analysis = chat_completion.choices[0].message.content
    except AttributeError:
        analysis = "Analysis could not be performed."

    return analysis


def typing_effect(text, delay=0.1):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()