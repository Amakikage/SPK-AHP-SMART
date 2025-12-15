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

df = pd.DataFrame({
    "Alternatif": [row["Alternatif"] for row in data_supabase],
})

st.session_state.alternatif = df
result_table = st.session_state.alternatif.copy()


# ============ HEADER + TOMBOL TAMBAH ==============
col1, col2 = st.columns([3,1])

with col1:
    st.subheader("Daftar Alternatif")
    st.table(result_table)

with col2:
    show_add = st.toggle("➕ Tambah Data")  # ganti modal dengan toggle


# ============ FORM TAMBAH DATA (EXPANDER) ===========
if show_add:
    with st.expander("Form Tambah Alternatif", expanded=True):
        new_name = st.text_input("Nama Alternatif Baru")

        if st.button("Simpan"):
            if new_name.strip() == "":
                st.error("Nama alternatif tidak boleh kosong.")
            else:
                # Insert ke Supabase
                try:
                    insert_result = execute_query(
                        st_supabase.table("tb_alternatif").insert({"Alternatif": new_name}),
                        ttl=0
                    )
                    if (
                        (isinstance(insert_result, dict) and insert_result.get("status_code", 200) < 300)
                        or (hasattr(insert_result, "status_code") and insert_result.status_code < 300)
                    ):
                        st.success("Alternatif berhasil ditambahkan ke database!")
                        st.rerun()
                    else:
                        st.error(f"Gagal menambah ke database: {insert_result}")
                except Exception as e:
                    st.error(f"Terjadi error saat insert: {e}")
