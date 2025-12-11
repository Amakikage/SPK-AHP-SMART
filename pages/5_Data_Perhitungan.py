import streamlit as st
import pandas as pd
import numpy as np

st.title("5. Perhitungan AHP + SMART")

if "weights" not in st.session_state:
    st.error("Hitung bobot AHP terlebih dahulu pada halaman Data Kriteria.")
    st.stop()

if "penilaian" not in st.session_state:
    st.error("Isi Data Penilaian terlebih dahulu.")
    st.stop()

weights = st.session_state.weights
pen = st.session_state.penilaian.copy()

norm = pen.copy()

# COST → Harga & Pengiriman
for col in ["Harga", "Pengiriman"]:
    v = norm[col].astype(float)
    norm[col] = (v.max() - v) / (v.max() - v.min())

# BENEFIT → 3 Likert
for col in ["Kualitas","Fleksibilitas","Pelayanan"]:
    v = norm[col].astype(float)
    norm[col] = (v - v.min()) / (v.max() - v.min())

criteria = ["Harga","Kualitas","Pengiriman","Fleksibilitas","Pelayanan"]
w = np.array([weights[c] for c in criteria])

scores = (norm[criteria].values * w).sum(axis=1)

result = pd.DataFrame({
    "Alternatif": pen["Alternatif"],
    "Score": scores,
})
result["Rank"] = result["Score"].rank(ascending=False, method="min").astype(int)
result = result.sort_values("Score", ascending=False)

st.subheader("Normalisasi SMART")
st.table(norm)

st.subheader("Hasil Perhitungan")
st.table(result)

st.session_state.hasil = result
