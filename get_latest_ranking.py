import argparse
from src.downloader import download_file, build_url
from src.processor import build_gpkg
from src.timemanager import get_current_date, get_last_update
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Télécharge et traite les données.")
    parser.add_argument(
        '--output-dir', 
        type=Path, 
        default=Path("./"), 
        help="Répertoire d'export pour le fichier GPKG"
    )
    args = parser.parse_args()

    last_update = get_last_update()
    date = get_current_date()
    url = build_url(date, last_update)
    file = f"./.data/data_{date}_{last_update}.xlsx"
    download_file(url, file)
    build_gpkg(Path(file), name=f"classement_{date}_{last_update}", date=date, output_dir=args.output_dir)

if __name__ == "__main__":
    main()