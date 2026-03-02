import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from st_supabase_connection import execute_query, SupabaseConnection

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

st.title("4. Data Penilaian (SMART Input)")

st.markdown("""
Halaman ini digunakan untuk memasukkan nilai alternatif terhadap setiap kriteria.
Pada metode SMART, kriteria dibedakan menjadi:

- **Cost** → Semakin kecil semakin baik
- **Benefit** → Semakin besar semakin baik
""")

# ====================== DEFINISI TIPE KRITERIA ======================
kriteria_info = {
    "Harga": "Cost",
    "Kualitas": "Benefit",
    "Pengiriman": "Cost",
    "Fleksibilitas": "Benefit",
    "Pelayanan": "Benefit"
}

# ====================== LOAD DATA ======================
data_supabase = execute_query(
    st_supabase.table("tb_alternatif").select("*").order("id"),
    ttl=0
)

if isinstance(data_supabase, dict) and "data" in data_supabase:
    data_supabase = data_supabase["data"]
elif hasattr(data_supabase, "data"):
    data_supabase = data_supabase.data
else:
    data_supabase = []

# Sidebar
with st.sidebar:
    if st.button("Logout", use_container_width=True):
        success, error_msg = auth.sign_out()
        if success:
            st.success("Berhasil logout!")
            st.rerun()
        else:
            st.error(f"Logout gagal: {error_msg}")

# ====================== DATAFRAME ======================
df = pd.DataFrame({
    "Alternatif": [row.get("Alternatif", "") for row in data_supabase],
    "Harga": [row.get("k1", 0) for row in data_supabase],
    "Kualitas": [row.get("k2", 0) for row in data_supabase],
    "Pengiriman": [row.get("k3", 0) for row in data_supabase],
    "Fleksibilitas": [row.get("k4", 0) for row in data_supabase],
    "Pelayanan": [row.get("k5", 0) for row in data_supabase]
})

st.session_state.penilaian = df

# ====================== TAMPILKAN TIPE KRITERIA ======================
st.subheader("Jenis Kriteria")

tipe_df = pd.DataFrame({
    "Kriteria": list(kriteria_info.keys()),
    "Tipe": list(kriteria_info.values())
})

def highlight_tipe(val):
    if val == "Cost":
        return "background-color: #ffcccc; font-weight: bold"
    elif val == "Benefit":
        return "background-color: #ccffcc; font-weight: bold"
    return ""

st.dataframe(tipe_df.style.applymap(highlight_tipe, subset=["Tipe"]))

st.info("Kriteria Cost akan diproses dengan normalisasi kebalikan (min/value), sedangkan Benefit menggunakan (value/max).")

st.divider()

# ====================== INPUT PENILAIAN ======================
st.subheader("Tabel Penilaian Alternatif")
st.caption("Isi nilai sesuai kondisi aktual masing-masing supplier.")

pen = st.data_editor(st.session_state.penilaian, num_rows="dynamic")
st.session_state.penilaian = pen

# ====================== SIMPAN ======================
if st.button("💾 Simpan Data Penilaian ke Database", type="primary", use_container_width=True):
    try:
        for idx, row in st.session_state.penilaian.iterrows():
            row_data = {
                "Alternatif": str(row["Alternatif"]),
                "k1": float(row["Harga"]),
                "k2": float(row["Kualitas"]),
                "k3": float(row["Pengiriman"]),
                "k4": float(row["Fleksibilitas"]),
                "k5": float(row["Pelayanan"])
            }

            existing = execute_query(
                st_supabase.table("tb_alternatif").select("id").eq("Alternatif", row_data["Alternatif"]),
                ttl=0
            )

            if isinstance(existing, dict) and "data" in existing:
                existing_data = existing["data"]
            elif hasattr(existing, "data"):
                existing_data = existing.data
            else:
                existing_data = []

            if existing_data:
                alt_id = existing_data[0]["id"]
                execute_query(
                    st_supabase.table("tb_alternatif").update(row_data).eq("id", alt_id),
                    ttl=0
                )
            else:
                execute_query(
                    st_supabase.table("tb_alternatif").insert(row_data),
                    ttl=0
                )

        st.success("✅ Data penilaian berhasil disimpan ke database!")

    except Exception as e:
        st.error(f"❌ Gagal menyimpan data: {e}")