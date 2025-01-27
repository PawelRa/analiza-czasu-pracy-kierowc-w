from pathlib import Path
from openpyxl import Workbook
from datetime import timedelta
from openpyxl.utils.dataframe import dataframe_to_rows
import pandas as pd
from config import DB_OUTPUT_PATH

# Wczytanie konfiguracji
DB_OUT = DB_OUTPUT_PATH

def timedelta_to_excel_numeric(td):
    """Konwertuje timedelta na liczbę odpowiadającą ułamkowi dnia w Excel."""
    if isinstance(td, timedelta):  # Sprawdzamy, czy td jest obiektem typu timedelta
        return td.total_seconds() / (24 * 3600)  # Liczba dni jako liczba zmiennoprzecinkowa
    elif isinstance(td, (int, float)):  # Jeśli to jest liczba, zwróć ją bez zmian
        return td
    else:
        return 0  # Jeśli jest to inny typ, zwróć 0 (możesz tu dodać inne zachowanie, jeśli chcesz)

def timedelta_to_time_format(td):
    """Konwertuje timedelta na format tekstowy hh:mm:ss, uwzględniając godziny ponad 24."""
    total_seconds = td.total_seconds()
    hours = int(total_seconds // 3600)  # Całkowite godziny
    minutes = int((total_seconds % 3600) // 60)  # Pozostałe minuty
    seconds = int(total_seconds % 60)  # Pozostałe sekundy
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def export_dataframe_to_excel(df):
    output_file_name = "result.xlsx"
    output_file_path = Path(DB_OUT) / output_file_name

    # Konwersja kolumn timedelta na ułamek dnia (dla Excela)
    for column in df.columns:
        if column != "ID":  # Pomijamy kolumnę kluczową
            # Sprawdzamy typ danych kolumny
            if df[column].dtype == "timedelta64[ns]":
                df[column] = df[column].apply(
                    lambda x: timedelta_to_excel_numeric(x) if pd.notnull(x) else ""
                )

    # Tworzenie arkusza Excel z poprawnym formatowaniem
    wb = Workbook()
    ws = wb.active

    # Wiersze z DataFrame (nagłówek i dane)
    for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), start=1):
        ws.append(row)
        # Ustaw format dla wszystkich wierszy poza nagłówkiem
        if r_idx == 1:
            continue
        for c_idx, cell in enumerate(row, start=1):
            if c_idx != 1:  # Ominięcie kolumny ID
                # Sprawdzamy typ danych dla komórki (tylko timedelta dostaje specjalny format)
                if isinstance(cell, float):  # Jeśli jest to wartość timedelta w formacie liczbowym
                    ws.cell(row=r_idx, column=c_idx).number_format = "[h]:mm:ss"

    # Zapis pliku Excel
    wb.save(output_file_path)
    print(f"Plik został zapisany jako {output_file_path}.")

def export_dataframe_to_csv (df):
    output_file_name = "result.csv"
    output_file_path = Path(DB_OUT) / output_file_name
    # Zapisanie wyników do pliku
    df.to_csv(output_file_path, index=False, sep=";")
    print(f"Wynik zapisany do pliku: {output_file_path}")