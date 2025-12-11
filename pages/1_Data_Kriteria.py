import streamlit as st
from st_supabase_connection import execute_query, SupabaseConnection
import pandas as pd
import numpy as np

st_supabase = st.connection(
    name="supabase_connection",
    type=SupabaseConnection,
    ttl=None,
)

st.title("1. Data Kriteria (AHP)")

# --- Ambil data dari Supabase ---
data_supabase = execute_query(
    st_supabase.table("tb_kriteria").select("*"),
    ttl=0
)


# --- FIX: Pastikan hasil query menjadi list of dict ---
if isinstance(data_supabase, dict) and "data" in data_supabase:
    data_supabase = data_supabase["data"]
elif hasattr(data_supabase, "data"):
    data_supabase = data_supabase.data

# --- Isi default jika belum ada ---
if "kriteria" not in st.session_state:
    if data_supabase:
        st.session_state.kriteria = [row["kriteria"] for row in data_supabase]
    else:
        st.session_state.kriteria = []


# ====================== EDIT NAMA KRITERIA ======================
st.subheader("Daftar Kriteria")
df_k = pd.DataFrame({"Kriteria": st.session_state.kriteria})
edited = st.data_editor(df_k, num_rows="dynamic")
st.session_state.kriteria = edited["Kriteria"].tolist()

# ====================== MATRIX AHP ======================
n = len(st.session_state.kriteria)

if "pairwise" not in st.session_state or st.session_state.get("pairwise_shape") != n:
    M = np.eye(n, dtype=float) + 1e-9  # untuk menghindari pembagian dengan nol

    if st.session_state.kriteria == ["Harga", "Kualitas", "Pengiriman", "Fleksibilitas", "Pelayanan"]:
        M = np.array([
            [1,   3,   4,   5,   7],
            [1/3, 1,   2,   3,   5],
            [1/4, 1/2, 1,   2,   3],
            [1/5, 1/3, 1/2, 1,   1],
            [1/7, 1/5, 1/3, 1,   1]
        ], dtype=float)

    st.session_state.pairwise = pd.DataFrame(
        M.astype(float),
        index=st.session_state.kriteria,
        columns=st.session_state.kriteria
    )
    st.session_state.pairwise_shape = n

# ====================== EDIT MATRIX ======================
st.subheader("Matriks Perbandingan Berpasangan (AHP)")
pair = st.data_editor(st.session_state.pairwise, num_rows="dynamic")

# ====================== PERBAIKI RESIPROKAL ======================
M = pair.copy().astype(float)

for i in range(n):
    for j in range(n):
        if i == j:
            M.iat[i, j] = 1.0
        else:
            a = M.iat[i, j]
            b = M.iat[j, i]

            if (pd.isna(a) or a <= 0) and (not pd.isna(b) and b > 0):
                M.iat[i, j] = 1 / b
            elif (pd.isna(b) or b <= 0) and (not pd.isna(a) and a > 0):
                M.iat[j, i] = 1 / a
            elif (pd.isna(a) or a <= 0) and (pd.isna(b) or b <= 0):
                M.iat[i, j] = 1

st.session_state.pairwise = M
st.write(M)

# ====================== TOMBOL CEK KONSISTENSI ======================
if st.button("Cek Konsistensi AHP"):
    st.session_state.run_ahp = True

st.subheader("Hasil Perhitungan AHP")

if not ("run_ahp" in st.session_state and st.session_state.run_ahp):
    st.info("Tekan tombol 'Cek Konsistensi AHP' untuk menghitung bobot.")
else:
    col_sum = M.sum(axis=0)
    norm = M / col_sum
    priority = norm.mean(axis=1)

    lambda_max = (M.dot(priority)).sum()
    CI = (lambda_max - n) / (n - 1)

    RI = {1:0.00, 2:0.00, 3:0.58, 4:0.90, 5:1.12}
    CR = CI / RI.get(n, 1.12)

    st.session_state.weights = dict(zip(st.session_state.kriteria, priority))

    st.table(pd.DataFrame({
        "Kriteria": st.session_state.kriteria,
        "Bobot": priority
    }))

    st.write(f"Lambda Max = {lambda_max:.4f}")
    st.write(f"CI = {CI:.4f}")
    st.write(f"CR = {CR:.4f}")

    if CR <= 0.1:
        st.success("Konsisten (CR ≤ 0.1)")
    else:
        st.error("Tidak Konsisten (CR > 0.1) — periksa kembali matriks.")
