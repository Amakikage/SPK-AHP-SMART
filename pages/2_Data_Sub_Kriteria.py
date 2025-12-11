import streamlit as st
import pandas as pd

st.title("2. Data Sub-Kriteria (SMART)")

st.write("Sub-kriteria hanya untuk Harga & Pengiriman.")

if 'subkriteria' not in st.session_state:
    df = pd.DataFrame({
        "Kriteria": ["Harga", "Pengiriman"],
        "SubKriteria": ["Harga Biji Kopi", "Waktu Pengiriman"]
    })
    st.session_state.subkriteria = df

edited = st.data_editor(st.session_state.subkriteria, num_rows="dynamic")
st.session_state.subkriteria = edited

st.subheader("Sub-Kriteria Saat Ini:")
st.table(edited)


st.info("Tidak menggunakan bobot sub-kriteria — SMART langsung memakai nilai numerik.")
