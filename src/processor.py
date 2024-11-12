import polars as pl 
from pathlib import Path

def load_excel_data(path_file: Path) -> pl.DataFrame:
    print(str(path_file))
    df = pl.read_excel(str(path_file))
    # On garde que les colonnes de B à U et les lignes de 6 à 40
    df = df.slice(5, 40)
    df = df[:, 1:21]
    print(df)
    df.write_csv("./.data/test.csv")
    return df