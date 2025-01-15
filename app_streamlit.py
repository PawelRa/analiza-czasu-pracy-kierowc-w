import streamlit as st
from pathlib import Path
from dotenv import dotenv_values
from utils.file_operations import delete_overtime_files, delete_task_files

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
    st.title("Zarządzanie plikami aplikacji")
    st.sidebar.header("Opcje")

    # Wybór sekcji: overtime/task
    section = st.sidebar.radio("Wybierz sekcję:", ["overtime", "task"])

    # Ustawienie sesji dla komunikatów
    if "message_clear" not in st.session_state:
        st.session_state.message_clear = False

    if "last_section" not in st.session_state:
        st.session_state.last_section = section

    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

    # Zmiana sekcji, czyszczenie komunikatów
    if section != st.session_state.last_section:
        st.session_state.message_clear = True  # Ustawienie flagi, aby komunikaty były usunięte
        st.session_state.last_section = section
        st.session_state.uploaded_files = []  # Resetowanie listy wgranych plików

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

    # Wyświetlenie listy istniejących plików
    st.subheader("Istniejące pliki:")
    existing_files = list(directory.glob("*.csv"))
    existing_files_names = [f.name for f in existing_files]

    if existing_files:
        st.write(existing_files_names)
    else:
        st.write("Brak plików w katalogu.")

    # Wyświetlenie brakujących plików
    missing_files = [file for file in required_files if file not in existing_files_names]
    if missing_files:
        st.subheader("Brakujące pliki:")
        st.write(missing_files)
    else:
        st.success("Wszystkie wymagane pliki są obecne.")

    # Wgrywanie nowych plików
    st.subheader("Dodaj pliki:")
    uploaded_files = st.file_uploader("Wgraj pliki CSV", type=["csv"], accept_multiple_files=True)

    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files  # Zapisujemy wgrane pliki w sesji
        for uploaded_file in uploaded_files:
            if uploaded_file.name in required_files:
                save_path = directory / uploaded_file.name
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"Plik {uploaded_file.name} został zapisany.")
            else:
                st.warning(f"Plik {uploaded_file.name} nie jest wymagany w tej sekcji.")

    # Czyszczenie komunikatów po zmianie sekcji
    if st.session_state.message_clear:
        st.session_state.message_clear = False
        st.empty()  # Usunięcie wszystkich wyświetlonych komunikatów

if __name__ == "__main__":
    main()
