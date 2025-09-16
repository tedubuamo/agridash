from fastapi import APIRouter, HTTPException
import pandas as pd
import json
import os

router = APIRouter()

# API sebelah kiri
@router.get("/comparison/{tahun}")
def get_chart_data(tahun: int):
    base_dir = os.path.dirname(os.path.abspath(__file__))  
    
    # ==== File sumber pertama ====
    file_path_pangan = os.path.join(base_dir, "../../dataset/All/harvest_production_pangan.xlsx")
    df_pangan = pd.read_excel(file_path_pangan, sheet_name="harvest_area")
    
    # ==== File sumber kedua ====
    file_path_harvest = os.path.join(base_dir, "../../dataset/All/harvest.xlsx")
    df_harvest = pd.read_excel(file_path_harvest, sheet_name="harvest_area")

    # Filter berdasarkan tahun
    luas_df = df_pangan[df_pangan["Year"] == tahun]
    prod_df = df_harvest[df_harvest["Year"] == tahun]

    # Hitung total luas panen per kecamatan
    luas_df["total_luas"] = luas_df[["rice", "corn", "cassava", "swpot", "peanuts", "soybeans"]].sum(axis=1)

    # Hitung total produksi per kecamatan
    prod_df["total_produksi"] = prod_df[["rice", "corn", "cassava", "swpot", "peanuts", "soybeans"]].sum(axis=1)

    # Gabungkan data berdasarkan kecamatan/district
    merged = pd.merge(
        luas_df[["District", "region", "total_luas"]],
        prod_df[["Kecamatan", "total_produksi"]],
        left_on="District",
        right_on="Kecamatan",
        how="inner"
    )

    # Format output untuk chart
    result = []
    for _, row in merged.iterrows():
        result.append({
            "kecamatan": row["Kecamatan"],
            "region": row["region"],
            "luas_panen": round(row["total_luas"], 0),
            "produksi": round(row["total_produksi"], 0)
        })

    return result

# API Maps seblelah kiri (SEK BELOM)
@router.get("/maps/{tahun}/{daerah}/{komoditas}")
def get_maps_data(tahun: int, daerah: str, komoditas: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))  
    file_path_pangan = os.path.join(base_dir, "../../dataset/All/harvest_production_pangan.xlsx")
    file_path_geojson = os.path.join(base_dir, "blitar_kecamatan.geojson")

    df = pd.read_excel(file_path_pangan, sheet_name="harvest_area")
    df = df[df["Year"] == tahun]

    # Filter daerah
    if daerah.lower() != "all":
        daerah_list = [d.strip().lower() for d in daerah.split(",")]
        df = df[df["region"].str.lower().isin(daerah_list)]

    # Filter komoditas
    komoditas_list = ["rice", "corn", "cassava", "swpot", "peanuts", "soybeans"]
    if komoditas.lower() != "all":
        requested = [k.strip().lower() for k in komoditas.split(",")]
        valid_cols = [col for col in requested if col in komoditas_list]
        if not valid_cols:
            raise HTTPException(status_code=400, detail="Komoditas tidak valid")
        df["total"] = df[valid_cols].sum(axis=1).round(0)
    else:
        df["total"] = df[komoditas_list].sum(axis=1).round(0)

    df["District"] = df["District"].str.strip()
    agg_cols = komoditas_list + ["total", "region"]
    result = df.groupby("District")[agg_cols].first().reset_index()

    with open(file_path_geojson, "r", encoding="utf-8") as f:
        geojson = json.load(f)

    for feature in geojson["features"]:
        district_name = feature["properties"]["nm_kecamatan"].strip()
        row = result[result["District"] == district_name]

        if not row.empty:
            props = feature["properties"]
            props["region"] = row.iloc[0]["region"]
            props["total"] = int(row.iloc[0]["total"])
            for kom in komoditas_list:
                props[kom] = float(row.iloc[0][kom])
        else:
            props = feature["properties"]
            props["region"] = None
            props["total"] = 0
            for kom in komoditas_list:
                props[kom] = 0

    return geojson

# API sebelah kanan
@router.get("/sort/{tahun}")
def sort_production_data(tahun:int):
    base_dir = os.path.dirname(os.path.abspath(__file__))  
    file_path_pangan = os.path.join(base_dir, "../../dataset/All/harvest_production_pangan.xlsx")
    df = pd.read_excel(file_path_pangan, sheet_name="harvest_area")
    
    df_year = df[df["Year"] == tahun]
    df_year["total"] = df_year[["rice", "corn", "cassava", "swpot", "peanuts", "soybeans"]].sum(axis=1).round(0)

    df_sorted = df_year.sort_values(by="total", ascending=False)

    highest = df_sorted.head(5)[["District", "total"]].to_dict(orient="records")
    lowest = df_sorted.tail(5)[["District", "total"]].to_dict(orient="records")

    return {"highest": highest, "lowest": lowest} 
    
@router.get("/pieMaps/{tahun}/{daerah}/{komoditas}")
def pie_data(tahun:int, daerah: str, komoditas: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))  
    file_path_pangan = os.path.join(base_dir, "../../dataset/All/harvest_production_pangan.xlsx")
    df = pd.read_excel(file_path_pangan, sheet_name="harvest_area")
    df.columns = df.columns.str.strip().str.lower()
    filtered = df[(df["year"] == tahun) & (df["district"].str.lower() == daerah.lower())]

    if filtered.empty:
        return {"error": f"Tidak ada data untuk {daerah} di tahun {tahun}"}

    komoditas_list = ["rice", "corn", "cassava", "swpot", "peanuts", "soybeans"]

    if komoditas.lower() == "all":
        data = filtered[komoditas_list].to_dict(orient="records")[0]
        return {"year": tahun, "district": daerah, "data": data}
    
    if komoditas.lower() in komoditas_list:
        value = filtered.iloc[0][komoditas.lower()]
        return {"year": tahun, "district": daerah, "komoditas": komoditas, "value": value}

    return {"error": f"Komoditas {komoditas} tidak ditemukan"}
