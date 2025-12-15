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

# ====================== LOAD DATA ======================
data_supabase = execute_query(
    st_supabase.table("tb_alternatif").select("*").order("id"),
    ttl=0
)

if isinstance(data_supabase, dict) and "data" in data_supabase:
    data_supabase = data_supabase["data"]
elif hasattr(data_supabase, "data"):
    data_supabase = data_supabase.data

# Sidebar
with st.sidebar:
    if st.button("Logout", use_container_width=True):
        success, error_msg = auth.sign_out()
        if success:
            st.success("Berhasil logout!")
            st.rerun()
        else:
            st.error(f"Logout gagal: {error_msg}")

# Mapping fixed untuk kolom database
kriteria_mapping = {
    "k1": "Harga",
    "k2": "Kualitas",
    "k3": "Pengiriman",
    "k4": "Fleksibilitas",
    "k5": "Pelayanan"
}

df = pd.DataFrame({
    "Alternatif": [row["Alternatif"] for row in data_supabase],
    "Harga": [row.get("k1", 0) for row in data_supabase],
    "Kualitas": [row.get("k2", 5) for row in data_supabase],
    "Pengiriman": [row.get("k3", 0) for row in data_supabase],
    "Fleksibilitas": [row.get("k4", 5) for row in data_supabase],
    "Pelayanan": [row.get("k5", 5) for row in data_supabase]
})
st.session_state.penilaian = df

pen = st.data_editor(st.session_state.penilaian, num_rows="dynamic")
st.session_state.penilaian = pen

# Tombol Simpan ke Database
if st.button("💾 Simpan Data Penilaian ke Database", type="primary", use_container_width=True):
    try:
        for idx, row in st.session_state.penilaian.iterrows():
            row_data = {
                "id": idx + 1,
                "Alternatif": str(row["Alternatif"]),
                "k1": float(row["Harga"]),
                "k2": float(row["Kualitas"]),
                "k3": float(row["Pengiriman"]),
                "k4": float(row["Fleksibilitas"]),
                "k5": float(row["Pelayanan"])
            }
            # Cek apakah alternatif sudah ada (berdasarkan nama)
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
            if existing_data and len(existing_data) > 0:
                # Update
                alt_id = existing_data[0]["id"]
                execute_query(
                    st_supabase.table("tb_alternatif").update(row_data).eq("id", alt_id),
                    ttl=0
                )
            else:
                # Insert tanpa kolom id
                execute_query(
                    st_supabase.table("tb_alternatif").insert({k: v for k, v in row_data.items()}),
                    ttl=0
                )
        st.success("\u2705 Data penilaian berhasil disimpan ke database!")
    except Exception as e:
        st.error(f"\u274c Gagal menyimpan data: {e}")

st.divider()

st.subheader("Tabel Penilaian")
result_table = st.session_state.penilaian.copy()
result_table.index = result_table.index + 1  # Mulai dari 1
st.table(result_table)
