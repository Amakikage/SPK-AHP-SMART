import streamlit as st
import pandas as pd

st.title("3. Data Alternatif (Supplier)")

if "alternatif" not in st.session_state:
    st.session_state.alternatif = pd.DataFrame({
        "Alternatif": [
            "Beska","Fow","Gerai Hutan","Pesirah","Benawa",
            "Samping Roastery","Koloni","Agam Pisan","Dialek","Diego"
        ]
    })

edited = st.data_editor(st.session_state.alternatif, num_rows="dynamic")
st.session_state.alternatif = edited

st.subheader("Daftar Alternatif:")
st.table(edited)
