import streamlit as st
import pandas as pd
import altair as alt

st.title("6. Hasil Akhir & Download")

if "hasil" not in st.session_state:
    st.error("Belum ada hasil perhitungan.")
    st.stop()

res = st.session_state.hasil.copy()
res["Score"] = res["Score"].round(4)

st.subheader("Ranking Akhir")
st.table(res)

chart = alt.Chart(res).mark_bar().encode(
    x="Score",
    y=alt.Y("Alternatif", sort="-x")
).properties(height=400)

st.altair_chart(chart, use_container_width=True)

csv = res.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "hasil_ahp_smart.csv", "text/csv")
