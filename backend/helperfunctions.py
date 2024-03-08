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


def post_message(city, gravity, range_km, description):
    url = f"{API_BASE_URL}/messages"
    data = {
        "city": city,
        "gravity": gravity,
        "range_km": range_km,
        "description": description
    }
    response = requests.post(url, json=data)
    return response.json()

def get_messages():
    url = f"{API_BASE_URL}/messages"
    response = requests.get(url)
    return response.json()