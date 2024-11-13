import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path


def dms_to_decimal(degrees, minutes, seconds, direction):
    "Convertir des coordonnées DMS en degrés décimaux"
    degrees = degrees.strip()
    minutes = minutes.strip().replace("'", "")  
    seconds = seconds.strip().replace("'", "")  
    
    decimal = float(degrees) + float(minutes)/60 + float(seconds)/(60*60)
    
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal

def read_xlsx(file: Path):
    """Charger le excel dans un dataframe sans en-têtes et réorganiser les colonnes"""
    # Définir les noms de colonnes dans l'ordre souhaité
    columns = [
        'rang', 'code', 'bateau', 'heure', 'latitude', 'longitude',
        '30m_cap', '30m_vitesse', '30m_vmg', '30m_distance',
        'last_rank_cap', 'last_rank_vitesse', 'last_rank_vmg', 'last_rank_distance',
        '24h_cap', '24h_vitesse', '24h_vmg', '24h_distance', 'dtf', 'dtl'
    ]
    
    df = pd.read_excel(file, usecols="B:U", skiprows=5, nrows=40, header=None, names=columns, engine="calamine")
    df = df.apply(lambda col: col.map(lambda x: x.replace('\r\n', ' - ') if isinstance(x, str) else x))

    return df



def parse_coordinates(coord):
    direction = coord[-1]  # Dernier caractère (N/S/E/W)
    parts = coord[:-1].split('°')  # On retire la direction et on sépare les degrés des minutes
    degrees = parts[0]
    minutes, seconds = parts[1].split('.')
    return degrees, minutes, seconds, direction


def build_gpkg(file: Path, name: str, output_dir: Path = Path("./")):
    df = read_xlsx(file)

    df['latitude_decimal'] = df['latitude'].apply(lambda x: dms_to_decimal(*parse_coordinates(x)))
    df['longitude_decimal'] = df['longitude'].apply(lambda x: dms_to_decimal(*parse_coordinates(x)))

    geometry = [Point(lon, lat) for lon, lat in zip(df['longitude_decimal'], df['latitude_decimal'])]

    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    output_path = output_dir / f"{name}.gpkg"
    
    gdf.to_file(output_path, driver="GPKG")
