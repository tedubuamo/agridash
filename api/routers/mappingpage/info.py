from fastapi import APIRouter
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
import os
import json

router = APIRouter()

@router.get("/maps_prod/{tahun}")
def get_info(tahun: int):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    geojson_path = os.path.join(base_dir, "blitar_kecamatan.geojson")
    excel_path = os.path.join(base_dir, "hasil_cluster_final.xlsx") 

    try:
        with open(geojson_path, "r", encoding="utf-8") as f:
            geojson_data = json.load(f)
    except FileNotFoundError:
        return JSONResponse(content={"error": "File GeoJSON tidak ditemukan"}, status_code=404)
    except json.JSONDecodeError:
        return JSONResponse(content={"error": "Format GeoJSON tidak valid"}, status_code=400)

    try:
        df = pd.read_excel(excel_path, sheet_name="hasil_clust_best")
    except FileNotFoundError:
        return JSONResponse(content={"error": "File Excel tidak ditemukan"}, status_code=404)

    df_filtered = df[
        (df["Tahun"] == tahun) &
        (df["kinerja"].str.lower() == "produksi") &
        (df["jenis"].str.lower() == "tanaman pangan")
    ].copy()

    if "k" in df_filtered.columns:
        df_filtered = df_filtered.drop(columns=["k"])

    for feature in geojson_data["features"]:
        nama_kec = feature["properties"].get("nm_kecamatan", "").strip().lower()
        match = df_filtered[df_filtered["Kecamatan"].str.strip().str.lower() == nama_kec]

        if not match.empty:
            row = match.iloc[0].to_dict()
            for col, val in row.items():
                feature["properties"][col] = val

    return JSONResponse(content=geojson_data)

@router.get("/wide_prod/{tahun}")
def get_info(tahun: int):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    geojson_path = os.path.join(base_dir, "blitar_kecamatan.geojson")

    try:
        with open(geojson_path, "r", encoding="utf-8") as f:
            geojson_data = json.load(f)
    except FileNotFoundError:
        return JSONResponse(content={"error": "File GeoJSON tidak ditemukan"}, status_code=404)
    except json.JSONDecodeError:
        return JSONResponse(content={"error": "Format GeoJSON tidak valid"}, status_code=400)
    
    return JSONResponse(content=geojson_data)

@router.get("/centroid_prod/{tahun}")
def get_info(tahun: int):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(base_dir, "hasil_cluster_final.xlsx")

    try:
        df = pd.read_excel(excel_path, sheet_name="Centroid_best", engine="openpyxl")
    except FileNotFoundError:
        return JSONResponse(content={"error": "File Excel tidak ditemukan"}, status_code=404)

    df_filtered = df[
        (df["Tahun"] == tahun) &
        (df["kinerja"].str.lower() == "produksi") &
        (df["jenis"].str.lower() == "tanaman pangan")
    ].copy()

    df_filtered = df_filtered.drop(columns=["n_members","centroid__bawang merah","centroid__cabai besar","centroid__cabai rawit","centroid__kacang panjang","centroid__ketimun","centroid__kubis",
                                            "centroid__tomat","centroid__bayam","centroid__cabai","centroid__sawi","centroid__ubi jalar"], errors="ignore")
    df_filtered = df_filtered.replace([np.inf, -np.inf,np.nan], 0)
    df_filtered = df_filtered.where(pd.notnull(df_filtered), None).round(0)
    result = df_filtered.to_dict(orient="records")

    return JSONResponse(content=result)

@router.get("/centroid_wide/{tahun}")
def get_info(tahun: int):
    import numpy as np
    base_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(base_dir, "hasil_cluster_final.xlsx")

    try:
        df = pd.read_excel(excel_path, sheet_name="Centroid_best", engine="openpyxl")
    except FileNotFoundError:
        return JSONResponse(content={"error": "File Excel tidak ditemukan"}, status_code=404)

    # Filter data sesuai tahun dan jenis yang relevan
    df_filtered = df[
        (df["Tahun"] == tahun) &
        (df["kinerja"].str.lower() == "luas lahan panen") &
        (df["jenis"].str.lower().isin(["tanaman pangan", "hortikultura"])) &
        (df["metode"].str.lower() != "k-means")
    ].copy()

    # Drop kolom yang tidak relevan
    df_filtered = df_filtered.drop(columns=[
        "n_members", "centroid__bayam", "centroid__cabai", "centroid__sawi", "centroid__ubi jalar"
    ], errors="ignore")

    # Bersihkan nilai ekstrem dan kosong
    df_filtered = df_filtered.replace([np.inf, -np.inf, np.nan], 0)

    # Gabungkan berdasarkan cluster
    numeric_cols = [col for col in df_filtered.columns if col.startswith("centroid__")]
    grouped = df_filtered.groupby("cluster")[numeric_cols].sum().reset_index()

    # Tambahkan kembali kolom Tahun, kinerja, jenis, metode (ambil dari baris pertama per cluster)
    meta_cols = ["Tahun", "kinerja", "jenis", "metode"]
    meta_info = df_filtered.groupby("cluster")[meta_cols].first().reset_index()

    # Gabungkan metadata dan hasil agregasi
    merged = pd.merge(meta_info, grouped, on="cluster")

    # Final cleaning
    merged = merged.round(0)
    result = merged.to_dict(orient="records")

    return JSONResponse(content=result)

