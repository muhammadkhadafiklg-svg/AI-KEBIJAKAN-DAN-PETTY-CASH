import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests

# ==========================================
# 1. PENGATURAN HALAMAN
# ==========================================
st.set_page_config(page_title="Asisten Petty Cash", page_icon="🤖", layout="wide")
st.title("🤖 Asisten AI Petty Cash & COA")

# ==========================================
# 2. AUTENTIKASI API KEY
# ==========================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except KeyError:
    st.error("API Key belum dimasukkan di menu Secrets Streamlit!")
    st.stop()

# ==========================================
# 3. DETEKSI MESIN OTOMATIS (MEMPERBAIKI ERROR 404)
# ==========================================
# Aplikasi akan mencari mesin yang tersedia khusus untuk API Key Anda
nama_mesin_aktif = None
try:
    daftar_mesin = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            nama_pendek = m.name.replace("models/", "")
            daftar_mesin.append(nama_pendek)
            
    if daftar_mesin:
        # Prioritaskan mesin flash jika ada, jika tidak, pakai mesin apa saja yang pertama kali muncul
        nama_mesin_aktif = next((mesin for mesin in daftar_mesin if 'flash' in mesin), daftar_mesin[0])
except Exception as e:
    st.error(f"Gagal mengecek daftar server Google: {e}")
    st.stop()

if not nama_mesin_aktif:
    st.error("🚨 Kunci API Anda tidak diizinkan mengakses mesin AI apa pun oleh Google. Anda WAJIB membuat Kunci API baru dan pilih opsi 'Create API key in New Project'.")
    st.stop()
else:
    st.caption(f"✅ Berhasil terhubung ke server Google: **{nama_mesin_aktif}**")

# ==========================================
# 4. FUNGSI TARIK DATA (CSV)
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
# 5. INSTRUKSI & MODEL AI
# ==========================================
instruksi = f"""
Anda adalah Asisten AI untuk membantu kasir toko mengidentifikasi kode COA dan aturan klaim Petty Cash.
1. ATURAN:\n{data_aturan}\n
2. KAMUS:\n{sheet_1}\n
3. MASTER 1:\n{sheet_2}\n
4. MASTER 2:\n{sheet_3}\n
Jawab ringkas dan langsung pada intinya.
"""

# Gunakan mesin yang berhasil terdeteksi di Langkah 3
model = genai.GenerativeModel(model_name=nama_mesin_aktif, system_instruction=instruksi)

# ==========================================
# 6. ANTARMUKA OBROLAN
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if st.button("🗑️ Hapus Riwayat Chat"):
    st.session_state.messages = []
    st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ketik pertanyaan kasir (misal: 'COA galon?')..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("model"):
        tunggu = st.empty()
        tunggu.markdown("⏳ *Mencari kode COA...*")
        try:
            respon = model.generate_content(prompt)
            tunggu.markdown(respon.text)
            st.session_state.messages.append({"role": "model", "content": respon.text})
        except Exception as e:
            tunggu.error(f"Error AI: {e}")
