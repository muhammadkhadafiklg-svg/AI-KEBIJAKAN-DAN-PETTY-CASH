import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests

# ==========================================
# 1. PENGATURAN HALAMAN & DESAIN MINIMALIS
# ==========================================
# Layout diubah menjadi "centered" agar kolom chat lebih fokus dan nyaman dibaca
st.set_page_config(page_title="Petty Cash AI", page_icon="✨", layout="centered")

# CSS Kustom untuk mempercantik UI (Menyembunyikan menu, membulatkan tombol)
st.markdown("""
    <style>
        /* Sembunyikan elemen bawaan Streamlit */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Desain tombol obrolan baru */
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
        
        /* Jarak untuk input chat */
        .stChatInputContainer {
            padding-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SIDEBAR (PANEL SAMPING PROFESIONAL)
# ==========================================
with st.sidebar:
    # Logo dan Nama Aplikasi
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://cdn-icons-png.flaticon.com/512/2942/2942813.png" width="70" style="margin-bottom: 10px;">
            <h2 style="margin: 0; color: #1E1E1E; font-size: 22px;">Finance AI</h2>
            <p style="color: #666666; font-size: 13px;">Sistem Asisten Petty Cash</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 **Tips:**\nKetikkan nama barang atau transaksi secara spesifik (misal: *'beli materai'*, *'bayar listrik'*).")
    
    st.divider()
    
    if st.button("🔄 Bersihkan Obrolan", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.divider()
    
    # Profil Pembuat (Tampilan ID Card Korporat)
    st.markdown("""
        <div style="text-align: center; margin-top: 40px; padding: 15px; background-color: #f8f9fa; border-radius: 10px; border: 1px solid #eeeeee;">
            <p style="font-size: 11px; color: #888888; margin: 0; text-transform: uppercase; letter-spacing: 1px;">Developed By</p>
            <p style="font-size: 16px; font-weight: bold; color: #2c3e50; margin: 5px 0 2px 0;">M Khadafi Zainal</p>
            <p style="font-size: 12px; font-weight: 600; color: #0056b3; margin: 0;">Finance Representative</p>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. HEADER UTAMA (BANNER BERSIH)
# ==========================================
st.markdown("""
    <div style="background-color: #f4f7f6; padding: 20px 25px; border-radius: 12px; margin-bottom: 30px; border-left: 5px solid #0056b3;">
        <h3 style="margin: 0; color: #1a1a1a; font-size: 24px;">✨ AI Petty Cash & COA</h3>
        <p style="margin: 8px 0 0 0; color: #555555; font-size: 15px;">Dapatkan panduan kode COA dan validasi aturan klaim perusahaan secara instan.</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 4. AUTENTIKASI API KEY
# ==========================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except KeyError:
    st.error("API Key belum dimasukkan di menu Secrets Streamlit!")
    st.stop()

# ==========================================
# 5. FUNGSI TARIK DATA (CSV)
# ==========================================
def buat_link_csv(url):
    if "/d/" in url and "/edit" in url:
        return f"https://docs.google.com/spreadsheets/d/{url.split('/d/')[1].split('/edit')[0]}/export?format=csv"
    return None

@st.cache_data(ttl=3600) 
def tarik_data():
    try:
        r = requests.get("https://docs.google.com/document/d/1mx8BqBj8FsTf0LIdkIXkrXb-DeLmGmt-_ndpdv99nto/export?format=txt")
        aturan = r.text if r.status_code == 200 else "Gagal baca aturan."
        
        l1 = buat_link_csv("https://docs.google.com/spreadsheets/d/1fjzpfQNVNmtMBJ9-ihmILOncZOsjJHhJv3uptZhQH6c/edit?usp=sharing")
        l2 = buat_link_csv("https://docs.google.com/spreadsheets/d/1jCvhYPqyTDJkpismwkPmz3z-wMDs2nE7xC0Doh4cEBI/edit?usp=sharing")
        l3 = buat_link_csv("https://docs.google.com/spreadsheets/d/1SmLN23EHaZOR-ujT9SJifnnFC4tkzIjo9o3KYmXBFD4/edit?usp=sharing")
        
        d1 = pd.read_csv(l1).head(300).to_string(index=False) if l1 else ""
        d2 = pd.read_csv(l2).head(300).to_string(index=False) if l2 else ""
        d3 = pd.read_csv(l3).head(300).to_string(index=False) if l3 else ""
        return aturan, d1, d2, d3
    except Exception:
        return "", "", "", ""

data_aturan, sheet_1, sheet_2, sheet_3 = tarik_data()

# ==========================================
# 6. INSTRUKSI & MODEL AI
# ==========================================
instruksi = f"""
Anda adalah Asisten AI profesional yang bertugas membantu tim operasional toko mengidentifikasi kode COA dan aturan klaim Petty Cash.
REFERENSI DATA:
1. ATURAN PETTY CASH:\n{data_aturan}\n
2. KAMUS KLAIM:\n{sheet_1}\n
3. MASTER COA 1:\n{sheet_2}\n
4. MASTER COA 2:\n{sheet_3}\n
Jawab dengan ramah, rapi, dan langsung pada intinya. Gunakan format tabel jika diperlukan agar mudah dibaca kasir.
"""

model = genai.GenerativeModel(model_name="gemini-3.8-flash", system_instruction=instruksi)

# ==========================================
# 7. ANTARMUKA OBROLAN
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "model", "content": "Halo! Saya siap membantu pencatatan *Petty Cash* Anda hari ini. Transaksi apa yang ingin Anda cari kode COA-nya?"}
    ]

for msg in st.session_state.messages:
    # Menggunakan ikon simpel dan bersih untuk chat
    ikon = "👤" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=ikon):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ketikkan pencarian Anda di sini..."):
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("model", avatar="✨"):
        tunggu = st.empty()
        tunggu.markdown("⏳ *Memindai database kebijakan perusahaan...*")
        try:
            respon = model.generate_content(prompt)
            tunggu.markdown(respon.text)
            st.session_state.messages.append({"role": "model", "content": respon.text})
        except Exception as e:
            tunggu.error(f"Koneksi terganggu: {e}")
