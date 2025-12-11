import streamlit as st
from st_supabase_connection import execute_query, SupabaseConnection
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

st_supabase = st.connection(
    name="supabase_connection",
    type=SupabaseConnection,
    ttl=None,
)

st.title("1. Data Kriteria (AHP)")

# ====================== LOAD DATA ======================
data_supabase = execute_query(
    st_supabase.table("tb_kriteria").select("*").order("id"),
    ttl=0
)

if isinstance(data_supabase, dict) and "data" in data_supabase:
    data_supabase = data_supabase["data"]
elif hasattr(data_supabase, "data"):
    data_supabase = data_supabase.data

# ====================== KRITERIA ======================
if "kriteria" not in st.session_state:
    if data_supabase:
        st.session_state.kriteria = [row["kriteria"] for row in data_supabase]
    else:
        st.session_state.kriteria = []

st.subheader("Daftar Kriteria")
df_k = pd.DataFrame({"Kriteria": st.session_state.kriteria})
edited_k = st.data_editor(df_k, num_rows="dynamic")
st.session_state.kriteria = edited_k["Kriteria"].tolist()

# ====================== INIT MATRIX ======================
n = len(st.session_state.kriteria)

if "pairwise" not in st.session_state or st.session_state.get("pairwise_shape") != n:
    M = np.zeros((n, n)).astype(str)

    # default 1 di diagonal
    for i in range(n):
        for j in range(n):
            if i == j:
                M[i][j] = "1"

    # jika ada data dari supabase
    if data_supabase and n > 0:
        for i, row in enumerate(data_supabase):
            for j in range(n):
                col = f"k{j+1}"
                if col in row and row[col] is not None:
                    M[i][j] = str(row[col])

    st.session_state.pairwise = pd.DataFrame(
        M,
        index=st.session_state.kriteria,
        columns=st.session_state.kriteria
    )
    st.session_state.pairwise_shape = n

# ====================== EDIT MATRIX TAMPILAN STRING ======================
st.subheader("Matriks Perbandingan Berpasangan (AHP)")

pair_str = st.data_editor(
    st.session_state.pairwise,
    num_rows="dynamic"
)

# konversi ke float untuk perhitungan
M = pair_str.copy()
for i in range(n):
    for j in range(n):
        try:
            M.iat[i, j] = float(M.iat[i, j])
        except:
            M.iat[i, j] = 1.0

M = M.astype(float)

# ====================== RECIPROCAL AUTO ======================
for i in range(n):
    for j in range(n):
        if i == j:
            M.iat[i, j] = 1.0
        else:
            a = M.iat[i, j]
            b = M.iat[j, i]

            if a <= 0 and b > 0:
                M.iat[i, j] = 1 / b
            elif b <= 0 and a > 0:
                M.iat[j, i] = 1 / a
            elif a <= 0 and b <= 0:
                M.iat[i, j] = 1.0

# simpan kembali tampilan string tanpa mengubah angka input
M_display = M.applymap(lambda x: str(int(x)) if x.is_integer() else str(x))
st.session_state.pairwise = M_display

# ====================== SIMPAN ======================
if st.button("💾 Simpan Matriks ke Supabase"):
    try:
        st_supabase.table("tb_kriteria").delete().neq("id", 0).execute()

        for i, krit in enumerate(st.session_state.kriteria):
            row_data = {
                "kriteria": krit,
                "k1": float(M.iat[i, 0]),
                "k2": float(M.iat[i, 1]),
                "k3": float(M.iat[i, 2]) if n > 2 else 0,
                "k4": float(M.iat[i, 3]) if n > 3 else 0,
                "k5": float(M.iat[i, 4]) if n > 4 else 0,
            }
            st_supabase.table("tb_kriteria").insert(row_data).execute()

        st.success("✅ Data berhasil disimpan!")
    except Exception as e:
        st.error(f"❌ Error: {e}")

# ====================== HITUNG AHP ======================
if st.button("Cek Konsistensi AHP"):
    st.session_state.run_ahp = True

st.subheader("Hasil Perhitungan AHP")

if not st.session_state.get("run_ahp", False):
    st.info("Tekan tombol untuk menghitung.")
else:
    col_sum = M.sum(axis=0)
    norm = M / col_sum
    priority = norm.mean(axis=1)

    lambda_max = (M.dot(priority)).sum()
    CI = (lambda_max - n) / (n - 1)

    RI = {1:0.0, 2:0.0, 3:0.58, 4:0.90, 5:1.12}
    CR = CI / RI.get(n, 1.12)

    st.table(pd.DataFrame({
        "Kriteria": st.session_state.kriteria,
        "Bobot": [round(w, 4) for w in priority]
    }))

    st.write(f"λ Max = {lambda_max:.4f}")
    st.write(f"CI = {CI:.4f}")
    st.write(f"CR = {CR:.4f}")

    if CR <= 0.1:
        st.success("Konsisten ✔")
    else:
        st.error("Tidak konsisten ❌")