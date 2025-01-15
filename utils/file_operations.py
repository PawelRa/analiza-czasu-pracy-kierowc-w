from pathlib import Path

def delete_overtime_files(overtime_path: Path):
    """Usuń wszystkie pliki z katalogu overtime."""
    for file in overtime_path.glob("*.csv"):
        file.unlink()
    print(f"Wszystkie pliki w katalogu {overtime_path} zostały usunięte.")

def delete_task_files(task_path: Path):
    """Usuń wszystkie pliki z katalogu task."""
    for file in task_path.glob("*.csv"):
        file.unlink()
    print(f"Wszystkie pliki w katalogu {task_path} zostały usunięte.")
