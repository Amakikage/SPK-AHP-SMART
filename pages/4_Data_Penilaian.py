import streamlit as st
import pandas as pd
import numpy as np

st.title("4. Data Penilaian (SMART Input)")

if "alternatif" not in st.session_state:
    st.error("Isi Data Alternatif terlebih dahulu.")
    st.stop()

alts = st.session_state.alternatif["Alternatif"].tolist()

if "penilaian" not in st.session_state:
    df = pd.DataFrame({"Alternatif": alts})
    np.random.seed(42)
    df["Harga"] = np.random.randint(190, 251, len(alts))
    df["Pengiriman"] = np.random.randint(1, 4, len(alts))
    df["Kualitas"] = np.random.choice([5,3,1], len(alts))
    df["Fleksibilitas"] = np.random.choice([5,3,1], len(alts))
    df["Pelayanan"] = np.random.choice([5,3,1], len(alts))
    st.session_state.penilaian = df

pen = st.data_editor(st.session_state.penilaian, num_rows="dynamic")
st.session_state.penilaian = pen

# Buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("Acak Ulang Harga & Pengiriman"):
        df = st.session_state.penilaian.copy()
        df["Harga"] = np.random.randint(190, 251, len(df))
        df["Pengiriman"] = np.random.randint(1, 4, len(df))
        st.session_state.penilaian = df
        st.experimental_rerun()

with col2:
    if st.button("Acak Ulang Likert"):
        df = st.session_state.penilaian.copy()
        df["Kualitas"] = np.random.choice([5,3,1], len(df))
        df["Fleksibilitas"] = np.random.choice([5,3,1], len(df))
        df["Pelayanan"] = np.random.choice([5,3,1], len(df))
        st.session_state.penilaian = df
        st.experimental_rerun()

st.table(st.session_state.penilaian)
