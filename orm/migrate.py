import importlib

if __name__ == "__main__":
    mod = importlib.import_module("blueprints.notes.migrations.0001_initial")
    print(mod)