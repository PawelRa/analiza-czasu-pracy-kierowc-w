import pandas as pd
from pathlib import Path
from dotenv import dotenv_values
from datetime import timedelta
from utils.process_overtime_files import process_overtime_files
from utils.process_task_files import process_task_files

# Wczytanie konfiguracji
ENV = dotenv_values(".env")
DB_PATH = Path("data")
DB_IN_OVERTIME = DB_PATH / "input" / "overtime"
DB_IN_TASKS = DB_PATH / "input" / "tasks"
DB_OUT = DB_PATH / "output"

# Przetwarzanie plików nadgodzin
df_overtime = process_overtime_files(DB_IN_OVERTIME)
df_tasks = process_task_files(DB_IN_TASKS)

# Połączenie dwóch DataFrame
df = pd.merge(df_overtime, df_tasks, on="ID", how="outer")

# Wypełnienie pustych komórek zerem w formacie timedelta
for column in df.columns:
    if column != "ID":  # Nie dotyczy kolumny kluczowej
        df[column] = df[column].fillna(timedelta(0))

# OBLICZENIA
# Definicja limitu rocznych nadgodzin
annual_overtime_limit = timedelta(hours=416)

# Obliczanie czasu prowadzenia
columns_to_sum_time_driving = ["JRJ", "PTU", "TP", "WZZ", "ZDZ", "ZT"]
# columns_to_sum_time_driving = ["JRJ", "PTU", "WZZ", "ZDZ", "ZT"]
# Filtracja kolumn, które faktycznie istnieją w DataFrame
existing_time_driving_columns = [col for col in columns_to_sum_time_driving if col in df.columns]

if existing_time_driving_columns:
    # Obliczenie sumy dla istniejących kolumn
    lead_time = df[existing_time_driving_columns].sum().sum()
else:
    # Jeżeli żadna z kolumn nie istnieje, ustaw czas_prowadzenia na timedelta(0)
    lead_time = timedelta(0)

print(f"Czas prowadzenia = {lead_time}")


# Ścieżka do pliku wynikowego
# output_path = "result.xlsx"

# Konwersja kolumn timedelta na format dni dziesiętnych (kompatybilny z Excela)
# for column in df.columns:
#     if column != "ID":  # Pomijamy kolumnę kluczową
#         df[column] = df[column].dt.total_seconds() / (24 * 3600)  # Konwersja timedelta na dni dziesiętne


# Eksport do Excela z formatowaniem
# df.to_excel(output_path, index=False)
# print(f"Plik został zapisany jako {output_path}.")


# Zapisanie wyników do pliku
# output_file = DB_OUT / "combined_overtime.csv"
# df_overtime.to_csv(output_file, index=False, sep=";")
# print(f"Wynik zapisany do pliku: {output_file}")
