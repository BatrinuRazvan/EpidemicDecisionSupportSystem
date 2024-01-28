from backend import helperfunctions


def del_status_values():
    conn = helperfunctions.get_db_connection()
    cursor = conn.cursor()

    query = "DROP TABLE status"
    cursor.execute(query)
    conn.commit()

    query = "create table status (DAY_ID INT AUTO_INCREMENT, TOTAL INT, CURED INT, DEAD INT, SICK INT, PRIMARY KEY (DAY_ID))"
    cursor.execute(query)
    conn.commit()

    cursor.close()
    conn.close()

def store_status_values(healthy_people, immune, deaths, sick):
    conn = helperfunctions.get_db_connection()
    cursor = conn.cursor()

    query = ("INSERT INTO status (TOTAL, CURED, DEAD, SICK) "
             "VALUES (%s, %s, %s, %s)")
    values = (healthy_people, immune, deaths, sick)

    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()
