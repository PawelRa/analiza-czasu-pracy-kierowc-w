import pandas as pd
from pathlib import Path
from utils.convert_to_time import convert_to_time

def process_overtime_files(input_dir):
    """
    Przetwarza wszystkie pliki nadgodzin znajdujące się w katalogu input_dir.
    
    Args:
        input_dir (Path): Ścieżka do katalogu z plikami wejściowymi.
        
    Returns:
        pd.DataFrame: Połączony dataframe z ID jako klucz i sumami nadgodzin jako kolumnami.
    """
    all_files = list(input_dir.glob("*.csv"))  # Znajduje wszystkie pliki CSV w katalogu
    combined_df = None  # Dataframe wynikowy
    
    for file_path in all_files:
        # Odczytanie liczby kolumn w pliku
        first_row = pd.read_csv(file_path, sep=';', encoding='windows-1250', nrows=1, header=None)
        num_columns = len(first_row.columns)

        # Pobranie tylko kolumn kluczowych: pierwszej i ostatniej
        needed_columns = [0, num_columns - 1]
        df = pd.read_csv(
            file_path,
            sep=';',
            encoding='windows-1250',
            usecols=needed_columns,
            header=None
        )
        
        # Czyszczenie danych
        column_name = file_path.stem  # Użycie nazwy pliku (bez rozszerzenia) jako nazwy kolumny
        df.columns = ["ID", column_name]
        df = df.dropna(how='all')
        df = df[~df.apply(lambda x: x.str.contains(";", na=False).all(), axis=1)]
        df = df[~df.iloc[:, 0].str.contains("Składnik", na=False)]
        df = df[~df.iloc[:, 0].str.contains("Razem", na=False)]
        df = df[~df.iloc[:, -1].str.contains("Suma", na=False)]
        df = df[~df.apply(lambda x: x.str.contains("Zestawienie godzin w okresie", na=False).any(), axis=1)]

        # Konwersja sumy czasu do formatu timedelta
        df[column_name] = df[column_name].apply(lambda x: convert_to_time(str(x)))
        
        # Łączenie z dataframe wynikowym
        if combined_df is None:
            combined_df = df
        else:
            combined_df = pd.merge(combined_df, df, on="ID", how="outer")
    
    return combined_df
