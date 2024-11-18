"Downloader"

import logging
from pathlib import Path

import requests


def download_file(url: str, output_path: str) -> bool:
    """
    Télécharge un fichier à partir d'une URL et le sauvegarde à l'emplacement spécifié.

    Args:
        url (str): L'URL du fichier à télécharger.
        output_path (str): Le chemin où le fichier doit être sauvegardé.

    Returns:
        bool: True si le téléchargement est réussi, False sinon.

    Example:
        >>> download_file("https://example.com/file.zip", "/path/to/save/file.zip")
        True
    """
    try:

        response = requests.get(url, stream=True)
        response.raise_for_status()

        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        return True
    except (requests.RequestException, IOError) as e:

        logging.error(f"Erreur pendant le téléchargement : {e}")
        return False


def build_url(date: str, heure: str) -> str:
    """
    Construit l'URL de téléchargement du fichier Excel du classement du Vendée Globe
    en fonction de la date et de l'heure fournies.

    Args:
        date (str): La date au format AAAAMMJJ (ex. 20241110).
        heure (str): L'heure au format HHMMSS (ex. 130400).

    Returns:
        str: L'URL complète pour télécharger le fichier Excel.

    Example:
        >>> build_vendeeglobe_url("20241110", "130400")
        'https://www.vendeeglobe.org/sites/default/files/ranking/
        vendeeglobe_leaderboard_20241110_130400.xlsx'
    """
    base_url = "https://www.vendeeglobe.org/sites/default/files/ranking/"
    file_name = f"vendeeglobe_leaderboard_{date}_{heure}.xlsx"
    return base_url + file_name
