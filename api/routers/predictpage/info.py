from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
import pandas as pd
import os

router = APIRouter()

@router.get("/info/{jenis}")
def get_info(
    jenis: str,
    komoditas: Optional[List[str]] = Query(default=None, description="Daftar komoditas atau gunakan 'all'")
):
    base_dir = os.path.dirname(os.path.abspath(__file__))  
    file_path_prediksi = os.path.join(base_dir, "../../dataset/Peramalan/aktual_prediksi_AD1.xlsx")
    df_prediksi = pd.read_excel(file_path_prediksi, sheet_name="aktual_prediksi_AD1")

    expected_cols = ["Kategori", "Komoditas", "Tahun", "Luas Lahan Panen", "Produksi"]
    if not all(col in df_prediksi.columns for col in expected_cols):
        raise HTTPException(status_code=400, detail="Kolom dataset tidak sesuai")
        
    df_filtered = df_prediksi[df_prediksi["Kategori"].str.strip().str.lower() == jenis.lower()]
    if df_filtered.empty:
        raise HTTPException(status_code=404, detail="Data tidak ditemukan")

    if komoditas and "all" not in [k.lower() for k in komoditas]:
        komoditas_clean = [k.strip().lower() for k in komoditas]
        df_filtered = df_filtered[df_filtered["Komoditas"].str.strip().str.lower().isin(komoditas_clean)]

    if df_filtered.empty:
        raise HTTPException(status_code=404, detail="Data tidak ditemukan")

    return {"category": jenis, "data": df_filtered.to_dict(orient="records")}