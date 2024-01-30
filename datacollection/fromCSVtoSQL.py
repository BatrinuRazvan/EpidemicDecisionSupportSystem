import pandas as pd
import mysql.connector
import numpy as np

# Read the CSV file
csv_file_path = 'D:\\Licenta\\EDSS\\EpidemicDecisionalSupportSystem\\datacollection\\data_download_file_reference_2022.csv'
df = pd.read_csv(csv_file_path)

# Filter columns based on your requirements
required_columns = ['date', 'cumulative_deaths', 'daily_deaths', 'cumulative_cases',
                     'daily_cases', 'cumulative_hospitalizations', 'mask_use_mean',
                     'cumulative_all_vaccinated', 'cumulative_all_fully_vaccinated', 'all_bed_capacity', 'icu_bed_capacity',
                     'hospital_beds_mean', 'icu_beds_mean', 'infection_fatality', 'location_id']

df_filtered = df[required_columns]

# Filter rows where location_id is 1
df_filtered = df_filtered[df_filtered['location_id'] == 1]

# Drop the location_id column
df_filtered = df_filtered.drop('location_id', axis=1)

# Replace NaN values with 0
df_filtered.replace([np.inf, -np.inf], np.nan, inplace=True)
df_filtered.fillna(0, inplace=True)

# Rename columns to match the MySQL table
df_filtered.columns = ['DATE_ID', 'SUM_DEATHS', 'DAILY_DEATHS', 'SUM_CASES', 'DAILY_CASES',
                       'SUM_HOSPITAL', 'MASK_USE', 'SUM_VAC', 'SUM_FULL_VAC', 'HOSPITAL_CAPACITY', 'ICU_CAPACITY', 'CURR_HOSP_OCC', 'CURR_ICU_OCC', 'INFECTION_FATALITY']


# Connect to MySQL database using mysql-connector
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='1234',
    database='edss'
)

# Create a MySQL cursor
cursor = conn.cursor()

# Insert data into the table using executemany
insert_query = """
    INSERT INTO covid_global
    (DATE_ID, SUM_DEATHS, DAILY_DEATHS, SUM_CASES, DAILY_CASES, 
    SUM_HOSPITAL, MASK_USE, SUM_VAC, SUM_FULL_VAC, HOSPITAL_CAPACITY, 
    ICU_CAPACITY, CURR_HOSP_OCC, CURR_ICU_OCC, INFECTION_FATALITY) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

data_to_insert = [tuple(row) for row in df_filtered.itertuples(index=False, name=None)]

cursor.executemany(insert_query, data_to_insert)

# Commit the changes
conn.commit()

# Close the cursor and database connection
cursor.close()
conn.close()

