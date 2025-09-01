import os
import sys
import pandas as pd
import sqlite3
# Add parent directory to import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from validate import validate_csv

def connect_to_db(db_path):
    # Create and return DB connection
    conn = sqlite3.connect(db_path) 
    return conn

def create_table(conn, entity_name, fields):
    # Create DB table with name entity_name
    columns = ', '.join([f"{field} TEXT" for field in fields])
    create_table_query = f"CREATE TABLE {entity_name} ({columns})"
    conn.execute(create_table_query)
    conn.commit()

def insert_rows(conn, df, entity_name):
    # Insert row from dataframe to DB
    columns = ', '.join(df.columns)
    placeholders = ', '.join(['?' for _ in df.columns])
    insert_query = f"INSERT INTO {entity_name} ({columns}) VALUES ({placeholders})"
    cursor = conn.cursor()
    for row in df.values.tolist():
        cursor.execute(insert_query, row)
    conn.commit()

def load_to_sqlite(entity_name, csv_path, ontology, db_path):
    # Load valid csv file data from CSV to DB
    if not validate_csv(ontology, csv_path):
        return False
    conn = connect_to_db(db_path)
    df = pd.read_csv(csv_path)
    fields = ontology[entity_name]['fields']
    create_table(conn, entity_name, fields)
    insert_rows(conn, df, entity_name)

def transform(df, entity_name):
    # perform transform operations in here
    df['gender'] = df['gender'].str.lower().replace({ 
        'm': 'Male', 
        'male': 'Male',
        'f': 'Female',
        'female': 'Female'
    })
    df['signup_date'] = pd.to_datetime(df['signup_date'], errors='coerce')  
    df['email'] = df['email'].str.strip().str.lower()  
    return df