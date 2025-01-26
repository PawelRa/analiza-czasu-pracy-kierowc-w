from pathlib import Path
import pandas as pd
from datetime import timedelta

# Konfiguracja ścieżek
DB_INPUT_PATH = Path("data/input")
DB_OUTPUT_PATH = Path("data/output")
CHARTS_PATH = Path("data/charts")
PROCESSED_DATA_PATH = Path("data/processed/processed_data.pkl")

# Ścieżki do podkatalogów
OVERTIME_PATH = DB_INPUT_PATH / "overtime"
TASK_PATH = DB_INPUT_PATH / "tasks"

# Listy wymaganych plików
OVERTIME_FILES = ["50.csv", "100.csv", "norma.csv", "przepracowane.csv"]
TASK_FILES = ["JRJ.csv", "PMP.csv", "PTU.csv", "PZ.csv", "REZ.csv", "UW.csv", "WZZ.csv", "ZDZ.csv", "ZT.csv"]

# Konstanta rocznej normy czasu pracy
ANNUAL_WORKING_TIME_STANDARD_IN_HOURS = pd.Timedelta(hours=2000)

# roczny limit nadgodzin
ANNUAL_OVERTIME_LIMIT_FOR_FULLTIME_EMPLOYMENT = pd.Timedelta(hours=416)
