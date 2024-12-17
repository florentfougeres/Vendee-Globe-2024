import logging
import re
from datetime import datetime
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, MultiLineString, Point

from src.downloader import build_url, download_file
from src.timemanager import *


def parse_coordinates(coord: str) -> tuple[int, int, int, str]:
    """Analyse une chaîne de caractères représentant une coordonnée
    en degrés, minutes, secondes et direction.

    Args:
        coord (str): Coordonnée en format 'DD°MM.SS[D]' où D est la
        direction (N/S/E/W).

    Returns:
        tuple[int, int, int, str]: Un tuple contenant les degrés (int),
        minutes (int), secondes (int), et la direction (str : 'N', 'S', 'E' ou 'W').
    """
    direction = coord[-1]  # Dernier caractère (N/S/E/W)
    parts = coord[:-1].replace("'", "").replace('"', "").split("°")
    degrees = parts[0].strip()
    minutes, seconds = parts[1].split(".")

    return int(degrees), int(minutes), int(seconds), direction


def dms_to_decimal(degrees: int, minutes: int, seconds: int, direction: str) -> float:
    """Convertir des degrés minutes secondes en degrés décimaux

    Args:
        degrees (int): Degrés
        minutes (int): Minutes
        seconds (int): Secondes
        direction (str): Direction (N / S / E / O)

    Returns:
        float: Coordordonnées décimales
    """

    decimal = float(degrees) + float(minutes) / 60 + float(seconds) / (60 * 60)

    if direction in ["S", "W"]:
        decimal = -decimal
    return decimal


def parse_hour(hour_str: str, date_obj: datetime) -> datetime | None:
    """Parse une chaîne de caractères représentant une heure et combine avec une date
    pour créer un objet datetime.

    Args:
        hour_str (str): Chaîne représentant l'heure, au format 'HH:MM' avec éventuellement
                        le suffixe ' FR'.
        date_obj (datetime): Objet datetime représentant la date à laquelle l'heure sera
                             combinée.

    Returns:
        datetime | None: Un objet datetime combinant la date et l'heure si l'heure est valide,
                         sinon None.
    """
    if pd.isnull(hour_str):
        return None

    cleaned_str = re.search(r"\b\d{2}:\d{2}\b", hour_str.replace(" FR", ""))
    if cleaned_str:
        return datetime.combine(
            date_obj, datetime.strptime(cleaned_str.group(), "%H:%M").time()
        )
    return None


def read_xlsx(file: Path, param_date: str) -> pd.DataFrame:
    """Charge un fichier Excel dans un DataFrame sans en-têtes et réorganise les colonnes.

    Args:
        file (Path): Chemin vers le fichier Excel.
        param_date (str): Date en format 'YYYYMMDD' utilisée pour associer un timestamp
                          aux heures du fichier.

    Returns:
        pd.DataFrame: DataFrame contenant les données chargées et nettoyées, avec une colonne
                      timestamp et les colonnes skipper et bateau séparées.
    """
    # Définir les noms de colonnes dans l'ordre souhaité
    columns = [
        "rang",
        "code",
        "nom",
        "heure",
        "latitude",
        "longitude",
        "30m_cap",
        "30m_vitesse",
        "30m_vmg",
        "30m_distance",
        "last_rank_cap",
        "last_rank_vitesse",
        "last_rank_vmg",
        "last_rank_distance",
        "24h_cap",
        "24h_vitesse",
        "24h_vmg",
        "24h_distance",
        "dtf",
        "dtl",
    ]

    df = pd.read_excel(
        file,
        usecols="B:U",
        skiprows=5,
        nrows=40,
        header=None,
        names=columns,
        engine="calamine",
    )

    # Nettoyage des sauts de ligne dans les chaînes
    df = df.apply(
        lambda col: col.map(
            lambda x: x.replace("\r\n", " - ") if isinstance(x, str) else x
        )
    )

    date_obj = datetime.strptime(param_date, "%Y%m%d")
    df["timestamp"] = df["heure"].apply(lambda x: parse_hour(x, date_obj))
    df[["skipper", "bateau"]] = df["nom"].str.split(pat=" - ", n=1, expand=True)
    # On supprime les abandons
    df = df[df["rang"] != "RET"]

    return df


def build_gpkg(file: Path, name: str, date: str, output_dir: Path = Path("./")) -> None:
    """Construire un fichier GeoPackage (.gpkg) à partir d'un fichier Excel et d'une date.

    Args:
        file (Path): Chemin vers le fichier Excel contenant les données.
        name (str): Nom de base pour le fichier GeoPackage de sortie.
        date (str): Date utilisée pour générer les coordonnées de timestamp.
        output_dir (Path, optional): Répertoire où sauvegarder le fichier .gpkg. Par défaut,
                                     le répertoire courant.
    """
    gdf = create_geom(file, date)
    output_path = output_dir / f"{name}.gpkg"
    gdf.to_file(output_path, driver="GPKG")


