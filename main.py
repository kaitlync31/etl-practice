import importlib
import inspect
import sys
import pandas as pd
from ontology import ontology

tests_module = importlib.import_module("tests.tests")

# Discover all test functions
all_tests = {
    name: func for name, func in inspect.getmembers(tests_module, inspect.isfunction)
    if name.startswith("test")
}

def run_tests(test_names, csv_path=None, db_path=None, entity_name=None):
    for name in test_names:
        func = all_tests.get(name)
        if func is None:
            print(f"❓ {name}: Not found")
            continue

        try:
            sig = inspect.signature(func)
            param_count = len(sig.parameters)

            if param_count == 1:
                func(ontology)
            elif param_count == 2:
                if param_count == 2:
                    if name == "test10" or name == "test11" or name == 'test12':
                        df = pd.read_csv(csv_path)
                        func(df, entity_name)
                    else:
                        if csv_path is None:
                            raise ValueError(f"{name} requires a CSV path (use --csv)")
                        func(ontology, csv_path)
            elif param_count == 3:
                if db_path is None:
                    raise ValueError(f"{name} requires a DB path (use --db)")
                func(entity_name, ontology, db_path)
            elif param_count == 4:
                if csv_path is None:
                    raise ValueError(f"{name} requires a CSV path (use --csv)")
                if db_path is None:
                    raise ValueError(f"{name} requires a DB path (use --db)")
                func(entity_name, csv_path, ontology, db_path)
            else:
                raise ValueError(f"{name} has unsupported number of arguments")

            print(f"✅ {name}: Passed")
        except AssertionError:
            print(f"❌ {name}: Failed (AssertionError)")
        except Exception as e:
            print(f"⚠️ {name}: Error - {e}")

if __name__ == "__main__":
    args = sys.argv[1:]
    entity_name = None
    csv_path = None
    db_path = None
    test_names = []

    skip_next = False
    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue

        if arg == "--entity":
            entity_name = args[i + 1]
            skip_next = True
        elif arg == "--csv":
            csv_path = args[i + 1]
            skip_next = True
        elif arg == "--db":
            db_path = args[i + 1]
            skip_next = True
        else:
            test_names.append(arg)

    if not test_names:
        test_names = list(all_tests.keys())

    run_tests(test_names, csv_path=csv_path, db_path=db_path, entity_name=entity_name)

