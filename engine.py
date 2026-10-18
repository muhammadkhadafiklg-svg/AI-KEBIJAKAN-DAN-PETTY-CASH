import streamlit as st
import pandas as pd
import requests

# ==========================================
# 1. PENGATURAN HALAMAN & DESAIN MINIMALIS
# ==========================================
st.set_page_config(page_title="Pencarian Data Petty Cash & Kebijakan", page_icon="🔍", layout="centered")

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            color: #333333;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            border-color: #0056b3;
            color: #0056b3;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SIDEBAR (PANEL SAMPING)
# ==========================================
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://cdn-icons-png.flaticon.com/512/2942/2942813.png" width="70" style="margin-bottom: 10px;">
            <h2 style="margin: 0; color: #1E1E1E; font-size: 22px;">Pusat Data</h2>
            <p style="color: #666666; font-size: 13px;">Sistem Pencarian Mandiri</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 **Informasi:**\nSistem ini berjalan murni menggunakan database lokal tanpa batasan token AI. Bebas error!")
    
    st.divider()
    
    st.markdown("""
        <div style="text-align: center; margin-top: 40px; padding: 15px; background-color: #f8f9fa; border-radius: 10px; border: 1px solid #eeeeee;">
            <p style="font-size: 11px; color: #888888; margin: 0; text-transform: uppercase; letter-spacing: 1px;">Developed By</p>
            <p style="font-size: 16px; font-weight: bold; color: #2c3e50; margin: 5px 0 2px 0;">M Khadafi Zainal</p>
            <p style="font-size: 12px; font-weight: 600; color: #0056b3; margin: 0;">Finance Representative</p>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. HEADER UTAMA
# ==========================================
st.markdown("""
    <div style="background-color: #f4f7f6; padding: 20px 25px; border-radius: 12px; margin-bottom: 30px; border-left: 5px solid #0056b3;">
        <h3 style="margin: 0; color: #1a1a1a; font-size: 24px;">🔍 Cari Kode COA & Kebijakan Operasional</h3>
        <p style="margin: 8px 0 0 0; color: #555555; font-size: 15px;">Ketik kata kunci untuk melihat data langsung dari Google Sheet secara instan.</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 4. TARIK DATA DARI GOOGLE SHEETS / DOCS
# ==========================================
def buat_link_csv(url):
    if "/d/" in url and "/edit" in url:
        return f"https://docs.google.com/spreadsheets/d/{url.split('/d/')[1].split('/edit')[0]}/export?format=csv"
    return None

@st.cache_data(ttl=3600) 
def tarik_data_mentah():
    try:
        # Tarik Google Doc Aturan (Opsional, ditampilkan sebagai teks)
        r = requests.get("https://docs.google.com/document/d/1mx8BqBj8FsTf0LIdkIXkrXb-DeLmGmt-_ndpdv99nto/export?format=txt")
        aturan = r.text.strip() if r.status_code == 200 else "Gagal baca aturan."
        
        l1 = buat_link_csv("https://docs.google.com/spreadsheets/d/1fjzpfQNVNmtMBJ9-ihmILOncZOsjJHhJv3uptZhQH6c/edit?usp=sharing")
        l2 = buat_link_csv("https://docs.google.com/spreadsheets/d/1jCvhYPqyTDJkpismwkPmz3z-wMDs2nE7xC0Doh4cEBI/edit?usp=sharing")
        l3 = buat_link_csv("https://docs.google.com/spreadsheets/d/1SmLN23EHaZOR-ujT9SJifnnFC4tkzIjo9o3KYmXBFD4/edit?usp=sharing")
        
        df1 = pd.read_csv(l1).dropna(how='all').dropna(axis=1, how='all').fillna("") if l1 else pd.DataFrame()
        df2 = pd.read_csv(l2).dropna(how='all').dropna(axis=1, how='all').fillna("") if l2 else pd.DataFrame()
        df3 = pd.read_csv(l3).dropna(how='all').dropna(axis=1, how='all').fillna("") if l3 else pd.DataFrame()
        
        return aturan, df1, df2, df3
    except Exception:
        return "", pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

data_aturan, df1, df2, df3 = tarik_data_mentah()

# ==========================================
# 5. KOTAK PENCARIAN & HASIL (TANPA AI)
# ==========================================
keyword = st.text_input("✨ Masukkan Kata Kunci Pencarian (Contoh: galon, transport, atk):", placeholder="Ketik di sini...")

if keyword:
    kw = keyword.lower()
    
    st.markdown("### 📊 Hasil Pencarian Data:")
    
    # Fungsi filter tabel
    def filter_tabel(df, nama_tabel):
        if df.empty: return
        mask = df.apply(lambda row: row.astype(str).str.lower().str.contains(kw).any(), axis=1)
        hasil = df[mask]
        if not hasil.empty:
            st.markdown(f"**Ditemukan di {nama_tabel}:**")
            st.dataframe(hasil, use_container_width=True)
            
    filter_tabel(df1, "Kamus COA / Sheet 1")
    filter_tabel(df2, "Master Data 1 / Sheet 2")
    filter_tabel(df3, "Master Data 2 / Sheet 3")
    
    # Cek apakah kata kunci ada di Aturan Google Doc
    if kw in data_aturan.lower():
        st.markdown("**Ditemukan di Dokumen Aturan Perusahaan:**")
        st.info(data_aturan)
        
else:
    st.info("👆 Silakan ketik kata kunci pada kolom di atas untuk mulai mencari data secara instan.")
