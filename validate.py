import pandas as pd
import warnings
from ontology import ontology

def validate_csv(ontology, csv):
    """
    Function to ensure that an imported CSV file matches an ontology.

    Assumptions: the CSV file name matches the entity name in the ontology {data_dir}/{entity_name}.csv (except entity name must be capitalized)

    Constraints: a CSV with fewer columns than the ontology fields must fail
                a CSV that doesn't contain all the ontology fields must fail
                a CSV that has all the ontology fields, but contains other column, must raise a warning
    """
    entity_name = csv.split('/')[-1].split('.')[0].split('_')[0].lower()
    ontology_fields = ontology[entity_name]['fields']

    df = pd.read_csv(csv)
    
    # Check if the CSV has fewer columns than the ontology fields 
    if len(df.columns) < len(ontology_fields):
        return False
    
    # Check if the CSV contains all the ontology fields
    missing_fields = set(ontology_fields) - set(df.columns)
    if missing_fields:
        return False
    
    # Check for extra fields not in the ontology
    extra_fields = set(df.columns) - set(ontology_fields)
    if extra_fields:
        warnings.warn(f"CSV contains extra fields not in the ontology", UserWarning)
    
    return True  