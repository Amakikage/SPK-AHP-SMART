import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from st_supabase_connection import execute_query, SupabaseConnection

# ================== PATH & AUTH ==================
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import auth

auth.initialize_auth_state()
auth.require_auth()

# ================== SUPABASE ==================
st_supabase = st.connection(
    name="supabase_connection",
    type=SupabaseConnection,
    ttl=None,
)

# ================== TITLE ==================
st.title("📊 Data Alternatif (SMART)")

# ================== LOAD DATA ==================
data_supabase = execute_query(
    st_supabase
    .table("tb_alternatif")
    .select("id, Alternatif")
    .order("id"),
    ttl=0
)

if isinstance(data_supabase, dict) and "data" in data_supabase:
    data_supabase = data_supabase["data"]
elif hasattr(data_supabase, "data"):
    data_supabase = data_supabase.data
else:
    data_supabase = []

df = pd.DataFrame(data_supabase)

if df.empty:
    df = pd.DataFrame(columns=["id", "Alternatif"])

st.session_state["alternatif"] = df.copy()

# ================== SIDEBAR ==================
with st.sidebar:
    st.markdown("### 👤 Account")
    if st.button("Logout", use_container_width=True):
        success, error_msg = auth.sign_out()
        if success:
            st.success("Berhasil logout!")
            st.rerun()
        else:
            st.error(f"Logout gagal: {error_msg}")

# =================================================
# =============== TAMBAH DATA (ATAS) ===============
# =================================================
st.subheader("➕ Tambah Alternatif")

col_add1, col_add2 = st.columns([4, 1], vertical_alignment="bottom")

with col_add1:
    new_name = st.text_input(
        "Nama Alternatif",
        placeholder="Contoh: Supplier Kopi Aceh Gayo",
        label_visibility="collapsed"
    )

with col_add2:
    if st.button("Simpan", use_container_width=True):
        new_name = new_name.strip()

        if new_name == "":
            st.error("Nama alternatif tidak boleh kosong.")
            st.stop()

        if new_name.lower() in (
            st.session_state["alternatif"]["Alternatif"]
            .str.lower()
            .tolist()
        ):
            st.warning("Alternatif sudah ada.")
            st.stop()

        try:
            execute_query(
                st_supabase
                .table("tb_alternatif")
                .insert({"Alternatif": new_name}),
                ttl=0
            )
            st.success("Alternatif berhasil ditambahkan.")
            st.rerun()
        except Exception as e:
            st.error(f"Terjadi error: {e}")

st.divider()

# =================================================
# ================== TABEL DATA ===================
# =================================================
st.subheader("📋 Daftar Alternatif")

df_tampil = st.session_state["alternatif"].copy()

if not df_tampil.empty:
    df_tampil.insert(0, "No", range(1, len(df_tampil) + 1))
    df_tampil["No"] = df_tampil["No"].astype(str)
    df_tampil = df_tampil[["No", "Alternatif"]]
    df_tampil.rename(columns={"Alternatif": "Nama Alternatif"}, inplace=True)

st.dataframe(
    df_tampil,
    use_container_width=False,
    hide_index=True,
    column_config={
        "No": st.column_config.NumberColumn(
            "No",
            width=35
            ),
        "Nama Alternatif": st.column_config.TextColumn(
            "Nama Alternatif",
            width="large"
        )
    }
)

# =================================================
# ================== HAPUS DATA ===================
# =================================================
st.subheader("🗑️ Hapus Alternatif")

if not st.session_state["alternatif"].empty:
    opsi = st.session_state["alternatif"]

    pilihan_id = st.selectbox(
        "Pilih alternatif",
        opsi["id"],
        format_func=lambda x: opsi.loc[opsi["id"] == x, "Alternatif"].values[0]
    )

    if st.button("Hapus"):
        try:
            execute_query(
                st_supabase
                .table("tb_alternatif")
                .delete()
                .eq("id", pilihan_id),
                ttl=0
            )
            st.success("Alternatif berhasil dihapus.")
            st.rerun()
        except Exception as e:
            st.error(f"Gagal menghapus data: {e}")
