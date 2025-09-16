from fastapi import APIRouter, HTTPException
import pandas as pd
import os

router = APIRouter()

# API sebelah kiri
@router.get("/info/{tahun}")
def get_chart_data(tahun: int):
    base_dir = os.path.dirname(os.path.abspath(__file__))  
    
    # ==== File sumber pertama ====
    file_path_pangan = os.path.join(base_dir, "../../dataset/All/harvest_production_pangan.xlsx")
    df_pangan = pd.read_excel(file_path_pangan, sheet_name="harvest_area")
    
    # ==== File sumber kedua ====
    file_path_harvest = os.path.join(base_dir, "../../dataset/All/harvest.xlsx")
    df_harvest = pd.read_excel(file_path_harvest, sheet_name="harvest_area")

    # Pastikan kolom angka jadi numerik untuk keduanya
    for col in df_pangan.columns[3:]:
        df_pangan[col] = pd.to_numeric(df_pangan[col], errors="coerce")
    for col in df_harvest.columns[3:]:
        df_harvest[col] = pd.to_numeric(df_harvest[col], errors="coerce")

    tanaman_pangan = ["rice", "corn", "cassava", "swpot", "peanuts", "soybeans"]

    # Filter berdasarkan tahun
    if "Year" not in df_pangan.columns or "Year" not in df_harvest.columns:
        return {"error": "Kolom 'Year' tidak ditemukan di salah satu file Excel."}

    df_pangan = df_pangan[df_pangan["Year"] == tahun]
    df_harvest = df_harvest[df_harvest["Year"] == tahun]

    if df_pangan.empty and df_harvest.empty:
        return {"error": f"Tidak ada data untuk tahun {tahun}"}

    def process_df(df, category_list):
        regional_sum = df.groupby("region")[category_list].sum()
        total_all = regional_sum.sum(axis=1).sum()
        regional_percent = ((regional_sum.sum(axis=1) / total_all) * 100).round(0).astype(int)
        total_north_south = regional_sum.loc[["north", "south"]].sum().sum()

        return {
            "year": tahun,
            "by_region": regional_sum.to_dict(orient="index"),
            "percent": regional_percent.to_dict(),
            "produksi_panen": (total_north_south).round(0),
        }

    summary = {
        "harvest_production_pangan": process_df(df_pangan, tanaman_pangan),
        "harvest": process_df(df_harvest, tanaman_pangan)}

    return summary

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

# API sebelah kanan
@router.get("/harvest/{komoditas}")
def get_harvest_data(komoditas: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))  
    file_path_harvest = os.path.join(base_dir, "../../dataset/All/harvest.xlsx")
    df_harvest = pd.read_excel(file_path_harvest, sheet_name="harvest_area")

    komoditas_mapping = {
        "rice": "rice",
        "corn": "corn",
        "cassava": "cassava",
        "swpot": "swpot",
        "peanuts": "peanuts",
        "soybeans": "soybeans",
        "g_beans": "g_beans",
        "r_onions": "r_onions",
        "l_chilies": "l_chilies",
        "cayenne": "cayenne",
        "cabbage": "cabbage",
        "tomatoes": "tomatoes",
        "l_beans": "l_beans",
        "cucumber": "cucumber"
    }

    if komoditas not in komoditas_mapping:
        raise HTTPException(status_code=400, detail="Komoditas tidak valid")

    # Ambil nama kolom sesuai mapping
    kolom_excel = komoditas_mapping[komoditas]

    # Agregasi per tahun
    grouped = df_harvest.groupby("Year")[kolom_excel].sum().reset_index().round(0)

    # Konversi ke JSON
    result = grouped.to_dict(orient="records")
    return result

# API sebelah kanan
@router.get("/horticulture/{tahun}")
def get_chart_data(tahun: int):

    base_dir = os.path.dirname(os.path.abspath(__file__))  
    file_path_harvest = os.path.join(base_dir, "../../dataset/All/harvest.xlsx")
    df_harvest = pd.read_excel(file_path_harvest, sheet_name="harvest_area")

    for col in df_harvest.columns[3:]:
        df_harvest[col] = pd.to_numeric(df_harvest[col], errors="coerce")

    tanaman_holtikultura = ["g_beans","r_onions","l_chilies","cayenne","cabbage","tomatoes","l_beans","cucumber"]

    if "Year" not in df_harvest.columns:
        return {"error": "Kolom 'Year' tidak ditemukan di salah satu file Excel."}

    df_harvest = df_harvest[df_harvest["Year"] == tahun]

    if df_harvest.empty:
        return {"error": f"Tidak ada data untuk tahun {tahun}"}

    def process_df(df, category_list):
        regional_sum = df.groupby("region")[category_list].sum()
        total_all = regional_sum.sum(axis=1).sum()
        regional_percent = ((regional_sum.sum(axis=1) / total_all) * 100).round(0).astype(int)
        total_north_south = regional_sum.loc[["north", "south"]].sum().sum()

        return {
            "year": tahun,
            "by_region": regional_sum.to_dict(orient="index"),
            "percent": regional_percent.to_dict(),
            "produksi_panen": (total_north_south).round(0),
        }

    summary = {
        "harvest": process_df(df_harvest, tanaman_holtikultura)}

    return summary

@router.get("/scatter/{tahun}/{x}/{y}")
def get_scatter_data(tahun: int, x: str, y: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))  
    file_path_harvest = os.path.join(base_dir, "../../dataset/All/harvest.xlsx")
    df = pd.read_excel(file_path_harvest, sheet_name="harvest_area")
    data_tahun = df[df["Year"] == tahun]

    if x not in data_tahun.columns or y not in data_tahun.columns:
        return {"error": f"Kolom {x} atau {y} tidak ditemukan"}

    region_map = {
        "south": "Selatan",
        "north": "Utara"
    }

    result = []
    for _, row in data_tahun.iterrows():
        result.append({
            "kecamatan": row["Kecamatan"],
            "wilayah": region_map.get(row["region"], row["region"]),
            "x": row[x],
            "y": row[y]
        })

    return result

@router.get("/spider/{tahun}/{kecamatan}/{komoditas}")
def get_spider_data(tahun: int, kecamatan: str, komoditas: str):
    import os
    import pandas as pd

    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path_harvest = os.path.join(base_dir, "../../dataset/All/harvest_production_pangan.xlsx")
    df = pd.read_excel(file_path_harvest, sheet_name="harvest_area")
    komoditas = komoditas.lower()

    # Filter berdasarkan tahun
    data = df[df["Year"] == tahun]

    if komoditas not in data.columns:
        return {"error": f"Komoditas '{komoditas}' tidak ditemukan"}

    # Filter kecamatan
    if kecamatan.lower() != "all":
        # Pisahkan string kecamatan menjadi list
        kecamatan_list = [k.strip().lower() for k in kecamatan.split(",")]
        data = data[data["District"].str.lower().isin(kecamatan_list)]

    # Ambil semua kecamatan + nilai komoditas
    labels = data["District"].tolist()
    values = data[komoditas].tolist()

    return {
        "tahun": tahun,
        "komoditas": komoditas,
        "kecamatan": kecamatan,
        "labels": labels,
        "values": values
    }

