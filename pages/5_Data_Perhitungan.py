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

# Sidebar
with st.sidebar:
    if st.button("Logout", use_container_width=True):
        success, error_msg = auth.sign_out()
        if success:
            st.success("Berhasil logout!")
            st.rerun()
        else:
            st.error(f"Logout gagal: {error_msg}")

st.title("5. Perhitungan AHP + SMART")

if "kriteria" not in st.session_state or not st.session_state.kriteria:
    st.error("Hitung bobot AHP terlebih dahulu pada halaman Data Kriteria.")
    st.stop()

if "penilaian" not in st.session_state:
    st.error("Isi Data Penilaian terlebih dahulu.")
    st.stop()

if "bobot_ahp" not in st.session_state:
    st.error("Hitung bobot AHP terlebih dahulu pada halaman Data Kriteria.")
    st.stop()

bobot = st.session_state.bobot_ahp.copy()
penilaian = st.session_state.penilaian.copy()

norm = penilaian.copy()

# COST → Harga & Pengiriman
# COST → Harga & Pengiriman
for col in ["Harga", "Pengiriman"]:
    v = norm[col].astype(float)
    norm[col] = 100 * (v.max() - v) / (v.max() - v.min())

# BENEFIT → 3 Likert
for col in ["Kualitas", "Fleksibilitas", "Pelayanan"]:
    v = norm[col].astype(float)
    norm[col] = 100 * (v - v.min()) / (v.max() - v.min())

criteria = ["Harga", "Kualitas", "Pengiriman", "Fleksibilitas", "Pelayanan"]
norm[criteria] = norm[criteria].astype(float).round()

weighted = norm.copy()

for i, col in enumerate(criteria):
    weighted[col] = weighted[col] * bobot[i]

weighted[criteria] = weighted[criteria].round(5)

\

# ====== PERHITUNGAN NILAI AKHIR ====== 
scores = (norm[criteria].values * bobot).sum(axis=1)
scores = np.round(scores , 4)

hasil = pd.DataFrame({
    "Alternatif": penilaian["Alternatif"],
    "Score": scores,
})
hasil["Ranking"] = hasil["Score"].rank(ascending=False, method="min").astype(int)
hasil = hasil.sort_values("Score", ascending=False)

st.subheader("Nilai Utiliy (SMART)")
st.table(norm)

st.subheader("Normalisasi Bobot AHP x Nilai Utiliy")
st.table(weighted[["Alternatif"] + criteria])

st.subheader("Hasil Perhitungan")
st.table(hasil)

st.session_state.hasil = hasil