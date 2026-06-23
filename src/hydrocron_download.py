from pathlib import Path
import geopandas as gpd
import requests
import io
import pandas as pd
import numpy as np
import earthaccess

earthaccess.login()

ROOT = Path(__file__).resolve().parents[1]
india_reaches = gpd.read_file(
    ROOT / "data" / "processed" / "india_reaches.shp"
)

print(india_reaches.columns)

print(
    india_reaches["river_name"]
    .dropna()
    .unique()[:200]
)
river_names = sorted(
    india_reaches["river_name"]
    .dropna()
    .unique()
)

print("Total rivers:", len(river_names))

for r in river_names:
    if "god" in r.lower():
        print(r)

godavari = india_reaches[
    india_reaches["river_name"] == "Godavari"
]

print("Godavari reaches:", len(godavari))

godavari = india_reaches[
    india_reaches["river_name"]
    .str.contains("Godavari", na=False)
]

print("Godavari system reaches:", len(godavari))

print(
    sorted(
        godavari["river_name"].unique()
    )
)

godavari_reaches = gpd.read_file(
    ROOT / "data" / "processed" / "godavari_reaches.shp"
)

reach_ids = godavari_reaches["reach_id"].unique()

print("Number of reach IDs:", len(reach_ids))

swot_vars = (
    "reach_id,time,wse,wse_u,wse_r_u,"
    "width,width_u,reach_q,reach_q_b,"
    "dark_frac,ice_clim_f,ice_dyn_f,"
    "xtrk_dist,obs_frac_n,xovr_cal_q,"
    "p_length,crid"
)
test_reach = str(reach_ids[5])


found_reaches = []
missing_reaches = []

for i, rid in enumerate(reach_ids, start=1):

    print(f"{i}/{len(reach_ids)}", end="\r")

    api_url = (
        "https://soto.podaac.earthdatacloud.nasa.gov/"
        "hydrocron/v1/timeseries"
        "?feature=Reach"
        f"&feature_id={rid}"
        "&output=csv"
        "&start_time=2024-10-01T00:00:00Z"
        "&end_time=2025-09-30T23:59:59Z"
        f"&fields={swot_vars}"
    )

    try:
        response = requests.get(api_url).json()

        if "error" in response:

            missing_reaches.append({
                "reach_id": rid,
                "error": response["error"]
            })

        elif response.get("status") == "200 OK":

            found_reaches.append({
                "reach_id": rid,
                "hits": response["hits"]
            })

    except Exception as e:

        missing_reaches.append({
            "reach_id": rid,
            "error": str(e)
        })

# Save successful reaches
pd.DataFrame(found_reaches).to_csv(
    ROOT / "data" / "hydrocron" / "godavari_reaches_with_data.csv",
    index=False
)

# Save failed reaches
pd.DataFrame(missing_reaches).to_csv(
    ROOT / "data" / "hydrocron" / "godavari_reaches_without_data.csv",
    index=False
)

print("\n=================================")
print("Total Godavari reaches:", len(reach_ids))
print("Reaches with observations:", len(found_reaches))
print("Reaches without observations:", len(missing_reaches))
print("=================================")

print("CSV files saved.")

print("Saved:")
print("  godavari_reaches_with_data.csv")
print("  godavari_reaches_without_data.csv")

 