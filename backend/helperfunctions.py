import mysql.connector
from decouple import config
import pandas as pd


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

def fetch_data():
    try:
        conn = get_db_connection()
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