def create_geom(file: Path, date: str) -> gpd.GeoDataFrame:
    """Créer un GeoDataFrame avec une colonne de géométrie à partir des données Excel.

    Args:
        file (Path): Chemin vers le fichier Excel contenant les données.
        date (str): Date utilisée pour générer les coordonnées de timestamp.

    Returns:
        gpd.GeoDataFrame: Un GeoDataFrame avec la géométrie et les données associées.
    """
    df = read_xlsx(file, date)

    df["latitude_decimal"] = df["latitude"].apply(
        lambda x: dms_to_decimal(*parse_coordinates(x))
    )
    df["longitude_decimal"] = df["longitude"].apply(
        lambda x: dms_to_decimal(*parse_coordinates(x))
    )

    geometry = [
        Point(lon, lat)
        for lon, lat in zip(df["longitude_decimal"], df["latitude_decimal"])
    ]

    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

    return gdf


def aggreger_geodataframes(liste_geodfs: list[gpd.GeoDataFrame]) -> gpd.GeoDataFrame:
    """Agrège une liste de GeoDataFrames en un seul GeoDataFrame.

    Args:
        liste_geodfs (list): Liste de GeoDataFrames à combiner.

    Returns:
        gpd.GeoDataFrame: GeoDataFrame résultant de l'agrégation.

    Raises:
        ValueError: Si la liste de GeoDataFrames est vide.
    """
    if not liste_geodfs:
        raise ValueError("La liste de GeoDataFrames est vide.")

    geodf_agrege = gpd.GeoDataFrame(pd.concat(liste_geodfs, ignore_index=True))
    return geodf_agrege


def create_trajectoire(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Crée une trajectoire pour chaque code en regroupant les points par code
    et en créant une `MultiLineString` lorsqu'une transition longitude dépasse +180/-180.

    Args:
        gdf (gpd.GeoDataFrame): Le GeoDataFrame contenant les données à regrouper.

    Returns:
        gpd.GeoDataFrame: Un GeoDataFrame contenant des `MultiLineString` ou `LineString` pour chaque code.
    """
    # Tri des points par code et timestamp
    gdf = gdf.sort_values(by=["code", "timestamp"])

    def build_trajectory(group):
        points = list(group.geometry)
        lines = []
        current_line = [points[0]]

        for p1, p2 in zip(points[:-1], points[1:]):

            if abs(p1.x - p2.x) > 180:
                lines.append(LineString(current_line))
                current_line = [p2]
            else:
                current_line.append(p2)

        if current_line:
            lines.append(LineString(current_line))

        return MultiLineString(lines) if len(lines) > 1 else lines[0]

    trajectories = gdf.groupby("code").apply(build_trajectory)

    trajectory_gdf = gpd.GeoDataFrame(
        {"geometry": trajectories}, crs=gdf.crs
    ).reset_index()

    gdf_stat = build_gdf_last_pointages()
    gdf_stat = gdf_stat.drop(columns="geometry")
    gdf_joint = trajectory_gdf.merge(gdf_stat, on="code", how="left")

    return gdf_joint


def export_to_file(
    gdf: gpd.GeoDataFrame,
    filepath: Path,
    driver: str = "GeoJSON",
    layer_name: str = None,
) -> None:
    """Exporte un GeoDataFrame dans un fichier au format spécifié.

    Args:
        gdf (gpd.GeoDataFrame): Le GeoDataFrame à exporter.
        filepath (Path): Le chemin du fichier de sortie.
        driver (str, optional): Le format de sortie, par exemple "GeoJSON" ou "GPKG". Par défaut "GeoJSON".
        layer_name (str, optional): Le nom de la couche, requis pour certains formats comme "GPKG".
                                    Ignoré pour les formats ne supportant pas de couches (ex : GeoJSON).
    """
    try:
        # Gérer le paramètre layer_name si nécessaire pour certains formats
        if driver == "GPKG" and layer_name:
            gdf.to_file(filepath, layer=layer_name, driver=driver)
        else:
            gdf.to_file(filepath, driver=driver)

        logging.info(f"Exportation réussie vers {filepath} avec le driver '{driver}'.")
    except Exception as e:
        logging.error(f"Erreur lors de l'exportation : {e}")


def build_gdf_last_pointages():
    last_update = get_last_update()
    date = get_current_date()
    url = build_url(date, last_update)
    file = f"./.data/data_{date}_{last_update}.xlsx"
    download_file(url, file)
    gdf = create_geom(Path(file), date)
    return gdf
