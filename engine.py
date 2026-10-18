import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests

# ==========================================
# 1. PENGATURAN HALAMAN & CSS KUSTOM
# ==========================================
st.set_page_config(page_title="Petty Cash AI", page_icon="💼", layout="wide")

# Menyembunyikan menu bawaan Streamlit agar terlihat lebih profesional
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stChatInput {padding-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SIDEBAR (PANEL SAMPING)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4744/4744315.png", width=100) # Ikon keuangan/buku
    st.title("💼 Info Sistem")
    st.info("Aplikasi AI ini dirancang khusus untuk mempercepat pencarian kode COA dan Aturan Klaim Petty Cash bagi kasir toko.")
    
    st.divider()
    
    if st.button("🔄 Mulai Obrolan Baru", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.divider()
    st.markdown("👨‍💻 **Dibuat oleh:**")
    st.markdown("### M Khadafi Zainal")
    st.caption("*( Finance Representative )*")

# ==========================================
# 3. HEADER UTAMA
# ==========================================
st.title("🤖 AI Assistant Petty Cash")
st.markdown("---")

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
Anda adalah Asisten AI profesional yang bertugas membantu kasir toko mengidentifikasi kode COA dan aturan klaim Petty Cash.
REFERENSI DATA:
1. ATURAN PETTY CASH:\n{data_aturan}\n
2. KAMUS KLAIM:\n{sheet_1}\n
3. MASTER COA 1:\n{sheet_2}\n
4. MASTER COA 2:\n{sheet_3}\n
Jawab dengan ramah, rapi, dan langsung pada intinya. Gunakan tabel jika diperlukan untuk menyajikan data agar mudah dibaca kasir.
"""

model = genai.GenerativeModel(model_name="gemini-3.8-flash", system_instruction=instruksi)

# ==========================================
# 7. ANTARMUKA OBROLAN
# ==========================================
if "messages" not in st.session_state:
    # Memberikan pesan sambutan otomatis dari AI
    st.session_state.messages = [
        {"role": "model", "content": "Halo! Saya adalah Asisten AI Petty Cash Anda. Silakan ketikkan nama barang atau transaksi (contoh: *'beli galon'*, *'service AC'*), dan saya akan mencarikan aturan serta kode COA-nya untuk Anda."}
    ]

# Render isi chat dengan Avatar
for msg in st.session_state.messages:
    ikon = "🧑‍💼" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=ikon):
        st.markdown(msg["content"])

# Kolom Input Chat
if prompt := st.chat_input("Ketikkan barang atau transaksi di sini..."):
    with st.chat_message("user", avatar="🧑‍💼"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("model", avatar="🤖"):
        tunggu = st.empty()
        tunggu.markdown("⏳ *Mencari di database perusahaan...*")
        try:
            respon = model.generate_content(prompt)
            tunggu.markdown(respon.text)
            st.session_state.messages.append({"role": "model", "content": respon.text})
        except Exception as e:
            tunggu.error(f"Terjadi kesalahan pada server AI: {e}")
