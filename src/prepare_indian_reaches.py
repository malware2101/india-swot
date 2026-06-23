from pathlib import Path

import geopandas as gpd
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
FIGURES_DIR = ROOT / "figures"

def find_asia_reach_files():

    as_folder = (
        DATA_DIR
        / "sword_raw"
        / "SWORD_v16_shp (1)"
        / "shp"
        / "AS"
    )

    reach_files = sorted(
        as_folder.glob("as_sword_reaches*.shp")
    )

    print(f"Found {len(reach_files)} reach shapefiles")

    return reach_files


def get_indian_basin_files(reach_files):

    india_basins = [
        "hb43",
        "hb44",
        "hb45",
        "hb46",
        "hb48",
        "hb49",
    ]

    selected = []

    for f in reach_files:
        if any(basin in f.name for basin in india_basins):
            selected.append(f)

    print(f"India basin files found: {len(selected)}")

    return selected


def merge_india_basins(india_files):
    """Read and merge multiple India basin shapefiles into one GeoDataFrame."""
    if not india_files:
        print("No India files to merge")
        return None

    gdfs = []
    for f in india_files:
        print("Reading:", f.name)
        gdfs.append(gpd.read_file(f))

    india_reaches = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))

    print("\nTotal reaches:", len(india_reaches))

    return india_reaches

def inspect_first_reach_file(reach_files):

    if not reach_files:
        print("No reach files provided")
        return

    gdf = gpd.read_file(reach_files[0])

    print("\nColumns:")
    print(gdf.columns)

    print("\nNumber of reaches:")
    print(len(gdf))

def load_india_boundary():

    world = gpd.read_file(
        ROOT / "data" / "countries" / "ne_110m_admin_0_countries" / "ne_110m_admin_0_countries.shp"
    )

    india = world[
        world["ADMIN"] == "India"
    ]

    print(
        "India boundary loaded:",
        len(india)
    )

    return india

def clip_to_india(india_reaches, india):

    india_reaches_clip = gpd.clip(
        india_reaches,
        india
    )

    print(
        "\nClipped reaches:",
        len(india_reaches_clip)
    )

    return india_reaches_clip

def save_india_reaches(india_reaches_clip):

    output_file = (
        ROOT
        / "data"
        / "processed"
        / "india_reaches.shp"
    )

    india_reaches_clip.to_file(
        output_file
    )

    print(
        f"Saved to: {output_file}"
    )

   

if __name__ == "__main__":

    reach_files = find_asia_reach_files()
    india_files = get_indian_basin_files(reach_files)
    if india_files:
        print("\nFirst 5 India basin files:")
        for f in india_files[:5]:
            print(f.name)

        inspect_first_reach_file(india_files)
    else:
        print("\nNo India basin files found. Showing first 5 Asia files:")
        for f in reach_files[:5]:
            print(f.name)

        inspect_first_reach_file(reach_files)

    if india_files:
        india_reaches = merge_india_basins(india_files)
    else:
        india_reaches = None

    india= load_india_boundary()
    india_reaches_clip = clip_to_india(
    india_reaches,
    india
) 
    save_india_reaches(india_reaches_clip)   
