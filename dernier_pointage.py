"Dernier pointage en date"

import argparse
from pathlib import Path
from src.downloader import download_file, build_url
from src.processor import build_gpkg
from src.timemanager import get_current_date, get_last_update


def main():
    """
    Point d'entrée principal du programme.

    Cette fonction parse les arguments de la ligne de commande, obtient la dernière mise à jour
    et la date actuelle, construit l'URL pour télécharger le fichier, puis appelle les fonctions
    pour télécharger et traiter les données. Enfin, elle génère un fichier GPKG dans le répertoire
    spécifié ou dans le répertoire par défaut.
    """
    parser = argparse.ArgumentParser(description="Télécharge et traite les données.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./"),
        help="Répertoire d'export pour le fichier GPKG",
    )
    args = parser.parse_args()

    last_update = get_last_update()
    date = get_current_date()
    url = build_url(date, last_update)
    file = f"./.data/data_{date}_{last_update}.xlsx"
    download_file(url, file)
    build_gpkg(
        Path(file),
        name=f"classement_{date}_{last_update}",
        date=date,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
