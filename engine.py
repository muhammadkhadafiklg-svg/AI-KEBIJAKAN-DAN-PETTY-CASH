import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests

# ==========================================
# 1. PENGATURAN HALAMAN
# ==========================================
st.set_page_config(page_title="Asisten Petty Cash", page_icon="🤖", layout="wide")
st.title("🤖 Asisten AI Petty Cash & COA")
st.caption("Tanyakan aturan Petty Cash, kode COA, atau riwayat klaim di sini.")

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
# 3. FUNGSI TARIK DATA (CSV)
# ==========================================
def buat_link_csv(url):
    if "/d/" in url and "/edit" in url:
        return f"https://docs.google.com/spreadsheets/d/{url.split('/d/')[1].split('/edit')[0]}/export?format=csv"
    return None

@st.cache_data(ttl=3600) 
def tarik_data():
    try:
        # Docs Aturan
        r = requests.get("https://docs.google.com/document/d/1mx8BqBj8FsTf0LIdkIXkrXb-DeLmGmt-_ndpdv99nto/export?format=txt")
        aturan = r.text if r.status_code == 200 else "Gagal baca aturan."
        
        # Link Google Sheets
        l1 = buat_link_csv("https://docs.google.com/spreadsheets/d/1fjzpfQNVNmtMBJ9-ihmILOncZOsjJHhJv3uptZhQH6c/edit?usp=sharing")
        l2 = buat_link_csv("https://docs.google.com/spreadsheets/d/1jCvhYPqyTDJkpismwkPmz3z-wMDs2nE7xC0Doh4cEBI/edit?usp=sharing")
        l3 = buat_link_csv("https://docs.google.com/spreadsheets/d/1SmLN23EHaZOR-ujT9SJifnnFC4tkzIjo9o3KYmXBFD4/edit?usp=sharing")
        
        # Tarik data (dibatasi 300 baris agar memori AI stabil)
        d1 = pd.read_csv(l1).head(300).to_string(index=False) if l1 else ""
        d2 = pd.read_csv(l2).head(300).to_string(index=False) if l2 else ""
        d3 = pd.read_csv(l3).head(300).to_string(index=False) if l3 else ""
        return aturan, d1, d2, d3
    except Exception:
        return "", "", "", ""

data_aturan, sheet_1, sheet_2, sheet_3 = tarik_data()

# ==========================================
# 4. INSTRUKSI & MODEL AI (SUDAH DIKUNCI KE VERSI TERBARU)
# ==========================================
instruksi = f"""
Anda adalah Asisten AI untuk membantu kasir toko mengidentifikasi kode COA dan aturan klaim Petty Cash.
1. ATURAN:\n{data_aturan}\n
2. KAMUS:\n{sheet_1}\n
3. MASTER 1:\n{sheet_2}\n
4. MASTER 2:\n{sheet_3}\n
Jawab ringkas, ramah, dan langsung pada intinya.
"""

# Menggunakan model spesifik yang diminta oleh server Google
model = genai.GenerativeModel(model_name="gemini-3.8-flash", system_instruction=instruksi)

# ==========================================
# 5. ANTARMUKA OBROLAN
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
