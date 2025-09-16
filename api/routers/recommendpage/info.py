from fastapi import APIRouter, HTTPException
import pandas as pd
import os

router = APIRouter()

@router.get("/tanpang/{musim}")
def get_info(musim: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "../../dataset/Sistem Rekomendasi/new_data_with_predictions_tanpang.xlsx")

    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membaca file: {str(e)}")

    musim = musim.lower().capitalize()  
    df = df[df["season"] == musim]

    if df.empty:
        raise HTTPException(status_code=404, detail=f"Tidak ada data untuk musim '{musim}'")

    result = []
    for _, row in df.iterrows():
        result.append({
            "kec": row["subdistrict"],
            "jagung": round(row["Probability_Jagung"] * 100, 2),
            "ketela": round(row["Probability_Ketela Pohon"] * 100, 2),
            "padi": round(row["Probability_Padi"] * 100, 2)
        })

    return {"musim": musim, "data": result}

@router.get("/horti/{musim}")
def get_horti_data(musim: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "../../dataset/SIstem Rekomendasi/new_data_with_predictions_horti.xlsx")

    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membaca file: {str(e)}")

    musim = musim.lower().capitalize()
    df = df[df["season"] == musim]

    if df.empty:
        raise HTTPException(status_code=404, detail=f"Tidak ada data untuk musim '{musim}'")

    komoditas_map = {
        "Cabai Besar": ["Probability_Cabai Besar"],
        "Cabai Rawit": ["Probability_Cabai Rawit"],
        "Bawang Merah": ["Probability_Bawang Merah"],
        "Tomat": ["Probability_Tomat"],
        "Kubis": ["Probability_Kubis"],
        "Kacang Panjang": ["Probability_Kacang Panjang"],
        "Melon": ["Probability_Melon"],
        "Semangka": ["Probability_Semangka"],
        "Kentang": ["Probability_Kentang"]
    }

    result = {kom: [] for kom in komoditas_map}
    labels = []

    for _, row in df.iterrows():
        labels.append(row["subdistrict"])
        for kom, cols in komoditas_map.items():
            total = sum([row[col] for col in cols if col in row]) * 100
            result[kom].append(round(total, 2))

    return {
        "labels": labels,
        "datasets": [
            {"label": kom, "data": result[kom]} for kom in komoditas_map
        ]
    }