import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import auth

auth.initialize_auth_state()
auth.require_auth()

# ===================== SIDEBAR =====================
with st.sidebar:
    if st.button("Logout", use_container_width=True):
        success, error_msg = auth.sign_out()
        if success:
            st.success("Berhasil logout!")
            st.rerun()
        else:
            st.error(f"Logout gagal: {error_msg}")

# ===================== TITLE =====================
st.title("5. Perhitungan AHP + SMART")
st.markdown("""
Halaman ini menampilkan proses pengambilan keputusan menggunakan:

- **AHP** → untuk menentukan bobot kriteria  
- **SMART** → untuk menghitung nilai akhir alternatif  

Proses dilakukan secara bertahap agar keputusan dapat dijelaskan secara transparan.
""")

# ===================== VALIDASI =====================
if "kriteria" not in st.session_state or not st.session_state.kriteria:
    st.error("Hitung bobot AHP terlebih dahulu pada halaman Data Kriteria.")
    st.stop()

if "penilaian" not in st.session_state:
    st.error("Isi Data Penilaian terlebih dahulu.")
    st.stop()

if "bobot_ahp" not in st.session_state:
    st.error("Hitung bobot AHP terlebih dahulu pada halaman Data Kriteria.")
    st.stop()

bobot = np.array(st.session_state.bobot_ahp)
penilaian = st.session_state.penilaian.copy()

# ===================== KRITERIA DINAMIS =====================
criteria = [
    str(k).strip()
    for k in st.session_state.kriteria
    if k is not None and str(k).strip() != ""
]

# Validasi agar tidak error panjang array
if len(criteria) != len(bobot):
    st.error("Jumlah kriteria dan bobot AHP tidak sesuai. Silakan hitung ulang AHP.")
    st.stop()

# ===================== TAMPILKAN BOBOT AHP =====================
st.subheader("Tahap 1: Bobot Kriteria (Hasil AHP)")

df_bobot = pd.DataFrame({
    "Kriteria": criteria,
    "Bobot": np.round(bobot, 5)
})

st.table(df_bobot)

st.info("Bobot menunjukkan tingkat kepentingan relatif setiap kriteria berdasarkan perbandingan AHP.")

# ===================== NORMALISASI SMART =====================
st.subheader("Tahap 2: Normalisasi Nilai (SMART)")

norm = penilaian.copy()

st.markdown("""
Normalisasi dilakukan berdasarkan tipe kriteria:

- **Cost** → (CMax - Cout) / (CMax - CMin) * 100
- **Benefit** → (Cout - CMin) / (CMax - CMin) * 100
""")

# Tetap pakai pembagian Cost & Benefit seperti sebelumnya
cost_cols = [col for col in criteria if col in ["Harga", "Pengiriman"]]
benefit_cols = [col for col in criteria if col in ["Kualitas", "Fleksibilitas", "Pelayanan"]]

# COST
for col in cost_cols:
    v = norm[col].astype(float)
    norm[col] = 100 * (v.max() - v) / (v.max() - v.min())

# BENEFIT
for col in benefit_cols:
    v = norm[col].astype(float)
    norm[col] = 100 * (v - v.min()) / (v.max() - v.min())

norm[criteria] = norm[criteria].round(2)

st.table(norm)

# ===================== PEMBOBOTAN =====================
st.subheader("Tahap 3: Perhitungan Nilai Terbobot")

weighted = norm.copy()

for i, col in enumerate(criteria):
    weighted[col] = weighted[col] * bobot[i]

weighted[criteria] = weighted[criteria].round(4)

st.table(weighted[["Alternatif"] + criteria])

st.caption("Nilai utilitas dikalikan dengan bobot AHP untuk mendapatkan nilai bobot setiap kriteria.")

# ===================== NILAI AKHIR =====================
st.subheader("Tahap 4: Perhitungan Nilai Akhir & Ranking")

scores = (norm[criteria].values * bobot).sum(axis=1)
scores = np.round(scores, 4)

hasil = pd.DataFrame({
    "Alternatif": penilaian["Alternatif"],
    "Score Akhir": scores,
})

hasil["Ranking"] = hasil["Score Akhir"].rank(
    ascending=False, method="min"
).astype(int)

hasil = hasil.sort_values("Score Akhir", ascending=False)

st.table(hasil)

# ===================== KESIMPULAN OTOMATIS =====================
st.subheader("Kesimpulan Keputusan")

terbaik = hasil.iloc[0]

st.success(
    f"Berdasarkan perhitungan AHP dan SMART, alternatif terbaik adalah "
    f"**{terbaik['Alternatif']}** dengan nilai akhir **{terbaik['Score Akhir']}**."
)

st.markdown("""
Sistem mendapatkan alternatif dengan nilai tertinggi sebagai pilihan terbaik 
karena memiliki kombinasi nilai kriteria dan bobot kepentingan yang paling optimal.
""")

# simpan hasil
st.session_state.hasil = hasil