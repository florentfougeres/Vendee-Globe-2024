import argparse
import logging
from src.downloader import download_file, build_url
from src.processor import load_excel_data
from pathlib import Path

def setup_logging(verbose: bool):
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

def main():
    parser = argparse.ArgumentParser(description="Traitement des données du Vendée Globe")

    parser.add_argument(
        '-d', '--date',
        type=str,
        required=True,
        help="Date sous forme AAAAMMJJ (ex. 20241111)"
    )

    parser.add_argument(
        '-H', '--heure',
        type=str,
        required=True,
        help="Heure sous forme HHMMSS (ex. 123456)"
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="Activer le mode verbose pour plus de détails"
    )

    args = parser.parse_args()
    date = args.date
    heure = args.heure
    verbose = args.verbose

    setup_logging(verbose)

    logging.info("Date: %s", date)
    logging.info("Heure: %s", heure)

    url = build_url(date, heure)
    file = "./.data/data_{0}_{1}.xlsx".format(date, heure)
    logging.debug("URL construite : %s", url)

    download_file(url, file)
    load_excel_data(str(Path(file)))


if __name__ == "__main__":
    main()
