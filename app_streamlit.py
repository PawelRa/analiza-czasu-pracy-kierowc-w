import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from dotenv import dotenv_values
from datetime import timedelta
from utils.file_operations import delete_overtime_files, delete_task_files
from utils.process_overtime_files import process_overtime_files
from utils.process_task_files import process_task_files
from utils.export_result_to_excel import export_dataframe_to_excel, export_dataframe_to_csv
from utils.analysis import analyze_data

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

# Konstanta rocznej normy czasu pracy
ANNUAL_WORKING_TIME_STANDARD_IN_HOURS = pd.Timedelta(hours=2000)

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

def plot_task_completion_time_histogram(df):
    # Lista kolumn odpowiadających zadaniom
    task_columns = ["JRJ", "PMP", "PTU", "PZ", "REZ", "UW", "WZZ", "ZDZ", "ZT"]
    
    # Obliczenie sumy dla każdej kolumny zadań
    task_sums = {col: df[col].sum() for col in task_columns if col in df.columns}
    
    # Konwersja wartości Timedelta na godziny
    task_hours = {task: task_sums[task].total_seconds() / 3600 for task in task_sums}
    
    # Tworzenie histogramu
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x=list(task_hours.keys()), 
        y=list(task_hours.values()), 
        palette="Blues_d", 
        ax=ax
    )
    
    ax.set_title("Czas realizacji zadań", fontsize=16)
    ax.set_xlabel("Rodzaj zadania", fontsize=12)
    ax.set_ylabel("Czas (w godzinach)", fontsize=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    
    # Wyświetlenie wykresu w Streamlit
    st.pyplot(fig)

def plot_overtime_distribution(df):
    # Upewnienie się, że kolumny zawierają wartości w formacie Timedelta
    df['50'] = pd.to_timedelta(df['50'], errors='coerce')
    df['100'] = pd.to_timedelta(df['100'], errors='coerce')

    # Obliczenie całkowitych nadgodzin (suma kolumn 50 i 100)
    df['total_overtime'] = df['50'] + df['100']
    
    # Usunięcie wierszy z NaT w kolumnie total_overtime
    df_clean = df.dropna(subset=['total_overtime'])
    
    # Konwersja na godziny dla histogramu
    overtime_hours = df_clean['total_overtime'].dt.total_seconds() / 3600  # Konwersja na godziny
    
    # Tworzenie histogramu
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(overtime_hours, bins=10, kde=False, color='skyblue', ax=ax)
    
    ax.set_title("Rozkład nadgodzin z podziałem na przedziały", fontsize=16)
    ax.set_xlabel("Nadgodziny (w godzinach)", fontsize=12)
    ax.set_ylabel("Liczba pracowników", fontsize=12)
    
    # Wyświetlenie wykresu w Streamlit
    st.pyplot(fig)

def plot_worked_hours_histogram(df):
    # Upewnienie się, że kolumna przepracowane zawiera wartości w formacie Timedelta
    df['przepracowane'] = pd.to_timedelta(df['przepracowane'], errors='coerce')
    
    # Usunięcie wierszy z NaT w kolumnie przepracowane
    df_clean = df.dropna(subset=['przepracowane'])

    # Konwersja na godziny, ponieważ timedelta nie jest kompatybilny z histogramami
    worked_hours = df_clean['przepracowane'].dt.total_seconds() / 3600  # Konwersja na godziny

    # Tworzenie histogramu
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.histplot(worked_hours, bins=20, kde=True, color='skyblue', ax=ax)
    ax.set_title("Histogram przepracowanych godzin")
    ax.set_xlabel("Przepracowane godziny")
    ax.set_ylabel("Liczba pracowników")

    # Wyświetlenie wykresu w Streamlit
    st.pyplot(fig)


def plot_overtime_usage(df):
    # Upewnienie się, że kolumny zawierają wartości w formacie Timedelta
    df['50'] = pd.to_timedelta(df['50'], errors='coerce')
    df['100'] = pd.to_timedelta(df['100'], errors='coerce')

    # Obliczenie sumy nadgodzin
    overtime_sum = df['50'].sum() + df['100'].sum()

    # Ustalenie liczby pracowników
    df_num_rows = df.shape[0]
    annual_overtime_limit = pd.Timedelta(hours=416) * df_num_rows  # Rok nadgodzin dla wszystkich pracowników

    # Procentowy udział nadgodzin
    overtime_percentage = (overtime_sum / annual_overtime_limit) * 100

    # Przygotowanie danych do wykresu kołowego
    labels = ['Wykorzystane nadgodziny', 'Pozostały czas']
    sizes = [overtime_percentage, 100 - overtime_percentage]
    colors = ['#ff9999','#66b3ff']

    # Wykres kołowy
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    st.pyplot(fig)

def plot_comparison_overtime_norm(df):
    # Upewnienie się, że kolumny zawierają wartości w formacie Timedelta
    df['50'] = pd.to_timedelta(df['50'], errors='coerce')
    df['100'] = pd.to_timedelta(df['100'], errors='coerce')
    df['norma'] = pd.to_timedelta(df['norma'], errors='coerce')
    
    # Usuwamy wiersze z NaT (puste wartości) w kluczowych kolumnach
    df_clean = df.dropna(subset=['50', '100', 'norma'])
    
    # Obliczenie sumy nadgodzin (50% i 100%)
    overtime_50_sum = df_clean['50'].sum()
    overtime_100_sum = df_clean['100'].sum()
    
    # Obliczenie sumy normy
    norma_sum = df_clean['norma'].sum()
    
    # Przygotowanie danych do wykresu
    overtime_values = [overtime_50_sum.total_seconds(), overtime_100_sum.total_seconds()]
    norma_values = [norma_sum.total_seconds()] * 2  # Powielamy normę dla obu typów nadgodzin (50% i 100%)

    # Wykres porównania nadgodzin i normy
    labels = ['50% Overtime', '100% Overtime']
    
    fig, ax = plt.subplots(figsize=(8, 6))
    bar_width = 0.35
    index = range(2)
    
    ax.bar(index, overtime_values, bar_width, label='Nadgodziny')
    ax.bar([i + bar_width for i in index], norma_values, bar_width, label='Norma')

    ax.set_xlabel('Rodzaj nadgodzin')
    ax.set_ylabel('Czas (w sekundach)')
    ax.set_title('Porównanie nadgodzin (50% i 100%) do normy')
    ax.set_xticks([i + bar_width / 2 for i in index])
    ax.set_xticklabels(labels)
    ax.legend()

    st.pyplot(fig)


def plot_worked_vs_overtime(df):
    # Upewnienie się, że kolumny zawierają wartości w formacie Timedelta
    df['przepracowane'] = pd.to_timedelta(df['przepracowane'], errors='coerce')
    df['50'] = pd.to_timedelta(df['50'], errors='coerce')
    df['100'] = pd.to_timedelta(df['100'], errors='coerce')
    
    # Usunięcie wierszy z brakującymi wartościami w kluczowych kolumnach
    df_clean = df.dropna(subset=['przepracowane', '50', '100'])

    # Obliczenie całkowitego przepracowanego czasu i nadgodzin
    worked_time = df_clean['przepracowane'].sum().total_seconds() / 3600  # Konwersja na godziny
    overtime_time = (df_clean['50'].sum() + df_clean['100'].sum()).total_seconds() / 3600  # Konwersja na godziny

    # Przygotowanie danych do wykresu
    labels = ['Przepracowane', 'Nadgodziny']
    values = [worked_time, overtime_time]

    # Tworzenie wykresu
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(labels, values, color=['#1f77b4', '#ff7f0e'])
    ax.set_ylabel('Czas (w godzinach)')
    ax.set_title('Porównanie przepracowanego czasu do nadgodzin')

    # Wyświetlenie wykresu w aplikacji Streamlit
    st.pyplot(fig)


def data_analysis_section():
    st.header("Analiza danych")
    try:
        # Przetwarzanie danych
        df_overtime = process_overtime_files(OVERTIME_PATH)
        df_tasks = process_task_files(TASK_PATH)

        # Połączenie danych
        df = pd.merge(df_overtime, df_tasks, on="ID", how="outer")

        # Wypełnienie pustych komórek zerem w formacie timedelta
        for column in df.columns:
            if column != "ID":
                df[column] = df[column].fillna(timedelta(0))

        # Usunięcie wierszy zawierających same zera
        zero_rows_mask = (df.iloc[:, 1:] == pd.Timedelta(0)).all(axis=1)
        df = df[~zero_rows_mask]

        # Wyświetlenie tabeli
        st.subheader("Podgląd danych")
        st.write(df)

        # Obliczenia
        st.markdown("# Obliczenia", unsafe_allow_html=True)
        columns_list = ['100', '50', 'norma', 'przepracowane', 'JRJ', 'PMP', 'PTU', 'PZ', 'REZ', 'UW', 'WZZ', 'ZDZ', 'ZT']
        columns_sums = {col: df[col].sum() for col in columns_list if col in df.columns}

        # Obliczenie brakujących etatów
        worked_time = columns_sums.get('przepracowane', pd.Timedelta(0))
        norma_time = columns_sums.get('norma', pd.Timedelta(0))
        sum_driving_time = sum(
            (columns_sums.get(col, pd.Timedelta(0)) for col in [
                "JRJ", "PMP", "PRZ", "PTU", "PZ", "REZ", "TP", "UW", "WZZ", "ZDZ", "ZT"
            ]),
            start=pd.Timedelta(0)
        )
        missing_positions_in_hours = (worked_time - norma_time) + (sum_driving_time - worked_time)
        missing_employment = round(missing_positions_in_hours / ANNUAL_WORKING_TIME_STANDARD_IN_HOURS, 2)

        st.write(f"Brakujące etaty (w godzinach): {missing_positions_in_hours}")
        st.write(f"Brakujące etaty (jako liczba pełnych etatów): {missing_employment}")

        # Wykorzystanie nadgodzin
        df_num_rows = df.shape[0]
        INCREASED_ANNUAL_OVERTIME_LIMIT_FOR_FULLTIME_EMPLOYMENT = pd.Timedelta(hours=416) * df_num_rows
        overtime_sum = columns_sums.get('50', pd.Timedelta(0)) + columns_sums.get('100', pd.Timedelta(0))
        overtime_percentage = round((overtime_sum / INCREASED_ANNUAL_OVERTIME_LIMIT_FOR_FULLTIME_EMPLOYMENT) * 100, 2)

        st.write(f"Wykorzystanie nadgodzin: {overtime_percentage}%")

        # Wizualizacje
        st.markdown("# Wizualizacje")
        st.subheader("Histogram przepracowanych godzin")
        plot_worked_hours_histogram(df)
        st.markdown("""
        Linia widoczna na histogramie to **estymacja funkcji gęstości jądra (KDE)**. 
        Przedstawia ona oszacowanie rozkładu przepracowanych godzin w postaci gładkiej krzywej. 
        Pomaga lepiej zrozumieć, jak wartości są rozłożone w całym zakresie danych.
        """)

        st.subheader("Histogram czasu realizacji zadań")
        plot_task_completion_time_histogram(df)

        st.subheader("Rozkład nadgodzin")
        plot_overtime_distribution(df)


        # plot_overtime_usage(df) # wstępnie ok
        # plot_comparison_overtime_norm(df) # wstępnie ok
        # plot_worked_vs_overtime(df)

        # Eksport danych
        st.subheader("Eksport wyników")
        if st.button("Eksportuj dane do Excel"):
            export_dataframe_to_excel(df)
            st.success("Dane zostały wyeksportowane do pliku Excel.")
        if st.button("Eksportuj dane do CSV"):
            export_dataframe_to_csv(df)
            st.success("Dane zostały wyeksportowane do pliku CSV.")

    except Exception as e:
        st.error(f"Wystąpił błąd podczas analizy danych: {e}")

if __name__ == "__main__":
    main()
