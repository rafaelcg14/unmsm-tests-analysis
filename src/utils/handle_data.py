import pandas as pd

def load_dataframe(year, career):
    filepath = f"data/processed/{year}/{year}-{career}.csv"

    return pd.read_csv(filepath)

def career_exists_for_year(year, career):
    try:
        temp_df = load_dataframe(year, career)

        return career in temp_df["carrera"].unique()
    
    except FileNotFoundError:
        return False