import pandas as pd
import os, csv

def create_csv_files():
    raw_base_path = "data/raw"
    processed_base_path = "data/processed"

    # Ensure processed directory exists
    os.makedirs(processed_base_path, exist_ok=True)

    # Iterate through years
    for year_folder in os.listdir(raw_base_path):
        year_path = os.path.join(raw_base_path, year_folder)
        if not os.path.isdir(year_path):
            continue

        # Iterate through careers in each year
        for career_file in os.listdir(year_path):
            career_name = career_file.replace(".csv", "").split(f"{year_folder}-")[1]
            raw_file_path = os.path.join(year_path, career_file)

            # Create processed directory for this year
            year_processed_path = os.path.join(processed_base_path, year_folder)
            os.makedirs(year_processed_path, exist_ok=True)

            # Filepath for this career's processed file
            processed_file_path = os.path.join(year_processed_path, career_file)

            # Read raw data
            df = pd.read_csv(raw_file_path)
            df = df.drop( columns=["nombre_completo"], errors="ignore")
            df.to_csv(processed_file_path, index=False)


def process_data():
    processed_base_path = "data/processed"
    
    for year_folder in os.listdir(processed_base_path):
        year_path = os.path.join(processed_base_path, year_folder)

        if not os.path.isdir(year_path):
            continue

        for career_file in os.listdir(year_path):
            file_path = os.path.join(year_path, career_file)

            df = pd.read_csv(file_path)
            
            # Extract rows with second choice careers
            second_chance_df = df[ df["segunda_opcion"].notna()]

            # Process second choice rows
            for _, row in second_chance_df.iterrows():
                second_chance_career = row["segunda_opcion"]
                second_chance_file_name = f"{year_folder}-{second_chance_career}.csv"
                second_chance_file_path = os.path.join(year_path, second_chance_file_name)

                # Ensure the directory exists
                os.makedirs(year_path, exist_ok=True)

                # Append row to the second chance career file
                row.to_frame().T.to_csv(
                    second_chance_file_path,
                    mode="a",
                    index=False,
                    header=not os.path.exists(second_chance_file_path)
                )
            
            # Remove rows with second choice careers different to main career
            # df = df[ df["segunda_opcion"].isna() | (df["segunda_opcion"] == df["carrera"]) ]

            # Save updated dataframe
            df.to_csv(file_path, index=False)

def clean_data():
    processed_base_path = "data/processed"

    for year_folder in os.listdir(processed_base_path):
        year_path = os.path.join(processed_base_path, year_folder)

        if not os.path.isdir(year_path):
            continue

        for career_file in os.listdir(year_path):
            file_path = os.path.join(year_path, career_file)

            df = pd.read_csv(file_path)

            df = df.drop( columns=["nombre_completo"], errors="ignore")

            df.to_csv(file_path, index=False)


create_csv_files()
process_data()