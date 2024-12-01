import pandas as pd
from pathlib import Path
from dotenv import dotenv_values
from utils.process_overtime_files import process_overtime_files

# Wczytanie konfiguracji
ENV = dotenv_values(".env")
DB_PATH = Path("data")
DB_IN = DB_PATH / "input" / "overtime"
DB_OUT = DB_PATH / "output"

# Przetwarzanie plików nadgodzin
df_overtime = process_overtime_files(DB_IN)

# Wyświetlenie wynikowego dataframe
print(df_overtime)

# Zapisanie wyników do pliku
# output_file = DB_OUT / "combined_overtime.csv"
# df_overtime.to_csv(output_file, index=False, sep=";")
# print(f"Wynik zapisany do pliku: {output_file}")
