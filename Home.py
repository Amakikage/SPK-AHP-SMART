import streamlit as st
import pandas as pd
from datetime import datetime
import auth

# Initialize authentication state first
auth.initialize_auth_state()

# Page config
st.set_page_config(
    page_title="AHP-SMART System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed" if not auth.is_authenticated() else "expanded"
)
# Hide sidebar on login page
if not auth.is_authenticated():
    st.markdown("""
        <style>
            [data-testid="collapsedControl"] {
                display: none
            }
            section[data-testid="stSidebar"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)


def login_page():
    """Display login page"""
    # Center the login form
    st.markdown("""
        <style>
            .block-container {
                max-width: 600px;
                padding-top: 5rem;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.subheader("AHP-SMART Method")
    
    tab1, tab2 = st.tabs(["Login", "Registrasi"])
    
    with tab1:
        st.markdown("### Login ke Akun Anda")
        
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Email", placeholder="email@example.com")
            password = st.text_input("Password", type="password", placeholder="Masukkan password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if not email or not password:
                    st.error("⚠️ Email dan password harus diisi!")
                else:
                    with st.spinner("Sedang login..."):
                        success, error_msg = auth.sign_in(email, password)
                        
                        if success:
                            st.success("✅ Login berhasil!")
                            st.rerun()
                        else:
                            st.error(f"❌ {error_msg}")
    
    with tab2:
        st.markdown("### Buat Akun Baru")
        
        with st.form("register_form", clear_on_submit=True):
            reg_name = st.text_input("Nama Lengkap", placeholder="Masukkan nama lengkap")
            reg_email = st.text_input("Email", placeholder="email@example.com", key="reg_email")
            reg_password = st.text_input("Password", type="password", placeholder="Min. 6 karakter", key="reg_password")
            reg_password_confirm = st.text_input("Konfirmasi Password", type="password", placeholder="Ketik ulang password")
            
            submit_register = st.form_submit_button("Daftar", use_container_width=True)
            
            if submit_register:
                if not all([reg_name, reg_email, reg_password, reg_password_confirm]):
                    st.error("⚠️ Semua field harus diisi!")
                elif reg_password != reg_password_confirm:
                    st.error("⚠️ Password tidak cocok!")
                elif len(reg_password) < 6:
                    st.error("⚠️ Password minimal 6 karakter!")
                else:
                    with st.spinner("Sedang mendaftarkan akun..."):
                        user_metadata = {
                            'fname': reg_name,
                            'full_name': reg_name
                        }
                        # auto_login=True untuk langsung login setelah registrasi
                        success, error_msg = auth.sign_up(reg_email, reg_password, user_metadata, auto_login=True)
                        
                        if success:
                            st.success("✅ Registrasi berhasil! Mengalihkan ke dashboard...")
                            st.rerun()
                        else:
                            st.error(f"❌ {error_msg}")


def dashboard_page():
    """Display main dashboard for authenticated users"""
    # Get user info using helper functions
    user_email = auth.get_user_email()
    user_name = auth.get_user_metadata('fname', auth.get_user_metadata('full_name', 'User'))
    
    # Sidebar
    with st.sidebar:
        if st.button("Logout", use_container_width=True):
            success, error_msg = auth.sign_out()
            if success:
                st.success("Berhasil logout!")
                st.rerun()
            else:
                st.error(f"Logout gagal: {error_msg}")
    
    # Main content
    st.title("📊 Dashboard Admin AHP-SMART")
    st.markdown(f"### Selamat datang, {user_name}! 👋")

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


def main():
    """Main application logic"""
    # Check authentication
    if not auth.is_authenticated():
        login_page()
    else:
        dashboard_page()


if __name__ == "__main__":
    main()
