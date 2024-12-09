from pathlib import Path
from dotenv import dotenv_values

# Wczytanie konfiguracji
ENV = dotenv_values(".env")
DB_OUT = ENV["DB_OUTPUT_PATH"]

# Ścieżka do pliku wynikowego


def export_dataframe_to_excel (df):
    output_file_name = "result.xlsx"
    output_file_path = Path(DB_OUT) / output_file_name

    # Konwersja kolumn timedelta na format dni dziesiętnych (kompatybilny z Excela)
    for column in df.columns:
        if column != "ID":  # Pomijamy kolumnę kluczową
            df[column] = df[column].dt.total_seconds() / (24 * 3600)  # Konwersja timedelta na dni dziesiętne


    # Eksport do Excela z formatowaniem
    df.to_excel(output_file_path, index=False)
    print(f"Plik został zapisany jako {output_file_path}.")

def export_dataframe_to_csv (df):
    output_file_name = "result.csv"
    output_file_path = Path(DB_OUT) / output_file_name
    # Zapisanie wyników do pliku
    df.to_csv(output_file_path, index=False, sep=";")
    print(f"Wynik zapisany do pliku: {output_file_path}")