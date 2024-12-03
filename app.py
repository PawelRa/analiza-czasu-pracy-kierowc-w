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
# Norma czasu pracy
ANNUAL_WORKING_TIME_STANDARD_IN_HOURS = pd.Timedelta(hours=2000)

# Tablica z sumami kolumn
columns_list = ['100', '50', 'norma', 'przepracowane', 'JRJ', 'PMP', 'PTU', 'PZ', 'REZ', 'UW', 'WZZ', 'ZDZ', 'ZT']
columns_sums = {col: df[col].sum() for col in columns_list if col in df.columns}

# Obliczenie czasu prowadzenia
# driving_time = sum(columns_sums.get(key, pd.Timedelta(0)) for key in columns_sums)
columns_to_sum_driving_time = ["JRJ", "PTU", "TP", "WZZ", "ZDZ", "ZT"]
# Suma wartości ze słownika columns_sums dla kolumn z columns_to_sum_driving_time
driving_time = sum(
    (columns_sums[col] for col in columns_to_sum_driving_time if col in columns_sums),
    start=pd.Timedelta(0)
)

# Obliczenie innych czynności
# Lista kolumn do zsumowania dla czasu zadań
columns_to_sum_other_tasks = ["PZ", "REZ", "UW"]

# Suma wartości ze słownika columns_sums dla kolumn z columns_to_sum_other_tasks
other_tasks = sum(
    (columns_sums[col] for col in columns_to_sum_other_tasks if col in columns_sums),
    start=pd.Timedelta(0)
)

# Obliczanie przerw ustawowych
# Lista kolumn do zsumowania dla przerw ustawowych
columns_to_sum_statutory_breaks = ["PMP", "PRZ"]

# Suma wartości ze słownika columns_sums dla kolumn z columns_to_sum_statutory_breaks
statutory_breaks = sum(
    (columns_sums[col] for col in columns_to_sum_statutory_breaks if col in columns_sums),
    start=pd.Timedelta(0)
)

# Obliczanie brakujących etatów
# Obliczenie brakujących godzin
# Kolumny do uwzględnienia w obliczeniu różnicy
columns_to_sum_driving_time = ["JRJ", "PMP", "PRZ", "PTU", "PZ", "REZ", "TP", "UW", "WZZ", "ZDZ", "ZT"]

# Suma kolumny 'przepracowane' oraz 'norma'
worked_time = columns_sums.get('przepracowane', pd.Timedelta(0))  # Ustalamy początkową wartość na Timedelta(0)
norma_time = columns_sums.get('norma', pd.Timedelta(0))  # Ustalamy początkową wartość na Timedelta(0)

#====================================================
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
