import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
from pathlib import Path
from datetime import datetime
import re


def dms_to_decimal(degrees, minutes, seconds, direction):
    "Convertir des coordonnées DMS en degrés décimaux"
    degrees = degrees.strip()
    minutes = minutes.strip().replace("'", "")
    seconds = seconds.strip().replace(
        "'",
        "",
    )

    decimal = float(degrees) + float(minutes) / 60 + float(seconds) / (60 * 60)

    if direction in ["S", "W"]:
        decimal = -decimal
    return decimal


def parse_hour(hour_str, date_obj):
    if pd.isnull(hour_str):
        return None

    cleaned_str = re.search(r"\b\d{2}:\d{2}\b", hour_str.replace(" FR", ""))
    if cleaned_str:
        return datetime.combine(
            date_obj, datetime.strptime(cleaned_str.group(), "%H:%M").time()
        )
    return None


def read_xlsx(file: Path, param_date: str):
    """Charger le excel dans un dataframe sans en-têtes et réorganiser les colonnes"""
    # Définir les noms de colonnes dans l"ordre souhaité
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
    df = df.apply(
        lambda col: col.map(
            lambda x: x.replace("\r\n", " - ") if isinstance(x, str) else x
        )
    )

    date_obj = datetime.strptime(param_date, "%Y%m%d")
    df["timestamp"] = df["heure"].apply(lambda x: parse_hour(x, date_obj))
    df[["skipper", "bateau"]] = df["nom"].str.split(pat=" - ", n=1, expand=True)

    return df


def parse_coordinates(coord):
    direction = coord[-1]  # Dernier caractère (N/S/E/W)
    parts = coord[:-1].split(
        "°"
    )  # On retire la direction et on sépare les degrés des minutes
    degrees = parts[0]
    minutes, seconds = parts[1].split(".")
    return degrees, minutes, seconds, direction


def build_gpkg(file: Path, name: str, date: str, output_dir: Path = Path("./")):
    gdf = create_geom(file, date)
    output_path = output_dir / f"{name}.gpkg"

    gdf.to_file(output_path, driver="GPKG")


def create_geom(file, date):
    """Créer un geodataframe avec la colonne de géometrie à partir du read excel
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


def aggreger_geodataframes(liste_geodfs: list):
    """
    Agrège une liste de GeoDataFrames en un seul GeoDataFrame.
    """

    if not liste_geodfs:
        raise ValueError("La liste de GeoDataFrames est vide.")

    geodf_agrege = gpd.GeoDataFrame(pd.concat(liste_geodfs, ignore_index=True))

    return geodf_agrege

def create_trejectoire(gdf):
    gdf = gdf.sort_values(by=['code', 'timestamp'])

    trajectories = gdf.groupby('code').apply(lambda x: LineString(x.geometry.tolist()))

    trajectory_gdf = gpd.GeoDataFrame(trajectories, columns=['geometry'], crs=gdf.crs).reset_index()

    return trajectory_gdf

def export_to_gpkg(gdf, filepath, layer_name="layer"):
    """
    Exporte un GeoDataFrame dans un fichier GeoPackage (.gpkg).
    
    Paramètres :
    - gdf (GeoDataFrame) : le GeoDataFrame à exporter.
    - filepath (str) : le chemin complet du fichier GeoPackage de sortie (incluant l'extension .gpkg).
    - layer_name (str) : nom de la couche dans le GeoPackage (par défaut 'layer').

    """
    try:
        # Exporter vers un fichier GeoPackage
        gdf.to_file(filepath, layer=layer_name, driver="GPKG")
        print(f"Exportation réussie vers {filepath} dans la couche '{layer_name}'.")
    except Exception as e:
        print(f"Erreur lors de l'exportation : {e}")