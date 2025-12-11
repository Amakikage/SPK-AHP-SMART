import streamlit as st
from st_supabase_connection import SupabaseConnection
st_supabase = st.connection(
    name="supabase_connection",
    type=SupabaseConnection,
    ttl=None,  # cache indefinitely; override when you need fresher data
)

# Example: list buckets without re-authenticating on every rerun
buckets = st_supabase.list_buckets()
# st.write(buckets)

st.set_page_config(page_title="AHP-SMART Admin", layout="wide")

# ================= LOGIN SYSTEM ===================
ADMIN_USER = "admin"
ADMIN_PASS = "12345"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ================= LOGIN PAGE =====================
def login_page():
    st.title("🔒 Login Admin")
    st.write("Masukkan username dan password untuk melanjutkan.")

    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == ADMIN_USER and pw == ADMIN_PASS:
            st.session_state.logged_in = True
            st.success("Login berhasil!")
            # gunakan st.rerun() karena st.experimental_rerun mungkin tidak ada di versi Streamlit kamu
            try:
                st.rerun()
            except Exception:
                # hanya untuk berjaga-jaga: jika rerun juga tidak tersedia, lakukan nothing
                pass
        else:
            st.error("Username atau password salah.")

# ================= DASHBOARD PAGE ==================
def dashboard_page():
    st.title("📊 Dashboard Admin AHP-SMART")
    st.header("selamat datang, admin!")

    # ---- METRIC BOXES ----
    col1, col2, col3 = st.columns(3)
    col1.metric("Jumlah Kriteria", 5)
    col2.metric("Jumlah Alternatif", 10)
    col3.metric("Status Sistem", "Aktif")

    st.divider()

    # ---- MENU ----
    colA, colB, colC = st.columns(3)

    with colA:
        st.subheader("⚙️ Kelola Data")
        st.write("Kriteria, Sub-kriteria, Alternatif.")
        if st.button("Buka Data Kriteria"):
            # gunakan try/except karena st.switch_page tidak ada di semua versi streamlit
            try:
                st.switch_page("pages/1_Data_Kriteria.py")
            except Exception:
                st.info("Navigasi halaman belum tersedia di versi Streamlit ini. Silakan buka file pages/1_Data_Kriteria.py secara manual.")

    with colB:
        st.subheader("📈 Perhitungan")
        st.write("Perhitungan AHP + SMART.")
        if st.button("Buka Perhitungan"):
            try:
                st.switch_page("pages/5_Data_Perhitungan.py")
            except Exception:
                st.info("Navigasi halaman belum tersedia di versi Streamlit ini. Silakan buka pages/5_Data_Perhitungan.py secara manual.")

    with colC:
        st.subheader("📥 Unduhan Laporan")
        st.write("Ekspor hasil perhitungan.")
        if st.button("Buka Hasil Akhir"):
            try:
                st.switch_page("pages/6_Data_Hasil_Akhir.py")
            except Exception:
                st.info("Navigasi halaman belum tersedia di versi Streamlit ini. Silakan buka pages/6_Data_Hasil_Akhir.py secara manual.")

    st.divider()

    if st.button("Logout"):
        st.session_state.logged_in = False
        try:
            st.rerun()
        except Exception:
            pass

# ============== ROUTING ===========================
if not st.session_state.logged_in:
    login_page()
else:
    dashboard_page()
