"Intégralité des pointages depuis le départ et trajectoire."
import argparse
import logging
from pathlib import Path
import re
from src.downloader import download_file, build_url
from src.processor import (
    build_gpkg,
    create_geom,
    aggreger_geodataframes,
    create_trejectoire,
    export_to_gpkg,
)
from src.timemanager import (
    update_hours,
    list_of_dates_between_today_and_departure,
    hours_exception,
)


def main():
    """
    Point d'entrée principal du programme.

    Cette fonction parse les arguments de la ligne de commande, configure la gestion des logs,
    télécharge les fichiers de données pour les différentes dates et heures, crée les géométries,
    agrège les données et exporte les résultats sous forme de fichiers GPKG pour les pointages
    et les trajectoires.
    """
    parser = argparse.ArgumentParser(description="Télécharge et traite les données.")
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("./"),
        help="Répertoire d'export pour le fichier GPKG",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Active le mode verbose pour plus de détails",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    all_dates = list_of_dates_between_today_and_departure()

    list_url = []
    list_file = []

    url_premier_jour = build_url("20241110", hours_exception)
    list_url.append(url_premier_jour)
    file_premier_jour = f"./.data/data_20241110_{hours_exception}.xlsx"
    list_file.append(file_premier_jour)

    for date in all_dates:
        for hours in update_hours:
            url = build_url(date, hours)
            list_url.append(url)
            file = f"./.data/data_{date}_{hours}.xlsx"
            list_file.append(file)

    for url, file in zip(list_url, list_file):
        if not Path(file).exists():
            logging.info(f"Téléchargement de {file}...")
            download_file(url, file)
        else:
            logging.info(f"Le fichier {file} existe déjà, téléchargement ignoré.")

    list_gdf = []
    for file in list_file:
        if Path(file).exists():
            date = (
                re.search(r"data_(\d{8})_", file).group(1)
                if re.search(r"data_(\d{8})_", file)
                else None
            )
            gdf = create_geom(file, date)
            list_gdf.append(gdf)

    final_gdf = create_trejectoire(aggreger_geodataframes(list_gdf))

    export_to_gpkg(aggreger_geodataframes(list_gdf), Path(args.output_dir / f"data_{date}.gpkg"), "pointages")
    export_to_gpkg(final_gdf, Path(args.output_dir / f"data_{date}.gpkg"), "trajectoire")


if __name__ == "__main__":
    main()
