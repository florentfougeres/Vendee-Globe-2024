import argparse
import logging
from src.downloader import download_file, build_url
from src.processor import build_gpkg
from src.timemanager import update_hours, list_of_dates_between_today_and_departure, hours_exception
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Télécharge et traite les données.")
    parser.add_argument(
        '-o', '--output-dir', 
        type=Path, 
        default=Path("./"), 
        help="Répertoire d'export pour le fichier GPKG"
    )
    parser.add_argument(
        '-v', '--verbose', 
        action='store_true', 
        help="Active le mode verbose pour plus de détails"
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    all_dates = list_of_dates_between_today_and_departure()
    
    list_url = []
    list_file = []

    for date in all_dates: 
        for hours in update_hours: 
            url = build_url(date, hours)
            list_url.append(url)
            file = f"./.data/data_{date}_{hours}.xlsx"
            list_file.append(file)

    url_premier_jour = build_url("20241110", hours_exception)
    list_url.append(url_premier_jour)
    file_premier_jour = f"./.data/data_20241110_{hours_exception}.xlsx"
    list_file.append(file_premier_jour)

    for url, file in zip(list_url, list_file):
        if not Path(file).exists():
            logging.info(f"Téléchargement de {file}...")
            download_file(url, file)
        else:
            logging.info(f"Le fichier {file} existe déjà, téléchargement ignoré.")

if __name__ == "__main__":
    main()
