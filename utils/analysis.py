import matplotlib.pyplot as plt
import seaborn as sns

def analyze_data(df):
    # Histogram czasu pracy kierowców
    df['przepracowane_h'] = df['przepracowane'].dt.total_seconds() / 3600
    plt.figure(figsize=(10, 6))
    plt.hist(df['przepracowane_h'], bins=20, color='skyblue', edgecolor='black')
    plt.title('Rozkład przepracowanego czasu kierowców')
    plt.xlabel('Czas przepracowany (godziny)')
    plt.ylabel('Liczba kierowców')
    plt.grid(axis='y')
    plt.show()

