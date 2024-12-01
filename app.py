import pandas as pd
import streamlit as st
from openai import OpenAI
from dotenv import dotenv_values
from pathlib import Path
from utils.convert_to_time import convert_to_time

ENV = dotenv_values(".env")
DB_PATH = Path("data")
DB_IN = DB_PATH / "input" / "overtime"
DB_OUT = DB_PATH / "output"
COLUMN_NAMES_150 = ["ID", "Suma"]

# nazwy plików z nadgodzinami
file_name50 = "50.csv"
file_name100 = "100.csv"

#wgranie pliku 50 nadgodzin
first_row50 = pd.read_csv(DB_IN / file_name50, sep=';', encoding='windows-1250', nrows=1, header=None)
num_columns = len(first_row50.columns)

needed_columns50 = [0, num_columns - 1]  # Pierwsza (0) i ostatnia (num_columns - 1)
df50 = pd.read_csv(
    DB_IN / file_name50, 
    sep=';', 
    encoding='windows-1250', 
    usecols=needed_columns50, 
    header=None
)

# przygotowanie danych z 50 nadgodzin
df50.columns = COLUMN_NAMES_150
df50 = df50.dropna(how='all')
df50 = df50[~df50.apply(lambda x: x.str.contains(";", na=False).all(), axis=1)]
df50 = df50[~df50.iloc[:, 0].str.contains("Składnik", na=False)]
df50 = df50[~df50.iloc[:, 0].str.contains("Razem", na=False)]
df50 = df50[~df50.iloc[:, -1].str.contains("Suma", na=False)]
df50 = df50[~df50.apply(lambda x: x.str.contains("Zestawienie godzin w okresie", na=False).any(), axis=1)]
df50['Suma'] = df50['Suma'].apply(lambda x: convert_to_time(str(x)))



#wgranie pliku 100 nadgodzin
first_row100 = pd.read_csv(DB_IN / file_name100, sep=';', encoding='windows-1250', nrows=1, header=None)
num_columns = len(first_row100.columns)

needed_columns100 = [0, num_columns - 1]  # Pierwsza (0) i ostatnia (num_columns - 1)
df100 = pd.read_csv(
    DB_IN / file_name100, 
    sep=';', 
    encoding='windows-1250', 
    usecols=needed_columns100, 
    header=None
)

# przygotowanie danych z 100 nadgodzin
df100.columns = COLUMN_NAMES_150
df100 = df100.dropna(how='all')
df100 = df100[~df100.apply(lambda x: x.str.contains(";", na=False).all(), axis=1)]
df100 = df100[~df100.iloc[:, 0].str.contains("Składnik", na=False)]
df100 = df100[~df100.iloc[:, 0].str.contains("Razem", na=False)]
df100 = df100[~df100.iloc[:, -1].str.contains("Suma", na=False)]
df100 = df100[~df100.apply(lambda x: x.str.contains("Zestawienie godzin w okresie", na=False).any(), axis=1)]
df100['Suma'] = df100['Suma'].apply(lambda x: convert_to_time(str(x)))

# łączenie tabel
df50 = df50.rename(columns={"Suma": "50"})
df100 = df100.rename(columns={"Suma": "100"})
df = pd.merge(df50, df100, on="ID", how="outer")

# pd.set_option('display.max_rows', None)
print(df)

# print(df50)
# print(df100)

# for value in df['Suma df50']:
#     print(type(value))

# for value in df['Suma df100']:
#     print(type(value))


# df.to_excel('output.xlsx', index=False, sheet_name='Arkusz1')
