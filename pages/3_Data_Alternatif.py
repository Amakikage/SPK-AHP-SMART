import streamlit as st
import pandas as pd

st.title("3. Data Alternatif (Supplier)")

# ============ INITIAL DATA ===============
if "alternatif" not in st.session_state:
    st.session_state.alternatif = pd.DataFrame({
        "Alternatif": [
            "Beska","Fow","Gerai Hutan","Pesirah","Benawa",
            "Samping Roastery","Koloni","Agam Pisan","Dialek","Diego"
        ]
    })


# ============ HEADER + TOMBOL TAMBAH ==============
col1, col2 = st.columns([4,1])

with col1:
    st.subheader("Daftar Alternatif")

with col2:
    tambah = st.button("Tambah Data")


# ============ POPUP TAMBAH DATA ==================
if tambah:
    with st.modal("Tambah Alternatif Baru"):
        new_name = st.text_input("Nama Alternatif")
        if st.button("Simpan"):
            if new_name.strip() != "":
                # Tambahkan ke DataFrame
                new_row = pd.DataFrame({"Alternatif": [new_name]})
                st.session_state.alternatif = pd.concat(
                    [st.session_state.alternatif, new_row],
                    ignore_index=True
                )
                st.success("Data berhasil ditambahkan!")
                st.rerun()
            else:
                st.error("Nama alternatif tidak boleh kosong.")


# ============ EDITOR UTAMA (HANYA 1 TABEL) ============
edited = st.data_editor(
    st.session_state.alternatif,
    num_rows="dynamic"
)

st.session_state.alternatif = edited
