import json
import mysql.connector
from backend import helperfunctions

def json_to_sql_insert(file_path):
    try:
        with open(file_path, 'r') as file:
            data_list = json.load(file)

        if not isinstance(data_list, list):
            data_list = [data_list]

        queries = []

        for data_dict in data_list:
            data_value = data_dict.get("data", "")
            cazuri_value = data_dict.get("cazuri", 0)
            decese_value = data_dict.get("decese", 0)

            sql_query = f"INSERT INTO COVID19_TM (data, cazuri, decese) VALUES ('{data_value}', {cazuri_value}, {decese_value});"
            queries.append(sql_query)

        queries.reverse()
        return queries
    except json.JSONDecodeError as e:
        return f"Error decoding JSON: {e}"
    except FileNotFoundError:
        return "File not found."
    except Exception as e:
        return f"An error occurred: {e}"

def execute_queries(file_path):
    try:
        # Connect to the MySQL database
        # conn = mysql.connector.connect(
        #     host='localhost',       # replace with your host, e.g., 'localhost'
        #     database='edss', # replace with your database name
        #     user='root',     # replace with your username
        #     password='1234'  # replace with your password
        # )
        conn = helperfunctions.get_db_connection()
        cursor = conn.cursor()

        sql_insert_queries = json_to_sql_insert(file_path)

        for query in sql_insert_queries:
            cursor.execute(query)
            conn.commit()
            print(f"Query executed successfully: {query}")

    except mysql.connector.Error as e:
        print(f"MySQL Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn.is_connected():
            conn.close()
            print("MySQL connection is closed")

# Example usage
file_path = "D:/Licenta/EDSS/EpidemicDecisionalSupportSystem/dataimprov/tmdate.json"
execute_queries(file_path)
