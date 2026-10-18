import streamlit as st
import pandas as pd
import requests

# ==========================================
# 1. PENGATURAN HALAMAN & DESAIN CHAT
# ==========================================
st.set_page_config(page_title="AI Petty Cash (Mode Gratis)", page_icon="✨", layout="centered")

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stChatInputContainer { padding-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SIDEBAR (PANEL SAMPING)
# ==========================================
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="margin: 0; color: #1E1E1E; font-size: 22px;">Finance Asisten</h2>
            <p style="color: #0056b3; font-size: 13px; font-weight:bold;">⚡ Mode Bebas Kuota (100% Gratis)</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 **Tips:** Ketik nama barang/transaksi (misal: *ATK, Galon, Tol*). Sistem akan membalas otomatis tanpa batas limit API.")
    
    if st.button("🔄 Bersihkan Obrolan", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ==========================================
# 3. HEADER UTAMA
# ==========================================
st.markdown("""
    <div style="background-color: #f4f7f6; padding: 20px; border-radius: 12px; margin-bottom: 20px; border-left: 5px solid #0056b3;">
        <h3 style="margin: 0; color: #1a1a1a; font-size: 22px;">✨ Chat Operasional Petty Cash</h3>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 4. TARIK DATA DARI GOOGLE SHEETS & DOCS
# ==========================================
def buat_link_csv(url):
    if "/d/" in url and "/edit" in url:
        return f"https://docs.google.com/spreadsheets/d/{url.split('/d/')[1].split('/edit')[0]}/export?format=csv"
    return None

@st.cache_data(ttl=3600) 
def tarik_data_mentah():
    try:
        r = requests.get("https://docs.google.com/document/d/1mx8BqBj8FsTf0LIdkIXkrXb-DeLmGmt-_ndpdv99nto/export?format=txt")
        aturan = r.text.strip() if r.status_code == 200 else ""
        
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
# 5. INISIALISASI CHAT
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "model", "content": "Halo! Saya Asisten Finance M Khadafi Zainal. Apa yang ingin Anda cari hari ini? (Ketik nama transaksi atau barang)"}
    ]

# Tampilkan riwayat chat
for msg in st.session_state.messages:
    ikon = "👤" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=ikon):
        st.markdown(msg["content"])

# ==========================================
# 6. LOGIK "AI SIMULASI" (UBAH DATA JADI KALIMAT)
# ==========================================
if prompt := st.chat_input("Tulis pesan di sini..."):
    # Tampilkan chat user
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("model", avatar="✨"):
        keyword = prompt.lower()
        jawaban_bot = ""
        ditemukan = False
        
        # Fungsi untuk merangkai baris Google Sheet menjadi kalimat peluru (Bullet Points)
        def rangkai_kalimat(df, nama_sumber):
            if df.empty: return ""
            mask = df.apply(lambda row: row.astype(str).str.lower().str.contains(keyword).any(), axis=1)
            hasil = df[mask]
            
            if not hasil.empty:
                # Ambil maksimal 5 hasil agar tidak terlalu panjang di chat
                hasil = hasil.head(5)
                teks = f"\n**Dari {nama_sumber}:**\n"
                for index, row in hasil.iterrows():
                    detail = []
                    for col in df.columns:
                        val = str(row[col]).strip()
                        if val:  # Jika kolom ada isinya
                            detail.append(f"**{col}:** {val}")
                    teks += "✅ " + " | ".join(detail) + "\n"
                return teks
            return ""

        # Cari di ketiga Google Sheet
        hasil_1 = rangkai_kalimat(df1, "Kamus COA")
        hasil_2 = rangkai_kalimat(df2, "Master Data 1")
        hasil_3 = rangkai_kalimat(df3, "Master Data 2")
        
        if hasil_1 or hasil_2 or hasil
