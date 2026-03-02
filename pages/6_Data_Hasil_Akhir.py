import streamlit as st
import pandas as pd
import altair as alt
import sys
from pathlib import Path
from datetime import datetime

# ===== PDF LIBRARY =====
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes
from reportlab.lib.units import inch

parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import auth

auth.initialize_auth_state()
auth.require_auth()

st.title("6. Hasil Akhir & Download")

# ===================== SIDEBAR =====================
with st.sidebar:
    if st.button("Logout", use_container_width=True):
        success, error_msg = auth.sign_out()
        if success:
            st.success("Berhasil logout!")
            st.rerun()
        else:
            st.error(f"Logout gagal: {error_msg}")

# ===================== VALIDASI =====================
if "hasil" not in st.session_state:
    st.error("Belum ada hasil perhitungan.")
    st.stop()

res = st.session_state.hasil.copy()

if "Score Akhir" in res.columns:
    res.rename(columns={"Score Akhir": "Score"}, inplace=True)

res["Score"] = res["Score"].round(4)
res = res.sort_values("Score", ascending=False).reset_index(drop=True)

# ===================== SUPPLIER TERBAIK =====================
st.subheader("🏆 Rekomendasi Supplier Terbaik")

terbaik = res.iloc[0]

st.success(
    f"Supplier terbaik adalah **{terbaik['Alternatif']}** "
    f"dengan skor akhir **{terbaik['Score']:.4f}**"
)

st.divider()

# ===================== GRAFIK =====================
st.subheader("Visualisasi Perbandingan Nilai")

res["Kategori"] = ["Terbaik" if i == 0 else "Lainnya" for i in range(len(res))]

chart = alt.Chart(res).mark_bar().encode(
    x=alt.X("Score:Q", title="Nilai Akhir"),
    y=alt.Y("Alternatif:N", sort="-x"),
    color=alt.Color(
        "Kategori:N",
        scale=alt.Scale(
            domain=["Terbaik", "Lainnya"],
            range=["#2ecc71", "#bdc3c7"]
        ),
        legend=None
    ),
    tooltip=["Alternatif", "Score"]
).properties(height=400)

st.altair_chart(chart, use_container_width=True)

st.divider()

# ===================== TABEL RANKING =====================
st.subheader("Ranking Akhir")

res["Ranking"] = [i+1 for i in range(len(res))]

st.table(res[["Ranking", "Alternatif", "Score"]])

st.divider()

# ===================== GENERATE PDF =====================
st.subheader("Download Laporan PDF")

if st.button("📄 Generate Laporan", use_container_width=True):

    file_path = "Laporan_Hasil_AHP_SMART.pdf"

    doc = SimpleDocTemplate(file_path, pagesize=pagesizes.A4)
    elements = []

    styles = getSampleStyleSheet()

    elements.append(Paragraph("LAPORAN HASIL SISTEM PENDUKUNG KEPUTUSAN", styles["Heading1"]))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Metode: AHP + SMART", styles["Normal"]))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(
        f"Tanggal Cetak: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 0.5 * inch))

    elements.append(Paragraph("Supplier Terbaik:", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(
        f"{terbaik['Alternatif']} dengan skor {terbaik['Score']:.4f}",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 0.5 * inch))

    # Tabel
    table_data = [["Ranking", "Alternatif", "Score"]]

    for _, row in res.iterrows():
        table_data.append([
            str(row["Ranking"]),
            row["Alternatif"],
            f"{row['Score']:.4f}"
        ])

    table = Table(table_data, colWidths=[1*inch, 3*inch, 1.5*inch])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ]))

    elements.append(table)

    doc.build(elements)

    with open(file_path, "rb") as f:
        st.download_button(
            "📥 Download Laporan PDF",
            f,
            file_name=file_path,
            mime="application/pdf",
            use_container_width=True
        )