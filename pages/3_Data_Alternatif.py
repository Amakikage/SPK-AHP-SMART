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
st.caption("Halaman ini digunakan untuk mengelola daftar alternatif (supplier) yang akan dinilai menggunakan metode SMART.")

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

df_db = pd.DataFrame(data_supabase)

if df_db.empty:
    df_db = pd.DataFrame(columns=["id", "Alternatif"])

st.session_state["alternatif"] = df_db.copy()

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
# =============== LAYOUT 2 KOLOM ==================
# =================================================
col1, col2 = st.columns([1, 1], gap="large")

# =================================================
# ================== TAMBAH DATA ===================
# =================================================
with col1:
    with st.container(border=True):
        st.subheader("➕ Tambah Alternatif")
        st.caption("Masukkan nama supplier yang akan dievaluasi.")

        with st.form("form_tambah_alternatif", clear_on_submit=True):
            new_name = st.text_input(
                "Nama Alternatif",
                placeholder="Contoh: Supplier Kopi Aceh Gayo"
            )

            submit = st.form_submit_button(
                "Simpan Alternatif",
                use_container_width=True
            )

            if submit:
                new_name = new_name.strip()

                if new_name == "":
                    st.warning("Nama alternatif tidak boleh kosong.")

                elif not df_db.empty and \
                    new_name.lower() in df_db["Alternatif"].str.lower().tolist():
                    st.warning("Alternatif sudah ada.")

                else:
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

# =================================================
# ================== TABEL DATA ===================
# =================================================
with col2:
    with st.container(border=True):
        st.subheader("📋 Daftar Alternatif")

        if df_db.empty:
            st.info("Belum ada alternatif yang ditambahkan.")
        else:
            df_tampil = df_db.copy()
            df_tampil.insert(0, "No", range(1, len(df_tampil) + 1))
            df_tampil = df_tampil[["No", "Alternatif"]]
            df_tampil.rename(columns={"Alternatif": "Nama Alternatif"}, inplace=True)

            st.dataframe(
                df_tampil,
                use_container_width=True,
                hide_index=True
            )

# =================================================
# ================== HAPUS DATA ===================
# =================================================
st.divider()

with st.expander("🗑️ Hapus Alternatif", expanded=False):

    if df_db.empty:
        st.info("Tidak ada alternatif yang bisa dihapus.")
    else:
        pilihan_id = st.selectbox(
            "Pilih alternatif yang akan dihapus",
            df_db["id"],
            format_func=lambda x: df_db.loc[
                df_db["id"] == x, "Alternatif"
            ].values[0]
        )

        if st.button("Hapus Alternatif", type="secondary"):
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