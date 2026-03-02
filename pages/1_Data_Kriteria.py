import streamlit as st
from st_supabase_connection import execute_query, SupabaseConnection
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# ====================== PATH & AUTH ======================
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import auth
auth.initialize_auth_state()
auth.require_auth()

# ====================== CUSTOM CSS ======================
st.markdown("""
<style>
.card {
    background-color: #ffffff;
    padding: 0px;
    border-radius: 1px;
    border: 1px solid #e0e0e0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    margin-bottom: 25px;
}
.section-title {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ====================== SUPABASE ======================
st_supabase = st.connection(
    name="supabase_connection",
    type=SupabaseConnection,
    ttl=None,
)

# ====================== HEADER ======================
st.title("⚖️ Data Kriteria (AHP)")

st.markdown("""
Halaman ini digunakan untuk mengelola **kriteria penilaian** dan menghitung 
**bobot kriteria menggunakan metode AHP (Analytical Hierarchy Process)**.
""")

# ====================== LOAD DATA ======================
data_supabase = execute_query(
    st_supabase.table("tb_kriteria").select("*").order("id"),
    ttl=0
)

if isinstance(data_supabase, dict) and "data" in data_supabase:
    data_supabase = data_supabase["data"]
elif hasattr(data_supabase, "data"):
    data_supabase = data_supabase.data
else:
    data_supabase = []

# ====================== KRITERIA ======================
if "kriteria" not in st.session_state:
    if data_supabase:
        st.session_state.kriteria = [row["kriteria"] for row in data_supabase]
    else:
        st.session_state.kriteria = []

# ====================== TAMBAH KRITERIA ======================
st.markdown('<div class="card">', unsafe_allow_html=True)

st.markdown('<div class="section-title">➕ Tambah Kriteria</div>', unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])
with col1:
    new_kriteria = st.text_input(
        "Nama Kriteria",
        key="new_kriteria",
        label_visibility="collapsed"
    )

with col2:
    if st.button("Tambah", use_container_width=True):
        if new_kriteria.strip() == "":
            st.warning("Nama kriteria tidak boleh kosong")
        elif new_kriteria in st.session_state.kriteria:
            st.warning("Kriteria sudah ada")
        else:
            st.session_state.kriteria.append(new_kriteria)
            st.session_state.pairwise_shape = -1
            st.success(f"Kriteria '{new_kriteria}' ditambahkan")

st.markdown('</div>', unsafe_allow_html=True)

# ====================== LAYOUT 2 KOLOM ======================
col_kiri, col_kanan = st.columns(2, gap="large")

# ====================== KOLOM KIRI ======================
with col_kiri:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📋 Daftar Kriteria</div>', unsafe_allow_html=True)

    df_k = pd.DataFrame({"Kriteria": st.session_state.kriteria})
    edited_k = st.data_editor(df_k, num_rows="dynamic")
    st.session_state.kriteria = edited_k["Kriteria"].tolist()

    st.markdown('</div>', unsafe_allow_html=True)

# ====================== KOLOM KANAN ======================
with col_kanan:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📏 Skala Perbandingan AHP (Saaty 1–9)</div>', unsafe_allow_html=True)

    skala_df = pd.DataFrame({
        "Nilai": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "Keterangan": [
            "Sama penting",
            "Mendekati sedikit lebih penting",
            "Sedikit lebih penting",
            "Mendekati lebih penting",
            "Lebih penting",
            "Mendekati sangat lebih penting",
            "Sangat lebih penting",
            "Mendekati mutlak",
            "Mutlak sangat penting"
        ]
    })

    st.table(skala_df)

    st.info("Jika A lebih penting dari B dengan nilai 5, maka B terhadap A otomatis bernilai 1/5.")

    st.markdown('</div>', unsafe_allow_html=True)

# ====================== MATRIKS AHP ======================
n = len(st.session_state.kriteria)

if "pairwise" not in st.session_state or st.session_state.get("pairwise_shape") != n:
    M = np.zeros((n, n)).astype(str)

    for i in range(n):
        for j in range(n):
            M[i][j] = "1" if i == j else ""

    if data_supabase and n > 0:
        max_baris = min(n, len(data_supabase))
        max_kolom = min(n, 5)

        for i in range(max_baris):
            row = data_supabase[i]
            for j in range(max_kolom):
                col = f"k{j+1}"
                if col in row and row[col] is not None:
                    M[i][j] = str(row[col])

    st.session_state.pairwise = pd.DataFrame(
        M,
        index=st.session_state.kriteria,
        columns=st.session_state.kriteria
    )
    st.session_state.pairwise_shape = n

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📊 Matriks Perbandingan Berpasangan</div>', unsafe_allow_html=True)

pair_str = st.data_editor(st.session_state.pairwise, num_rows="dynamic")

# ====================== KONVERSI ======================
M = pair_str.copy()
for i in range(n):
    for j in range(n):
        try:
            M.iat[i, j] = float(M.iat[i, j])
        except:
            M.iat[i, j] = 1.0

M = M.astype(float)

# ====================== RECIPROCAL ======================
for i in range(n):
    for j in range(n):
        if i == j:
            M.iat[i, j] = 1.0
        elif i < j:
            if M.iat[i, j] <= 0:
                M.iat[i, j] = 1.0
            M.iat[j, i] = 1 / M.iat[i, j]

st.session_state.pairwise = M.applymap(
    lambda x: str(int(x)) if float(x).is_integer() else str(round(x, 4))
)

st.markdown('</div>', unsafe_allow_html=True)

# ====================== SIMPAN ======================
if st.button("💾 Simpan Matriks ke Database"):
    try:
        st_supabase.table("tb_kriteria").delete().neq("id", 0).execute()

        for i, krit in enumerate(st.session_state.kriteria):
            row_data = {
                "kriteria": krit,
                "k1": float(M.iat[i, 0]) if n > 0 else 1,
                "k2": float(M.iat[i, 1]) if n > 1 else 1,
                "k3": float(M.iat[i, 2]) if n > 2 else 1,
                "k4": float(M.iat[i, 3]) if n > 3 else 1,
                "k5": float(M.iat[i, 4]) if n > 4 else 1,
            }
            st_supabase.table("tb_kriteria").insert(row_data).execute()

        st.success("✅ Data berhasil disimpan!")
    except Exception as e:
        st.error(f"❌ Error: {e}")

# ====================== NORMALISASI ======================
st.subheader("Normalisasi Matriks")
col_sum = M.sum(axis=0)
nilai = M / col_sum
nilai["Jumlah"] = nilai.sum(axis=1)
nilai = nilai.round(5)
st.table(nilai)

# ====================== HITUNG AHP ======================
if st.button("Cek Konsistensi AHP"):
    st.session_state.run_ahp = True

if st.session_state.get("run_ahp", False):
    norm = M / M.sum(axis=0)
    priority = norm.mean(axis=1)

    Aw = M.dot(priority)
    lambda_max = np.mean(Aw / priority)

    if n < 3:
        CI = 0
        CR = 0
    else:
        CI = (lambda_max - n) / (n)
        RI = {3: 0.58, 4: 0.90, 5: 1.12}
        CR = CI / RI.get(n, 1.12)

    df_result = pd.DataFrame({
        "Kriteria": st.session_state.kriteria,
        "Bobot": priority.round(5)
    })

    st.table(df_result)
    st.write(f"λ Max = {lambda_max:.5f}")
    st.write(f"CI = {CI:.5f}")
    st.write(f"CR = {CR:.5f}")

    if CR <= 0.1:
        st.success("Konsisten ✔")
    else:
        st.error("Tidak konsisten ❌")

    st.session_state.bobot_ahp = priority.values