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
        df_pangan = pd.read_excel(excel_path, sheet_name="hasil_clust_best")
    except FileNotFoundError:
        return JSONResponse(content={"error": "File Excel tidak ditemukan"}, status_code=404)

    df_pangan = df_pangan[
        (df_pangan["Tahun"] == tahun) &
        (df_pangan["kinerja"].str.lower() == "produksi") &
        (df_pangan["jenis"].str.lower() == "tanaman pangan")
    ].copy()

    df_pangan["__key_kec__"] = df_pangan["Kecamatan"].str.strip().str.lower()
    pangan_index = df_pangan.set_index("__key_kec__")

    try:
        df_centroid = pd.read_excel(excel_path, sheet_name="Centroid_best", engine="openpyxl")
    except Exception:
        df_centroid = pd.DataFrame()

    df_centroid = df_centroid[
        (df_centroid["Tahun"] == tahun) &
        (df_centroid["kinerja"].str.lower() == "produksi") &
        (df_centroid["jenis"].str.lower() == "tanaman pangan")
    ].copy()

    centroid_cols = [
        "centroid__jagung",
        "centroid__kacang tanah",
        "centroid__kedelai",
        "centroid__ketela pohon",
        "centroid__ketela rambat",
        "centroid__padi ladang",
        "centroid__padi sawah",
    ]

    if "cluster" not in df_centroid.columns:
        return JSONResponse(content={"error": "Kolom 'cluster' tidak ada di Centroid_best"}, status_code=400)
    df_centroid["cluster"] = pd.to_numeric(df_centroid["cluster"], errors="coerce").astype("Int64")

    agg = df_centroid.groupby("cluster")[centroid_cols].mean()
    cluster_to_dominant = {}
    for cluster_val, row in agg.iterrows():
        top_col = row[centroid_cols].idxmax()
        cluster_to_dominant[int(cluster_val)] = top_col

    for feature in geojson_data["features"]:
        props = feature.get("properties", {})
        nama_kec_key = props.get("nm_kecamatan", "").strip().lower()
        if nama_kec_key in pangan_index.index:
            row = pangan_index.loc[nama_kec_key].to_dict()
            for col, val in row.items():
                if col != "__key_kec__":
                    props[col] = val
        label_val = None
        if "label" in props and props["label"] is not None:
            try:
                label_val = int(props["label"])
            except Exception:
                pass
        if label_val is None and "cluster" in props and props["cluster"] is not None:
            try:
                label_val = int(props["cluster"])
            except Exception:
                pass
        if label_val is not None and label_val in cluster_to_dominant:
            dom_col = cluster_to_dominant[label_val]
            props["cluster"] = label_val
            props["komoditas_dominan"] = dom_col.replace("centroid__", "").strip()
        else:
            props["komoditas_dominan"] = "unknown"
        keep_fields = [
            "nm_kecamatan",
            "Tahun",
            "Kecamatan",
            "kinerja",
            "jenis",
            "metode",
            "label",
            "cluster",
            "komoditas_dominan"
        ]
        feature["properties"] = {k: props[k] for k in keep_fields if k in props}

    return JSONResponse(content=geojson_data)

@router.get("/wide_prod/{tahun}")
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
        df_pangan = pd.read_excel(excel_path, sheet_name="hasil_clust_best")
    except FileNotFoundError:
        return JSONResponse(content={"error": "File Excel tidak ditemukan"}, status_code=404)

    df_pangan["jenis"] = df_pangan["jenis"].str.strip().str.lower()
    df_pangan = df_pangan[
        (df_pangan["Tahun"] == tahun) &
        (df_pangan["kinerja"].str.lower() == "luas lahan panen") &
        (df_pangan["jenis"].isin(["tanaman pangan", "hortikultura"])) &
        (df_pangan["metode"].str.lower() != "k-means")
    ].copy()
    df_pangan["__key_kec__"] = df_pangan["Kecamatan"].str.strip().str.lower()

    try:
        df_centroid = pd.read_excel(excel_path, sheet_name="Centroid_best", engine="openpyxl")
    except Exception:
        df_centroid = pd.DataFrame()

    df_centroid["jenis"] = df_centroid["jenis"].str.strip().str.lower()
    df_centroid = df_centroid[
        (df_centroid["Tahun"] == tahun) &
        (df_centroid["kinerja"].str.lower() == "luas lahan panen") &
        (df_centroid["jenis"].isin(["tanaman pangan", "hortikultura"])) &
        (df_centroid["metode"].str.lower() != "k-means")
    ].copy()

    centroid_cols = [
        "centroid__bawang merah",
        "centroid__cabai besar",
        "centroid__cabai rawit",
        "centroid__kacang panjang",
        "centroid__ketimun",
        "centroid__kubis",
        "centroid__tomat",
        "centroid__jagung",
        "centroid__kacang tanah",
        "centroid__kedelai",
        "centroid__ketela pohon",
        "centroid__ketela rambat",
        "centroid__padi ladang",
        "centroid__padi sawah",
    ]

    if "cluster" not in df_centroid.columns:
        return JSONResponse(content={"error": "Kolom 'cluster' tidak ada di Centroid_best"}, status_code=400)

    df_centroid["cluster"] = pd.to_numeric(df_centroid["cluster"], errors="coerce").astype("Int64")

    agg = df_centroid.groupby("cluster")[centroid_cols].mean()
    cluster_to_dominant = {}
    for cluster_val, row in agg.iterrows():
        top_col = row[centroid_cols].idxmax()
        cluster_to_dominant[int(cluster_val)] = top_col

    for feature in geojson_data["features"]:
        props = feature.get("properties", {})
        nama_kec_key = props.get("nm_kecamatan", "").strip().lower()

        match = df_pangan[df_pangan["__key_kec__"] == nama_kec_key]
        if not match.empty:
            row = match.iloc[0].to_dict()
            for col, val in row.items():
                if col != "__key_kec__":
                    props[col] = val

        label_val = None
        if "label" in props and props["label"] is not None:
            try:
                label_val = int(props["label"])
            except Exception:
                pass
        if label_val is None and "cluster" in props and props["cluster"] is not None:
            try:
                label_val = int(props["cluster"])
            except Exception:
                pass

        if label_val is not None and label_val in cluster_to_dominant:
            dom_col = cluster_to_dominant[label_val]
            props["cluster"] = label_val
            props["komoditas_dominan"] = dom_col.replace("centroid__", "").strip()
        else:
            props["komoditas_dominan"] = "unknown"

        keep_fields = [
            "nm_kecamatan",
            "Tahun",
            "Kecamatan",
            "kinerja",
            "jenis",
            "metode",
            "label",
            "cluster",
            "komoditas_dominan"
        ]
        feature["properties"] = {k: props[k] for k in keep_fields if k in props}

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

