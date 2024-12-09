import pandas as pd
from pathlib import Path
from dotenv import dotenv_values
from datetime import timedelta
from utils.process_overtime_files import process_overtime_files
from utils.process_task_files import process_task_files
from utils.export_result_to_excel import *

# Wczytanie konfiguracji
ENV = dotenv_values(".env")
DB_INPUT_PATH = Path(ENV["DB_INPUT_PATH"])
DB_IN_OVERTIME = DB_INPUT_PATH / "overtime"
DB_IN_TASKS = DB_INPUT_PATH / "tasks"

# print(f"DB_IN_OVERTIME = {DB_IN_OVERTIME} ")

# Przetwarzanie plików nadgodzin
df_overtime = process_overtime_files(DB_IN_OVERTIME)
df_tasks = process_task_files(DB_IN_TASKS)

# Połączenie dwóch DataFrame
df = pd.merge(df_overtime, df_tasks, on="ID", how="outer")

# Wypełnienie pustych komórek zerem w formacie timedelta
for column in df.columns:
    if column != "ID":  # Nie dotyczy kolumny kluczowej
        df[column] = df[column].fillna(timedelta(0))

# # Usunięcie wierszy zawierających same zera
zero_rows_mask = (df.iloc[:, 1:] == pd.Timedelta(0)).all(axis=1)
df = df[~zero_rows_mask]

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
sum_driving_time = sum(
    (columns_sums.get(col, pd.Timedelta(0)) for col in columns_to_sum_driving_time),
    pd.Timedelta(0)  # Wartość startowa
)

print(f"SUMY KOLUMN = {columns_sums}")

# Suma kolumny 'przepracowane' oraz 'norma'
worked_time = columns_sums.get('przepracowane', pd.Timedelta(0))  # Ustalamy początkową wartość na Timedelta(0)
norma_time = columns_sums.get('norma', pd.Timedelta(0))  # Ustalamy początkową wartość na Timedelta(0)

missing_positions_in_hours = (worked_time - norma_time)+(sum_driving_time-worked_time)

missing_employment = round((missing_positions_in_hours / ANNUAL_WORKING_TIME_STANDARD_IN_HOURS), 2)

print(f"Brakujące etaty w godzinach = {missing_positions_in_hours}")
print(f"Brakujące etaty = {missing_employment}")

# Wykorzystanie nadgodzin w procentach
df_num_rows = df.shape[0]
INCREASED_ANNUAL_OVERTIME_LIMIT_FOR_FULLTIME_EMPLOYMENT = pd.Timedelta(hours=416) * df_num_rows

# Klucze do zsumowania
columns_to_sum_overtime = ["100", "50"]

# Obliczenie sumy kolumn
overtime_sum = columns_sums.get('50') + columns_sums.get('100')

print(f"df_num_rows = {df_num_rows}")

print(f"INCREASED_ANNUAL_OVERTIME_LIMIT_FOR_FULLTIME_EMPLOYMENT = {INCREASED_ANNUAL_OVERTIME_LIMIT_FOR_FULLTIME_EMPLOYMENT}")
# overtime_sum = columns_sums.get('50', pd.Timedelta(0)) + columns_sums.get('100', pd.Timedelta(0))

overtime_percentage = round((overtime_sum / INCREASED_ANNUAL_OVERTIME_LIMIT_FOR_FULLTIME_EMPLOYMENT) * 100, 2)

print(f"overtime_sum = {overtime_sum}")
print(f"overtime_sum / INCREASED_ANNUAL_OVERTIME_LIMIT_FOR_FULLTIME_EMPLOYMENT = {overtime_percentage} %")

export_dataframe_to_excel(df)
export_dataframe_to_csv(df)

