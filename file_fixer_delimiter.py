import pandas as pd
import os

# Specify the folder containing the CSV files
folder_path = os.path.dirname(__file__)  # Replace with the path to your folder

# Loop through all files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)

        try:
            # Use the 'python' engine for more flexible parsing and handle irregular whitespace
            df = pd.read_csv(file_path, sep=r'\s+', engine='python')

            # Save the file with comma as the delimiter
            new_file_path = os.path.join(folder_path, f"fixed_{filename}")
            df.to_csv(new_file_path, index=False)

            print(f"Converted '{filename}' to comma-delimited format.")

        except pd.errors.ParserError as e:
            print(f"Could not parse '{filename}': {e}")