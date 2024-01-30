from backend import helperfunctions
from datetime import datetime, timedelta

def get_current_date(counter):
    current_date = datetime.today()
    current_date += timedelta(days=counter)
    current_date.strftime("%Y-%m-%d")
    return current_date


def del_status_values():
    conn = helperfunctions.get_db_connection()
    cursor = conn.cursor()

    query = "DROP TABLE IF EXISTS status"
    cursor.execute(query)
    conn.commit()

    query = ("CREATE TABLE status (DATE_ID DATE, TOTAL INT, CURED INT, DEAD INT, SICK INT)")
    cursor.execute(query)
    conn.commit()

    cursor.close()
    conn.close()


def store_status_values(healthy_people, immune, deaths, sick, counter):
    conn = helperfunctions.get_db_connection()
    cursor = conn.cursor()

    query = ("INSERT INTO status (DATE_ID, TOTAL, CURED, DEAD, SICK) "
             "VALUES (%s, %s, %s, %s, %s)")
    values = (get_current_date(counter), healthy_people, immune, deaths, sick)

    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()
