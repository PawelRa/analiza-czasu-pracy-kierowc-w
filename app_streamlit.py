import streamlit as st
import pandas as pd
from pathlib import Path
from dotenv import dotenv_values
from utils.file_operations import delete_overtime_files, delete_task_files
from utils.process_overtime_files import process_overtime_files
from utils.process_task_files import process_task_files
from utils.analysis import analyze_data
from datetime import timedelta

# Wczytanie konfiguracji z pliku .env
ENV = dotenv_values(".env")
DB_INPUT_PATH = Path(ENV["DB_INPUT_PATH"])
DB_OUTPUT_PATH = Path(ENV["DB_OUTPUT_PATH"])

# Ścieżki do podkatalogów
OVERTIME_PATH = DB_INPUT_PATH / "overtime"
TASK_PATH = DB_INPUT_PATH / "tasks"

# Tworzenie katalogów (jeśli nie istnieją)
OVERTIME_PATH.mkdir(parents=True, exist_ok=True)
TASK_PATH.mkdir(parents=True, exist_ok=True)

# Listy wymaganych plików
OVERTIME_FILES = ["50.csv", "100.csv", "norma.csv", "przepracowane.csv"]
TASK_FILES = ["JRJ.csv", "PMP.csv", "PTU.csv", "PZ.csv", "REZ.csv", "UW.csv", "WZZ.csv", "ZDZ.csv", "ZT.csv"]

def main():
    st.title("Aplikacja do zarządzania i analizy danych")
    st.sidebar.header("Opcje")

    section = st.sidebar.radio("Wybierz sekcję:", ["Zarządzanie plikami", "Analiza danych"])

    if section == "Zarządzanie plikami":
        file_management_section()
    elif section == "Analiza danych":
        data_analysis_section()

def file_management_section():
    st.header("Zarządzanie plikami")
    section = st.sidebar.radio("Wybierz sekcję:", ["overtime", "task"])

    if section == "overtime":
        manage_files(OVERTIME_PATH, OVERTIME_FILES, "Pliki czasu pracy (overtime)")
        if st.sidebar.button("Usuń wszystkie pliki z overtime"):
            delete_overtime_files(OVERTIME_PATH)
            st.sidebar.success("Pliki z katalogu overtime zostały usunięte.")
    else:
        manage_files(TASK_PATH, TASK_FILES, "Pliki zadań (tasks)")
        if st.sidebar.button("Usuń wszystkie pliki z tasks"):
            delete_task_files(TASK_PATH)
            st.sidebar.success("Pliki z katalogu tasks zostały usunięte.")

def manage_files(directory, required_files, title):
    """Zarządzanie plikami w wybranym katalogu."""
    st.header(title)
    st.subheader("Istniejące pliki:")
    existing_files = list(directory.glob("*.csv"))
    existing_files_names = [f.name for f in existing_files]

    if existing_files:
        st.write(existing_files_names)
    else:
        st.write("Brak plików w katalogu.")

    missing_files = [file for file in required_files if file not in existing_files_names]
    if missing_files:
        st.subheader("Brakujące pliki:")
        st.write(missing_files)
    else:
        st.success("Wszystkie wymagane pliki są obecne.")

    st.subheader("Dodaj pliki:")
    uploaded_files = st.file_uploader("Wgraj pliki CSV", type=["csv"], accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.name in required_files:
                save_path = directory / uploaded_file.name
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"Plik {uploaded_file.name} został zapisany.")
            else:
                st.warning(f"Plik {uploaded_file.name} nie jest wymagany w tej sekcji.")

def data_analysis_section():
    st.header("Analiza danych")
    try:
        # Przetwarzanie danych
        df_overtime = process_overtime_files(OVERTIME_PATH)
        df_tasks = process_task_files(TASK_PATH)
        df = pd.merge(df_overtime, df_tasks, on="ID", how="outer")

        for column in df.columns:
            if column != "ID":
                df[column] = df[column].fillna(timedelta(0))

        zero_rows_mask = (df.iloc[:, 1:] == pd.Timedelta(0)).all(axis=1)
        df = df[~zero_rows_mask]

        st.subheader("Podgląd danych:")
        st.dataframe(df)

        # Obliczenia
        st.subheader("Wyniki analizy:")
        columns_sums = {col: df[col].sum() for col in df.columns if col != "ID"}
        st.write("Suma kolumn:", columns_sums)

        analyze_data(df)
        st.success("Analiza danych zakończona pomyślnie.")

    except Exception as e:
        st.error(f"Wystąpił błąd: {e}")

if __name__ == "__main__":
    main()
