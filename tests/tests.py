import sys
import os
import warnings
import numpy as np

# Add parent directory to import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from validate import validate_csv
from etl.etl import *

def test1(ontology):
    # Test that each entity in ontology has a "fields" key with a list
    entities = ontology.values()
    for e in entities:
        assert "fields" in e.keys() and isinstance(e['fields'],list)

def test2(ontology):
    # Test that all field names are valid Python variable names (str.isidentifier())
    entities = ontology.values()
    for e in entities:
        for field in e["fields"]:
            assert field.isidentifier()

def test3(ontology):
    # Test that foreign keys in relationships match real entity names
    # Assuming a relationship has the form 'foreign_key':'entity_name'
    entities = ontology.values()
    for e in entities:
        if 'relationships' in e and e['relationships']:
            for v in e['relationships'].values():
                assert v in ontology.keys()

import pandas as pd

def test4(ontology, csv):
    # Assert a valid CSV passes
    csv = 'data/ecommerce_data/customers.csv'
    # Assumption: CSV file has same name as entity, in the format "{data_dir}/{entity_name}.csv"
    # Assumption: Following the above, the first letter of entity name is uncapitalized
    assert validate_csv(ontology, csv)

def test5(ontology):
    # Assert that a CSV missing a column fails
    # Assumptions: same as above
    csv = 'data/ecommerce_data/customers_fail.csv'
    assert not validate_csv(ontology,csv)

def test6(ontology):
    # Assert a CSV with extra columns is either accepted or warned
    csv = 'data/ecommerce_data/customers_extra.csv'
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")  # Catch all warnings
        result = validate_csv(ontology, csv)
        assert result is True
        assert any(issubclass(warning.category, Warning) for warning in w)

def test7(entity_name, ontology, db_path):
    conn = connect_to_db(db_path)
    entity_name = entity_name.lower()
    fields = ontology[entity_name]["fields"]
    create_table(conn, entity_name, fields)
    cursor = conn.execute(f"""SELECT name FROM sqlite_schema WHERE type='table' AND name='{entity_name}'""")
    assert cursor.fetchone()
    conn.close()

def test8(entity_name, csv_path, ontology, db_path):
    csv_path = 'data/ecommerce_data/customers.csv'
    entity_name = entity_name.lower()
    conn = connect_to_db(db_path)
    conn.execute(f"DROP TABLE IF EXISTS {entity_name}")
    conn.commit()
    conn.close()
    # The number of rows in the table matches the CSV
    conn = connect_to_db(db_path)
    load_to_sqlite(entity_name, csv_path, ontology, db_path)
    # Get number of rows in df from csv
    df_rows = len(pd.read_csv(csv_path))
    cursor = conn.execute(f"""SELECT COUNT(*) FROM {entity_name}""")
    table_rows = cursor.fetchone()[0]
    assert df_rows == table_rows
    conn.close()

def test9(entity_name, csv_path, ontology, db_path):
    # Prevent loading invalid CSV
    fail_csv_path = "data/ecommerce_data/customers_fail.csv"
    entity_name = entity_name.lower()
    conn = connect_to_db(db_path)
    conn.execute(f"DROP TABLE IF EXISTS {entity_name}")
    conn.commit()
    conn.close()
    conn = connect_to_db(db_path)
    assert not load_to_sqlite(entity_name, fail_csv_path, ontology, db_path)
    cursor = conn.execute(f"""SELECT name FROM sqlite_master WHERE type='table' AND name='{entity_name}'""")
    assert cursor.fetchone() is None  # Table should not exist
    conn.close()

def test10(df, entity_name):
    # Input: dataframe where gender values can be m/f/M/F/male/female/Male/Female
    # Assert all gender values are either 'Male' or 'Female'
    assert all(item=='Male' or item=='Female' or np.isnan(item) for _,item in transform(df, entity_name)['gender'].items())

def test11(df, entity_name):
    # Input: dataframe with potentially messy dates
    # Output: signup_date column should contain values of type datetime64[ns] (pd.Timestamp)
    # Assert all dates are of type datetime64[ns] (pd.Timestamp)
    df = transform(df, entity_name)
    assert all(isinstance(signup_date, pd.Timestamp) or pd.isna(signup_date) for _, signup_date in df['signup_date'].items())
    assert df['signup_date'].isna().sum() == 24

def test12(df, entity_name):
    # Input: dataframe with potentially messy email addresses
    # Output: dataframe where all email addresses are lower case, include @, and lack whitespace padding
    # Assert that email addresses have been normalized
    df = transform(df, entity_name)
    assert df['email'].str.fullmatch(r'\S+@\S+\.\S+').all()
