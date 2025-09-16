from fastapi import APIRouter
from fastapi.responses import JSONResponse
import pandas as pd
import json
import os

router = APIRouter()

@router.get("/maps/{tahun}")
def map_data(tahun: int):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(base_dir, "../../dataset/Ketahanan Pangan/hasil_ketahanan.xlsx")
    geojson_path = os.path.join(base_dir, "jawa-timur-kabkota.geojson") 

    if not os.path.exists(excel_path):
        return {"error": "File Excel tidak ditemukan."}
    if not os.path.exists(geojson_path):
        return {"error": "File GeoJSON Jawa Timur tidak ditemukan."}

    try:
        # --- 1. Baca data Excel ---
        df = pd.read_excel(excel_path)
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
        df = df[df["year"] == tahun][["regency", "fsi_class"]]

        # Normalisasi nama untuk join
        df["regency_norm"] = df["regency"].str.strip().str.upper()

        # --- 2. Baca GeoJSON Jawa Timur ---
        with open(geojson_path, "r", encoding="utf-8") as f:
            geo = json.load(f)

        # --- 3. Join data FSI ke GeoJSON ---
        for feat in geo["features"]:
            reg_name = feat["properties"].get("name", "").strip().upper()
            match = df[df["regency_norm"] == reg_name]
            if not match.empty:
                feat["properties"]["fsi_class"] = int(match.iloc[0]["fsi_class"])
            else:
                feat["properties"]["fsi_class"] = None  # jika tidak ada data

        # --- 4. Return hasil ---
        return {
            "tahun": tahun,
            "jumlah": len(geo["features"]),
            "geojson": geo
        }

    except Exception as e:
        return {"error": f"Gagal memproses data: {str(e)}"}

@router.get("/line")
def line_data():
    # Tentukan path ke file Excel
    base_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(base_dir, "../../dataset/Ketahanan Pangan/hasil_ketahanan.xlsx")

    # Baca data Excel
    df = pd.read_excel(excel_path)

    # Filter hanya data untuk Blitar
    blitar_df = df[df["Regency"].str.lower() == "blitar"]

    # Siapkan response untuk Chart.js
    response = {
        "labels": blitar_df["Year"].tolist(),
        "data": blitar_df["fsi"].tolist()
    }

    return JSONResponse(content=response)

@router.get("/bar/{tahun}")
def bar_data(tahun: int):
    # Tentukan path ke file Excel
    base_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(base_dir, "../../dataset/Ketahanan Pangan/hasil_ketahanan.xlsx")

    # Baca data Excel
    df = pd.read_excel(excel_path)

    # Pastikan kolom 'Year' bertipe int agar bisa dibandingkan
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

    # Filter semua kabupaten/kota untuk tahun yang diminta
    df_filtered = df[df["Year"] == tahun]

    # Jika tidak ada data, kembalikan pesan kosong
    if df_filtered.empty:
        return JSONResponse(content={"labels": [], "data": []})

    # Siapkan response untuk Chart.js
    response = {
        "labels": df_filtered["Regency"].tolist(),
        "data": df_filtered["fsi"].tolist()
    }

    return JSONResponse(content=response)

@router.get("/boxplot")
def boxplot_data():
    # Path file Excel
    base_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(base_dir, "../../dataset/Ketahanan Pangan/hasil_ketahanan.xlsx")

    # Baca data Excel
    df = pd.read_excel(excel_path)

    # Pastikan kolom Year bertipe int
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

    # Ambil hanya kolom yang diperlukan
    df = df[["Year", "fsi"]]

    # Kelompokkan berdasarkan tahun
    grouped = df.groupby("Year")["fsi"].apply(list).reset_index()

    response = []
    for _, row in grouped.iterrows():
        response.append({
            "year": int(row["Year"]),
            "fsi_values": row["fsi"]  # list nilai FSI untuk tahun tersebut
        })

    return JSONResponse(content=response)